"""Exploitabilité d'une règle : `gold_ready`, `family_ready`, intégrité, rejeu.

Ce que ces tests protègent, dans l'ordre d'importance :

1. **`gold_ready` ne peut pas être vrai sans ses prérequis.** C'est la
   correction qui a fait tomber le chiffre de 41 à 9 : un énoncé porteur adossé
   à une source non consultée ne donne pas un gold prêt, il donne un gold qui a
   l'air prêt.
2. **Le registre reconstruit exactement le Rulebook livré.** Une ancienne
   formulation validée a réellement ressuscité une fois ; le rejeu complet est
   ce qui l'attrape.
3. **La file de revue pose des questions, pas des étiquettes.** « Revue
   requise » ne se traite pas : chaque entrée doit nommer la disposition et
   l'alternative.

Aucun accès réseau.
"""

from __future__ import annotations

import copy
import datetime as dt
from pathlib import Path
from typing import Any

import pytest

from src.bench.completude import ConstatCompletude, PREREQUIS_GOLD, analyser
from src.bench.rapport_readiness import (
    COLONNES_READINESS,
    RECOMMANDATIONS,
    recommandation,
    synthese,
)
from src.bench.readiness import (
    BlockerCategory,
    ConstatIntegrite,
    ORDRE_BLOCAGES,
    comparer_au_rejeu,
    controles_integrite,
    evaluer,
    prioriser,
)
from src.bench.regles import Rule
from src.bench.rulebook import Priority, RuleStatus
from src.bench.verification import Verification, appliquer, fusionner_registre
from tests.bench.fabriques import REGLE

ARTICLE = (
    "Article 12 Obligations de publication. 1. Les entités assujetties publient "
    "annuellement un rapport détaillant leur dispositif, dans un délai de 30 jours "
    "à compter de la clôture. 2. Par dérogation au paragraphe 1, les entités dont "
    "le total de bilan est inférieur à 20 000 000 EUR publient ce rapport tous les "
    "deux ans."
)

ENONCE = (
    "Les entités assujetties publient annuellement un rapport détaillant leur "
    "dispositif, dans un délai de 30 jours à compter de la clôture."
)


def regle(**modifications: Any) -> Rule:
    """Règle synthétique validée, porteuse, et complète — le cas favorable."""
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "status": "validated",
            "verification_method": "primary_text_fetched",
            "statement": ENONCE,
            "exceptions_status": "identified_and_incorporated",
            "exceptions": ["Par dérogation au paragraphe 1, les entités dont…"],
            "common_confusions": ["confondre le délai avec celui d'un autre régime"],
            "gold_ready": True,
            "gold_ready_reason": "énoncé porteur d'un fait vérifiable",
        }
    )
    brut.update(modifications)
    return Rule.model_validate(brut)


def constat_de(sujet: Rule, **surcharges: Any) -> ConstatCompletude:
    base = analyser(sujet, ARTICLE, ARTICLE, article_verifie=True, concordance=0.9)
    if not surcharges:
        return base
    criteres_gold = dict(base.criteres_gold)
    criteres_gold.update(surcharges.pop("criteres_gold", {}))
    return ConstatCompletude(
        **{
            **{
                k: getattr(base, k)
                for k in (
                    "rule_id", "domain", "priority", "structures", "exceptions_extraites",
                    "renvois", "exceptions_status", "gold_ready", "gold_ready_reason",
                    "criteres", "statut_propose", "motifs", "temporal_status",
                    "cross_reference_checked",
                )
            },
            "criteres_gold": criteres_gold,
            **surcharges,
        }
    )


# --------------------------------------------------------------------------- #
# §5 — gold_ready ne peut pas ignorer ses prérequis
# --------------------------------------------------------------------------- #


def test_le_cas_favorable_est_pret_sur_les_deux_seuils() -> None:
    etat = evaluer(regle(), constat_de(regle()))
    assert etat.gold_ready
    assert etat.family_ready
    assert etat.blocages == ()


