"""Hiérarchie RULE → CONCEPT → QUESTION FAMILY → TWIN GROUP.

Une question n'existe jamais seule : elle est rattachée à une ou plusieurs
règles validées. C'est ce rattachement qui permet, quand un texte change, de
retrouver tous les items à reversionner.
"""

from __future__ import annotations

import datetime as dt

from pydantic import Field, model_validator

from src.bench.modeles import ModeleStrict, Source
from src.bench.rulebook import (
    METHODES_SUFFISANTES,
    CandidateQuestionFamily,
    ExceptionsStatus,
    NegativeClaim,
    Priority,
    RuleStatus,
    RuleType,
    VerificationMethod,
)
from src.bench.vocabulaires import (
    Domain,
    ReasoningTrap,
    RegulatoryStatus,
    TwinRole,
)


class Rule(ModeleStrict):
    """Une règle de droit identifiée, datée, sourcée et versionnée.

    Trois champs qu'il ne faut jamais confondre :

    - `statement` : ce que le texte dit, au plus près de sa lettre ;
    - `operational_rule` : ce que cela implique pour un professionnel ;
    - `common_confusions` : ce avec quoi un modèle le confond.

    Écrire une inférence dans `statement` reviendrait à faire dire au texte ce
    qu'il ne dit pas — et à construire ensuite des questions sur cette invention.
    """

    # -- identité et versionnement ------------------------------------------ #
    id: str = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    supersedes: str | None = None

    domain: Domain
    subdomain: str = ""
    rule_type: RuleType

    # -- contenu -------------------------------------------------------------- #
    title: str = Field(min_length=1)
    #: Ce que dit le texte. Jamais une interprétation (spécification §14).
    statement: str = Field(min_length=1)
    #: Ce que cela signifie concrètement. Marqué comme interprétation, pas comme texte.
    operational_rule: str = ""
    #: Confusions typiques d'un LLM sur cette règle.
    common_confusions: list[str] = Field(default_factory=list)

    exceptions: list[str] = Field(default_factory=list)
    exceptions_status: ExceptionsStatus = ExceptionsStatus.UNKNOWN
    negative_claims: list[NegativeClaim] = Field(default_factory=list)

    # -- source ---------------------------------------------------------------- #
    source: Source
    verification_method: VerificationMethod = VerificationMethod.MODEL_KNOWLEDGE_UNVERIFIED
    secondary_sources: list[str] = Field(default_factory=list)

    # -- ancrage temporel ------------------------------------------------------- #
    regulatory_regime: str = Field(min_length=1)
    regulatory_status: RegulatoryStatus = RegulatoryStatus.IN_FORCE
    valid_from: dt.date
    valid_until: dt.date | None = None
    time_sensitive: bool = False

    # -- exploitation ------------------------------------------------------------ #
    priority: Priority = Priority.MEDIUM
    candidate_question_families: list[CandidateQuestionFamily] = Field(default_factory=list)
    reasoning_traps: list[ReasoningTrap] = Field(default_factory=list)
    related_rules: list[str] = Field(default_factory=list)

    # -- cycle de vie -------------------------------------------------------------- #
    status: RuleStatus = RuleStatus.DRAFT
    notes: str = ""

    # ------------------------------------------------------------------------ #

    @model_validator(mode="after")
    def _coherence_des_dates(self) -> Rule:
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("valid_until est antérieur à valid_from")
        if self.regulatory_status is RegulatoryStatus.REPEALED and self.valid_until is None:
            raise ValueError("une règle abrogée doit porter une date de fin (valid_until)")
        return self

    @model_validator(mode="after")
    def _versionnement(self) -> Rule:
        if self.version > 1 and not self.supersedes:
            raise ValueError(
                "version > 1 : supersedes doit nommer la version remplacée, "
                "sinon l'historique de la règle est perdu"
            )
        if self.version == 1 and self.supersedes:
            raise ValueError("version 1 : supersedes n'a pas de sens")
        return self

    @model_validator(mode="after")
    def _exceptions_explicites(self) -> Rule:
        """« Aucune exception identifiée » et « exceptions inconnues » ne sont pas la même chose."""
        if self.exceptions_status is ExceptionsStatus.LISTED and not self.exceptions:
            raise ValueError("exceptions_status « listed » sans exception listée")
        if self.exceptions_status is not ExceptionsStatus.LISTED and self.exceptions:
            raise ValueError(
                f"exceptions listées alors que exceptions_status vaut "
                f"« {self.exceptions_status.value} »"
            )
        return self

    @model_validator(mode="after")
    def _le_statut_depend_de_la_verification(self) -> Rule:
        """Un statut au-delà de `draft` exige une source réellement consultée.

        C'est le verrou central du Rulebook : aucune règle ne peut progresser
        parce qu'un modèle a écrit une référence de mémoire, ni parce qu'une page
        web la mentionne.
        """
        if self.status is RuleStatus.DRAFT:
            return self

        if self.verification_method not in METHODES_SUFFISANTES:
            raise ValueError(
                f"statut « {self.status.value} » exige une vérification sur texte "
                f"primaire ; verification_method vaut "
                f"« {self.verification_method.value} »"
            )
        if not self.source.is_verified:
            raise ValueError(
                f"statut « {self.status.value} » exige verified_by et verification_date"
            )
        return self

    @model_validator(mode="after")
    def _listes_propres(self) -> Rule:
        for nom in ("common_confusions", "exceptions", "related_rules", "secondary_sources"):
            valeurs: list[str] = getattr(self, nom)
            if any(not v.strip() for v in valeurs):
                raise ValueError(f"{nom} : aucune entrée ne peut être vide")
        if len(set(self.related_rules)) != len(self.related_rules):
            raise ValueError("related_rules : identifiants en double")
        if self.id in self.related_rules:
            raise ValueError("related_rules : une règle ne se référence pas elle-même")
        return self

    @property
    def is_usable(self) -> bool:
        """Une règle utilisable pour ancrer un gold est validée, rien de moins."""
        return self.status is RuleStatus.VALIDATED

    @property
    def needs_verification(self) -> bool:
        return self.verification_method not in METHODES_SUFFISANTES


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
    """Groupe de jumeaux : mêmes faits, une seule variable qui change."""

    id: str = Field(min_length=1)
    family_id: str = Field(min_length=1)
    label: str = ""
    varies: str = Field(min_length=1)

    @staticmethod
    def roles_distincts(roles: list[TwinRole]) -> bool:
        """Un groupe dont tous les items jouent le même rôle ne mesure rien."""
        return len(set(roles)) > 1
