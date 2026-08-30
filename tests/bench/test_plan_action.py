"""Plan de revue : ce qu'une action lève, et ce qu'un plan n'a pas le droit de dire.

Ce que ces tests protègent, dans l'ordre d'importance :

1. **Un plan ne promeut rien.** `expected_status_after_decision` parle au
   conditionnel, et la projection porte `PROJECTED_ONLY` partout.
2. **Un blocage de source ne dit pas pourquoi le texte manque.** Refus,
   document introuvable et acte lu à l'ancrage imprécis appellent trois
   travaux différents ; les confondre enverrait consulter un texte déjà lu.
3. **Un lot de lecture n'est pas un cluster de décision.** L'un partage un
   empêchement, l'autre une question ; seul le second tranche.
4. **L'ordre d'exécution ne touche pas aux priorités.** P0 reste P0 : le rang
   dit par où commencer, pas ce qui est grave.

Aucun accès réseau.
"""

from __future__ import annotations

import copy
import datetime as dt
from pathlib import Path
from typing import Any

import pytest

from src.bench.adjudication import construire
from src.bench.completude import analyser
from src.bench.plan_action import (
    ACTION_PAR_BLOCAGE,
    MARQUE_PROJECTION,
    ActionPrincipale,
    action_principale,
    clusters_de_decision,
    construire_lignes,
    elements_bloquants,
    lots_de_lecture,
    ordre_execution,
    preuve_requise,
    prochaine_action,
    projeter,
)
from src.bench.rapport_plan_action import COLONNES_PLAN, ecrire_plan_csv, plan_action
from src.bench.readiness import BlockerCategory, evaluer
from src.bench.regles import Rule
from src.bench.relecture import AccesSource
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV
from tests.bench.fabriques import REGLE

ARTICLE = (
    "Article 12 Obligations de publication. Les entités assujetties publient "
    "annuellement un rapport détaillant leur dispositif dans un délai de 30 jours."
)
JOUR = dt.date(2026, 8, 30)


def regle(**modifications: Any) -> Rule:
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "id": modifications.pop("id", "RULE-SYNTH-001"),
            "status": "source_checked",
            "verification_method": "primary_text_fetched",
            "priority": "CRITICAL",
            "exceptions_status": "unknown",
            "common_confusions": ["confondre le délai avec celui d'un autre régime"],
            "gold_ready": False,
            "gold_ready_reason": "",
        }
    )
    brut.update(modifications)
    return Rule.model_validate(brut)


def dossier_de(sujet: Rule, article: str = ARTICLE):
    constat = analyser(sujet, article, article, article_verifie=True, concordance=0.9)
    return constat, construire(sujet, constat, evaluer(sujet, constat), "", {sujet.id: sujet})


def dossier_sans_texte(sujet: Rule):
    """Le cas d'une règle dont le texte primaire n'a pas pu être lu."""
    constat = analyser(sujet, "", "", article_verifie=False, concordance=0.0)
    return constat, construire(sujet, constat, evaluer(sujet, constat), "", {sujet.id: sujet})


# --------------------------------------------------------------------------- #
# §2 — une action par règle, et la bonne
# --------------------------------------------------------------------------- #


def test_chaque_blocage_a_une_action_nommee() -> None:
    """Un blocage sans action laisserait une règle sans prochaine étape."""
    assert set(ACTION_PAR_BLOCAGE) == set(BlockerCategory)


def test_une_source_qui_refuse_sappelle_une_consultation() -> None:
    _, dossier = dossier_sans_texte(regle())
    assert dossier.blocage_categorie is BlockerCategory.SOURCE_INCOMPLETE
    assert (
        action_principale(dossier, AccesSource.REFUS_DE_LA_SOURCE)
        is ActionPrincipale.SOURCE_CONSULTATION
    )


def test_une_url_morte_sappelle_un_reancrage() -> None:
    """Aller lire ailleurs ne sert à rien quand l'URL ne désigne plus rien."""
    _, dossier = dossier_sans_texte(regle())
    assert (
        action_principale(dossier, AccesSource.DOCUMENT_INTROUVABLE)
        is ActionPrincipale.SOURCE_REANCHORING
    )


