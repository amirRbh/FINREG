"""RULE → QUESTION FAMILY : le blueprint d'une famille candidate (phase 7).

Une famille candidate n'est pas une question. Elle dit **ce qu'une question
pourrait mesurer** à partir d'une règle donnée, et sous quelles conditions elle
serait légitime : le comportement attendu, la répondabilité, le piège, les
erreurs qui disqualifieraient une réponse, et ce qui bloque encore.

Trois choses ne se confondent pas ici :

- `family_score` : la valeur pédagogique de l'angle (0 = artificiel, 3 = excellent) ;
- `priority` : la gravité de l'erreur pour un professionnel ;
- `candidate_family_status` : ce que l'état du Rulebook autorise aujourd'hui.

Une famille peut être excellente (`family_score = 3`), critique
(`priority = CRITICAL`) et néanmoins `blocked` : sa règle n'a pas encore été
confrontée à son texte primaire. Les trois axes sont indépendants, et c'est
volontaire — mélanger l'intérêt d'une question avec le droit de la poser
reviendrait à écrire du gold sur une source non vérifiée.

Convention de langue : noms de champs en anglais (contrat de données V0.2),
commentaires et messages en français.
"""

from __future__ import annotations

import datetime as dt
from enum import Enum

from pydantic import Field, model_validator

from src.bench.modeles import ModeleStrict, Source
from src.bench.rulebook import Priority
from src.bench.vocabulaires import (
    Answerability,
    COMPORTEMENTS_A_EXIGENCES,
    COMPORTEMENTS_PAR_TYPE,
    Domain,
    ExpectedBehavior,
    PIEGES_A_VERIFICATION_NEGATIVE,
    QuestionType,
    ReasoningTrap,
    REPONDABILITE_PAR_COMPORTEMENT,
    RegulatoryStatus,
)


class FamilyKind(str, Enum):
    """Les douze familles de base (spécification phase 7 §3).

    Chacune mesure une compétence distincte. Deux familles qui ne diffèrent que
    par la formulation ne sont pas deux familles : le contrôle de redondance
    (`redundancy_group_id`) est là pour le rappeler.
    """

    FACT_RECALL = "FACT_RECALL"
    QUALIFICATION = "QUALIFICATION"
    CALCULATION = "CALCULATION"
    FALSE_PREMISE = "FALSE_PREMISE"
    TRUE_PREMISE_ADVERSARIAL = "TRUE_PREMISE_ADVERSARIAL"
    CALIBRATED_ABSTENTION = "CALIBRATED_ABSTENTION"
    CONDITIONAL_ANSWER = "CONDITIONAL_ANSWER"
    TEMPORAL = "TEMPORAL"
    CROSS_REGULATORY = "CROSS_REGULATORY"
    EXCEPTION = "EXCEPTION"
    NEGATIVE_ASSERTION = "NEGATIVE_ASSERTION"
    MISSING_INFORMATION = "MISSING_INFORMATION"


#: Code court de chaque famille, tel que la spécification les nomme (F1 à F12).
CODES_FAMILLES: dict[FamilyKind, str] = {
    FamilyKind.FACT_RECALL: "F1",
    FamilyKind.QUALIFICATION: "F2",
    FamilyKind.CALCULATION: "F3",
    FamilyKind.FALSE_PREMISE: "F4",
    FamilyKind.TRUE_PREMISE_ADVERSARIAL: "F5",
    FamilyKind.CALIBRATED_ABSTENTION: "F6",
    FamilyKind.CONDITIONAL_ANSWER: "F7",
    FamilyKind.TEMPORAL: "F8",
    FamilyKind.CROSS_REGULATORY: "F9",
    FamilyKind.EXCEPTION: "F10",
    FamilyKind.NEGATIVE_ASSERTION: "F11",
    FamilyKind.MISSING_INFORMATION: "F12",
}

#: Ordre d'affichage stable : F1, F2, … F12 plutôt que l'ordre alphabétique.
ORDRE_FAMILLES: tuple[FamilyKind, ...] = tuple(CODES_FAMILLES)


class CandidateFamilyStatus(str, Enum):
    """Ce que l'état du Rulebook autorise pour cette famille.

    `blocked` n'est pas un rejet de l'angle : c'est l'état d'une famille dont la
    règle n'est pas encore utilisable. Elle redeviendra `ready` d'elle-même
    quand la vérification aura promu la règle — sans qu'on la réécrive.
    """

    #: Utilisable pour le benchmark final.
    READY = "ready"
    #: Utilisable sous réserve : une réserve non bloquante doit être levée.
    NEEDS_REVIEW = "needs_review"
    #: Interdite au benchmark final tant que ses causes ne sont pas levées.
    BLOCKED = "blocked"