@pytest.mark.parametrize(
    ("critere", "categorie"),
    [
        ("source_primaire_verifiee", BlockerCategory.SOURCE_INCOMPLETE),
        ("article_verifie", BlockerCategory.SOURCE_INCOMPLETE),
        ("exceptions_recherchees", BlockerCategory.EXCEPTION_UNRESOLVED),
        ("temporalite_etablie", BlockerCategory.TEMPORAL_UNRESOLVED),
        ("renvois_verifies", BlockerCategory.CROSS_REFERENCE_UNRESOLVED),
        ("affirmations_negatives_resolues", BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED),
    ],
)
def test_chaque_prerequis_manquant_interdit_gold_ready(
    critere: str, categorie: BlockerCategory
) -> None:
    """Le point qui a fait tomber 41 à 9 : la portance ne suffit jamais."""
    sujet = regle()
    constat = constat_de(sujet, gold_ready=False, criteres_gold={critere: False})
    etat = evaluer(sujet, constat)

    assert not etat.gold_ready
    assert not etat.family_ready
    assert categorie in {b.category for b in etat.blocages}


def test_les_prerequis_couvrent_les_conditions_de_la_specification() -> None:
    """Exceptions, temporalité, source, article, renvois : les cinq sont exigés."""
    assert set(PREREQUIS_GOLD) == {
        "source_primaire_verifiee",
        "article_verifie",
        "exceptions_recherchees",
        "temporalite_etablie",
        "renvois_verifies",
        "affirmations_negatives_resolues",
    }


# --------------------------------------------------------------------------- #
# §1 — ce que family_ready ajoute
# --------------------------------------------------------------------------- #


def test_family_ready_implique_toujours_gold_ready() -> None:
    for statut in ("draft", "source_checked", "validated"):
        sujet = regle(status=statut) if statut == "validated" else regle(
            status=statut, gold_ready=False, gold_ready_reason=""
        )
        etat = evaluer(sujet, constat_de(sujet))
        assert not etat.family_ready or etat.gold_ready, statut


def test_une_regle_prete_mais_non_validee_nancre_aucune_famille() -> None:
    """`gold_ready` parle du contenu ; `family_ready` exige aussi la signature."""
    sujet = regle(status="source_checked", gold_ready=False, gold_ready_reason="")
    etat = evaluer(sujet, constat_de(sujet))
    assert etat.gold_ready
    assert not etat.family_ready
    assert etat.blocker_category == BlockerCategory.HUMAN_REVIEW_REQUIRED.value
    assert etat.family_blocker == "statut_non_validated"


def test_une_regle_exacte_et_muette_nancre_aucune_famille() -> None:
    """Sans confusion ni piège, aucun angle ne se déduit : vraie et stérile."""
    sujet = regle(common_confusions=[], reasoning_traps=[], candidate_question_families=[])
    etat = evaluer(sujet, constat_de(sujet))
    assert etat.gold_ready
    assert not etat.family_ready
    assert etat.blocker_category == BlockerCategory.SCHEMA_INCOMPLETE.value


def test_le_blocage_principal_suit_lordre_de_fondamentalite() -> None:
    """On ne reproche pas son abstraction à une règle dont la source manque."""
    sujet = regle(status="source_checked", gold_ready=False, gold_ready_reason="")
    constat = constat_de(
        sujet, gold_ready=False, criteres_gold={"source_primaire_verifiee": False}
    )
    etat = evaluer(sujet, constat)
    assert etat.blocker_category == BlockerCategory.SOURCE_INCOMPLETE.value
    # La source précède tout le reste dans l'ordre déclaré.
    assert ORDRE_BLOCAGES[0] is BlockerCategory.SOURCE_INCOMPLETE


def test_les_categories_de_blocage_sont_normalisees() -> None:
    """Neuf catégories, pas une par règle."""
    assert len(list(BlockerCategory)) == 9
    assert set(ORDRE_BLOCAGES) == set(BlockerCategory)


# --------------------------------------------------------------------------- #
# §3 — priorisation
# --------------------------------------------------------------------------- #


def _blocage(categorie: BlockerCategory):
    from src.bench.readiness import Blocage

    return [Blocage(categorie, "critere", "explication")]


