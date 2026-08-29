"""ITEM — l'unité évaluée.

Un item n'est pas une question posée en l'air : il est rattaché à une famille et
à des règles, il déclare ce qu'on attend du modèle, et il est versionné. Un
changement réglementaire crée une nouvelle version, il n'écrase jamais l'ancienne.
"""

from __future__ import annotations

import datetime as dt

from pydantic import Field, model_validator

from src.bench.modeles import (
    AbstentionRequirements,
    GoldChecklist,
    ModeleStrict,
    NegativeClaimVerification,
    SecondarySource,
    Source,
)
from src.bench.vocabulaires import (
    Answerability,
    COMPORTEMENTS_A_EXIGENCES,
    COMPORTEMENTS_PAR_TYPE,
    Corpus,
    Domain,
    ExpectedBehavior,
    PIEGES_A_VERIFICATION_NEGATIVE,
    QuestionType,
    ReasoningTrap,
    RegulatoryStatus,
    STATUTS_VALIDES,
    TYPES_PAR_ROLE_JUMEAU,
    TwinRole,
    ValidationStatus,
    statut_admis,
)


class Item(ModeleStrict):
    # -- identité et versionnement ------------------------------------------ #
    base_id: str = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    #: Identifiant de la version précédente. L'historique reste consultable.
    supersedes: str | None = None

    corpus: Corpus
    domain: Domain

    # -- rattachement -------------------------------------------------------- #
    family_id: str = Field(min_length=1)
    rule_ids: list[str] = Field(min_length=1)
    twin_group_id: str | None = None
    twin_role: TwinRole | None = None

    # -- nature de la question ----------------------------------------------- #
    question_type: QuestionType
    reasoning_trap: ReasoningTrap = ReasoningTrap.NONE
    difficulty: int = Field(ge=1, le=5)
    question: str = Field(min_length=1)

    # -- attendu -------------------------------------------------------------- #
    answerability: Answerability
    expected_behavior: ExpectedBehavior
    gold_answer: str = Field(min_length=1)
    key_points: list[str] = Field(min_length=1)
    disqualifying_errors: list[str] = Field(default_factory=list)
    abstention_requirements: AbstentionRequirements | None = None
    #: Une réfutation qui n'énonce pas la règle correcte ne suffit pas.
    reframe_required: bool = False
    reframe_expectation: str = ""

    # -- sources -------------------------------------------------------------- #
    source: Source
    secondary_sources: list[SecondarySource] = Field(default_factory=list)
    negative_claim: bool = False
    negative_claim_verification: NegativeClaimVerification | None = None

    # -- ancrage temporel ------------------------------------------------------ #
    regulatory_regime: str = Field(min_length=1)
    regulatory_status: RegulatoryStatus = RegulatoryStatus.IN_FORCE
    valid_from: dt.date
    valid_until: dt.date | None = None
    #: Date à laquelle l'évaluation est réputée se placer.
    assessment_date: dt.date

    # -- dangerosité ------------------------------------------------------------ #
    #: Une réponse fausse ici conduirait-elle à un acte (déclarer, publier, classer).
    actionable: bool = True
    #: La question porte-t-elle sur une obligation réglementaire, pas sur du contexte.
    materially_regulatory: bool = True

    # -- cycle de vie ------------------------------------------------------------ #
    status: ValidationStatus = ValidationStatus.DRAFT
    checklist: GoldChecklist = Field(default_factory=GoldChecklist)

    # ---------------------------------------------------------------------- #
    # Identité
    # ---------------------------------------------------------------------- #

    @property
    def id(self) -> str:
        """Identifiant complet, version comprise : « SFDR-0042-v2 »."""
        return f"{self.base_id}-v{self.version}"

    @property
    def is_private(self) -> bool:
        return self.corpus is Corpus.PRIVE

    @property
    def is_gold(self) -> bool:
        return self.status in STATUTS_VALIDES

    # ---------------------------------------------------------------------- #
    # Cohérence interne
    # ---------------------------------------------------------------------- #

    @model_validator(mode="after")
    def _listes_propres(self) -> Item:
        for nom in ("rule_ids", "key_points", "disqualifying_errors"):
            valeurs: list[str] = getattr(self, nom)
            if any(not v.strip() for v in valeurs):
                raise ValueError(f"{nom} : aucune entrée ne peut être vide")
        if len(set(self.rule_ids)) != len(self.rule_ids):
            raise ValueError("rule_ids : identifiants en double")
        return self

    @model_validator(mode="after")
    def _versionnement(self) -> Item:
        if self.version > 1 and not self.supersedes:
            raise ValueError(
                "version > 1 : supersedes doit nommer la version remplacée, "
                "sinon l'historique du gold est perdu"
            )
        if self.version == 1 and self.supersedes:
            raise ValueError("version 1 : supersedes n'a pas de sens")
        if self.supersedes == self.id:
            raise ValueError("supersedes ne peut pas désigner l'item lui-même")
        return self

    @model_validator(mode="after")
    def _comportement_coherent_avec_le_type(self) -> Item:
        admis = COMPORTEMENTS_PAR_TYPE[self.question_type]
        if self.expected_behavior not in admis:
            raise ValueError(
                f"expected_behavior « {self.expected_behavior.value} » incompatible avec "
                f"question_type « {self.question_type.value} » "
                f"(admis : {sorted(c.value for c in admis)})"
            )
        return self

    @model_validator(mode="after")
    def _repondabilite_coherente(self) -> Item:
        from src.bench.vocabulaires import REPONDABILITE_PAR_COMPORTEMENT

        admis = REPONDABILITE_PAR_COMPORTEMENT[self.expected_behavior]
        if self.answerability not in admis:
            raise ValueError(
                f"answerability « {self.answerability.value} » incompatible avec "
                f"expected_behavior « {self.expected_behavior.value} » "
                f"(admis : {sorted(a.value for a in admis)})"
            )
        return self

    @model_validator(mode="after")
    def _exigences_dabstention(self) -> Item:
        attendu = self.expected_behavior in COMPORTEMENTS_A_EXIGENCES
        if attendu and self.abstention_requirements is None:
            raise ValueError(
                f"expected_behavior « {self.expected_behavior.value} » exige "
                "abstention_requirements : une abstention se note sur ce qu'elle réclame"
            )
        if not attendu and self.abstention_requirements is not None:
            raise ValueError(
                "abstention_requirements n'a de sens que pour un comportement "
                "d'abstention ou de demande d'information"
            )
        return self

    @model_validator(mode="after")
    def _reframe_reserve_aux_fausses_premisses(self) -> Item:
        if self.reframe_required and self.question_type is not QuestionType.FALSE_PREMISE:
            raise ValueError("reframe_required ne s'applique qu'à une fausse prémisse")
        if self.reframe_required and not self.reframe_expectation.strip():
            raise ValueError(
                "reframe_required : reframe_expectation doit dire quelle règle "
                "correcte la réponse doit rétablir"
            )
        return self

    @model_validator(mode="after")
    def _un_piege_qui_nen_est_pas_un(self) -> Item:
        if (
            self.question_type
            in (QuestionType.FALSE_PREMISE, QuestionType.TRUE_PREMISE_ADVERSARIAL)
            and self.reasoning_trap is ReasoningTrap.NONE
        ):
            raise ValueError(
                f"question_type « {self.question_type.value} » exige un reasoning_trap : "
                "sans piège nommé, l'item ne mesure rien de particulier"
            )
        return self

    @model_validator(mode="after")
    def _verification_negative(self) -> Item:
        piege_negatif = (
            self.question_type is QuestionType.FALSE_PREMISE
            and self.reasoning_trap in PIEGES_A_VERIFICATION_NEGATIVE
        )
        if piege_negatif and not self.negative_claim:
            raise ValueError(
                f"reasoning_trap « {self.reasoning_trap.value} » affirme une disposition "
                "inexistante : negative_claim doit valoir true"
            )
        if self.negative_claim and self.negative_claim_verification is None:
            raise ValueError(
                "negative_claim : une affirmation négative exige "
                "negative_claim_verification — on ne peut pas sourcer une absence "
                "en citant un texte"
            )
        if not self.negative_claim and self.negative_claim_verification is not None:
            raise ValueError(
                "negative_claim_verification sans negative_claim : incohérent"
            )
        return self

    @model_validator(mode="after")
    def _ancrage_temporel(self) -> Item:
        if self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("valid_until est antérieur à valid_from")
        if self.regulatory_status is RegulatoryStatus.REPEALED and self.valid_until is None:
            raise ValueError("regulatory_status « repealed » exige une date valid_until")
        if self.assessment_date < self.valid_from:
            raise ValueError(
                "assessment_date précède valid_from : l'item serait évalué avant "
                "l'entrée en vigueur de la règle qu'il teste"
            )
        if self.valid_until is not None and self.assessment_date > self.valid_until:
            raise ValueError("assessment_date dépasse valid_until")
        return self

    @model_validator(mode="after")
    def _jumeaux(self) -> Item:
        if (self.twin_group_id is None) != (self.twin_role is None):
            raise ValueError(
                "twin_group_id et twin_role vont ensemble : un jumeau sans rôle "
                "ne permet pas de mesurer la sensibilité à la prémisse"
            )
        if self.twin_role is not None:
            admis = TYPES_PAR_ROLE_JUMEAU[self.twin_role]
            if self.question_type not in admis:
                raise ValueError(
                    f"twin_role « {self.twin_role.value} » incompatible avec "
                    f"question_type « {self.question_type.value} »"
                )
        return self

    @model_validator(mode="after")
    def _cycle_de_vie(self) -> Item:
        if not statut_admis(self.corpus, self.status):
            raise ValueError(
                f"statut « {self.status.value} » inapplicable au corpus "
                f"« {self.corpus.value} »"
            )
        if self.status in STATUTS_VALIDES:
            if not self.checklist.is_complete:
                manquants = self.checklist.missing or ["reviewed_by/review_date"]
                raise ValueError(
                    f"statut « {self.status.value} » exige une grille complète ; "
                    f"manque : {manquants}"
                )
            if not self.source.is_verified:
                raise ValueError(
                    f"statut « {self.status.value} » exige une source primaire vérifiée"
                )
        return self

    # ---------------------------------------------------------------------- #
    # Traces sûres
    # ---------------------------------------------------------------------- #

    def redacted(self) -> dict:
        """Forme sans contenu, pour les journaux et les rapports.

        Ne contient ni question, ni réponse, ni point clé : un item privé doit
        pouvoir être tracé sans que son contenu quitte la machine.
        """
        return {
            "id": self.id,
            "corpus": self.corpus.value,
            "domain": self.domain.value,
            "question_type": self.question_type.value,
            "expected_behavior": self.expected_behavior.value,
            "status": self.status.value,
        }
