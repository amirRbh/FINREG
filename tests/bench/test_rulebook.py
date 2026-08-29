"""Phase 6 — contrôle qualité du Regulatory Rulebook."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.bench.qc_rulebook import charger_rulebook, controler, erreurs
from src.bench.regles import Rule
from src.bench.rulebook import (
    CandidateQuestionFamily,
    ExceptionsStatus,
    NegativeClaim,
    Priority,
    RuleStatus,
    RuleType,
    VerificationMethod,
)
from src.bench.vocabulaires import Domain, ReasoningTrap
from src.io_utils import lire_json
from tests.bench.fabriques import REGLE

RULEBOOK = Path("data/rules")
MANIFESTE = RULEBOOK / "rulebook-manifest.json"


@pytest.fixture(scope="module")
def regles() -> list[Rule]:
    return charger_rulebook()


# -- schéma de règle ------------------------------------------------------------ #


def regle(**modifications) -> dict:
    base = dict(REGLE)
    base.update(modifications)
    return base


def refuse(donnees: dict, fragment: str) -> None:
    with pytest.raises(ValidationError) as exc:
        Rule.model_validate(donnees)
    assert fragment in str(exc.value), str(exc.value)


def test_statut_au_dela_de_draft_exige_une_source_consultee():
    """Le verrou central : aucune règle ne progresse sur une référence de mémoire."""
    refuse(
        regle(status="source_checked", verification_method="model_knowledge_unverified"),
        "vérification sur texte primaire",
    )
    refuse(
        regle(status="validated", verification_method="secondary_source_only"),
        "vérification sur texte primaire",
    )


def test_statut_au_dela_de_draft_exige_un_verificateur_nomme():
    source = dict(REGLE["source"], verified_by="", verification_date=None)
    refuse(
        regle(status="source_checked", verification_method="primary_text_review", source=source),
        "verified_by et verification_date",
    )


def test_draft_nexige_rien():
    """Un brouillon non vérifié doit pouvoir exister : c'est le point de départ."""
    source = dict(REGLE["source"], verified_by="", verification_date=None)
    sujet = Rule.model_validate(
        regle(status="draft", verification_method="model_knowledge_unverified", source=source)
    )
    assert sujet.status is RuleStatus.DRAFT
    assert not sujet.is_usable
    assert sujet.needs_verification


def test_seule_une_regle_validee_ancre_un_gold():
    for statut in ("draft", "source_checked", "legal_review"):
        sujet = Rule.model_validate(
            regle(status=statut, verification_method="primary_text_review")
        )
        assert not sujet.is_usable, statut
    assert Rule.model_validate(
        regle(status="validated", verification_method="primary_text_review")
    ).is_usable


def test_exceptions_vides_et_exceptions_inconnues_sont_distinctes():
    """Confondre les deux produit des questions dangereusement simplifiées."""
    aucune = Rule.model_validate(regle(exceptions_status="none_identified"))
    inconnues = Rule.model_validate(regle(exceptions_status="unknown"))

    assert aucune.exceptions_status is ExceptionsStatus.NONE_IDENTIFIED
    assert inconnues.exceptions_status is ExceptionsStatus.UNKNOWN
    assert aucune.exceptions == inconnues.exceptions == []


def test_exceptions_listees_sans_exception_refusees():
    refuse(regle(exceptions_status="listed"), "sans exception listée")


def test_exceptions_listees_hors_statut_listed_refusees():
    refuse(regle(exceptions_status="unknown", exceptions=["une exception"]), "exceptions listées")


def test_absence_non_verifiable_refusee():
    """« Je n'ai pas trouvé » ne devient jamais « cela n'existe pas »."""
    with pytest.raises(ValidationError, match="texte primaire"):
        NegativeClaim(
            claim="Le texte imposerait un seuil de 25 %",
            status="verified_absent",
            verification_method="model_knowledge_unverified",
        )


def test_absence_verifiee_exige_de_dire_ou_lon_a_cherche():
    with pytest.raises(ValidationError, match="searched_in"):
        NegativeClaim(
            claim="Le texte imposerait un seuil de 25 %",
            status="verified_absent",
            verification_method="primary_text_review",
        )


def test_absence_verifiee_acceptee_quand_elle_est_documentee():
    revendication = NegativeClaim(
        claim="Le texte imposerait un seuil de 25 %",
        status="verified_absent",
        verification_method="primary_text_review",
        searched_in="Règlement (UE) 2019/2088, version consolidée du 2023-01-01",
    )
    assert revendication.status.value == "verified_absent"


def test_versionnement_dune_regle():
    refuse(regle(version=2), "supersedes")
    assert Rule.model_validate(regle(version=2, supersedes="RULE-SYNTH-001-v1")).version == 2


def test_regle_ne_se_reference_pas_elle_meme():
    refuse(regle(related_rules=[REGLE["id"]]), "elle-même")


# -- Rulebook livré ------------------------------------------------------------------ #


def test_le_rulebook_se_charge(regles):
    assert len(regles) >= 55
    assert len({r.id for r in regles}) == len(regles)


