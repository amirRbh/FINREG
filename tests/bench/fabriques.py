"""Fixtures SYNTHÉTIQUES pour les tests de FinReg-FR Bench.

Aucune règle de droit réelle ici. Les identifiants, articles et URL sont
volontairement fictifs (`SYNTH-*`, domaine `example.invalid`) pour qu'aucune de
ces données ne puisse être prise pour du gold juridique si elle fuit dans un
fichier de corpus.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

SOURCE_SYNTH: dict[str, Any] = {
    "text": "Texte synthétique de test (aucune valeur juridique)",
    "article": "Article SYNTH-1",
    "paragraph": "1",
    "url": "https://example.invalid/synth/1",
    "version_date": "2020-01-01",
    "verified_by": "Relecteur de test",
    "verification_date": "2026-01-15",
}

CHECKLIST_COMPLETE: dict[str, Any] = {
    "source_verified": True,
    "answer_verified": True,
    "key_points_verified": True,
    "disqualifying_errors_verified": True,
    "answerability_verified": True,
    "expected_behavior_verified": True,
    "reviewed_by": "Relecteur de test",
    "review_date": "2026-01-20",
}

REGLE: dict[str, Any] = {
    "id": "RULE-SYNTH-001",
    "domain": "SFDR",
    "regulatory_regime": "Régime synthétique de test",
    "title": "Règle synthétique 1",
    "source": copy.deepcopy(SOURCE_SYNTH),
    "regulatory_status": "in_force",
    "valid_from": "2020-01-01",
    "status": "validated",
}

CONCEPT: dict[str, Any] = {
    "id": "CONCEPT-SYNTH-001",
    "label": "Concept synthétique 1",
    "domain": "SFDR",
    "rule_ids": ["RULE-SYNTH-001"],
}

FAMILLE: dict[str, Any] = {
    "id": "FAM-SYNTH-001",
    "label": "Famille synthétique 1",
    "concept_id": "CONCEPT-SYNTH-001",
}

GROUPE: dict[str, Any] = {
    "id": "TWIN-SYNTH-001",
    "family_id": "FAM-SYNTH-001",
    "varies": "la véracité de la prémisse",
}

ITEM: dict[str, Any] = {
    "base_id": "SYNTH-0001",
    "version": 1,
    "corpus": "public",
    "domain": "SFDR",
    "family_id": "FAM-SYNTH-001",
    "rule_ids": ["RULE-SYNTH-001"],
    "question_type": "qualification",
    "reasoning_trap": "NONE",
    "difficulty": 2,
    "question": "Question synthétique de test ?",
    "answerability": "answerable",
    "expected_behavior": "answer",
    "gold_answer": "Réponse synthétique de test.",
    "key_points": ["point clé synthétique"],
    "disqualifying_errors": [],
    "source": copy.deepcopy(SOURCE_SYNTH),
    "regulatory_regime": "Régime synthétique de test",
    "regulatory_status": "in_force",
    "valid_from": "2020-01-01",
    "assessment_date": "2026-01-01",
    "status": "draft",
}


def item(**modifications: Any) -> dict[str, Any]:
    base = copy.deepcopy(ITEM)
    base.update(modifications)
    return base


def item_valide(**modifications: Any) -> dict[str, Any]:
    """Un item prêt à passer en `validated` : grille complète, source vérifiée."""
    base = item(status="validated", checklist=copy.deepcopy(CHECKLIST_COMPLETE))
    base.update(modifications)
    return base


def item_fausse_premisse(**modifications: Any) -> dict[str, Any]:
    """Fausse prémisse à article inexistant : exige une vérification négative."""
    base = item(
        base_id="SYNTH-FP-001",
        question_type="false_premise",
        reasoning_trap="FALSE_ARTICLE",
        expected_behavior="refute_premise",
        answerability="answerable",
        reframe_required=True,
        reframe_expectation="Rétablir la règle synthétique réellement applicable.",
        negative_claim=True,
        negative_claim_verification={
            "claim": "L'article SYNTH-99 imposerait une obligation.",
            "searched_in": "Texte synthétique de test, version du 2020-01-01",
            "searched_version_date": "2020-01-01",
            "actual_provision": "Le texte s'arrête à l'article SYNTH-12.",
            "verified_by": "Relecteur de test",
            "verification_date": "2026-01-15",
        },
    )
    base.update(modifications)
    return base


def item_abstention(**modifications: Any) -> dict[str, Any]:
    base = item(
        base_id="SYNTH-AB-001",
        question_type="calibrated_abstention",
        reasoning_trap="MISSING_INFORMATION",
        expected_behavior="abstain",
        answerability="unanswerable",
        abstention_requirements={
            "missing_information": ["la donnée synthétique X", "la donnée synthétique Y"],
            "reason_required": True,
            "conditional_conclusion_expected": True,
        },
    )
    base.update(modifications)
    return base


def ecrire_referentiel(racine: Path, **remplacements: Any) -> Path:
    """Matérialise règles, concepts, familles et groupes sur disque."""
    contenus = {
        "rules": remplacements.get("rules", [copy.deepcopy(REGLE)]),
        "concepts": remplacements.get("concepts", [copy.deepcopy(CONCEPT)]),
        "families": remplacements.get("families", [copy.deepcopy(FAMILLE)]),
        "twin_groups": remplacements.get("twin_groups", [copy.deepcopy(GROUPE)]),
    }
    for nom, contenu in contenus.items():
        dossier = racine / nom
        dossier.mkdir(parents=True, exist_ok=True)
        (dossier / f"{nom}.json").write_text(
            json.dumps(contenu, ensure_ascii=False), encoding="utf-8"
        )
    return racine


def ecrire_corpus(
    racine: Path, public: list[dict] | None = None, prive: list[dict] | None = None
) -> Path:
    for nom, contenu in (("public", public), ("private", prive)):
        dossier = racine / nom
        dossier.mkdir(parents=True, exist_ok=True)
        if contenu is not None:
            (dossier / "items.json").write_text(
                json.dumps(contenu, ensure_ascii=False), encoding="utf-8"
            )
    return racine
