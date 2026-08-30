"""Vocabulaires et modèles du Regulatory Rulebook.

Le Rulebook est la source unique dont dérivent concepts, familles, jumeaux et
items. Une règle y sépare explicitement trois choses que rien n'autorise à
confondre : **ce que le texte dit** (`statement`), **ce que cela implique en
pratique** (`operational_rule`), et **ce avec quoi on le confond**
(`common_confusions`).
"""

from __future__ import annotations

import datetime as dt
from enum import Enum

from pydantic import Field, model_validator

from src.bench.modeles import ModeleStrict


class RuleStatus(str, Enum):
    """Cycle de validation d'une règle (spécification §15).

    `source_checked` affirme que la source primaire a été consultée. Ce n'est
    jamais le résultat d'avoir trouvé une page web, et jamais un statut qu'un
    modèle peut s'accorder à lui-même.

    `source_checked` n'est pas `validated` : une source attestée dit que le
    texte a été lu, pas que la règle est complète. `requires_human_review` est
    réservé aux blocages **de fond** — un énoncé que le texte ne soutient pas,
    une ambiguïté juridique que rien de mécanique ne tranche. Une règle qui
    attend seulement la confirmation de ses exceptions reste `source_checked` :
    ce n'est pas la règle qui pose problème, c'est ce qu'on ignore encore
    d'elle.
    """

    DRAFT = "draft"
    SOURCE_CHECKED = "source_checked"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    LEGAL_REVIEW = "legal_review"
    VALIDATED = "validated"


class RuleType(str, Enum):
    DEFINITION = "DEFINITION"
    SCOPE = "SCOPE"
    OBLIGATION = "OBLIGATION"
    PROHIBITION = "PROHIBITION"
    THRESHOLD = "THRESHOLD"
    DEADLINE = "DEADLINE"
    EXCEPTION = "EXCEPTION"
    PROCEDURE = "PROCEDURE"
    DISCLOSURE = "DISCLOSURE"
    CLASSIFICATION = "CLASSIFICATION"
    RESPONSIBILITY = "RESPONSIBILITY"
    RECORD_KEEPING = "RECORD_KEEPING"
    GOVERNANCE = "GOVERNANCE"
    CALCULATION = "CALCULATION"


