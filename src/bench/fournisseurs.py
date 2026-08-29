"""Abstraction de fournisseur de modèle (spécification §18).

`ModelProvider.run(request) -> ProviderResult`. Le harnais ne connaît rien
d'autre d'un fournisseur : brancher un modèle réel se fait ici, sans toucher au
reste.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field

from src.bench.config import ProviderConfig
from src.io_utils import hash_texte


@dataclass(frozen=True)
class ProviderRequest:
    system_prompt: str
    question: str
    temperature: float
    seed: int | None = None
    timeout_s: float = 60.0


@dataclass
class ProviderResult:
    text: str
    metadata: dict = field(default_factory=dict)


class ProviderError(RuntimeError):
    """Échec d'appel côté fournisseur : tracé, jamais transformé en mauvaise note."""


class ModelProvider(abc.ABC):
    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self.id = config.id
        self.model_name = config.model_name
        self.model_version = config.model_version
        self.provider = config.provider
        self.zero_retention = config.zero_retention

    @abc.abstractmethod
    async def run(self, request: ProviderRequest) -> ProviderResult:
        """Rend le texte de la réponse, ou lève `ProviderError`."""


_ADAPTATEURS: dict[str, type[ModelProvider]] = {}


def enregistrer_adaptateur(nom: str, classe: type[ModelProvider]) -> None:
    """Point d'extension : c'est ici qu'on branche un fournisseur réel."""
    _ADAPTATEURS[nom] = classe


def creer_fournisseur(config: ProviderConfig) -> ModelProvider:
    if config.adapter not in _ADAPTATEURS:
        connus = ", ".join(sorted(_ADAPTATEURS)) or "(aucun)"
        raise ProviderError(
            f"adaptateur inconnu « {config.adapter} » pour « {config.id} ». "
            f"Adaptateurs enregistrés : {connus}."
        )
    return _ADAPTATEURS[config.adapter](config)


class SyntheticProvider(ModelProvider):
    """Fournisseur synthétique local : aucun réseau, réponses déterministes.

    Sert au développement et à toute la suite de tests. Ses réponses n'ont
    aucune valeur d'évaluation ; elles servent à vérifier la mécanique.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self.calls: list[ProviderRequest] = []
        #: Réponses imposées, par fragment présent dans la question.
        self.scripted: dict[str, str] = {}
        #: Fragments de question qui doivent déclencher une erreur d'appel.
        self.failing: set[str] = set()

    @property
    def call_count(self) -> int:
        return len(self.calls)

    async def run(self, request: ProviderRequest) -> ProviderResult:
        self.calls.append(request)

        for fragment in self.failing:
            if fragment in request.question:
                raise ProviderError(f"échec simulé pour « {fragment} »")

        for fragment, reponse in self.scripted.items():
            if fragment in request.question:
                return ProviderResult(text=reponse, metadata={"scripted": True})

        empreinte = hash_texte(self.model_name + request.question)[:8]
        return ProviderResult(
            text=(
                f"Réponse synthétique du modèle {self.model_name} ({empreinte}). "
                "Ce texte ne vaut pas évaluation."
            ),
            metadata={"synthetic": True},
        )


enregistrer_adaptateur("synthetic", SyntheticProvider)