def test_un_acte_deja_lu_ne_se_reconsulte_pas() -> None:
    """Texte récupéré et blocage de source : c'est l'ancrage qui manque, pas le texte."""
    _, dossier = dossier_sans_texte(regle())
    action = action_principale(dossier, AccesSource.TEXTE_RECUPERE)
    assert action is ActionPrincipale.SOURCE_REANCHORING
    assert "article précis" in preuve_requise(action, AccesSource.TEXTE_RECUPERE)
    assert "article précis" not in preuve_requise(action, AccesSource.DOCUMENT_INTROUVABLE)


def test_une_exception_non_tranchee_sappelle_une_adjudication() -> None:
    _, dossier = dossier_de(regle())
    assert dossier.blocage_categorie is BlockerCategory.EXCEPTION_UNRESOLVED
    assert (
        action_principale(dossier, AccesSource.TEXTE_RECUPERE)
        is ActionPrincipale.EXCEPTION_ADJUDICATION
    )


# --------------------------------------------------------------------------- #
# §1, §7 — un plan ne promeut rien
# --------------------------------------------------------------------------- #


def test_le_statut_projete_parle_au_conditionnel() -> None:
    constat, dossier = dossier_de(regle())
    (ligne,) = construire_lignes([dossier], {dossier.rule_id: AccesSource.TEXTE_RECUPERE})
    assert "possible si" in ligne.expected_status_after_decision
    assert "n'est pas accordé" in ligne.expected_status_after_decision
    assert constat is not None


def test_sur_un_texte_non_lu_le_plan_dit_ce_quil_ignore() -> None:
    """Les blocages qu'un texte fermé révélera ne se devinent pas."""
    _, dossier = dossier_sans_texte(regle())
    (ligne,) = construire_lignes([dossier], {dossier.rule_id: AccesSource.REFUS_DE_LA_SOURCE})
    assert "ne sont pas connus avant" in ligne.expected_status_after_decision
    assert not ligne.acheve_la_regle


def test_la_projection_est_marquee_partout() -> None:
    constat, dossier = dossier_de(regle())
    (ligne,) = construire_lignes([dossier], {dossier.rule_id: AccesSource.TEXTE_RECUPERE})
    projection = projeter([ligne], {dossier.rule_id: constat}, 12, 9, 9)
    rendu = plan_action(
        [ligne], [], [], projection, ["un blocage"], "faire ceci", "empreinte", JOUR
    )
    section = rendu.split("## Simulation")[1].split("## BLOCKING ITEMS")[0]
    assert section.count(MARQUE_PROJECTION) >= 3
    assert "| `validated` | 12 |" in rendu
    assert "éligible" in section


def test_une_regle_dont_le_texte_manque_nest_jamais_comptee_comme_achevee() -> None:
    _, dossier = dossier_sans_texte(regle())
    (ligne,) = construire_lignes([dossier], {dossier.rule_id: AccesSource.REFUS_DE_LA_SOURCE})
    projection = projeter([ligne], {}, 12, 9, 9)
    assert projection.eligibles_apres_arbitrage == 0


# --------------------------------------------------------------------------- #
# §5 — deux axes de regroupement qui ne disent pas la même chose
# --------------------------------------------------------------------------- #


def test_un_lot_de_lecture_regroupe_par_document() -> None:
    dossiers = [dossier_sans_texte(regle(id=f"RULE-SYNTH-00{n}"))[1] for n in (1, 2)]
    lignes = construire_lignes(
        dossiers, {d.rule_id: AccesSource.REFUS_DE_LA_SOURCE for d in dossiers}
    )
    (lot,) = lots_de_lecture(lignes)
    assert lot.nature == "lot de lecture"
    assert lot.regles_debloquees == 2
    assert lot.regles_achevees == 0, "une consultation ne tranche aucune décision"


def test_une_regle_seule_ne_fait_pas_un_lot() -> None:
    """L'annoncer comme un lot gonflerait le rendement affiché."""
    _, dossier = dossier_sans_texte(regle())
    lignes = construire_lignes([dossier], {dossier.rule_id: AccesSource.REFUS_DE_LA_SOURCE})
    assert lots_de_lecture(lignes) == []