class Priority(str, Enum):
    """Gravité d'une erreur de compréhension sur cette règle."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CandidateQuestionFamily(str, Enum):
    """Familles de questions que la règle pourrait alimenter. Une suggestion, pas une question."""

    RECALL = "recall"
    QUALIFICATION = "qualification"
    FALSE_PREMISE = "false_premise"
    TRUE_PREMISE_ADVERSARIAL = "true_premise_adversarial"
    ABSTENTION = "abstention"
    CALCULATION = "calculation"
    TEMPORAL = "temporal"
    CROSS_REGULATORY = "cross_regulatory"


class ExceptionsStatus(str, Enum):
    """État de la recherche d'exceptions, exclusions, exemptions et conditions.

    Confondre « on a cherché, il n'y en a pas » avec « on n'a pas cherché »
    produit des questions dangereusement simplifiées : une règle présentée sans
    ses exceptions se teste comme un absolu qu'elle n'est pas.

    Cinq issues, et une distinction qui porte tout le reste : **avoir identifié
    des exceptions ne suffit pas, encore faut-il les avoir incorporées**. Une
    règle qui sait que des dérogations existent sans les porter est plus
    dangereuse qu'une règle qui l'ignore : elle a l'air complète.

    `NONE_IDENTIFIED` ne se déduit jamais d'une recherche textuelle
    infructueuse. Ne pas trouver le mot « dérogation » dans un article ne prouve
    pas qu'aucun autre article n'y déroge — c'est `REQUIRES_HUMAN_REVIEW` qui
    porte ce cas.
    """

    #: On a cherché la structure juridique, il n'y a pas d'exception. Jamais
    #: attribué par une recherche automatique.
    NONE_IDENTIFIED = "none_identified"
    #: Des exceptions existent et la règle les porte.
    IDENTIFIED_AND_INCORPORATED = "identified_and_incorporated"
    #: Des exceptions existent et la règle ne les porte pas encore.
    IDENTIFIED_BUT_NOT_INCORPORATED = "identified_but_not_incorporated"
    #: La notion d'exception n'a pas de sens pour cette règle.
    NOT_APPLICABLE = "not_applicable"
    #: Il faut un juriste pour trancher : l'automate ne peut pas conclure.
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    #: Personne n'a encore cherché.
    UNKNOWN = "unknown"


#: Statuts qui attestent qu'une recherche d'exceptions a réellement eu lieu et
#: a abouti. Seuls ceux-ci autorisent une règle à passer `validated` : les
#: autres disent soit qu'on n'a pas cherché, soit qu'on n'a pas conclu, soit
#: qu'on sait sans avoir intégré.
EXCEPTIONS_ABOUTIES: frozenset[ExceptionsStatus] = frozenset(
    {
        ExceptionsStatus.NONE_IDENTIFIED,
        ExceptionsStatus.IDENTIFIED_AND_INCORPORATED,
        ExceptionsStatus.NOT_APPLICABLE,
    }
)

#: Statuts qui portent effectivement une liste d'exceptions.
EXCEPTIONS_PORTEES: frozenset[ExceptionsStatus] = frozenset(
    {ExceptionsStatus.IDENTIFIED_AND_INCORPORATED}
)


class VerificationMethod(str, Enum):
    """Comment la source a été établie. Conditionne le statut atteignable."""

    #: Texte primaire effectivement récupéré et lu.
    PRIMARY_TEXT_FETCHED = "primary_text_fetched"
    #: Texte primaire lu par un humain.
    PRIMARY_TEXT_REVIEW = "primary_text_review"
    #: Source secondaire seulement : ne suffit jamais pour le gold juridique.
    SECONDARY_SOURCE_ONLY = "secondary_source_only"
    #: Référence issue de la connaissance du modèle, non confrontée au texte.
    MODEL_KNOWLEDGE_UNVERIFIED = "model_knowledge_unverified"


#: Méthodes qui permettent de dépasser le statut `draft`.
METHODES_SUFFISANTES: frozenset[VerificationMethod] = frozenset(
    {VerificationMethod.PRIMARY_TEXT_FETCHED, VerificationMethod.PRIMARY_TEXT_REVIEW}
)


class NegativeClaimStatus(str, Enum):
    #: Vérifié absent du texte primaire dans la version consultée.
    VERIFIED_ABSENT = "verified_absent"
    #: Le texte dit autre chose que ce que prétend l'affirmation.
    PRESENT_CONTRARY = "present_contrary"
    #: Pas encore vérifié. « Je n'ai pas trouvé » n'est pas « cela n'existe pas ».
    UNVERIFIED = "unverified"


class NegativeClaim(ModeleStrict):
    """Une affirmation fausse, et l'état de sa vérification.

    Une absence ne s'enregistre que lorsqu'elle se vérifie de façon robuste
    (spécification §6). Le schéma refuse `verified_absent` sans méthode
    suffisante : c'est ce qui empêche de transformer « je n'ai pas trouvé » en
    « cela n'existe pas ».
    """

    claim: str = Field(min_length=1)
    status: NegativeClaimStatus = NegativeClaimStatus.UNVERIFIED
    verification_method: VerificationMethod = VerificationMethod.MODEL_KNOWLEDGE_UNVERIFIED
    searched_in: str = ""
    actual_provision: str = ""
    note: str = ""

    @model_validator(mode="after")
    def _absence_robuste(self) -> NegativeClaim:
        if self.status is NegativeClaimStatus.VERIFIED_ABSENT:
            if self.verification_method not in METHODES_SUFFISANTES:
                raise ValueError(
                    "negative_claim « verified_absent » exige une vérification sur "
                    "texte primaire : « je n'ai pas trouvé » n'est pas « cela n'existe pas »"
                )
            if not self.searched_in.strip():
                raise ValueError(
                    "negative_claim « verified_absent » exige searched_in : "
                    "une absence n'est opposable que si l'on dit où l'on a cherché"
                )
        return self
