"""Orchestration d'une campagne complète : charger, exécuter, juger, rapporter."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from src.bench.config import BenchConfig
from src.bench.fournisseurs import (
    ModelProvider,
    ProviderRequest,
    creer_fournisseur,
)
from src.bench.juge import JudgeProtocol, juger_reponse
from src.bench.jugement import Judgment
from src.bench.rapport import Campagne
from src.bench.registre import charger_prive, charger_public
from src.bench.runner import BenchRunner, lire_prompt_systeme, verifier_non_retention
from src.bench.vocabulaires import Corpus
from src.cache import CacheDisque
from src.scoring.references import Registre as RegistreReferences


class ProviderJudge(JudgeProtocol):
    """Adapte un `ModelProvider` à l'interface du juge.

    Le juge est soumis au même garde-fou que les modèles évalués : il reçoit le
    texte des items.
    """

    def __init__(self, fournisseur: ModelProvider, prompt: str, temperature: float = 0.0):
        self.fournisseur = fournisseur
        self.prompt = prompt
        self.temperature = temperature
        self.appels = 0

    def juger(self, paquet) -> str:
        import asyncio

        self.appels += 1
        requete = ProviderRequest(
            system_prompt=self.prompt,
            question=paquet.to_prompt(),
            temperature=self.temperature,
        )
        return asyncio.run(self.fournisseur.run(requete)).text


class SyntheticJudge(JudgeProtocol):
    """Juge synthétique local : JSON valide, déterministe, sans réseau.

    Ses verdicts n'ont aucune valeur d'évaluation. Ils permettent de vérifier la
    mécanique de bout en bout sans appeler de modèle.
    """

    def __init__(self, verdict: str = "correct", confidence: float = 0.8):
        self.verdict = verdict
        self.confidence = confidence
        self.paquets = []

    def juger(self, paquet) -> str:
        self.paquets.append(paquet)
        return json.dumps(
            {
                "verdict": self.verdict,
                "rationale": "Jugement synthétique, sans valeur d'évaluation.",
                "confidence": self.confidence,
            },
            ensure_ascii=False,
        )


def executer_campagne(
    config: BenchConfig,
    racine_projet: Path = Path("."),
    juge: JudgeProtocol | None = None,
    fabrique=creer_fournisseur,
) -> Campagne:
    """Chaîne complète, sans rien écrire hors cache."""
    racine = Path(racine_projet)

    if config.corpus is Corpus.PRIVE:
        registre = charger_prive(
            racine / config.registry_root,
            racine / config.corpus_root,
            je_confirme_usage_local=True,
        )
    else:
        registre = charger_public(racine / config.registry_root, racine / config.corpus_root)

    items = sorted(registre.items, key=lambda i: i.id)
    prompt = lire_prompt_systeme(racine / config.system_prompt_path)

    runner = BenchRunner(
        config,
        prompt,
        CacheDisque(racine / config.cache_root, config.corpus),
        fabrique=fabrique,
    )
    execution = runner.execute(items)

    references = RegistreReferences.charger(racine / config.references_path)
    juge = juge or SyntheticJudge()

    # Le juge voit le texte des items : même garde-fou que les modèles évalués.
    if isinstance(juge, ProviderJudge):
        verifier_non_retention(items, juge.fournisseur)

    index = {item.id: item for item in items}
    jugements: list[Judgment] = []
    for reponse in execution.responses:
        item = index.get(reponse.item_id)
        if item is None:
            continue
        jugements.append(
            juger_reponse(item, reponse, references, juge, config.judge.audit_rate)
        )

    return Campagne(
        config=config,
        items=items,
        responses=execution.responses,
        judgments=jugements,
        metadata=execution.metadata,
    )
