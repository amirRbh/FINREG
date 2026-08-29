"""Vocabulaires fermés de FinReg-FR Bench V0.2.

Les valeurs sont en anglais : elles font partie du contrat de données du
benchmark, fixé par la spécification V0.2. Les commentaires restent en français.

Ce module ne contient que des énumérations et les tables de cohérence qui les
relient. Aucun modèle, pour qu'il puisse être importé partout sans cycle.
"""

from __future__ import annotations

from enum import Enum

# Le corpus est défini une seule fois dans le dépôt : on réutilise la V0.1.
from src.schema import Corpus  # noqa: F401  (ré-export volontaire)


class Domain(str, Enum):
    """Domaines couverts en V0. Les pondérations sont dans `plan.py`, pas ici."""

    SFDR = "SFDR"
    MIFID = "MIFID"
    AMF = "AMF"
    DORA = "DORA"
    LCBFT = "LCBFT"


class QuestionType(str, Enum):
    FACT = "fact"
    QUALIFICATION = "qualification"
    CALCULATION = "calculation"
    FALSE_PREMISE = "false_premise"
    #: Le dual de la fausse prémisse : une prémisse vraie qui ressemble à un piège.
    #: Sans cette famille, un modèle peut apprendre « FinReg = toujours réfuter ».
    TRUE_PREMISE_ADVERSARIAL = "true_premise_adversarial"
    CALIBRATED_ABSTENTION = "calibrated_abstention"


class ReasoningTrap(str, Enum):
    NONE = "NONE"
    FALSE_THRESHOLD = "FALSE_THRESHOLD"
    FALSE_ARTICLE = "FALSE_ARTICLE"
    CONCEPT_CONFLATION = "CONCEPT_CONFLATION"
    SCOPE_CONFUSION = "SCOPE_CONFUSION"
    TEMPORAL_CONFUSION = "TEMPORAL_CONFUSION"
    CAUSAL_INFERENCE = "CAUSAL_INFERENCE"
    OVERGENERALIZATION = "OVERGENERALIZATION"
    MISSING_INFORMATION = "MISSING_INFORMATION"
    CROSS_REGULATORY_CONFLATION = "CROSS_REGULATORY_CONFLATION"
    NEGATIVE_ASSERTION = "NEGATIVE_ASSERTION"
    EXCEPTION_OMISSION = "EXCEPTION_OMISSION"
    DEFINITION_DRIFT = "DEFINITION_DRIFT"


class Answerability(str, Enum):
    ANSWERABLE = "answerable"
    PARTIALLY_ANSWERABLE = "partially_answerable"
    UNANSWERABLE = "unanswerable"


class ExpectedBehavior(str, Enum):
    ANSWER = "answer"
    REFUTE_PREMISE = "refute_premise"
    ABSTAIN = "abstain"
    ANSWER_WITH_CONDITIONS = "answer_with_conditions"
    REQUEST_MISSING_INFORMATION = "request_missing_information"
    CALCULATE = "calculate"


class RegulatoryStatus(str, Enum):
    IN_FORCE = "in_force"
    AMENDED = "amended"
    TRANSITIONAL = "transitional"
    PROPOSED = "proposed"
    REPEALED = "repealed"


class ValidationStatus(str, Enum):
    """Cycle de vie d'un gold.

    Public  : draft → review → validated → published
    Privé   : draft → review → validated → locked
    """

    DRAFT = "draft"
    REVIEW = "review"
    VALIDATED = "validated"
    PUBLISHED = "published"
    LOCKED = "locked"


class TwinRole(str, Enum):
    """Rôle d'un item dans son groupe de jumeaux.

    Un groupe fait varier une seule chose à la fois : c'est ce qui permet de
    mesurer la sensibilité à la prémisse plutôt que la difficulté de la question.
    """

    TRUE_PREMISE = "true_premise"
    FALSE_PREMISE = "false_premise"
    INSUFFICIENT_INFORMATION = "insufficient_information"
    CONTEXT_SHIFT = "context_shift"


# --------------------------------------------------------------------------- #
# Tables de cohérence
# --------------------------------------------------------------------------- #

#: Comportements attendus admissibles pour chaque type de question.
COMPORTEMENTS_PAR_TYPE: dict[QuestionType, frozenset[ExpectedBehavior]] = {
    QuestionType.FACT: frozenset(
        {ExpectedBehavior.ANSWER, ExpectedBehavior.ANSWER_WITH_CONDITIONS}
    ),
    QuestionType.QUALIFICATION: frozenset(
        {ExpectedBehavior.ANSWER, ExpectedBehavior.ANSWER_WITH_CONDITIONS}
    ),
    QuestionType.CALCULATION: frozenset(
        {ExpectedBehavior.CALCULATE, ExpectedBehavior.REQUEST_MISSING_INFORMATION}
    ),
    QuestionType.FALSE_PREMISE: frozenset({ExpectedBehavior.REFUTE_PREMISE}),
    QuestionType.TRUE_PREMISE_ADVERSARIAL: frozenset(
        {
            ExpectedBehavior.ANSWER,
            ExpectedBehavior.ANSWER_WITH_CONDITIONS,
            ExpectedBehavior.CALCULATE,
        }
    ),
    QuestionType.CALIBRATED_ABSTENTION: frozenset(
        {ExpectedBehavior.ABSTAIN, ExpectedBehavior.REQUEST_MISSING_INFORMATION}
    ),
}

