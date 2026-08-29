"""Validation des golds et transitions de cycle de vie.

Aucun item ne passe en `validated` sans que les six contrôles de la
spécification §12 soient cochés. Rien ne devient `published` ou `locked` sans
être passé par `validated`. Une version figée ne se modifie pas : elle se
reversionne.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.bench.items import Item
from src.bench.vocabulaires import (
    STATUTS_FIGES,
    STATUTS_VALIDES,
    TRANSITIONS,
    ValidationStatus,
)


class TransitionInterdite(ValueError):
    """Passage de statut non prévu par le cycle de vie du corpus concerné."""


@dataclass(frozen=True)
class Blocage:
    """Ce qui empêche une promotion, dit en clair au rédacteur du corpus."""

    champ: str
    message: str

    def __str__(self) -> str:
        return f"{self.champ} : {self.message}"


def blocages_pour(item: Item, cible: ValidationStatus) -> list[Blocage]:
    """Ce qui manque à un item pour atteindre `cible`. Vide = promotion possible."""
    blocages: list[Blocage] = []

    transitions = TRANSITIONS.get(item.corpus, {})
    if cible not in transitions:
        blocages.append(
            Blocage("status", f"« {cible.value} » inapplicable au corpus « {item.corpus.value} »")
        )
        return blocages

    if item.status in STATUTS_FIGES:
        blocages.append(
            Blocage(
                "status",
                f"« {item.status.value} » est figé : créez une nouvelle version "
                "plutôt que de modifier celle-ci",
            )
        )
        return blocages

    if cible not in transitions.get(item.status, frozenset()):
        blocages.append(
            Blocage(
                "status",
                f"transition « {item.status.value} » → « {cible.value} » non prévue "
                f"(possible : {sorted(s.value for s in transitions.get(item.status, []))})",
            )
        )

    if cible in STATUTS_VALIDES:
        for manquant in item.checklist.missing:
            blocages.append(Blocage(f"checklist.{manquant}", "contrôle non effectué"))
        if not item.checklist.reviewed_by:
            blocages.append(Blocage("checklist.reviewed_by", "relecteur non nommé"))
        if item.checklist.review_date is None:
            blocages.append(Blocage("checklist.review_date", "date de relecture absente"))
        if not item.source.is_verified:
            blocages.append(
                Blocage("source", "source primaire non vérifiée (verified_by, verification_date)")
            )
        if item.negative_claim and item.negative_claim_verification is None:
            blocages.append(
                Blocage(
                    "negative_claim_verification",
                    "affirmation négative non attestée",
                )
            )

    return blocages


def peut_promouvoir(item: Item, cible: ValidationStatus) -> bool:
    return not blocages_pour(item, cible)


def promouvoir(item: Item, cible: ValidationStatus) -> Item:
    """Rend une **copie** au statut cible, ou lève.

    L'item d'origine n'est jamais muté : un gold figé doit rester tel qu'il a été
    utilisé pour produire un résultat.
    """
    blocages = blocages_pour(item, cible)
    if blocages:
        detail = "; ".join(str(b) for b in blocages)
        raise TransitionInterdite(f"{item.id} → « {cible.value} » : {detail}")
    return item.model_copy(update={"status": cible})


def nouvelle_version(item: Item, **modifications) -> Item:
    """Crée la version suivante d'un gold, en conservant l'ancienne.

    La nouvelle version repart en `draft` : un changement réglementaire remet le
    gold en jeu, il ne conserve pas la validation de la version précédente.
    """
    from src.bench.modeles import GoldChecklist

    base = {
        "version": item.version + 1,
        "supersedes": item.id,
        "status": ValidationStatus.DRAFT,
        "checklist": GoldChecklist(),
    }
    base.update(modifications)
    return item.model_copy(update=base)


def items_publiables(items: list[Item]) -> list[Item]:
    """Les seuls items qu'un export public a le droit de reprendre."""
    from src.bench.vocabulaires import Corpus

    return [
        item
        for item in items
        if item.corpus is Corpus.PUBLIC and item.status is ValidationStatus.PUBLISHED
    ]