def test_un_cluster_de_decision_porte_la_question_partagee() -> None:
    dossiers = [dossier_de(regle(id=f"RULE-SYNTH-00{n}"))[1] for n in (1, 2)]
    lignes = construire_lignes(
        dossiers, {d.rule_id: AccesSource.TEXTE_RECUPERE for d in dossiers}
    )
    (cluster,) = clusters_de_decision(dossiers, lignes)
    assert cluster.nature == "cluster de décision"
    assert cluster.regles_debloquees == 2
    assert "?" in cluster.question_unique


# --------------------------------------------------------------------------- #
# §6 — l'ordre n'est pas la gravité
# --------------------------------------------------------------------------- #


def test_une_consultation_collective_passe_avant_une_decision_p0_isolee() -> None:
    """Même rendement, pas même gravité : le plan trie par ce qu'une action débloque."""
    bloquees = [dossier_sans_texte(regle(id=f"LCB-{n}"))[1] for n in (1, 2, 3)]
    isolee = dossier_de(regle(id="P0-SEULE"))[1]
    acces = {d.rule_id: AccesSource.REFUS_DE_LA_SOURCE for d in bloquees}
    acces[isolee.rule_id] = AccesSource.TEXTE_RECUPERE

    lignes = construire_lignes([*bloquees, isolee], acces)
    groupes = lots_de_lecture(lignes)
    etapes = ordre_execution(lignes, groupes)

    assert etapes[0].nature == "lot de lecture"
    assert etapes[0].regles_debloquees == 3
    assert etapes[-1].regles == ("P0-SEULE",)
    # Les priorités elles-mêmes ne bougent pas.
    assert {ligne.priority for ligne in lignes} == {"P0"}


def test_la_prochaine_action_est_unique_et_concrete() -> None:
    bloquees = [dossier_sans_texte(regle(id=f"LCB-{n}"))[1] for n in (1, 2)]
    lignes = construire_lignes(
        bloquees, {d.rule_id: AccesSource.REFUS_DE_LA_SOURCE for d in bloquees}
    )
    etapes = ordre_execution(lignes, lots_de_lecture(lignes))
    suivante = prochaine_action(etapes)
    assert suivante.startswith("SOURCE_CONSULTATION")
    assert "LCB-1" in suivante and "LCB-2" in suivante


# --------------------------------------------------------------------------- #
# §1, §8 — la queue et les critères de sortie
# --------------------------------------------------------------------------- #


def test_la_queue_csv_porte_les_colonnes_de_la_specification(tmp_path: Path) -> None:
    import csv

    _, dossier = dossier_de(regle())
    lignes = construire_lignes([dossier], {dossier.rule_id: AccesSource.TEXTE_RECUPERE})
    chemin = tmp_path / "plan.csv"
    ecrire_plan_csv(lignes, chemin)
    with chemin.open(encoding=ENCODAGE_CSV, newline="") as flux:
        lecteur = csv.DictReader(flux, delimiter=SEPARATEUR_CSV)
        assert tuple(lecteur.fieldnames or ()) == COLONNES_PLAN
        (ligne,) = list(lecteur)
    assert ligne["proposed_action"] == "EXCEPTION_ADJUDICATION"
    assert ligne["source_access_status"] == "TEXTE_RECUPERE"
    assert ligne["exact_decision_required"].endswith("?")


def test_une_anomalie_dintegrite_prime_sur_tout() -> None:
    _, dossier = dossier_de(regle())
    lignes = construire_lignes([dossier], {dossier.rule_id: AccesSource.TEXTE_RECUPERE})
    bloquants = elements_bloquants(lignes, ["rejeu_divergent RULE-SYNTH-001"], family_ready=9)
    assert "anomalie" in bloquants[0]


def test_un_texte_jamais_lu_figure_parmi_les_bloquants() -> None:
    _, dossier = dossier_sans_texte(regle())
    lignes = construire_lignes([dossier], {dossier.rule_id: AccesSource.REFUS_DE_LA_SOURCE})
    bloquants = elements_bloquants(lignes, [], family_ready=9)
    assert any("texte primaire n'a pas été lu" in item for item in bloquants)


@pytest.mark.parametrize("action", list(ActionPrincipale))
def test_chaque_action_dit_ce_quelle_exige_comme_preuve(action: ActionPrincipale) -> None:
    """Sans preuve attendue, « revue faite » ne se contrôle pas."""
    assert preuve_requise(action, AccesSource.TEXTE_RECUPERE).strip()