#: Niveaux de répondabilité admissibles pour chaque comportement attendu.
REPONDABILITE_PAR_COMPORTEMENT: dict[ExpectedBehavior, frozenset[Answerability]] = {
    ExpectedBehavior.ANSWER: frozenset({Answerability.ANSWERABLE}),
    ExpectedBehavior.CALCULATE: frozenset({Answerability.ANSWERABLE}),
    ExpectedBehavior.ANSWER_WITH_CONDITIONS: frozenset(
        {Answerability.ANSWERABLE, Answerability.PARTIALLY_ANSWERABLE}
    ),
    # Réfuter suppose qu'on sait quoi rétablir : la question sous-jacente est traitable.
    ExpectedBehavior.REFUTE_PREMISE: frozenset(
        {Answerability.ANSWERABLE, Answerability.PARTIALLY_ANSWERABLE}
    ),
    ExpectedBehavior.REQUEST_MISSING_INFORMATION: frozenset(
        {Answerability.PARTIALLY_ANSWERABLE, Answerability.UNANSWERABLE}
    ),
    ExpectedBehavior.ABSTAIN: frozenset({Answerability.UNANSWERABLE}),
}

#: Comportements qui exigent que l'item décrive ce qu'une bonne abstention doit contenir.
COMPORTEMENTS_A_EXIGENCES: frozenset[ExpectedBehavior] = frozenset(
    {ExpectedBehavior.ABSTAIN, ExpectedBehavior.REQUEST_MISSING_INFORMATION}
)

#: Pièges qui reposent sur l'affirmation d'une disposition inexistante. Ils imposent
#: une vérification négative : attester que la chose citée n'existe pas.
PIEGES_A_VERIFICATION_NEGATIVE: frozenset[ReasoningTrap] = frozenset(
    {
        ReasoningTrap.FALSE_THRESHOLD,
        ReasoningTrap.FALSE_ARTICLE,
        ReasoningTrap.NEGATIVE_ASSERTION,
    }
)

#: Rôle de jumeau attendu selon le type de question, quand le rôle est renseigné.
TYPES_PAR_ROLE_JUMEAU: dict[TwinRole, frozenset[QuestionType]] = {
    TwinRole.TRUE_PREMISE: frozenset(
        {
            QuestionType.TRUE_PREMISE_ADVERSARIAL,
            QuestionType.FACT,
            QuestionType.QUALIFICATION,
            QuestionType.CALCULATION,
        }
    ),
    TwinRole.FALSE_PREMISE: frozenset({QuestionType.FALSE_PREMISE}),
    TwinRole.INSUFFICIENT_INFORMATION: frozenset(
        {QuestionType.CALIBRATED_ABSTENTION, QuestionType.CALCULATION}
    ),
    TwinRole.CONTEXT_SHIFT: frozenset(
        {
            QuestionType.FACT,
            QuestionType.QUALIFICATION,
            QuestionType.CALCULATION,
            QuestionType.TRUE_PREMISE_ADVERSARIAL,
        }
    ),
}

#: Transitions autorisées du cycle de vie, par corpus.
TRANSITIONS: dict[Corpus, dict[ValidationStatus, frozenset[ValidationStatus]]] = {
    Corpus.PUBLIC: {
        ValidationStatus.DRAFT: frozenset({ValidationStatus.REVIEW}),
        ValidationStatus.REVIEW: frozenset(
            {ValidationStatus.DRAFT, ValidationStatus.VALIDATED}
        ),
        ValidationStatus.VALIDATED: frozenset(
            {ValidationStatus.REVIEW, ValidationStatus.PUBLISHED}
        ),
        ValidationStatus.PUBLISHED: frozenset(),
    },
    Corpus.PRIVE: {
        ValidationStatus.DRAFT: frozenset({ValidationStatus.REVIEW}),
        ValidationStatus.REVIEW: frozenset(
            {ValidationStatus.DRAFT, ValidationStatus.VALIDATED}
        ),
        ValidationStatus.VALIDATED: frozenset(
            {ValidationStatus.REVIEW, ValidationStatus.LOCKED}
        ),
        ValidationStatus.LOCKED: frozenset(),
    },
}

#: Statuts terminaux : un gold qui les atteint n'est plus modifiable, il est reversionné.
STATUTS_FIGES: frozenset[ValidationStatus] = frozenset(
    {ValidationStatus.PUBLISHED, ValidationStatus.LOCKED}
)

#: Statuts à partir desquels la grille de validation doit être entièrement cochée.
STATUTS_VALIDES: frozenset[ValidationStatus] = frozenset(
    {ValidationStatus.VALIDATED, ValidationStatus.PUBLISHED, ValidationStatus.LOCKED}
)


def statut_admis(corpus: Corpus, statut: ValidationStatus) -> bool:
    """Un statut `published` n'a pas de sens en privé, ni `locked` en public."""
    return statut in TRANSITIONS[corpus]
