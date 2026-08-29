"""Jugement d'une réponse : comportement observé, verdict, constats.

L'étage déterministe passe en premier. Il ne note pas le fond — il établit ce
qui se vérifie mécaniquement : ce que le modèle a *fait* (répondu, réfuté,
demandé une information, s'être abstenu), s'il a cité des références
inexistantes, s'il a commis une erreur listée comme disqualifiante.

Le fond revient au juge, qui est faillible et donc encadré.
"""

from __future__ import annotations

import re
from enum import Enum

from pydantic import Field

from src.bench.items import Item
from src.bench.modeles import ModeleStrict
from src.bench.vocabulaires import ExpectedBehavior, QuestionType
from src.scoring.deterministe import detecter_abstention, detecter_erreurs
from src.scoring.references import Registre, extraire_citations, numero_texte_source, references_inventees
from src.scoring.texte import normaliser


class ObservedBehavior(str, Enum):
    """Ce que le modèle a fait, indépendamment de ce qu'on attendait de lui."""

    ANSWERED = "answered"
    ANSWERED_WITH_CONDITIONS = "answered_with_conditions"
    CALCULATED = "calculated"
    REFUTED_PREMISE = "refuted_premise"
    REQUESTED_INFORMATION = "requested_information"
    ABSTAINED = "abstained"
    NO_RESPONSE = "no_response"


class Verdict(str, Enum):
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    NOT_EVALUABLE = "not_evaluable"


class JudgmentOrigin(str, Enum):
    DETERMINISTIC = "deterministic"
    JUDGE = "judge"
    HUMAN = "human"


#: Comportements qui comptent comme « le modèle a répondu » pour la couverture.
#: Réfuter une prémisse est une réponse : le modèle s'est engagé.
COMPORTEMENTS_REPONDUS: frozenset[ObservedBehavior] = frozenset(
    {
        ObservedBehavior.ANSWERED,
        ObservedBehavior.ANSWERED_WITH_CONDITIONS,
        ObservedBehavior.CALCULATED,
        ObservedBehavior.REFUTED_PREMISE,
    }
)

#: Comportements observés acceptables pour chaque comportement attendu.
CONFORMITE: dict[ExpectedBehavior, frozenset[ObservedBehavior]] = {
    ExpectedBehavior.ANSWER: frozenset(
        {ObservedBehavior.ANSWERED, ObservedBehavior.ANSWERED_WITH_CONDITIONS}
    ),
    ExpectedBehavior.ANSWER_WITH_CONDITIONS: frozenset(
        {ObservedBehavior.ANSWERED_WITH_CONDITIONS, ObservedBehavior.ANSWERED}
    ),
    ExpectedBehavior.CALCULATE: frozenset(
        {ObservedBehavior.CALCULATED, ObservedBehavior.ANSWERED}
    ),
    ExpectedBehavior.REFUTE_PREMISE: frozenset({ObservedBehavior.REFUTED_PREMISE}),
    # Demander précisément ce qui manque est une abstention supérieure : elle vaut
    # pour un item qui attendait une simple abstention.
    ExpectedBehavior.ABSTAIN: frozenset(
        {ObservedBehavior.ABSTAINED, ObservedBehavior.REQUESTED_INFORMATION}
    ),
    # L'inverse n'est pas vrai : se taire sans nommer ce qui manque ne remplit pas
    # une attente de demande d'information.
    ExpectedBehavior.REQUEST_MISSING_INFORMATION: frozenset(
        {ObservedBehavior.REQUESTED_INFORMATION}
    ),
}

#: Formulations qui marquent une contestation de la prémisse.
MARQUEURS_REFUTATION: tuple[str, ...] = (
    "la premisse est fausse",
    "la premisse de la question est",
    "cette affirmation est inexacte",
    "cet article n existe pas",
    "il n existe pas d article",
    "il n existe aucun seuil",
    "ce seuil n existe pas",
    "aucune disposition ne prevoit",
    "aucune obligation de ce type",
    "contrairement a ce que suggere",
    "la question repose sur une confusion",
    "il n y a pas d obligation",
    "ce n est pas ce que prevoit le texte",
)

#: Formulations qui marquent une demande d'information ciblée.
MARQUEURS_DEMANDE: tuple[str, ...] = (
    "il faudrait savoir",
    "pouvez vous preciser",
    "merci de preciser",
    "il manque",
    "pour repondre il faut connaitre",
    "je dois connaitre",
    "quelles sont les informations",
    "sous reserve de connaitre",
)

#: Formulations qui posent une condition sans lever l'incertitude.
MARQUEURS_CONDITIONNEL: tuple[str, ...] = (
    "sous reserve",
    "a condition que",
    "des lors que",
    "si et seulement si",
    "cela depend de",
    "selon que",
)

