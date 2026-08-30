"""Pack d'arbitrage P0/P1 : ce que le relecteur reçoit, et ce qu'il ne reçoit pas.

Ce que ces tests protègent, dans l'ordre d'importance :

1. **Aucune décision ne s'écrit toute seule.** Le dossier sort avec ses colonnes
   de décision vides, et une décision non signée — ou un « rien trouvé » sans
   périmètre attesté — est refusée par le schéma, pas par une consigne.
2. **Un fait n'est pas une lecture.** `TEXTUAL_FACTS` ne porte que ce qui est
   écrit ; ce qui demande un arbitrage vit dans `INTERPRETIVE_QUESTION`.
3. **Le regroupement partage une question, jamais une règle.** Deux règles du
   même article gardent leur énoncé, leur version et leur décision.
4. **La relecture des artefacts ne peut rien inventer** : si le blocage relu
   n'est pas celui que l'audit avait publié, rien ne s'écrit.

Aucun accès réseau.
"""

from __future__ import annotations

import copy
import datetime as dt
from pathlib import Path
from typing import Any

import pytest

from src.bench.adjudication import (
    DecisionAdjudication,
    DecisionRelecteur,
    PropositionMecanique,
    cluster_id,
    construire,
    preparer,
    regroupements,
)
from src.bench.completude import CRITERES_VALIDATION, ConstatCompletude, analyser
from src.bench.rapport_adjudication import (
    COLONNES_A_REMPLIR,
    ecrire_dossier,
    lire_decisions,
    pack,
    progression,
)
from src.bench.readiness import BlockerCategory, evaluer
from src.bench.regles import Rule
from src.bench.relecture import divergences
from src.bench.rulebook import ExceptionsStatus
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV
from tests.bench.fabriques import REGLE

ARTICLE_AVEC_DEROGATION = (
    "Article 12 Obligations de publication. 1. Les entités assujetties publient "
    "annuellement un rapport détaillant leur dispositif, dans un délai de 30 jours "
    "à compter de la clôture. 2. Par dérogation au paragraphe 1, les entités dont "
    "le total de bilan est inférieur à 20 000 000 EUR publient ce rapport tous les "
    "deux ans."
)
ARTICLE_SANS_STRUCTURE = (
    "Article 12 Obligations de publication. Les entités assujetties publient "
    "annuellement un rapport détaillant leur dispositif dans un délai de 30 jours."
)
ENONCE = (
    "Les entités assujetties publient annuellement un rapport détaillant leur "
    "dispositif, dans un délai de 30 jours à compter de la clôture."
)
JOUR = dt.date(2026, 8, 30)


def regle(**modifications: Any) -> Rule:
    """Règle synthétique consultée mais non validée — le cas qui demande un arbitrage."""
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "id": modifications.pop("id", "RULE-SYNTH-001"),
            "status": "source_checked",
            "verification_method": "primary_text_fetched",
            "statement": ENONCE,
            "priority": "CRITICAL",
            "exceptions_status": "unknown",
            "common_confusions": ["confondre le délai avec celui d'un autre régime"],
            "gold_ready": False,
            "gold_ready_reason": "",
        }
    )
    brut.update(modifications)
    return Rule.model_validate(brut)


def dossier_de(sujet: Rule, article: str = ARTICLE_SANS_STRUCTURE, **surcharges: Any):
    constat = analyser(sujet, article, article, article_verifie=True, concordance=0.9)
    if surcharges:
        constat = ConstatCompletude(
            **{
                **{
                    champ: getattr(constat, champ)
                    for champ in (
                        "rule_id", "domain", "priority", "structures", "exceptions_extraites",
                        "renvois", "exceptions_status", "gold_ready", "gold_ready_reason",
                        "criteres", "criteres_gold", "statut_propose", "motifs",
                        "temporal_status", "cross_reference_checked",
                    )
                },
                **surcharges,
            }
        )
    etat = evaluer(sujet, constat)
    return construire(sujet, constat, etat, "Article 12 Obligations de publication…", {sujet.id: sujet})


# --------------------------------------------------------------------------- #
# §7, §11 — aucune décision ne s'écrit toute seule
# --------------------------------------------------------------------------- #