@pytest.mark.parametrize(
    ("priorite", "categorie", "attendu"),
    [
        (Priority.CRITICAL, BlockerCategory.EXCEPTION_UNRESOLVED, "P0"),
        (Priority.CRITICAL, BlockerCategory.RULE_TOO_ABSTRACT, "P1"),
        (Priority.HIGH, BlockerCategory.TEMPORAL_UNRESOLVED, "P1"),
        (Priority.HIGH, BlockerCategory.SCHEMA_INCOMPLETE, "P2"),
        (Priority.MEDIUM, BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED, "P2"),
        (Priority.MEDIUM, BlockerCategory.RULE_TOO_ABSTRACT, "P3"),
        (Priority.LOW, BlockerCategory.EXCEPTION_UNRESOLVED, "P3"),
    ],
)
def test_la_priorite_est_deterministe(
    priorite: Priority, categorie: BlockerCategory, attendu: str
) -> None:
    assert prioriser(regle(priority=priorite.value), _blocage(categorie)) == attendu


def test_une_regle_sans_blocage_na_pas_de_priorite() -> None:
    assert prioriser(regle(), []) == ""


# --------------------------------------------------------------------------- #
# §2 — la file dit quoi trancher, pas « revue requise »
# --------------------------------------------------------------------------- #


def test_chaque_decision_nomme_ce_quil_faut_trancher() -> None:
    for categorie, critere in (
        (BlockerCategory.EXCEPTION_UNRESOLVED, "exceptions_recherchees"),
        (BlockerCategory.TEMPORAL_UNRESOLVED, "temporalite_etablie"),
        (BlockerCategory.SOURCE_INCOMPLETE, "source_primaire_verifiee"),
        (BlockerCategory.CROSS_REFERENCE_UNRESOLVED, "renvois_verifies"),
    ):
        sujet = regle()
        constat = constat_de(sujet, gold_ready=False, criteres_gold={critere: False})
        etat = evaluer(sujet, constat)
        assert etat.decision_requise.startswith("Le relecteur humain doit décider")
        assert etat.decision_requise.rstrip().endswith(".")
        assert "revue requise" not in etat.decision_requise.lower()
        # La question nomme la disposition concernée.
        assert sujet.source.article in etat.decision_requise or sujet.source.text in etat.decision_requise


# --------------------------------------------------------------------------- #
# §6 — le rejeu du registre
# --------------------------------------------------------------------------- #


def _constat(rule_id: str, **modifications: Any) -> Verification:
    base = {
        "rule_id": rule_id,
        "verdict": "confirme",
        "verification_method": "primary_text_review",
        "verified_by": "Relecteur de test",
        "verification_date": "2026-08-29",
        "target_status": "source_checked",
    }
    base.update(modifications)
    return Verification.model_validate(base)


def test_le_registre_rejoue_reconstruit_exactement_le_rulebook(tmp_path: Path) -> None:
    """Cycle complet : vérification, correction, complétude, rejeu.

    C'est le test qui aurait attrapé la résurrection observée : un énoncé corrigé
    puis une incorporation d'exceptions, rejoués dans l'ordre, doivent redonner
    la dernière formulation — pas une intermédiaire.
    """
    initiale = Rule.model_validate(
        {
            **copy.deepcopy(REGLE),
            "status": "draft",
            "verification_method": "model_knowledge_unverified",
            "statement": "Formulation d'origine, imprécise.",
            "source": {**REGLE["source"], "verified_by": "", "verification_date": None},
            "gold_ready": False,
            "gold_ready_reason": "",
        }
    )
    rid = initiale.id

    etapes = [
        _constat(rid),
        _constat(
            rid,
            verdict="corrige",
            statement="Formulation corrigée, au plus près du texte.",
            target_status="source_checked",
        ),
        _constat(
            rid,
            target_status="validated",
            exceptions_status="identified_and_incorporated",
            exceptions=["Par dérogation au paragraphe 1, les entités…"],
            gold_ready=True,
            gold_ready_reason="énoncé porteur d'un fait vérifiable",
        ),
    ]

    courantes = [initiale]
    registre: list[Verification] = []
    for etape in etapes:
        courantes = appliquer(courantes, [etape])
        registre = fusionner_registre([etape], tmp_path / "absent.json") if not registre else [
            *registre,
            etape,
        ]

    livree = courantes[0]
    assert livree.version == 3
    assert livree.statement == "Formulation corrigée, au plus près du texte."
    assert livree.status is RuleStatus.VALIDATED

    anomalies = comparer_au_rejeu([livree], [initiale], registre)
    assert anomalies == [], [str(a) for a in anomalies]


