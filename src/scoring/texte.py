"""Normalisation de texte partagée par l'étage déterministe.

Une comparaison de conformité doit être insensible à la casse, aux accents et
à la ponctuation, mais rester prévisible : on ne fait aucune correspondance
approximative silencieuse.
"""

from __future__ import annotations

import re
import unicodedata

_PONCTUATION = re.compile(r"[^\w\s()./-]+", flags=re.UNICODE)
_ESPACES = re.compile(r"\s+")


def sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def normaliser(texte: str) -> str:
    """Minuscules, sans accents, ponctuation retirée, espaces compactés."""
    texte = sans_accents(texte).lower()
    texte = texte.replace("’", "'").replace("œ", "oe")
    texte = _PONCTUATION.sub(" ", texte)
    return _ESPACES.sub(" ", texte).strip()


#: Points qui ne terminent pas une phrase : cotes d'articles et abréviations courantes.
_ABREVIATIONS = re.compile(
    r"\b(?:art|articles?|al|cf|ex|p|pp|no|n°|s|ss|c|par|ann|[LRD])\.",
    flags=re.IGNORECASE,
)
_SENTINELLE = "\x00"


def normaliser_leger(texte: str) -> str:
    """Minuscules, sans accents, espaces compactés — mais ponctuation conservée.

    C'est la forme contre laquelle sont évaluées les erreurs disqualifiantes
    exprimées en expression régulière : l'auteur du motif écrit contre un texte
    qui ressemble encore au sien, ponctuation et symboles compris.
    """
    texte = sans_accents(texte).lower().replace("’", "'")
    return _ESPACES.sub(" ", texte).strip()


def phrases(texte: str) -> list[str]:
    """Découpe grossière en phrases, utilisée pour rattacher un article à son texte.

    Les points d'abréviation (« art. », « L. 511-1 ») sont neutralisés avant le
    découpage : sans cela une cote d'article se retrouverait coupée en deux.
    """
    protege = _ABREVIATIONS.sub(lambda m: m.group(0).replace(".", _SENTINELLE), texte)
    morceaux = re.split(r"(?<=[.;:!?])\s+|\n+", protege)
    return [m.replace(_SENTINELLE, ".").strip() for m in morceaux if m.strip()]
