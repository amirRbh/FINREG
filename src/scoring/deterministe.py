"""Étage déterministe du scoring.

Il passe **avant** le juge et tranche ce qui se tranche sans modèle :
références inventées, erreurs disqualifiantes, abstention. Ce qu'il n'établit
pas est laissé au juge, sous les plafonds qu'il impose (CLAUDE.md §6).

Un plafond n'est jamais une note : c'est une borne haute que le juge ne peut
pas dépasser. Un fait vérifié mécaniquement prime sur l'appréciation d'un LLM.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.schema import Axe, ConstatDeterministe, Flag, Item, NotesAxes, TypeItem
from src.scoring.references import (
    Registre,
    extraire_citations,
    numero_texte_source,
    references_inventees,
)
from src.scoring.texte import normaliser, normaliser_leger, sans_accents

#: Formulations qui marquent une abstention explicite.
MARQUEURS_ABSTENTION: tuple[str, ...] = (
    "je ne sais pas",
    "je ne peux pas repondre",
    "je ne suis pas en mesure",
    "je ne dispose pas",
    "je m abstiens",
    "je prefere m abstenir",
    "il n est pas possible de repondre",
    "je ne peux pas l affirmer",
    "sans certitude suffisante",
    "je ne peux pas confirmer",
    "cette question ne peut pas etre tranchee",
)

#: Préfixe qui permet à un item d'exprimer une erreur disqualifiante en expression
#: régulière plutôt qu'en formulation littérale.
PREFIXE_REGEX = "re:"


def detecter_abstention(reponse: str) -> bool:
    normalisee = normaliser(reponse)
    return any(marqueur in normalisee for marqueur in MARQUEURS_ABSTENTION)


def detecter_erreurs_disqualifiantes(reponse: str, item: Item) -> list[str]:
    """Correspondance des erreurs listées par l'item sur le texte de la réponse.

    Une entrée littérale est comparée sur la forme normalisée (casse, accents,
    ponctuation retirée). Une entrée préfixée par `re:` est traitée comme une
    expression régulière, évaluée contre une forme légère qui conserve la
    ponctuation : l'auteur du motif écrit contre un texte qui ressemble au sien.
    """
    normalisee = normaliser(reponse)
    legere = normaliser_leger(reponse)
    detectees: list[str] = []

    for erreur in item.erreurs_disqualifiantes:
        if erreur.startswith(PREFIXE_REGEX):
            # Le motif n'est pas normalisé : cela détruirait sa syntaxe (| [] {}).
            # Seuls la casse et les accents sont alignés sur la réponse.
            motif = sans_accents(erreur[len(PREFIXE_REGEX):].strip()).lower()
            try:
                trouve = re.search(motif, legere) is not None
            except re.error:
                # Un motif invalide est une erreur de corpus, pas une réponse fautive :
                # on ne disqualifie pas la réponse sur un motif qu'on ne sait pas lire.
                trouve = False
        else:
            trouve = normaliser(erreur) in normalisee

        if trouve:
            detectees.append(erreur)

    return detectees


def evaluer(item: Item, reponse: str, registre: Registre) -> ConstatDeterministe:
    """Construit le constat déterministe d'une réponse."""
    texte_source = numero_texte_source(item.source.article, item.source.texte)
    citations = extraire_citations(reponse, texte_source)
    inventees = references_inventees(citations, registre)
    disqualifiantes = detecter_erreurs_disqualifiantes(reponse, item)
    abstention = detecter_abstention(reponse)

    plafonds: dict[Axe, int] = {}
    flags: list[Flag] = []

    if inventees:
        # Une source inventée est l'erreur la plus grave : elle annule le sourcing
        # et borne l'exactitude comme la calibration.
        flags.append(Flag.HALLUCINATION_SOURCE)
        plafonds[Axe.SOURCING] = 0
        plafonds[Axe.EXACTITUDE] = min(plafonds.get(Axe.EXACTITUDE, 2), 1)
        plafonds[Axe.CALIBRATION] = min(plafonds.get(Axe.CALIBRATION, 2), 1)

    if disqualifiantes:
        flags.append(Flag.ERREUR_DISQUALIFIANTE)
        plafonds[Axe.EXACTITUDE] = 0

    articles_cites = [c for c in citations if c.genre != "texte"]
    if not citations and not abstention:
        # Aucune référence du tout : rien à opposer à un contrôleur.
        flags.append(Flag.SOURCING_INCOMPLET)
        plafonds[Axe.SOURCING] = 0
    elif citations and not articles_cites:
        # Un texte cité sans article : le sourcing existe mais n'est pas opposable.
        flags.append(Flag.SOURCING_INCOMPLET)
        plafonds[Axe.SOURCING] = min(plafonds.get(Axe.SOURCING, 2), 1)

    if abstention:
        flags.append(Flag.ABSTENTION)
    elif item.type is TypeItem.ABSTENTION:
        # L'item attendait une abstention et le modèle a répondu quand même.
        flags.append(Flag.SURCONFIANCE)
        plafonds[Axe.CALIBRATION] = 0

    return ConstatDeterministe(
        references_citees=[c.cle() for c in citations],
        references_inventees=[c.cle() for c in inventees],
        erreurs_disqualifiantes_detectees=disqualifiantes,
        abstention_detectee=abstention,
        plafonds=plafonds,
        flags=flags,
    )


def appliquer_plafonds(notes: NotesAxes, constat: ConstatDeterministe) -> NotesAxes:
    """Borne les notes du juge par les plafonds établis mécaniquement."""
    valeurs = notes.as_dict()
    for axe, plafond in constat.plafonds.items():
        valeurs[axe.value] = min(valeurs[axe.value], plafond)
    return NotesAxes(**valeurs)


def tranche_seul(constat: ConstatDeterministe) -> bool:
    """Vrai si le déterministe a plafonné les quatre axes à 0 : le juge n'a plus rien à dire."""
    return all(constat.plafonds.get(axe) == 0 for axe in Axe)


def notes_plancher(constat: ConstatDeterministe) -> NotesAxes:
    """Notes quand le déterministe tranche seul : tout ce qu'il a plafonné, au plafond."""
    return NotesAxes(**{axe.value: constat.plafonds.get(axe, 0) for axe in Axe})


def charger_registre(chemin: str | Path) -> Registre:
    return Registre.charger(Path(chemin))