def test_le_rejeu_detecte_la_resurrection_dune_formulation_validee() -> None:
    """Le cas réel : une correction disparue, l'ancien énoncé validé à sa place."""
    initiale = Rule.model_validate(
        {
            **copy.deepcopy(REGLE),
            "status": "draft",
            "verification_method": "model_knowledge_unverified",
            "statement": "Formulation d'origine, imprécise.",
            "source": {**REGLE["source"], "verified_by": "", "verification_date": None},
            "gold_ready": False,
            "gold_ready_reason": "",
        }
    )
    rid = initiale.id
    registre = [
        _constat(rid),
        _constat(
            rid,
            verdict="corrige",
            statement="Formulation corrigée, au plus près du texte.",
            target_status="source_checked",
        ),
    ]
    # Le Rulebook « livré » a gardé l'énoncé d'origine malgré la correction.
    ressuscitee = Rule.model_validate(
        {
            **initiale.model_dump(mode="json"),
            "status": "validated",
            "verification_method": "primary_text_review",
            "source": {
                **REGLE["source"],
                "verified_by": "Relecteur de test",
                "verification_date": "2026-08-29",
            },
            "exceptions_status": "none_identified",
            "gold_ready": True,
            "gold_ready_reason": "motif quelconque",
        }
    )
    anomalies = comparer_au_rejeu([ressuscitee], [initiale], registre)
    assert any(a.controle == "rejeu_divergent" for a in anomalies)


# --------------------------------------------------------------------------- #
# §7 — intégrité
# --------------------------------------------------------------------------- #


def test_une_regle_prete_sans_source_est_signalee() -> None:
    # Une règle en `draft` : le schéma interdit d'aller plus loin sans source
    # consultée, mais rien ne l'empêche de porter un `gold_ready` erroné.
    sujet = regle(
        status="draft",
        source={**REGLE["source"], "verified_by": "", "verification_date": None},
        verification_method="model_knowledge_unverified",
    )
    constat = constat_de(sujet, gold_ready=False, criteres_gold={"source_primaire_verifiee": False})
    etat = evaluer(sujet, constat)
    anomalies = controles_integrite([sujet], {sujet.id: constat}, {sujet.id: etat}, [])
    assert any(a.controle == "gold_ready_sans_source" for a in anomalies)


def test_une_regle_prete_avec_exceptions_inconnues_est_signalee() -> None:
    sujet = regle(exceptions_status="unknown", exceptions=[])
    constat = constat_de(sujet)
    etat = evaluer(sujet, constat)
    anomalies = controles_integrite([sujet], {sujet.id: constat}, {sujet.id: etat}, [])
    assert any(a.controle == "gold_ready_exceptions_inconnues" for a in anomalies)


def test_une_divergence_entre_stocke_et_calcule_est_signalee() -> None:
    sujet = regle()
    constat = constat_de(sujet, gold_ready=False, criteres_gold={"temporalite_etablie": False})
    etat = evaluer(sujet, constat)
    anomalies = controles_integrite([sujet], {sujet.id: constat}, {sujet.id: etat}, [])
    assert any(a.controle == "gold_ready_divergent" for a in anomalies)


def test_une_regle_validee_non_corroboree_est_signalee() -> None:
    sujet = regle()
    constat = analyser(sujet, ARTICLE, ARTICLE, article_verifie=True, concordance=0.05)
    etat = evaluer(sujet, constat)
    anomalies = controles_integrite([sujet], {sujet.id: constat}, {sujet.id: etat}, [])
    assert any(a.controle == "validee_non_corroboree" for a in anomalies)