class TwinType(str, Enum):
    """Nature du couple de jumeaux (spécification phase 7 §6)."""

    FALSE_TRUE = "FALSE_TRUE"
    TRUE_FALSE = "TRUE_FALSE"
    TRUE_MISSING = "TRUE_MISSING"
    FALSE_MISSING = "FALSE_MISSING"
    TEMPORAL_TWIN = "TEMPORAL_TWIN"
    SCOPE_TWIN = "SCOPE_TWIN"
    EXCEPTION_TWIN = "EXCEPTION_TWIN"


class CriticalErrorKind(str, Enum):
    """Erreurs potentiellement disqualifiantes (spécification phase 7 §11).

    Ce sont des *catégories* d'erreur, pas des formulations. La liste littérale
    d'un item (`disqualifying_errors`) sera écrite à la rédaction de la
    question : le scoring déterministe la compare mot à mot, et une catégorie ne
    se compare pas mot à mot.
    """

    INCORRECT_ARTICLE = "incorrect_article"
    INVENTED_THRESHOLD = "invented_threshold"
    WRONG_SCOPE = "wrong_scope"
    WRONG_REGULATORY_REGIME = "wrong_regulatory_regime"
    FAILURE_TO_MENTION_EXCEPTION = "failure_to_mention_exception"
    INCORRECT_MANDATORY_PROHIBITED = "incorrect_mandatory_prohibited_distinction"
    INCORRECT_PPE_CLASSIFICATION = "incorrect_ppe_classification"
    INCORRECT_REFUSAL_CONTINUATION = "incorrect_refusal_continuation_obligation"
    INCORRECT_ICT_CLASSIFICATION = "incorrect_ict_classification"
    INCORRECT_SUSTAINABILITY_CLASSIFICATION = "incorrect_sustainability_classification"


class HoldoutRecommendation(str, Enum):
    """Orientation public/privé, sans arbitrage définitif (phase 7 §14).

    L'affectation réelle se décidera quand on saura où les modèles échouent.
    Ce champ ne fait que transporter le signal jusque-là.
    """

    PUBLIC_PREFERRED = "public_preferred"
    PRIVATE_PREFERRED = "private_preferred"
    EITHER = "either"


# --------------------------------------------------------------------------- #
# Tables de cohérence : ce qu'une famille impose au futur item
# --------------------------------------------------------------------------- #


class ProfilFamille(ModeleStrict):
    """Le contrat qu'une famille impose aux items qu'elle engendrera."""

    question_type: QuestionType
    expected_behavior: ExpectedBehavior
    answerability: Answerability