def test_le_dossier_csv_sort_avec_ses_colonnes_de_decision_vides(tmp_path: Path) -> None:
    """Une valeur par défaut dans ces colonnes serait un arbitrage que personne n'a rendu."""
    import csv

    chemin = tmp_path / "dossier.csv"
    ecrire_dossier([dossier_de(regle())], chemin)
    with chemin.open(encoding=ENCODAGE_CSV, newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=SEPARATEUR_CSV))
    assert lignes, "le dossier doit porter une ligne par règle"
    for colonne in COLONNES_A_REMPLIR:
        assert lignes[0][colonne] == ""
    assert lignes[0]["rule_id"] == "RULE-SYNTH-001"


def test_une_absence_sans_perimetre_examine_est_refusee() -> None:
    """« Je n'ai pas trouvé » ne devient jamais « il n'y en a pas » sans périmètre."""
    with pytest.raises(ValueError, match="source_scope"):
        DecisionAdjudication.model_validate(
            {
                "rule_id": "RULE-SYNTH-001",
                "reviewer_decision": "NONE_IDENTIFIED",
                "reviewer_name": "Relecteur de test",
                "review_date": "2026-08-30",
            }
        )


def test_une_absence_attestee_sur_son_perimetre_est_recevable() -> None:
    decision = DecisionAdjudication.model_validate(
        {
            "rule_id": "RULE-SYNTH-001",
            "reviewer_decision": "NONE_IDENTIFIED",
            "reviewer_name": "Relecteur de test",
            "review_date": "2026-08-30",
            "source_scope": "acte entier, version consolidée au 2026-01-01",
        }
    )
    assert decision.reviewer_decision is DecisionRelecteur.NONE_IDENTIFIED


def test_une_decision_anonyme_est_refusee() -> None:
    """Une décision que personne ne signe n'est opposable à personne."""
    with pytest.raises(ValueError, match="reviewer_name"):
        DecisionAdjudication.model_validate(
            {
                "rule_id": "RULE-SYNTH-001",
                "reviewer_decision": "REQUIRES_FURTHER_REVIEW",
                "review_notes": "à revoir avec le texte consolidé",
            }
        )


@pytest.mark.parametrize(
    ("decision", "motif"),
    [
        ("IDENTIFIED_AND_INCORPORATED", "incorporer une exception, c'est l'écrire"),
        ("RULE_REFORMULATED", "enonce_reformule"),
        ("REQUIRES_FURTHER_REVIEW", "review_notes"),
    ],
)
def test_chaque_decision_exige_ce_qu_elle_affirme(decision: str, motif: str) -> None:
    with pytest.raises(ValueError, match=motif):
        DecisionAdjudication.model_validate(
            {
                "rule_id": "RULE-SYNTH-001",
                "reviewer_decision": decision,
                "reviewer_name": "Relecteur de test",
                "review_date": "2026-08-30",
            }
        )


def test_la_lecture_des_decisions_est_tout_ou_rien(tmp_path: Path) -> None:
    """Un dossier à moitié valide laisserait le Rulebook dans un état non arbitré."""
    chemin = tmp_path / "dossier.csv"
    ecrire_dossier([dossier_de(regle()), dossier_de(regle(id="RULE-SYNTH-002"))], chemin)
    contenu = chemin.read_text(encoding=ENCODAGE_CSV).splitlines()
    # Une ligne valide, une ligne irrecevable (absence sans périmètre).
    contenu[1] = contenu[1].replace(";;;;;;;", ";NONE_IDENTIFIED;Relecteur;2026-08-30;acte entier;;;")
    contenu[2] = contenu[2].replace(";;;;;;;", ";NONE_IDENTIFIED;Relecteur;2026-08-30;;;;")
    chemin.write_text("\n".join(contenu) + "\n", encoding=ENCODAGE_CSV)

    with pytest.raises(ValueError, match="irrecevable"):
        lire_decisions(chemin)


def test_une_ligne_vide_n_est_pas_une_decision(tmp_path: Path) -> None:
    chemin = tmp_path / "dossier.csv"
    ecrire_dossier([dossier_de(regle())], chemin)
    assert lire_decisions(chemin) == []


# --------------------------------------------------------------------------- #
# §5 — un fait n'est pas une lecture
# --------------------------------------------------------------------------- #


