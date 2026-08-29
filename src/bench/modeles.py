"""Modèles de base : source, vérification négative, grille de validation.

Le système n'invente jamais une source. Une source primaire est obligatoire pour
chaque item, y compris pour les fausses prémisses : réfuter une prémisse suppose
de pouvoir montrer ce que le texte dit réellement.
"""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModeleStrict(BaseModel):
    """Base commune : aucun champ inconnu, chaînes détourées."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Source(ModeleStrict):
    """Source primaire d'un item : le texte qui fait droit."""

    text: str = Field(min_length=1)
    article: str = Field(min_length=1)
    paragraph: str = ""
    url: str = Field(min_length=1)
    version_date: dt.date
    verified_by: str = ""
    verification_date: dt.date | None = None

    @property
    def is_verified(self) -> bool:
        """Une source n'est vérifiée que si un humain nommé l'a datée."""
        return bool(self.verified_by) and self.verification_date is not None


class SecondarySource(ModeleStrict):
    """Source secondaire : doctrine, position, Q&A.

    Elle complète une source primaire, elle ne la remplace jamais pour le gold
    juridique — c'est pourquoi elle n'a pas les mêmes exigences de vérification.
    """

    text: str = Field(min_length=1)
    url: str = Field(min_length=1)
    kind: str = Field(default="doctrine", min_length=1)
    version_date: dt.date | None = None


class NegativeClaimVerification(ModeleStrict):
    """Atteste qu'une disposition prétendument existante n'existe pas.

    Une fausse prémisse du genre « le seuil de 25 % de l'article 47 » ne peut pas
    être sourcée positivement : il n'y a rien à citer. Ce modèle enregistre ce qui
    a été cherché, où, dans quelle version, et par qui — c'est la seule façon de
    rendre une affirmation négative opposable.
    """

    #: Ce que la prémisse prétend, tel qu'elle le prétend.
    claim: str = Field(min_length=1)
    #: Périmètre effectivement inspecté (texte et version consultés).
    searched_in: str = Field(min_length=1)
    searched_version_date: dt.date
    #: Ce que le texte dit réellement à la place, si quelque chose.
    actual_provision: str = ""
    verified_by: str = Field(min_length=1)
    verification_date: dt.date

    @property
    def is_verified(self) -> bool:
        return True  # les champs obligatoires suffisent à l'attester


class GoldChecklist(ModeleStrict):
    """Grille de validation d'un gold.

    Les six contrôles de la spécification §12. Aucun item ne passe en `validated`
    sans que les six soient cochés : la grille est la condition, pas la trace.
    """

    source_verified: bool = False
    answer_verified: bool = False
    key_points_verified: bool = False
    disqualifying_errors_verified: bool = False
    answerability_verified: bool = False
    expected_behavior_verified: bool = False
    reviewed_by: str = ""
    review_date: dt.date | None = None

    @property
    def missing(self) -> list[str]:
        return [
            nom
            for nom in (
                "source_verified",
                "answer_verified",
                "key_points_verified",
                "disqualifying_errors_verified",
                "answerability_verified",
                "expected_behavior_verified",
            )
            if not getattr(self, nom)
        ]

    @property
    def is_complete(self) -> bool:
        return not self.missing and bool(self.reviewed_by) and self.review_date is not None


class AbstentionRequirements(ModeleStrict):
    """Ce qu'une bonne abstention doit contenir.

    Une abstention réussie n'est pas une non-réponse : elle nomme ce qui manque,
    dit pourquoi, et dit ce qu'on pourrait conclure si on l'avait.
    """

    #: Informations que le modèle doit réclamer, nommément.
    missing_information: list[str] = Field(min_length=1)
    #: Raison pour laquelle la question ne peut pas être tranchée en l'état.
    reason_required: bool = True
    #: Le modèle doit-il dire ce qu'il pourrait conclure une fois l'information obtenue.
    conditional_conclusion_expected: bool = False

    @model_validator(mode="after")
    def _pas_dexigence_vide(self) -> AbstentionRequirements:
        if any(not element.strip() for element in self.missing_information):
            raise ValueError("missing_information : aucune entrée ne peut être vide")
        return self