#: Type de question, comportement attendu et répondabilité de chaque famille.
#: C'est ici que la V0.2 et la phase 7 se rejoignent : les douze familles de la
#: phase 7 se projettent sur les six `QuestionType` du harnais, qui font foi.
PROFILS: dict[FamilyKind, ProfilFamille] = {
    FamilyKind.FACT_RECALL: ProfilFamille(
        question_type=QuestionType.FACT,
        expected_behavior=ExpectedBehavior.ANSWER,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.QUALIFICATION: ProfilFamille(
        question_type=QuestionType.QUALIFICATION,
        expected_behavior=ExpectedBehavior.ANSWER,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.CALCULATION: ProfilFamille(
        question_type=QuestionType.CALCULATION,
        expected_behavior=ExpectedBehavior.CALCULATE,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.FALSE_PREMISE: ProfilFamille(
        question_type=QuestionType.FALSE_PREMISE,
        expected_behavior=ExpectedBehavior.REFUTE_PREMISE,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.TRUE_PREMISE_ADVERSARIAL: ProfilFamille(
        question_type=QuestionType.TRUE_PREMISE_ADVERSARIAL,
        expected_behavior=ExpectedBehavior.ANSWER,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.CALIBRATED_ABSTENTION: ProfilFamille(
        question_type=QuestionType.CALIBRATED_ABSTENTION,
        expected_behavior=ExpectedBehavior.ABSTAIN,
        answerability=Answerability.UNANSWERABLE,
    ),
    FamilyKind.CONDITIONAL_ANSWER: ProfilFamille(
        question_type=QuestionType.QUALIFICATION,
        expected_behavior=ExpectedBehavior.ANSWER_WITH_CONDITIONS,
        answerability=Answerability.PARTIALLY_ANSWERABLE,
    ),
    FamilyKind.TEMPORAL: ProfilFamille(
        question_type=QuestionType.FACT,
        expected_behavior=ExpectedBehavior.ANSWER,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.CROSS_REGULATORY: ProfilFamille(
        question_type=QuestionType.QUALIFICATION,
        expected_behavior=ExpectedBehavior.ANSWER,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.EXCEPTION: ProfilFamille(
        question_type=QuestionType.QUALIFICATION,
        expected_behavior=ExpectedBehavior.ANSWER_WITH_CONDITIONS,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.NEGATIVE_ASSERTION: ProfilFamille(
        question_type=QuestionType.FALSE_PREMISE,
        expected_behavior=ExpectedBehavior.REFUTE_PREMISE,
        answerability=Answerability.ANSWERABLE,
    ),
    FamilyKind.MISSING_INFORMATION: ProfilFamille(
        question_type=QuestionType.CALIBRATED_ABSTENTION,
        expected_behavior=ExpectedBehavior.REQUEST_MISSING_INFORMATION,
        answerability=Answerability.PARTIALLY_ANSWERABLE,
    ),
}

#: Familles dont une réponse fausse conduit un professionnel à un acte fautif :
#: déclarer ou ne pas déclarer, classer, publier, refuser une entrée en relation.
FAMILLES_DANGEREUSES: frozenset[FamilyKind] = frozenset(
    {
        FamilyKind.QUALIFICATION,
        FamilyKind.CALCULATION,
        FamilyKind.FALSE_PREMISE,
        FamilyKind.NEGATIVE_ASSERTION,
        FamilyKind.EXCEPTION,
        FamilyKind.CROSS_REGULATORY,
        FamilyKind.CONDITIONAL_ANSWER,
    }
)

#: Familles qui alimentent naturellement le privé : ce sont celles où l'on veut
#: mesurer sans que le corpus d'entraînement des modèles ait pu les absorber.
FAMILLES_HOLDOUT: frozenset[FamilyKind] = frozenset(
    {
        FamilyKind.FALSE_PREMISE,
        FamilyKind.TRUE_PREMISE_ADVERSARIAL,
        FamilyKind.NEGATIVE_ASSERTION,
        FamilyKind.EXCEPTION,
        FamilyKind.TEMPORAL,
        FamilyKind.CROSS_REGULATORY,
    }
)

#: Score minimal pour qu'une famille soit retenue dans la carte.
#: En deçà, l'angle existe mais l'item serait forcé — et la spécification §10
#: interdit de forcer une famille pour remplir un quota.
SCORE_RETENU = 2


class TemporalBlueprint(ModeleStrict):
    """Ancrage temporel d'une famille temporelle (phase 7 §13).

    Une réforme proposée n'est jamais un régime applicable : elle se déclare
    `proposed` et ne peut pas servir de gold. C'est la seule façon d'éviter des
    questions dont la bonne réponse serait du droit qui n'existe pas encore.
    """

    #: Date à laquelle la question se place.
    target_date: dt.date
    #: Régime applicable à cette date.
    applicable_regime: str = Field(min_length=1)
    #: Version du texte à consulter pour trancher.
    text_version_date: dt.date
    #: Régime antérieur, quand la question porte sur un changement.
    previous_regime: str = ""
    #: Ce qui change entre les deux régimes, en une phrase.
    transition: str = ""
    regulatory_status: RegulatoryStatus = RegulatoryStatus.IN_FORCE

    @model_validator(mode="after")
    def _une_reforme_nest_pas_un_regime(self) -> TemporalBlueprint:
        if self.regulatory_status is RegulatoryStatus.PROPOSED:
            raise ValueError(
                "une réforme proposée ne peut pas servir de régime applicable : "
                "elle se teste comme proposition, jamais comme droit en vigueur"
            )
        return self


class CandidateFamily(ModeleStrict):
    """Un angle d'interrogation possible sur une règle, et ses conditions.

    Ce modèle ne contient **aucune question rédigée**. C'est délibéré : la
    phase 7 décide de ce qui est mesurable, la phase 8 décidera de ce qui est
    demandé. Écrire une question ici reviendrait à rédiger du gold sur des
    règles dont aucune n'est encore vérifiée.
    """

    # -- identité -------------------------------------------------------------- #
    id: str = Field(min_length=1)
    rule_id: str = Field(min_length=1)
    domain: Domain
    family_kind: FamilyKind
    family_code: str = Field(min_length=2)

    # -- ce que la famille mesure ---------------------------------------------- #
    concept_tested: str = Field(min_length=1)
    redundancy_group_id: str = Field(min_length=1)
    family_score: int = Field(ge=0, le=3)
    family_rationale: str = Field(min_length=1)
    priority: Priority
    predicted_difficulty: int = Field(ge=1, le=5)
    difficulty_rationale: str = Field(min_length=1)

    # -- contrat imposé au futur item ------------------------------------------ #
    question_type: QuestionType
    expected_behavior: ExpectedBehavior
    answerability: Answerability
    #: Piège mesuré. `NONE` pour une prémisse vraie : c'est ce qui la distingue
    #: de son jumeau (phase 7 §3, F5).
    reasoning_trap: ReasoningTrap = ReasoningTrap.NONE
    #: Piège que la prémisse vraie **imite** sans le contenir. Le schéma `Item`
    #: exige un piège nommé pour `true_premise_adversarial` : c'est cette valeur
    #: qui y sera reportée, pendant que `reasoning_trap` reste `NONE` ici.
    mimicked_trap: ReasoningTrap | None = None
    requires_negative_claim: bool = False
    #: Ce qu'une bonne abstention devra réclamer, nommément.
    abstention_focus: list[str] = Field(default_factory=list)
    #: Régimes avec lesquels la confusion est juridiquement plausible.
    cross_regulatory_with: list[str] = Field(default_factory=list)
    candidate_disqualifying_errors: list[CriticalErrorKind] = Field(default_factory=list)
    temporal_blueprint: TemporalBlueprint | None = None

    # -- jumeaux ---------------------------------------------------------------- #
    twin_candidate: bool = False
    twin_group_id: str | None = None
    twin_type: TwinType | None = None
    twin_partner_id: str | None = None

    # -- source ------------------------------------------------------------------ #
    #: Recopiée de la règle : une famille sans source ne peut rien ancrer.
    source: Source
    regulatory_regime: str = Field(min_length=1)
    regulatory_status: RegulatoryStatus = RegulatoryStatus.IN_FORCE

    # -- exploitabilité ----------------------------------------------------------- #
    candidate_family_status: CandidateFamilyStatus
    #: Ce qui interdit la famille aujourd'hui. Vide si `ready`.
    blocking_reasons: list[str] = Field(default_factory=list)
    #: Ce qui la limite sans l'interdire.
    review_reasons: list[str] = Field(default_factory=list)
    public_eligible: bool = True
    private_eligible: bool = True
    holdout_recommendation: HoldoutRecommendation = HoldoutRecommendation.EITHER
    notes: str = ""

    # ------------------------------------------------------------------------- #

    @model_validator(mode="after")
    def _profil_conforme_a_la_famille(self) -> CandidateFamily:
        """Le contrat d'une famille ne s'écarte pas de son profil déclaré."""
        profil = PROFILS[self.family_kind]
        if self.question_type is not profil.question_type:
            raise ValueError(
                f"famille « {self.family_kind.value} » : question_type "
                f"« {self.question_type.value} » au lieu de « {profil.question_type.value} »"
            )
        if self.family_code != CODES_FAMILLES[self.family_kind]:
            raise ValueError(
                f"family_code « {self.family_code} » ne correspond pas à "
                f"« {self.family_kind.value} »"
            )
        return self

    @model_validator(mode="after")
    def _comportement_et_repondabilite(self) -> CandidateFamily:
        """Les mêmes tables de cohérence que l'item : une famille ne promet rien d'infaisable."""
        admis = COMPORTEMENTS_PAR_TYPE[self.question_type]
        if self.expected_behavior not in admis:
            raise ValueError(
                f"expected_behavior « {self.expected_behavior.value} » incompatible "
                f"avec question_type « {self.question_type.value} »"
            )
        admises = REPONDABILITE_PAR_COMPORTEMENT[self.expected_behavior]
        if self.answerability not in admises:
            raise ValueError(
                f"answerability « {self.answerability.value} » incompatible avec "
                f"expected_behavior « {self.expected_behavior.value} »"
            )
        return self

    @model_validator(mode="after")
    def _pieges_coherents(self) -> CandidateFamily:
        """Une fausse prémisse nomme son piège ; une prémisse vraie n'en contient pas."""
        if (
            self.question_type is QuestionType.FALSE_PREMISE
            and self.reasoning_trap is ReasoningTrap.NONE
        ):
            raise ValueError(
                "une fausse prémisse sans piège nommé ne mesure rien de particulier"
            )
        if self.question_type is QuestionType.TRUE_PREMISE_ADVERSARIAL:
            if self.reasoning_trap is not ReasoningTrap.NONE:
                raise ValueError(
                    "une prémisse vraie ne contient pas de piège : reasoning_trap "
                    "doit valoir NONE, et le piège imité va dans mimicked_trap"
                )
            if self.mimicked_trap is None or self.mimicked_trap is ReasoningTrap.NONE:
                raise ValueError(
                    "une prémisse vraie adversariale imite un piège : mimicked_trap "
                    "doit le nommer, sinon la question n'est pas comparable à son jumeau"
                )
        elif self.mimicked_trap is not None:
            raise ValueError(
                "mimicked_trap n'a de sens que pour une prémisse vraie adversariale"
            )
        return self

    @model_validator(mode="after")
    def _verification_negative_requise(self) -> CandidateFamily:
        """Affirmer qu'une disposition n'existe pas exige une connaissance négative."""
        piege_negatif = (
            self.question_type is QuestionType.FALSE_PREMISE
            and self.reasoning_trap in PIEGES_A_VERIFICATION_NEGATIVE
        )
        if piege_negatif and not self.requires_negative_claim:
            raise ValueError(
                f"piège « {self.reasoning_trap.value} » : la famille affirme une "
                "disposition inexistante, requires_negative_claim doit valoir true"
            )
        return self

    @model_validator(mode="after")
    def _exigences_dabstention(self) -> CandidateFamily:
        """Une abstention se note sur ce qu'elle réclame, pas sur son silence."""
        attendu = self.expected_behavior in COMPORTEMENTS_A_EXIGENCES
        if attendu and not self.abstention_focus:
            raise ValueError(
                f"expected_behavior « {self.expected_behavior.value} » exige "
                "abstention_focus : dire ce que le modèle doit réclamer"
            )
        if not attendu and self.abstention_focus:
            raise ValueError(
                "abstention_focus n'a de sens que pour une abstention ou une "
                "demande d'information"
            )
        return self

    @model_validator(mode="after")
    def _jumeaux_coherents(self) -> CandidateFamily:
        renseignes = [self.twin_group_id, self.twin_type, self.twin_partner_id]
        if self.twin_candidate and not all(renseignes):
            raise ValueError(
                "twin_candidate : twin_group_id, twin_type et twin_partner_id sont "
                "requis — un jumeau sans jumeau ne mesure aucune sensibilité"
            )
        if not self.twin_candidate and any(renseignes):
            raise ValueError("twin_group_id/twin_type/twin_partner_id sans twin_candidate")
        if self.twin_partner_id == self.id:
            raise ValueError("une famille ne peut pas être son propre jumeau")
        return self

    @model_validator(mode="after")
    def _statut_motive(self) -> CandidateFamily:
        """Un blocage se motive ; une famille prête n'a rien à lever."""
        if self.candidate_family_status is CandidateFamilyStatus.BLOCKED:
            if not self.blocking_reasons:
                raise ValueError("candidate_family_status « blocked » sans motif")
        elif self.blocking_reasons:
            raise ValueError(
                f"candidate_family_status « {self.candidate_family_status.value} » "
                "avec des motifs de blocage"
            )
        if (
            self.candidate_family_status is CandidateFamilyStatus.NEEDS_REVIEW
            and not self.review_reasons
        ):
            raise ValueError("candidate_family_status « needs_review » sans réserve")
        if not self.public_eligible and not self.private_eligible:
            raise ValueError(
                "une famille exclue des deux corpus n'a aucune raison d'exister"
            )
        return self

    @model_validator(mode="after")
    def _famille_temporelle_ancree(self) -> CandidateFamily:
        """Une famille temporelle sans régime applicable ne teste aucune date."""
        if self.family_kind is FamilyKind.TEMPORAL and self.temporal_blueprint is None:
            raise ValueError(
                "famille TEMPORAL sans temporal_blueprint : la question ne saurait "
                "pas à quelle date ni sous quel régime elle se place"
            )
        if self.family_kind is not FamilyKind.TEMPORAL and self.temporal_blueprint is not None:
            raise ValueError("temporal_blueprint réservé aux familles temporelles")
        return self

    @property
    def is_ready(self) -> bool:
        """Seule une famille prête peut engendrer un item du benchmark final."""
        return self.candidate_family_status is CandidateFamilyStatus.READY

    @property
    def is_retained(self) -> bool:
        """Retenue dans la carte : l'angle vaut la peine, indépendamment du blocage."""
        return self.family_score >= SCORE_RETENU