def test_les_faits_textuels_ne_portent_que_ce_qui_est_ecrit() -> None:
    dossier = dossier_de(regle())
    joints = " ".join(dossier.textual_facts)
    assert "signée le" in joints
    assert "existe dans l'acte cité" in joints
    # Ce qui demande un arbitrage n'a rien à faire parmi les faits.
    assert dossier.interpretive_question not in dossier.textual_facts
    assert "demande un juriste" not in joints


def test_la_question_neutre_est_unique_et_binaire() -> None:
    dossier = dossier_de(regle())
    assert dossier.neutral_legal_question.count("?") == 1
    assert " ou " in dossier.neutral_legal_question


def test_le_perimetre_d_une_absence_porte_sur_l_acte_entier() -> None:
    """Une absence ne s'établit pas sur l'article cité : le périmètre le dit."""
    sujet = regle(
        negative_claims=[{"claim": "Le texte fixerait un seuil de 10 %.", "status": "unverified"}]
    )
    dossier = dossier_de(sujet)
    assert dossier.blocage_categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED
    assert "entier" in dossier.perimetre_a_examiner
    assert "pas sur un extrait" in dossier.perimetre_a_examiner


def test_les_autres_blocages_restent_visibles() -> None:
    """La priorité P0 tient souvent à un blocage que la question n'aborde pas."""
    sujet = regle(
        negative_claims=[{"claim": "Le texte fixerait un seuil de 10 %.", "status": "unverified"}]
    )
    dossier = dossier_de(sujet)
    restants = " ".join(dossier.blocages_restants)
    assert "EXCEPTION_UNRESOLVED" in restants
    assert "statut_non_validated" in restants


# --------------------------------------------------------------------------- #
# §6 — la proposition mécanique dit ce que l'automate a vu, rien de plus
# --------------------------------------------------------------------------- #


def test_sans_structure_reperee_la_proposition_nomme_le_perimetre_balaye() -> None:
    dossier = dossier_de(regle(), ARTICLE_SANS_STRUCTURE)
    assert (
        dossier.mechanical_proposal
        is PropositionMecanique.NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE
    )


def test_une_structure_limitante_sans_phrase_isolable_rend_l_exception_probable() -> None:
    dossier = dossier_de(
        regle(),
        ARTICLE_SANS_STRUCTURE,
        exceptions_status=ExceptionsStatus.IDENTIFIED_BUT_NOT_INCORPORATED,
    )
    assert dossier.mechanical_proposal is PropositionMecanique.EXCEPTION_LIKELY


def test_sans_texte_lu_rien_ne_se_tranche_sur_ce_fondement() -> None:
    sujet = regle()
    constat = analyser(sujet, "", "", article_verifie=False, concordance=0.0)
    etat = evaluer(sujet, constat)
    dossier = construire(sujet, constat, etat, "", {sujet.id: sujet})
    assert dossier.blocage_categorie is BlockerCategory.SOURCE_INCOMPLETE
    assert dossier.mechanical_proposal is PropositionMecanique.INSUFFICIENT_SOURCE
    assert "hors de cet environnement" in dossier.perimetre_a_examiner


# --------------------------------------------------------------------------- #
# §9 — le regroupement partage une question, jamais une règle
# --------------------------------------------------------------------------- #


def test_deux_regles_du_meme_article_partagent_le_dossier_de_revue() -> None:
    premiere, seconde = regle(), regle(id="RULE-SYNTH-002")
    assert cluster_id(premiere, BlockerCategory.EXCEPTION_UNRESOLVED) == cluster_id(
        seconde, BlockerCategory.EXCEPTION_UNRESOLVED
    )


def test_une_autre_question_sur_le_meme_article_ne_se_regroupe_pas() -> None:
    """Un article commun ne suffit pas : c'est la question qui se partage."""
    sujet = regle()
    assert cluster_id(sujet, BlockerCategory.EXCEPTION_UNRESOLVED) != cluster_id(
        sujet, BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED
    )


def test_le_regroupement_ne_fusionne_pas_les_regles() -> None:
    dossiers = [dossier_de(regle()), dossier_de(regle(id="RULE-SYNTH-002"))]
    groupes = regroupements(dossiers)
    assert len(groupes) == 1
    (groupe,) = groupes.values()
    assert [d.rule_id for d in groupe] == ["RULE-SYNTH-001", "RULE-SYNTH-002"]
    assert {d.current_statement for d in groupe} == {ENONCE}
    assert all(not hasattr(d, "reviewer_decision") for d in groupe)


