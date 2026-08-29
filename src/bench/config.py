"""Configuration d'une campagne d'évaluation.

Gelée dans le dossier de run, telle qu'utilisée. `zero_retention` n'accepte
qu'un booléen `true` littéral : une garantie contractuelle ne se déduit pas
d'une valeur approximative.
"""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from src.bench.modeles import ModeleStrict
from src.bench.plan import BenchmarkPlan
from src.bench.qa import SeuilsQA
from src.bench.vocabulaires import Corpus


def _booleen_strict(valeur: object) -> bool:
    """Absent, null, « true », 1 : tout ce qui n'est pas un booléen vaut refus."""
    return valeur is True


class ProviderConfig(ModeleStrict):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    adapter: str = Field(min_length=1)
    zero_retention: bool = False
    active: bool = True

    _strict = field_validator("zero_retention", mode="before")(
        classmethod(lambda cls, v: _booleen_strict(v))
    )


class ExecutionConfig(ModeleStrict):
    #: Trois exécutions par item (spécification §18).
    runs_per_item: int = Field(default=3, ge=1)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    seed: int | None = None
    concurrency: int = Field(default=4, ge=1)
    requests_per_minute: int = Field(default=60, ge=1)
    timeout_s: float = Field(default=60.0, gt=0)


class JudgeConfig(ModeleStrict):
    adapter: str = "fake-judge"
    model_name: str = "judge-synthetic"
    model_version: str = "0"
    zero_retention: bool = False
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    #: Part des réponses tirées pour l'audit aléatoire (spécification §16.6).
    audit_rate: float = Field(default=0.05, ge=0.0, le=1.0)

    _strict = field_validator("zero_retention", mode="before")(
        classmethod(lambda cls, v: _booleen_strict(v))
    )


class BenchConfig(ModeleStrict):
    benchmark_version: str = Field(min_length=1)
    corpus: Corpus
    registry_root: str = "registry"
    corpus_root: str = "corpus"
    system_prompt_path: str = "prompts/system-v1.txt"
    references_path: str = "registry/references.json"
    cache_root: str = ".cache"
    runs_root: str = "runs"
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    judge: JudgeConfig = Field(default_factory=JudgeConfig)
    plan: BenchmarkPlan = Field(default_factory=BenchmarkPlan)
    qa_thresholds: SeuilsQA = Field(default_factory=SeuilsQA)
    providers: list[ProviderConfig] = Field(min_length=1)

    @model_validator(mode="after")
    def _identifiants_uniques(self) -> BenchConfig:
        vus = [p.id for p in self.providers]
        doublons = sorted({i for i in vus if vus.count(i) > 1})
        if doublons:
            raise ValueError(f"identifiants de fournisseur en double : {doublons}")
        return self

    @property
    def active_providers(self) -> list[ProviderConfig]:
        return [p for p in self.providers if p.active]
