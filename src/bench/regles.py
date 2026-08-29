"""Hiérarchie RULE → CONCEPT → QUESTION FAMILY → TWIN GROUP.

Une question n'existe jamais seule : elle est rattachée à une ou plusieurs règles
validées. C'est ce rattachement qui permet, quand un texte change, de retrouver
tous les items à reversionner.
"""

from __future__ import annotations

import datetime as dt

from pydantic import Field, model_validator

from src.bench.modeles import ModeleStrict, Source
from src.bench.vocabulaires import (
    Domain,
    RegulatoryStatus,
    TwinRole,
    ValidationStatus,
)


class Rule(ModeleStrict):
    """Une règle de droit identifiée, datée et sourcée."""

    id: str = Field(min_length=1)
    domain: Domain
    regulatory_regime: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source: Source
    regulatory_status: RegulatoryStatus = RegulatoryStatus.IN_FORCE
    valid_from: dt.date
    valid_until: dt.date | None = None
    status: ValidationStatus = ValidationStatus.DRAFT
    notes: str = ""

    @model_validator(mode="after")
    def _coherence_des_dates(self) -> Rule:
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("valid_until est antérieur à valid_from")
        if self.regulatory_status is RegulatoryStatus.REPEALED and self.valid_until is None:
            raise ValueError("une règle abrogée doit porter une date de fin (valid_until)")
        return self

    @model_validator(mode="after")
    def _une_regle_validee_est_sourcee(self) -> Rule:
        # On ne rattache une question qu'à des règles validées : une règle validée
        # dont la source n'est pas vérifiée rendrait ce rattachement creux.
        if self.status is not ValidationStatus.DRAFT and not self.source.is_verified:
            raise ValueError(
                "une règle au-delà de « draft » exige une source vérifiée "
                "(verified_by et verification_date)"
            )
        return self

    @property
    def is_usable(self) -> bool:
        """Une règle utilisable pour ancrer un gold est au moins validée."""
        return self.status in (
            ValidationStatus.VALIDATED,
            ValidationStatus.PUBLISHED,
            ValidationStatus.LOCKED,
        )


class Concept(ModeleStrict):
    """Notion réglementaire transverse, adossée à une ou plusieurs règles."""

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    domain: Domain
    rule_ids: list[str] = Field(min_length=1)
    definition: str = ""

    @model_validator(mode="after")
    def _pas_de_rattachement_vide(self) -> Concept:
        if any(not r.strip() for r in self.rule_ids):
            raise ValueError("rule_ids : aucun identifiant ne peut être vide")
        if len(set(self.rule_ids)) != len(self.rule_ids):
            raise ValueError("rule_ids : identifiants en double")
        return self


class QuestionFamily(ModeleStrict):
    """Angle d'interrogation d'un concept. Les items d'une famille sont comparables."""

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    concept_id: str = Field(min_length=1)
    description: str = ""


class TwinGroup(ModeleStrict):
    """Groupe de jumeaux : mêmes faits, une seule variable qui change.

    Le groupe déclare sa famille et les rôles qu'il couvre ; l'appartenance
    effective des items est vérifiée par le registre, pas ici, pour que la
    déclaration et la réalité puissent diverger et être signalées.
    """

    id: str = Field(min_length=1)
    family_id: str = Field(min_length=1)
    label: str = ""
    #: Ce que le groupe cherche à mesurer, en une phrase.
    varies: str = Field(min_length=1)

    @staticmethod
    def roles_distincts(roles: list[TwinRole]) -> bool:
        """Un groupe dont tous les items jouent le même rôle ne mesure rien."""
        return len(set(roles)) > 1
