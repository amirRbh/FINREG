"""Runner V0.2 : exécute les items contre les fournisseurs déclarés.

Trois exécutions par item, température 0, prompt système versionné et haché.
Le garde-fou de non-rétention est appliqué au lot entier **avant** qu'un seul
prompt soit assemblé : si un item privé vise un fournisseur non conforme, rien
ne part.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from src.bench.config import BenchConfig, ProviderConfig
from src.bench.fournisseurs import (
    ModelProvider,
    ProviderRequest,
    creer_fournisseur,
)
from src.bench.items import Item
from src.bench.reponses import ModelResponse, RunMetadata
from src.bench.vocabulaires import Corpus
from src.cache import CacheDisque, hash_prompt
from src.io_utils import hash_texte
from src.limiteur import LimiteurDebit
from src.securite import PrivateCorpusLeakError


def lire_prompt_systeme(chemin: Path) -> str:
    """Le prompt système est un fichier versionné, jamais une chaîne en dur."""
    texte = Path(chemin).read_text(encoding="utf-8")
    if not texte.strip():
        raise ValueError(f"prompt système vide : {chemin}")
    return texte


def verifier_non_retention(items: list[Item], fournisseur: ModelProvider) -> None:
    """Refuse d'envoyer un item privé à un destinataire sans non-rétention.

    Le message ne cite aucun contenu d'item — seulement des identifiants — pour
    qu'un contenu privé ne se retrouve pas dans une trace.
    """
    if fournisseur.zero_retention is True:
        return
    prives = [item for item in items if item.corpus is Corpus.PRIVE]
    if prives:
        raise PrivateCorpusLeakError(
            f"Corpus privé : envoi refusé vers « {fournisseur.id} » "
            f"(modèle « {fournisseur.model_name} »), qui ne déclare pas "
            f"zero_retention=true. {len(prives)} item(s) concernés. "
            "Aucun appel n'a été émis."
        )


@dataclass
class ExecutionResult:
    responses: list[ModelResponse] = field(default_factory=list)
    metadata: dict[str, RunMetadata] = field(default_factory=dict)
    network_calls: int = 0
    from_cache: int = 0
    errors: int = 0

    def by_key(self) -> dict[tuple[str, str, int], ModelResponse]:
        return {(r.item_id, r.model_id, r.run_index): r for r in self.responses}


class BenchRunner:
    def __init__(
        self,
        config: BenchConfig,
        system_prompt: str,
        cache: CacheDisque,
        fabrique: Callable[[ProviderConfig], ModelProvider] = creer_fournisseur,
        limiteur: LimiteurDebit | None = None,
        horloge: Callable[[], dt.datetime] = lambda: dt.datetime.now(dt.timezone.utc),
    ) -> None:
        self.config = config
        self.system_prompt = system_prompt
        self.system_prompt_sha256 = hash_texte(system_prompt)
        self.cache = cache
        self.fabrique = fabrique
        self.limiteur = limiteur or LimiteurDebit(config.execution.requests_per_minute)
        self.horloge = horloge
        self._semaphore = asyncio.Semaphore(config.execution.concurrency)
        self.max_concurrency_seen = 0
        self._en_vol = 0

    def _metadata(self, fournisseur: ModelProvider) -> RunMetadata:
        return RunMetadata(
            model_name=fournisseur.model_name,
            model_version=fournisseur.model_version,
            provider=fournisseur.provider,
            temperature=self.config.execution.temperature,
            seed=self.config.execution.seed,
            timestamp=self.horloge(),
            system_prompt_version=Path(self.config.system_prompt_path).stem,
            system_prompt_sha256=self.system_prompt_sha256,
            benchmark_version=self.config.benchmark_version,
        )

    async def _appeler(
        self, fournisseur: ModelProvider, item: Item, run_index: int
    ) -> ModelResponse:
        empreinte = hash_prompt(self.system_prompt, item.question)

        cache = self.cache.lire(empreinte, fournisseur.model_name, run_index)
        if cache is not None:
            return ModelResponse(
                item_id=item.id, model_id=fournisseur.id, run_index=run_index, text=cache
            )

        requete = ProviderRequest(
            system_prompt=self.system_prompt,
            question=item.question,
            temperature=self.config.execution.temperature,
            seed=self.config.execution.seed,
            timeout_s=self.config.execution.timeout_s,
        )

        await self.limiteur.acquerir()
        async with self._semaphore:
            self._en_vol += 1
            self.max_concurrency_seen = max(self.max_concurrency_seen, self._en_vol)
            debut = time.monotonic()
            try:
                resultat = await asyncio.wait_for(
                    fournisseur.run(requete), timeout=self.config.execution.timeout_s
                )
            except Exception as exc:  # tracé, jamais transformé en mauvaise note
                return ModelResponse(
                    item_id=item.id,
                    model_id=fournisseur.id,
                    run_index=run_index,
                    text="",
                    error=f"{type(exc).__name__}: {exc}",
                    latency_ms=int((time.monotonic() - debut) * 1000),
                )
            finally:
                self._en_vol -= 1

        latence = int((time.monotonic() - debut) * 1000)
        # Seul un appel réussi est mis en cache : une erreur doit pouvoir être rejouée.
        self.cache.ecrire(empreinte, fournisseur.model_name, run_index, resultat.text)
        return ModelResponse(
            item_id=item.id,
            model_id=fournisseur.id,
            run_index=run_index,
            text=resultat.text,
            latency_ms=latence,
        )

    async def execute_async(self, items: list[Item]) -> ExecutionResult:
        fournisseurs = {c.id: self.fabrique(c) for c in self.config.active_providers}

        # Contrôle du lot entier avant toute construction de prompt.
        for fournisseur in fournisseurs.values():
            verifier_non_retention(items, fournisseur)

        taches = [
            self._appeler(fournisseur, item, run_index)
            for item in items
            for fournisseur in fournisseurs.values()
            for run_index in range(self.config.execution.runs_per_item)
        ]
        reponses = await asyncio.gather(*taches)

        # Ordre stable : l'ordonnancement concurrent ne transparaît pas dans les artefacts.
        reponses = sorted(reponses, key=lambda r: (r.item_id, r.model_id, r.run_index))

        return ExecutionResult(
            responses=list(reponses),
            metadata={cle: self._metadata(f) for cle, f in fournisseurs.items()},
            network_calls=sum(1 for r in reponses if r.latency_ms is not None and not r.error),
            from_cache=sum(1 for r in reponses if r.latency_ms is None and not r.error),
            errors=sum(1 for r in reponses if r.error),
        )

    def execute(self, items: list[Item]) -> ExecutionResult:
        return asyncio.run(self.execute_async(items))
