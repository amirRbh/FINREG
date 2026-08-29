"""Contrat commun des fournisseurs de modèle.

Un fournisseur est un composant qui envoie du texte à un tiers : il porte donc
les attributs que le garde-fou de non-rétention inspecte (`id`, `modele`,
`zero_retention`).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass

from src.schema import ConfigFournisseur


@dataclass(frozen=True)
class Requete:
    prompt_systeme: str
    question: str
    temperature: float


class Fournisseur(abc.ABC):
    """Adaptateur vers un modèle. Une seule opération : compléter une requête."""

    def __init__(self, config: ConfigFournisseur) -> None:
        self.config = config
        self.id = config.id
        self.modele = config.modele
        self.zero_retention = config.zero_retention

    @abc.abstractmethod
    async def completer(self, requete: Requete, timeout_s: float) -> str:
        """Rend le texte de la réponse, ou lève une exception."""


class ErreurFournisseur(RuntimeError):
    """Échec d'appel côté fournisseur, rattrapé et tracé par le runner."""


#: Adaptateurs disponibles, par nom déclaré dans la config.
_ADAPTATEURS: dict[str, type[Fournisseur]] = {}


def enregistrer_adaptateur(nom: str, classe: type[Fournisseur]) -> None:
    """Point d'extension : c'est ici qu'on branche un fournisseur réel."""
    _ADAPTATEURS[nom] = classe


def creer_fournisseur(config: ConfigFournisseur) -> Fournisseur:
    if config.adaptateur not in _ADAPTATEURS:
        connus = ", ".join(sorted(_ADAPTATEURS)) or "(aucun)"
        raise ErreurFournisseur(
            f"adaptateur inconnu « {config.adaptateur} » pour le fournisseur "
            f"« {config.id} ». Adaptateurs enregistrés : {connus}."
        )
    return _ADAPTATEURS[config.adaptateur](config)