def test_un_fichier_par_domaine():
    attendus = {"sfdr.json", "mifid.json", "amf.json", "dora.json", "lcbft.json"}
    presents = {c.name for c in RULEBOOK.glob("*.json")} - {"rulebook-manifest.json"}
    assert presents == attendus


def test_tous_les_domaines_sont_couverts(regles):
    assert {r.domain for r in regles} == set(Domain)


def test_aucune_erreur_bloquante_de_qc(regles):
    constats = erreurs(controler(regles))
    assert constats == [], "\n".join(str(c) for c in constats)


def test_toutes_les_regles_ont_un_enonce(regles):
    assert all(r.statement.strip() for r in regles)


def test_aucune_source_fictive(regles):
    """Une URL hors des domaines officiels trahirait une source fabriquée."""
    officiels = ("eur-lex.europa.eu", "legifrance.gouv.fr", "amf-france.org")
    assert all(any(d in r.source.url for d in officiels) for r in regles)


def test_toutes_les_regles_ont_un_article_et_un_regime(regles):
    assert all(r.source.article.strip() for r in regles)
    assert all(r.regulatory_regime.strip() for r in regles)


def test_les_regles_liees_existent(regles):
    connus = {r.id for r in regles}
    for r in regles:
        assert set(r.related_rules) <= connus, f"{r.id} → {set(r.related_rules) - connus}"


def test_les_vocabulaires_sont_respectes(regles):
    for r in regles:
        assert isinstance(r.rule_type, RuleType)
        assert isinstance(r.priority, Priority)
        assert all(isinstance(f, CandidateQuestionFamily) for f in r.candidate_question_families)
        assert all(isinstance(t, ReasoningTrap) for t in r.reasoning_traps)


def test_aucune_regle_nest_marquee_verifiee_a_tort(regles):
    """Le point d'honnêteté de la phase : rien n'est présenté comme vérifié."""
    assert all(r.status is RuleStatus.DRAFT for r in regles)
    assert all(
        r.verification_method is VerificationMethod.MODEL_KNOWLEDGE_UNVERIFIED for r in regles
    )
    assert not any(r.is_usable for r in regles)


def test_aucune_absence_declaree_verifiee(regles):
    """Aucune affirmation négative ne peut être dite vérifiée sans consultation."""
    for r in regles:
        for n in r.negative_claims:
            assert n.status.value == "unverified"


def test_les_regles_critiques_portent_des_pieges(regles):
    """Une règle critique sans piège identifié n'alimentera aucune question adversariale."""
    critiques = [r for r in regles if r.priority is Priority.CRITICAL]
    assert critiques
    assert all(r.reasoning_traps for r in critiques)
    assert all(r.candidate_question_families for r in critiques)


def test_la_separation_texte_interpretation_est_tenue(regles):
    """`statement` dit le texte, `operational_rule` dit ce qu'on en tire."""
    for r in regles:
        assert r.statement.strip()
        assert r.operational_rule.strip()
        assert r.statement != r.operational_rule


def test_liens_inter_reglementaires_presents(regles):
    """Le Rulebook doit relier les domaines, sinon aucune question croisée n'est possible."""
    index = {r.id: r for r in regles}
    croises = [
        (r.id, cible)
        for r in regles
        for cible in r.related_rules
        if index[cible].domain is not r.domain
    ]
    assert len(croises) >= 5, croises


# -- manifeste --------------------------------------------------------------------------- #


def test_le_manifeste_existe_et_est_complet():
    manifeste = lire_json(MANIFESTE)
    for cle in (
        "rulebook_version", "generation_date", "number_of_rules", "rules_per_domain",
        "rules_per_type", "rules_per_priority", "number_source_checked",
        "number_validated", "number_time_sensitive", "number_critical",
    ):
        assert cle in manifeste, cle


def test_le_manifeste_est_exact(regles):
    manifeste = lire_json(MANIFESTE)
    assert manifeste["number_of_rules"] == len(regles)
    assert manifeste["number_validated"] == 0
    assert manifeste["number_source_checked"] == 0
    assert manifeste["number_critical"] == sum(1 for r in regles if r.priority is Priority.CRITICAL)
    assert manifeste["number_time_sensitive"] == sum(1 for r in regles if r.time_sensitive)
    assert manifeste["rules_per_domain"] == {
        d: sum(1 for r in regles if r.domain.value == d)
        for d in sorted({r.domain.value for r in regles})
    }


def test_le_manifeste_nest_pas_charge_comme_une_regle():
    """Il vit dans data/rules/ : le chargeur doit l'ignorer."""
    assert MANIFESTE.is_file()
    assert all(r.id != "rulebook-manifest" for r in charger_rulebook())


def test_le_rapport_qc_existe():
    rapport = Path("RULEBOOK_QC.md")
    assert rapport.is_file()
    contenu = rapport.read_text(encoding="utf-8")
    assert "n'est utilisable pour ancrer un gold" in contenu


# -- non-régression : la phase 6 ne génère aucune question --------------------------------- #


def test_aucune_question_na_ete_generee():
    """La phase 6 construit les règles, pas le dataset."""
    reel = Path("corpus")
    items = list((reel / "public").glob("*.json")) if (reel / "public").is_dir() else []
    for chemin in items:
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
        assert len(contenu) < 50, f"{chemin} semble contenir un dataset de questions"
