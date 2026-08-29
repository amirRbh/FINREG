"""Étape 5 — juge LLM et file de revue. Le juge est un faux fournisseur local."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from src.providers.base import Requete
from src.providers.fake import FauxFournisseur
from src.schema import (
    Axe,
    ConfigFournisseur,
    Flag,
    Item,
    NotesAxes,
    ReponseBrute,
    Score,
)
from src.scoring.deterministe import evaluer
from src.scoring.juge import Juge, SortieJugeInvalide, analyser_sortie, construire_message
from src.scoring.references import Registre
from src.scoring.revue import (
    CorrectionInvalide,
    appliquer_corrections,
    detecter_divergences,
    exporter_csv,
    lire_corrections,
)
from src.securite import PrivateCorpusLeakError
from tests.fabriques import item

REGISTRE = Registre.charger(Path("registry/references.json"))
PROMPT_JUGE = "Barème du juge."


class JugeFactice(FauxFournisseur):
    """Rend une sortie imposée, sans réseau."""

    def __init__(self, sortie: str, zero_retention: bool = True):
        super().__init__(
            ConfigFournisseur(
                id="juge", nom="Juge", editeur="Interne",
                adaptateur="fake", modele="juge-factice", zero_retention=zero_retention,
            )
        )
        self.sortie = sortie

    async def completer(self, requete: Requete, timeout_s: float) -> str:
        self.appels.append(requete)
        return self.sortie


def sortie(exactitude=2, sourcing=2, calibration=2, exploitabilite=2, justification="Correct."):
    return json.dumps(
        {
            "notes": {
                "exactitude": exactitude, "sourcing": sourcing,
                "calibration": calibration, "exploitabilite": exploitabilite,
            },
            "justification": justification,
        },
        ensure_ascii=False,
    )


def reponse_brute(texte: str, index_run: int = 0) -> ReponseBrute:
    return ReponseBrute(
        item_id="SFDR-0001", fournisseur_id="f-a", modele="modele-a",
        index_run=index_run, hash_prompt="h", texte=texte,
    )


def noter(sujet: Item, texte: str, juge_sortie: str, index_run: int = 0) -> Score:
    constat = evaluer(sujet, texte, REGISTRE)
    juge = Juge(JugeFactice(juge_sortie), PROMPT_JUGE)
    return asyncio.run(juge.noter(sujet, reponse_brute(texte, index_run), constat))


# --------------------------------------------------------------------------- #
# Sortie JSON stricte
# --------------------------------------------------------------------------- #


def test_sortie_json_valide():
    rendu = analyser_sortie(sortie(2, 1, 1, 2, "Bien sourcé."))
    assert rendu.notes.as_dict() == {
        "exactitude": 2, "sourcing": 1, "calibration": 1, "exploitabilite": 2
    }
    assert rendu.justification == "Bien sourcé."


def test_sortie_dans_un_bloc_de_code_est_acceptee():
    assert analyser_sortie(f"```json\n{sortie()}\n```").notes.exactitude == 2


def test_sortie_precedee_de_bavardage_est_recuperee():
    assert analyser_sortie(f"Voici mon évaluation :\n{sortie()}").notes.exactitude == 2


@pytest.mark.parametrize(
    "mauvaise",
    [
        "pas du json du tout",
        "{ ceci n'est pas du json }",
        '{"notes": {"exactitude": 2}}',
        '{"notes": {"exactitude": 5, "sourcing": 1, "calibration": 1, "exploitabilite": 1}, "justification": "x"}',
        '{"notes": {"exactitude": 1, "sourcing": 1, "calibration": 1, "exploitabilite": 1}}',
        '{"notes": {"exactitude": "deux", "sourcing": 1, "calibration": 1, "exploitabilite": 1}, "justification": "x"}',
        "[1, 2, 3]",
    ],
)
def test_sortie_non_conforme_est_une_erreur_pas_une_note_par_defaut(mauvaise):
    with pytest.raises(SortieJugeInvalide):
        analyser_sortie(mauvaise)


def test_justification_vide_refusee():
    mauvaise = json.dumps(
        {"notes": {"exactitude": 1, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
         "justification": ""}
    )
    with pytest.raises(SortieJugeInvalide):
        analyser_sortie(mauvaise)


# --------------------------------------------------------------------------- #
# Articulation avec l'étage déterministe
# --------------------------------------------------------------------------- #


def test_le_juge_ne_peut_pas_depasser_les_plafonds():
    """Un fait vérifié mécaniquement prime sur la générosité du juge."""
    score = noter(
        Item.model_validate(item()),
        "L'article 47 du règlement (UE) 2019/2088 impose cette publication.",
        sortie(2, 2, 2, 2),
    )
    assert score.notes.sourcing == 0
    assert score.notes.exactitude == 1
    assert score.notes.calibration == 1
    assert score.notes.exploitabilite == 2
    assert Flag.HALLUCINATION_SOURCE in score.flags
    assert score.origine == "juge"


def test_le_juge_nest_pas_appele_quand_le_deterministe_tranche():
    """Économie d'appel : quand tout est plafonné à 0, il n'y a plus rien à noter."""
    sujet = Item.model_validate(item(type="abstention", erreurs_disqualifiantes=["obligatoire"]))
    constat = evaluer(sujet, "C'est obligatoire.", REGISTRE)
    for axe in Axe:
        constat.plafonds[axe] = 0

    juge_factice = JugeFactice(sortie())
    juge = Juge(juge_factice, PROMPT_JUGE)
    score = asyncio.run(juge.noter(sujet, reponse_brute("C'est obligatoire."), constat))

    assert juge_factice.nb_appels == 0
    assert score.origine == "deterministe"
    assert score.total() == 0


def test_le_constat_automatique_est_transmis_au_juge():
    sujet = Item.model_validate(item())
    texte = "L'article 47 du règlement (UE) 2019/2088 impose cette publication."
    message = construire_message(sujet, texte, evaluer(sujet, texte, REGISTRE))

    assert "CONSTAT AUTOMATIQUE" in message
    assert "2019/2088:47" in message
    assert sujet.reponse_reference in message


def test_le_juge_est_soumis_au_garde_fou():
    """Le juge voit le texte des items : il ne peut pas y échapper."""
    prive = Item.model_validate(item("private", id="PRIV-1"))
    juge_non_conforme = JugeFactice(sortie(), zero_retention=False)
    juge = Juge(juge_non_conforme, PROMPT_JUGE)
    constat = evaluer(prive, "Réponse.", REGISTRE)

    with pytest.raises(PrivateCorpusLeakError):
        asyncio.run(juge.noter(prive, reponse_brute("Réponse."), constat))

    assert juge_non_conforme.nb_appels == 0


# --------------------------------------------------------------------------- #
# File de revue
# --------------------------------------------------------------------------- #


def scores_divergents(notes_par_run: list[dict]) -> list[Score]:
    from src.schema import ConstatDeterministe

    return [
        Score(
            item_id="SFDR-0001", fournisseur_id="f-a", index_run=index,
            notes=NotesAxes(**notes), constat=ConstatDeterministe(),
        )
        for index, notes in enumerate(notes_par_run)
    ]


def test_ecart_superieur_a_un_point_part_en_revue():
    scores = scores_divergents([
        {"exactitude": 2, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
        {"exactitude": 0, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
        {"exactitude": 1, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
    ])
    entrees = detecter_divergences(scores, seuil=1)

    assert [e.axe for e in entrees] == [Axe.EXACTITUDE]
    assert entrees[0].ecart == 2
    assert entrees[0].notes_par_run == {0: 2, 1: 0, 2: 1}


def test_ecart_dun_point_ne_part_pas_en_revue():
    """« plus d'un point » : un écart de 1 est toléré."""
    scores = scores_divergents([
        {"exactitude": 2, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
        {"exactitude": 1, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
    ])
    assert detecter_divergences(scores, seuil=1) == []


def test_un_seul_run_ne_peut_pas_diverger():
    scores = scores_divergents([{"exactitude": 2, "sourcing": 1, "calibration": 1, "exploitabilite": 1}])
    assert detecter_divergences(scores, seuil=1) == []


def test_aller_retour_csv(tmp_path):
    """Le cœur de la boucle : exporter, corriger à la main, réinjecter."""
    sujet = Item.model_validate(item())
    scores = scores_divergents([
        {"exactitude": 2, "sourcing": 2, "calibration": 1, "exploitabilite": 1},
        {"exactitude": 0, "sourcing": 0, "calibration": 1, "exploitabilite": 1},
    ])
    entrees = detecter_divergences(scores, seuil=1, items={"SFDR-0001": sujet})
    chemin = exporter_csv(entrees, tmp_path / "revue.csv")

    contenu = chemin.read_text(encoding="utf-8-sig")
    assert "item_id;fournisseur_id;axe" in contenu
    assert sujet.question in contenu  # le relecteur a le contexte sous les yeux

    # Correction à la main : on remplit note_humaine sur les deux lignes.
    corrige = contenu.replace(
        "SFDR-0001;f-a;exactitude;run 0 : 2 / run 1 : 0;2;;",
        "SFDR-0001;f-a;exactitude;run 0 : 2 / run 1 : 0;2;1;tranché à 1;",
    ).replace(
        "SFDR-0001;f-a;sourcing;run 0 : 2 / run 1 : 0;2;;",
        "SFDR-0001;f-a;sourcing;run 0 : 2 / run 1 : 0;2;2;source correcte;",
    )
    chemin.write_text(corrige, encoding="utf-8-sig")

    corrections = lire_corrections(chemin)
    assert {(c.axe, c.note) for c in corrections} == {(Axe.EXACTITUDE, 1), (Axe.SOURCING, 2)}

    corriges = appliquer_corrections(scores, corrections)
    assert all(s.notes.exactitude == 1 for s in corriges)
    assert all(s.notes.sourcing == 2 for s in corriges)
    assert all(s.origine == "humain" for s in corriges)
    # Les axes non corrigés ne bougent pas.
    assert all(s.notes.calibration == 1 for s in corriges)


def test_ligne_sans_note_humaine_est_ignoree(tmp_path):
    sujet = Item.model_validate(item())
    scores = scores_divergents([
        {"exactitude": 2, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
        {"exactitude": 0, "sourcing": 1, "calibration": 1, "exploitabilite": 1},
    ])
    chemin = exporter_csv(
        detecter_divergences(scores, seuil=1, items={"SFDR-0001": sujet}), tmp_path / "r.csv"
    )

    assert lire_corrections(chemin) == []
    assert appliquer_corrections(scores, []) == scores


@pytest.mark.parametrize("note", ["3", "-1", "deux", "1.5"])
def test_note_humaine_invalide_bloque_toute_la_reinjection(tmp_path, note):
    """Un fichier partiellement fautif ne s'applique pas à moitié."""
    chemin = tmp_path / "r.csv"
    chemin.write_text(
        "item_id;fournisseur_id;axe;notes_par_run;ecart;note_humaine;justification_humaine\n"
        f"SFDR-0001;f-a;exactitude;run 0 : 2;2;{note};\n",
        encoding="utf-8-sig",
    )
    with pytest.raises(CorrectionInvalide):
        lire_corrections(chemin)


def test_axe_inconnu_refuse(tmp_path):
    chemin = tmp_path / "r.csv"
    chemin.write_text(
        "item_id;fournisseur_id;axe;notes_par_run;ecart;note_humaine;justification_humaine\n"
        "SFDR-0001;f-a;elegance;run 0 : 2;2;1;\n",
        encoding="utf-8-sig",
    )
    with pytest.raises(CorrectionInvalide, match="axe inconnu"):
        lire_corrections(chemin)


def test_colonnes_manquantes_refusees(tmp_path):
    chemin = tmp_path / "r.csv"
    chemin.write_text("item_id;note_humaine\nSFDR-0001;1\n", encoding="utf-8-sig")
    with pytest.raises(CorrectionInvalide, match="colonnes manquantes"):
        lire_corrections(chemin)


def test_le_bareme_du_juge_est_versionne():
    texte = Path("prompts/judge.txt").read_text(encoding="utf-8")
    for axe in ("EXACTITUDE", "SOURCING", "CALIBRATION", "EXPLOITABILITE"):
        assert axe in texte
    assert "objet JSON" in texte