# --------------------------------------------------------------------------- #
# §1, §8 — P0 d'abord, et rien d'autre que P0/P1
# --------------------------------------------------------------------------- #


def test_le_pack_traite_les_p0_avant_les_p1_et_ignore_le_reste() -> None:
    critique = regle(
        id="RULE-SYNTH-001",
        priority="CRITICAL",
        negative_claims=[{"claim": "Le texte fixerait un seuil.", "status": "unverified"}],
    )
    moindre = regle(id="RULE-SYNTH-002", priority="MEDIUM")
    regles = [moindre, critique]
    constats = {
        r.id: analyser(r, ARTICLE_SANS_STRUCTURE, ARTICLE_SANS_STRUCTURE, article_verifie=True, concordance=0.9)
        for r in regles
    }
    etats = {r.id: evaluer(r, constats[r.id]) for r in regles}
    dossiers = preparer(regles, constats, etats, {r.id: "" for r in regles})

    assert [d.rule_id for d in dossiers] == ["RULE-SYNTH-001"]
    assert dossiers[0].priorite_revue == "P0"

    rendu = pack(dossiers, "empreinte-test", ("data/verification/dossier-completude.csv",), JOUR)
    assert "## P0 — REVIEW REQUIRED" in rendu
    # La règle de priorité moindre n'entre pas dans le pack : on arbitre P0 et P1.
    assert "RULE-SYNTH-002" not in rendu
    assert "## P1 — REVIEW REQUIRED" not in rendu


def test_le_pack_ne_redige_aucune_question_de_benchmark() -> None:
    """La phase prépare des décisions : elle ne rédige ni item, ni famille."""
    dossier = dossier_de(regle())
    rendu = pack([dossier], "empreinte-test", ("artefact",), JOUR)
    assert "réponse de référence" not in rendu
    assert "twin" not in rendu.lower()
    assert "NEUTRAL_LEGAL_QUESTION" in rendu


# --------------------------------------------------------------------------- #
# §13 — la progression compte, elle ne projette pas
# --------------------------------------------------------------------------- #


def test_la_progression_n_annonce_aucun_etat_apres() -> None:
    sujet = regle()
    dossier = dossier_de(sujet)
    constat = analyser(sujet, ARTICLE_SANS_STRUCTURE, ARTICLE_SANS_STRUCTURE, article_verifie=True, concordance=0.9)
    rendu = progression([dossier], [], [sujet], {sujet.id: evaluer(sujet, constat)}, JOUR)
    assert "| P0 | 1 | 0 | 1 |" in rendu
    assert "| `gold_ready` | 0 | — |" in rendu
    assert "prévisionnel" in rendu


# --------------------------------------------------------------------------- #
# §12 — la relecture des artefacts ne peut rien inventer
# --------------------------------------------------------------------------- #


def test_un_blocage_relu_different_du_blocage_publie_arrete_tout() -> None:
    sujet = regle()
    constat = analyser(sujet, ARTICLE_SANS_STRUCTURE, ARTICLE_SANS_STRUCTURE, article_verifie=True, concordance=0.9)
    etats = {sujet.id: evaluer(sujet, constat)}
    publie = {
        sujet.id: {
            "family_blocker": "temporalite_etablie",
            "blocker_category": "TEMPORAL_UNRESOLVED",
        }
    }
    ecarts = divergences(etats, publie)
    assert ecarts and sujet.id in ecarts[0]


def test_une_regle_absente_des_artefacts_publies_est_signalee() -> None:
    sujet = regle()
    constat = analyser(sujet, ARTICLE_SANS_STRUCTURE, ARTICLE_SANS_STRUCTURE, article_verifie=True, concordance=0.9)
    ecarts = divergences({sujet.id: evaluer(sujet, constat)}, {})
    assert "absente de la matrice" in ecarts[0]


def test_les_criteres_relus_sont_ceux_que_l_analyse_produit() -> None:
    """Deux listes de critères qui divergeraient feraient mentir la relecture."""
    sujet = regle()
    constat = analyser(sujet, ARTICLE_AVEC_DEROGATION, ARTICLE_AVEC_DEROGATION, article_verifie=True, concordance=0.9)
    assert tuple(constat.criteres) == CRITERES_VALIDATION
