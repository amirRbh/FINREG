"""Étape 6 — agrégation, export public et dossier de run auditable."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

from src.aggregate import agreger
from src.export import ExportInvalide, exporter
from src.io_utils import lire_json
from src.run import Execution, charger_run, ecrire_run, executer, hash_run
from src.schema import (
    Config,
    ConfigExecution,
    ConfigFournisseur,
    ConfigJuge,
    ConstatDeterministe,
    Corpus,
    Flag,
    Item,
    NotesAxes,
    Score,
)
from tests.fabriques import ecrire_corpus, item

FOURNISSEURS = [
    ConfigFournisseur(id="m-a", nom="Modèle A", editeur="Éditeur A",
                      adaptateur="fake", modele="modele-a"),
    ConfigFournisseur(id="m-b", nom="Modèle B", editeur="Éditeur B",
                      adaptateur="fake", modele="modele-b"),
]


def config(**modifications) -> Config:
    base = {
        "corpus": Corpus.PUBLIC,
        "fournisseurs": FOURNISSEURS,
        "execution": ConfigExecution(nb_runs=2, concurrence=2, requetes_par_minute=100000),
        "juge": ConfigJuge(adaptateur="fake-juge"),
    }
    base.update(modifications)
    return Config(**base)


def score(item_id, fournisseur_id, index_run, notes, flags=None) -> Score:
    return Score(
        item_id=item_id, fournisseur_id=fournisseur_id, index_run=index_run,
        notes=NotesAxes(**notes), flags=flags or [], constat=ConstatDeterministe(),
    )


PARFAIT = {"exactitude": 2, "sourcing": 2, "calibration": 2, "exploitabilite": 2}
NUL = {"exactitude": 0, "sourcing": 0, "calibration": 0, "exploitabilite": 0}
MOYEN = {"exactitude": 1, "sourcing": 1, "calibration": 1, "exploitabilite": 1}


# --------------------------------------------------------------------------- #
# Agrégation
# --------------------------------------------------------------------------- #


def test_score_global_est_la_moyenne_des_items():
    items = [Item.model_validate(item(id="A-1")), Item.model_validate(item(id="A-2"))]
    scores = [
        score("A-1", "m-a", 0, PARFAIT),
        score("A-2", "m-a", 0, NUL),
    ]
    agregats = agreger(config(), items, scores)
    par_id = {a.fournisseur_id: a for a in agregats}

    assert par_id["m-a"].score_global == 50.0
    assert par_id["m-a"].nb_items == 2


def test_ecart_type_mesure_linstabilite_entre_runs():
    items = [Item.model_validate(item(id="A-1"))]
    scores = [score("A-1", "m-a", 0, PARFAIT), score("A-1", "m-a", 1, NUL)]

    agregat = next(a for a in agreger(config(), items, scores) if a.fournisseur_id == "m-a")
    assert agregat.score_global == 50.0
    assert agregat.ecart_type == 50.0


def test_ecart_type_nul_quand_le_modele_est_stable():
    items = [Item.model_validate(item(id="A-1"))]
    scores = [score("A-1", "m-a", 0, MOYEN), score("A-1", "m-a", 1, MOYEN)]

    agregat = next(a for a in agreger(config(), items, scores) if a.fournisseur_id == "m-a")
    assert agregat.ecart_type == 0.0


def test_taux_hallucination_source():
    items = [Item.model_validate(item(id="A-1")), Item.model_validate(item(id="A-2"))]
    scores = [
        score("A-1", "m-a", 0, MOYEN, [Flag.HALLUCINATION_SOURCE]),
        score("A-2", "m-a", 0, MOYEN),
    ]
    agregat = next(a for a in agreger(config(), items, scores) if a.fournisseur_id == "m-a")
    assert agregat.taux_hallucination_source == 50.0


def test_taux_dabstention_correcte_porte_sur_les_items_dabstention():
    """Le taux ne se calcule que sur les questions qui appelaient une abstention."""
    items = [
        Item.model_validate(item(id="ABS-1", type="abstention")),
        Item.model_validate(item(id="ABS-2", type="abstention")),
        Item.model_validate(item(id="ORD-1")),
    ]
    scores = [
        score("ABS-1", "m-a", 0, MOYEN, [Flag.ABSTENTION]),
        score("ABS-2", "m-a", 0, MOYEN, [Flag.SURCONFIANCE]),
        score("ORD-1", "m-a", 0, MOYEN),
    ]
    agregat = next(a for a in agreger(config(), items, scores) if a.fournisseur_id == "m-a")

    assert agregat.nb_items_abstention == 2
    assert agregat.taux_abstention_correcte == 50.0


def test_abstention_doit_tenir_sur_tous_les_runs():
    """S'abstenir une fois sur deux n'est pas une abstention correcte."""
    items = [Item.model_validate(item(id="ABS-1", type="abstention"))]
    scores = [
        score("ABS-1", "m-a", 0, MOYEN, [Flag.ABSTENTION]),
        score("ABS-1", "m-a", 1, MOYEN, [Flag.SURCONFIANCE]),
    ]
    agregat = next(a for a in agreger(config(), items, scores) if a.fournisseur_id == "m-a")
    assert agregat.taux_abstention_correcte == 0.0


def test_scores_par_domaine_et_par_axe():
    items = [
        Item.model_validate(item(id="S-1", domaine="SFDR")),
        Item.model_validate(item(id="D-1", domaine="DORA")),
    ]
    scores = [
        score("S-1", "m-a", 0, PARFAIT),
        score("D-1", "m-a", 0, {"exactitude": 2, "sourcing": 0, "calibration": 2, "exploitabilite": 0}),
    ]
    agregat = next(a for a in agreger(config(), items, scores) if a.fournisseur_id == "m-a")

    assert agregat.scores_domaines == {"DORA": 50.0, "SFDR": 100.0}
    assert agregat.scores_axes == {
        "exactitude": 2.0, "sourcing": 1.0, "calibration": 2.0, "exploitabilite": 1.0
    }


def test_classement_par_score_decroissant():
    items = [Item.model_validate(item(id="A-1"))]
    scores = [score("A-1", "m-a", 0, NUL), score("A-1", "m-b", 0, PARFAIT)]

    assert [a.fournisseur_id for a in agreger(config(), items, scores)] == ["m-b", "m-a"]


def test_modele_sans_score_reste_dans_le_classement():
    items = [Item.model_validate(item(id="A-1"))]
    agregats = agreger(config(), items, [score("A-1", "m-a", 0, PARFAIT)])

    absent = next(a for a in agregats if a.fournisseur_id == "m-b")
    assert absent.score_global == 0.0
    assert absent.nb_items == 0


# --------------------------------------------------------------------------- #
# Export public
# --------------------------------------------------------------------------- #


def exporter_jeu(tmp_path, items, scores, reponses=None, cfg=None):
    cfg = cfg or config()
    agregats = agreger(cfg, items, scores)
    exporter(
        tmp_path, cfg, items, scores, agregats,
        reponses or {}, dt.date(2026, 9, 15),
    )
    return lire_json(tmp_path / "results.json"), lire_json(tmp_path / "questions.json")


def test_export_au_format_du_site(tmp_path):
    """Les clés doivent correspondre exactement au contrat de src/lib/finreg.ts."""
    items = [Item.model_validate(item(id="SFDR-0001"))]
    scores = [score("SFDR-0001", "m-a", 0, PARFAIT), score("SFDR-0001", "m-a", 1, PARFAIT)]
    resultats, questions = exporter_jeu(
        tmp_path, items, scores, {("SFDR-0001", "m-a", 0): "Réponse du modèle."}
    )

    assert set(resultats) == {"date_execution", "nb_questions", "nb_runs", "modeles"}
    assert resultats["date_execution"] == "2026-09-15"
    assert resultats["nb_questions"] == 1
    assert set(resultats["modeles"][0]) == {
        "id", "nom", "editeur", "score_global", "taux_hallucination_source",
        "taux_abstention_correcte", "ecart_type", "scores_domaines", "scores_axes",
    }

    assert set(questions[0]) == {
        "id", "domaine", "type", "difficulte", "question",
        "reponse_reference", "source", "reponses_modeles",
    }
    assert set(questions[0]["source"]) == {"texte", "article", "url"}
    assert set(questions[0]["reponses_modeles"]["m-a"]) == {"texte", "score", "flags"}


def test_la_source_publiee_nexpose_pas_le_verificateur(tmp_path):
    """Le site ne reçoit que les trois champs de son contrat."""
    items = [Item.model_validate(item(id="SFDR-0001"))]
    _, questions = exporter_jeu(tmp_path, items, [score("SFDR-0001", "m-a", 0, PARFAIT)])

    assert "verifie_par" not in json.dumps(questions, ensure_ascii=False)


def test_note_publiee_sur_dix(tmp_path):
    items = [Item.model_validate(item(id="A-1"))]
    resultats_notes = {}
    for notes, attendu in [(PARFAIT, 10), (MOYEN, 5), (NUL, 0)]:
        _, questions = exporter_jeu(
            tmp_path / str(attendu), items, [score("A-1", "m-a", 0, notes)]
        )
        resultats_notes[attendu] = questions[0]["reponses_modeles"]["m-a"]["score"]

    assert resultats_notes == {10: 10, 5: 5, 0: 0}


def test_texte_publie_vient_du_run_median(tmp_path):
    """Ni le meilleur ni le pire run : celui du milieu."""
    items = [Item.model_validate(item(id="A-1"))]
    scores = [
        score("A-1", "m-a", 0, PARFAIT),
        score("A-1", "m-a", 1, MOYEN),
        score("A-1", "m-a", 2, NUL),
    ]
    reponses = {
        ("A-1", "m-a", 0): "le meilleur",
        ("A-1", "m-a", 1): "le median",
        ("A-1", "m-a", 2): "le pire",
    }
    _, questions = exporter_jeu(tmp_path, items, scores, reponses)

    assert questions[0]["reponses_modeles"]["m-a"]["texte"] == "le median"


def test_les_flags_sont_lunion_des_runs(tmp_path):
    """Un défaut apparu sur un seul run reste visible."""
    items = [Item.model_validate(item(id="A-1"))]
    scores = [
        score("A-1", "m-a", 0, MOYEN, [Flag.HALLUCINATION_SOURCE]),
        score("A-1", "m-a", 1, MOYEN, [Flag.SOURCING_INCOMPLET]),
    ]
    _, questions = exporter_jeu(tmp_path, items, scores)

    assert questions[0]["reponses_modeles"]["m-a"]["flags"] == [
        "hallucination_source", "sourcing_incomplet"
    ]


def test_un_item_prive_est_exclu_de_lexport(tmp_path):
    items = [
        Item.model_validate(item(id="PUB-1")),
        Item.model_validate(item("private", id="PRIV-1")),
    ]
    scores = [score("PUB-1", "m-a", 0, PARFAIT), score("PRIV-1", "m-a", 0, PARFAIT)]
    resultats, questions = exporter_jeu(tmp_path, items, scores)

    assert [q["id"] for q in questions] == ["PUB-1"]
    assert resultats["nb_questions"] == 1
    assert "PRIV-1" not in json.dumps(questions, ensure_ascii=False)


def test_aucun_contenu_prive_ne_fuit_dans_lexport(tmp_path):
    prive = Item.model_validate(item("private", id="PRIV-1", question="SECRET-QUESTION"))
    items = [Item.model_validate(item(id="PUB-1")), prive]
    scores = [score("PUB-1", "m-a", 0, PARFAIT), score("PRIV-1", "m-a", 0, PARFAIT)]

    exporter_jeu(tmp_path, items, scores, {("PRIV-1", "m-a", 0): "réponse privée"})
    tout = (tmp_path / "questions.json").read_text(encoding="utf-8")
    tout += (tmp_path / "results.json").read_text(encoding="utf-8")

    assert "SECRET-QUESTION" not in tout
    assert "réponse privée" not in tout


def test_domaine_inconnu_du_site_bloque_lexport(tmp_path):
    """Un domaine que le site ne sait pas afficher est une erreur, pas un silence."""
    items = [Item.model_validate(item(id="X-1", domaine="EMIR"))]
    with pytest.raises(ExportInvalide, match="domaines inconnus"):
        exporter_jeu(tmp_path, items, [score("X-1", "m-a", 0, PARFAIT)])


def test_export_sans_reponse_connue_ne_plante_pas(tmp_path):
    items = [Item.model_validate(item(id="A-1"))]
    _, questions = exporter_jeu(tmp_path, items, [score("A-1", "m-a", 0, PARFAIT)], {})
    assert questions[0]["reponses_modeles"]["m-a"]["texte"] == ""


# --------------------------------------------------------------------------- #
# Dossier de run
# --------------------------------------------------------------------------- #


def projet_jouet(tmp_path) -> tuple[Path, Config]:
    """Un projet complet et minuscule, pour exécuter la chaîne de bout en bout."""
    racine = tmp_path / "projet"
    (racine / "prompts").mkdir(parents=True)
    (racine / "prompts" / "system.txt").write_text("Prompt système.\n", encoding="utf-8")
    (racine / "prompts" / "judge.txt").write_text("Barème du juge.\n", encoding="utf-8")
    (racine / "registry").mkdir()
    (racine / "registry" / "references.json").write_text(
        Path("registry/references.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    ecrire_corpus(
        racine / "corpus",
        public=[item(id="A-1", question="Première question ?"),
                item(id="A-2", question="Seconde question ?")],
    )

    cfg = config(
        racine_corpus=str(racine / "corpus"),
        chemin_prompt_systeme=str(racine / "prompts" / "system.txt"),
        chemin_prompt_juge=str(racine / "prompts" / "judge.txt"),
        chemin_registre=str(racine / "registry" / "references.json"),
        racine_cache=str(racine / ".cache"),
        racine_runs=str(racine / "runs"),
    )
    return racine, cfg


def test_le_dossier_de_run_contient_tout_ce_quun_audit_demande(tmp_path):
    racine, cfg = projet_jouet(tmp_path)
    dossier = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))

    assert dossier.name == "2026-09-15-1430"
    for fichier in ("config.json", "empreintes.json", "reponses.json",
                    "scores.json", "resume.json", "revue.csv"):
        assert (dossier / fichier).is_file(), fichier

    empreintes = lire_json(dossier / "empreintes.json")
    assert len(empreintes["prompt_systeme"]["sha256"]) == 64
    assert len(empreintes["prompt_juge"]["sha256"]) == 64
    assert len(empreintes["corpus"]["version"]) == 64
    assert empreintes["corpus"]["nb_items"] == 2

    gelee = lire_json(dossier / "config.json")
    assert gelee["execution"]["temperature"] == 0.0
    assert gelee["execution"]["nb_runs"] == 2


def test_un_run_nest_jamais_reecrit_en_place(tmp_path):
    racine, cfg = projet_jouet(tmp_path)
    horodatage = dt.datetime(2026, 9, 15, 14, 30)
    ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), horodatage)

    with pytest.raises(FileExistsError):
        ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), horodatage)


def test_deux_runs_identiques_produisent_les_memes_fichiers(tmp_path):
    """La reproductibilité à l'identique, c'est ce qui rend le rapport opposable."""
    racine, cfg = projet_jouet(tmp_path)

    a = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))
    b = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 16, 9, 5))

    assert a.name != b.name
    assert hash_run(a) == hash_run(b)


def test_relire_un_run_dont_le_corpus_a_change_est_refuse(tmp_path):
    racine, cfg = projet_jouet(tmp_path)
    dossier = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))

    ecrire_corpus(
        Path(cfg.racine_corpus),
        public=[item(id="A-1", question="Question modifiée après coup ?")],
    )

    with pytest.raises(ValueError, match="corpus a changé"):
        charger_run(dossier)


def test_le_resume_dit_dou_viennent_les_notes(tmp_path):
    racine, cfg = projet_jouet(tmp_path)
    dossier = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))

    resume = lire_json(dossier / "resume.json")
    assert resume["nb_runs"] == 2
    assert resume["nb_items"] == 2
    assert set(resume["origine_des_scores"]) <= {"deterministe", "juge", "humain"}
    assert [m["rang"] for m in resume["classement"]] == [1, 2]
