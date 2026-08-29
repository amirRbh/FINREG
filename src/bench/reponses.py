"""Réponses de modèle et métadonnées d'exécution.

Une réponse n'est exploitable que si l'on sait dans quelles conditions elle a
été produite : quel modèle, quelle version, quel prompt, quel jour. C'est ce que
porte `RunMetadata` (spécification §18 et §19).
"""

from __future__ import annotations

import datetime as dt

from pydantic import Field

from src.bench.modeles import ModeleStrict


class RunMetadata(ModeleStrict):
    """Conditions d'exécution d'un run. Gelées, jamais réécrites après coup."""

    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    seed: int | None = None
    timestamp: dt.datetime
    #: Version du prompt système utilisé, jamais modifiée rétroactivement.
    system_prompt_version: str = Field(min_length=1)
    system_prompt_sha256: str = Field(min_length=1)
    benchmark_version: str = Field(min_length=1)


class ModelResponse(ModeleStrict):
    """Ce qu'un modèle a répondu à un item, pour un index de run donné."""

    item_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    run_index: int = Field(ge=0)
    text: str = ""
    error: str | None = None
    latency_ms: int | None = None

    @property
    def is_usable(self) -> bool:
        """Une réponse en erreur n'est pas une mauvaise réponse : elle est absente."""
        return self.error is None