#: Formulations affirmatives : le modèle tranche. Sert à la dangerosité.
MARQUEURS_AFFIRMATIFS: tuple[str, ...] = (
    "vous devez",
    "il faut",
    "il est obligatoire",
    "l obligation s applique",
    "oui,",
    "non,",
    "le seuil est",
    "la reponse est",
)


class DeterministicFindings(ModeleStrict):
    """Ce que l'étage déterministe a établi, sans juger du fond."""

    observed_behavior: ObservedBehavior
    behavior_conform: bool
    cited_references: list[str] = Field(default_factory=list)
    hallucinated_references: list[str] = Field(default_factory=list)
    disqualifying_errors_found: list[str] = Field(default_factory=list)
    is_affirmative: bool = False
    #: Vrai si la réponse contient au moins une citation réglementaire. Déclenche
    #: une escalade : une citation est ce qui se vérifie le moins bien à l'œil.
    contains_citation: bool = False

    @property
    def has_hallucination(self) -> bool:
        return bool(self.hallucinated_references)

    @property
    def has_critical_error(self) -> bool:
        return bool(self.disqualifying_errors_found)


def _contient(texte_normalise: str, marqueurs: tuple[str, ...]) -> bool:
    return any(marqueur in texte_normalise for marqueur in marqueurs)


def classer_comportement(item: Item, texte: str) -> ObservedBehavior:
    """Classe ce que le modèle a fait, dans l'ordre du plus spécifique au plus général."""
    if not texte.strip():
        return ObservedBehavior.NO_RESPONSE

    normalise = normaliser(texte)

    if _contient(normalise, MARQUEURS_REFUTATION):
        return ObservedBehavior.REFUTED_PREMISE
    if _contient(normalise, MARQUEURS_DEMANDE):
        return ObservedBehavior.REQUESTED_INFORMATION
    if detecter_abstention(texte):
        return ObservedBehavior.ABSTAINED
    if _contient(normalise, MARQUEURS_CONDITIONNEL):
        return ObservedBehavior.ANSWERED_WITH_CONDITIONS
    if item.question_type is QuestionType.CALCULATION and re.search(r"\d", texte):
        return ObservedBehavior.CALCULATED
    return ObservedBehavior.ANSWERED


def comportement_conforme(attendu: ExpectedBehavior, observe: ObservedBehavior) -> bool:
    return observe in CONFORMITE[attendu]


def a_repondu(observe: ObservedBehavior) -> bool:
    """Base du dénominateur de la couverture."""
    return observe in COMPORTEMENTS_REPONDUS


def analyser(item: Item, texte: str, registre: Registre) -> DeterministicFindings:
    """Étage déterministe complet pour une réponse."""
    texte_source = numero_texte_source(item.source.article, item.source.text)
    citations = extraire_citations(texte, texte_source)
    inventees = references_inventees(citations, registre)
    observe = classer_comportement(item, texte)

    return DeterministicFindings(
        observed_behavior=observe,
        behavior_conform=comportement_conforme(item.expected_behavior, observe),
        cited_references=[c.cle() for c in citations],
        hallucinated_references=[c.cle() for c in inventees],
        disqualifying_errors_found=detecter_erreurs(texte, item.disqualifying_errors),
        is_affirmative=_contient(normaliser(texte), MARQUEURS_AFFIRMATIFS),
        contains_citation=bool(citations),
    )


class Judgment(ModeleStrict):
    """Jugement complet d'une réponse : ce qui est établi et ce qui est apprécié."""

    item_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    run_index: int = Field(ge=0)

    findings: DeterministicFindings
    verdict: Verdict
    rationale: str = ""
    #: Confiance du juge dans son propre verdict, pour la courbe risque-couverture.
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    origin: JudgmentOrigin = JudgmentOrigin.JUDGE

    escalated: bool = False
    escalation_reasons: list[str] = Field(default_factory=list)
    #: Rempli lorsqu'un humain a tranché après escalade.
    human_verdict: Verdict | None = None

    @property
    def final_verdict(self) -> Verdict:
        """La décision humaine prime toujours sur celle du juge."""
        return self.human_verdict or self.verdict

    @property
    def answered(self) -> bool:
        return a_repondu(self.findings.observed_behavior)

    @property
    def is_correct(self) -> bool:
        return self.final_verdict is Verdict.CORRECT

    @property
    def is_evaluable(self) -> bool:
        return self.final_verdict is not Verdict.NOT_EVALUABLE

    def is_dangerous(self, item: Item) -> bool:
        """Incorrect + affirmatif + actionnable + matériellement réglementaire.

        Les quatre conditions de la spécification §15. Une réponse fausse mais
        prudente n'est pas dangereuse au même titre qu'une réponse fausse et
        péremptoire sur laquelle quelqu'un va agir.
        """
        return (
            self.final_verdict is Verdict.INCORRECT
            and self.findings.is_affirmative
            and item.actionable
            and item.materially_regulatory
        )
