"""Garde-fou de non-rétention du corpus privé.

Règle non négociable (CLAUDE.md §3) : un item du corpus privé ne part jamais
vers un fournisseur qui ne garantit pas la non-rétention des données.

Le contrôle est fait **avant** toute construction de requête, pas juste avant
l'envoi : à ce stade le texte de l'item n'a même pas été recopié dans un
prompt. Aucun drapeau CLI, aucune variable d'environnement, aucun argument ne
permet de le contourner.
"""

from __future__ import annotations

from typing import Protocol

from src.schema import Corpus, Item


class PrivateCorpusLeakError(RuntimeError):
    """Tentative d'envoi d'un item privé à un fournisseur sans non-rétention.

    Volontairement une erreur, jamais un avertissement : l'exécution s'arrête.
    Le message ne contient aucun extrait d'item — seulement des identifiants —
    pour qu'un contenu privé ne se retrouve pas dans une trace ou un ticket.
    """


class DestinataireDonnees(Protocol):
    """Tout composant qui envoie du texte d'item à un tiers : modèle testé, juge."""

    id: str
    modele: str
    zero_retention: bool


def verifier_autorisation(corpus: Corpus, destinataire: DestinataireDonnees) -> None:
    """Autorise, ou lève `PrivateCorpusLeakError`.

    Le corpus public peut aller partout ; le corpus privé exige
    `zero_retention is True`, littéralement.
    """
    if corpus is not Corpus.PRIVE:
        return

    if destinataire.zero_retention is not True:
        raise PrivateCorpusLeakError(
            "Corpus privé : envoi refusé vers le destinataire "
            f"« {destinataire.id} » (modèle « {destinataire.modele} »), "
            "qui ne déclare pas zero_retention=true. "
            "Aucun appel n'a été émis. "
            "Corrigez la configuration du fournisseur, ou exécutez sur le corpus public."
        )


def verifier_autorisation_item(item: Item, destinataire: DestinataireDonnees) -> None:
    """Même contrôle, à la maille de l'item, quel que soit le corpus de l'exécution."""
    verifier_autorisation(item.corpus, destinataire)


def verifier_lot(items: list[Item], destinataire: DestinataireDonnees) -> None:
    """Contrôle un lot entier avant d'ouvrir la moindre connexion.

    Utilisé par le runner au démarrage : si un seul item privé est destiné à un
    fournisseur non conforme, rien ne part du tout.
    """
    for item in items:
        verifier_autorisation_item(item, destinataire)


def filtrer_publics(items: list[Item]) -> list[Item]:
    """Ne garde que les items publics. Utilisé par l'export (CLAUDE.md §8)."""
    return [item for item in items if item.corpus is Corpus.PUBLIC]