def test_le_cas_favorable_ne_declenche_aucune_anomalie() -> None:
    sujet = regle()
    constat = constat_de(sujet)
    etat = evaluer(sujet, constat)
    assert controles_integrite([sujet], {sujet.id: constat}, {sujet.id: etat}, []) == []


# --------------------------------------------------------------------------- #
# §8 — recommandation déterministe
# --------------------------------------------------------------------------- #


def test_une_anomalie_dintegrite_prime_sur_tout() -> None:
    sujet = regle()
    etat = evaluer(sujet, constat_de(sujet))
    anomalie = ConstatIntegrite("quelconque", sujet.id, "peu importe")
    verdict, motif = recommandation([etat], [anomalie])
    assert verdict == "NOT_READY"
    assert "incohérent" in motif


def test_sans_regle_prete_le_rulebook_nest_pas_pret() -> None:
    sujet = regle(status="source_checked", gold_ready=False, gold_ready_reason="")
    etat = evaluer(sujet, constat_de(sujet))
    assert recommandation([etat], [])[0] == "NOT_READY"


def test_un_arbitrage_p0_ou_p1_impose_la_revue_prealable() -> None:
    pret = regle(id="RULE-SYNTH-OK")
    bloquee = regle(id="RULE-SYNTH-P0", priority="CRITICAL")
    constat_bloquee = constat_de(
        bloquee, gold_ready=False, criteres_gold={"exceptions_recherchees": False}
    )
    etats = [evaluer(pret, constat_de(pret)), evaluer(bloquee, constat_bloquee)]
    assert recommandation(etats, [])[0] == "READY_AFTER_HUMAN_REVIEW"


def test_sans_blocage_critique_la_generation_est_ouverte() -> None:
    pret = regle()
    assert recommandation([evaluer(pret, constat_de(pret))], [])[0] == (
        "READY_FOR_FAMILY_GENERATION"
    )


def test_la_recommandation_est_toujours_lune_des_trois() -> None:
    sujet = regle()
    verdict, _ = recommandation([evaluer(sujet, constat_de(sujet))], [])
    assert verdict in RECOMMANDATIONS


def test_la_synthese_porte_la_forme_demandee() -> None:
    sujet = regle()
    etat = evaluer(sujet, constat_de(sujet))
    texte = synthese([etat], [sujet], [], (11, 0))
    for attendu in (
        "Rulebook", "Status", "Readiness", "Blockers", "Human review",
        "Critical integrity tests", "Recommendation",
        "gold_ready:", "family_ready:", "cross_reference:", "P0:", "passed:",
    ):
        assert attendu in texte, attendu


def test_la_matrice_porte_les_colonnes_demandees() -> None:
    assert list(COLONNES_READINESS) == [
        "ID", "status", "gold_ready", "family_ready",
        "family_blocker", "blocker_category", "explanation",
    ]


# --------------------------------------------------------------------------- #
# Le Rulebook livré
# --------------------------------------------------------------------------- #


def test_le_rulebook_livre_na_aucune_anomalie_dintegrite() -> None:
    """Le contrôle qui garde le dépôt : aucune incohérence tolérée en l'état."""
    from scripts.auditer_readiness import _rulebook_initial
    from src.bench.qc_rulebook import charger_rulebook
    from src.bench.verification import charger_registre

    livrees = charger_rulebook()
    anomalies = comparer_au_rejeu(livrees, _rulebook_initial(), charger_registre())
    assert anomalies == [], [str(a) for a in anomalies]


def test_aucune_regle_livree_nest_prete_sans_ses_prerequis() -> None:
    """§5 appliqué au dépôt : pas de `gold_ready` sur une base incomplète."""
    from src.bench.qc_rulebook import charger_rulebook
    from src.bench.rulebook import EXCEPTIONS_ABOUTIES, NegativeClaimStatus

    for sujet in charger_rulebook():
        if not sujet.gold_ready:
            continue
        assert sujet.source.is_verified, sujet.id
        assert sujet.exceptions_status in EXCEPTIONS_ABOUTIES, sujet.id
        assert all(
            c.status is not NegativeClaimStatus.UNVERIFIED for c in sujet.negative_claims
        ), sujet.id
