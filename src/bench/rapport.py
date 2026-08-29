"""Dossier de run et rapports (spécification §11 et §20).

Un run est immuable et reproductible à l'identique : c'est ce qui le rend
opposable. La latence et le fait d'avoir été servi par le cache décrivent
l'exécution, pas la réponse — ils sortent du périmètre comparé.

Le rapport public est le seul artefact destiné à sortir de la machine. Il est
construit à partir du seul corpus public, puis **contrôlé** contre les
identifiants privés avant d'être écrit.
"""

from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from src.bench.config import BenchConfig
from src.bench.isolation import assert_no_private_content, assert_no_private_ids
from src.bench.items import Item
from src.bench.jugement import Judgment
from src.bench.metriques import rapport_modele
from src.bench.plan import coverage_report
from src.bench.qa import Annotation, publiable
from src.bench.reponses import ModelResponse, RunMetadata
from src.bench.vocabulaires import Corpus
from src.io_utils import ecrire_json, hash_fichier, hash_texte, json_canonique

FORMAT_DOSSIER = "%Y-%m-%d-%H%M"

#: Fichiers dont le contenu doit être identique d'un run à l'autre.
FICHIERS_COMPARES = (
    "config.json",
    "fingerprints.json",
    "responses.json",
    "judgments.json",
    "metrics.json",
    "public_report.json",
)

#: Champs de réponse qui relèvent des circonstances, pas de la preuve.
CHAMPS_NON_REPRODUCTIBLES = ("latency_ms",)


@dataclass
class Campagne:
    """Tout ce qu'une campagne a produit, avant écriture."""

    config: BenchConfig
    items: list[Item]
    responses: list[ModelResponse]
    judgments: list[Judgment]
    metadata: dict[str, RunMetadata] = field(default_factory=dict)
    annotations: list[Annotation] = field(default_factory=list)

    @property
    def items_by_id(self) -> dict[str, Item]:
        return {item.id: item for item in self.items}

    @property
    def model_ids(self) -> list[str]:
        return sorted({j.model_id for j in self.judgments})

    def private_ids(self) -> list[str]:
        return sorted(item.id for item in self.items if item.corpus is Corpus.PRIVE)

    def private_texts(self) -> list[str]:
        textes: list[str] = []
        for item in self.items:
            if item.corpus is Corpus.PRIVE:
                textes += [item.question, item.gold_answer, *item.key_points]
        return textes


def nom_dossier(horodatage: dt.datetime | None = None) -> str:
    return (horodatage or dt.datetime.now()).strftime(FORMAT_DOSSIER)


def empreintes(campagne: Campagne) -> dict:
    """Ce qui identifie la campagne : prompts, registre, corpus, benchmark."""
    config = campagne.config
    return {
        "benchmark_version": config.benchmark_version,
        "system_prompt": {
            "path": config.system_prompt_path,
            "sha256": hash_fichier(Path(config.system_prompt_path)),
        },
        "references_registry": {
            "path": config.references_path,
            "sha256": hash_fichier(Path(config.references_path)),
        },
        "corpus": {
            "corpus": config.corpus.value,
            "count": len(campagne.items),
            "ids": sorted(item.id for item in campagne.items),
            "sha256": hash_texte(
                json_canonique(
                    [
                        item.model_dump(mode="json")
                        for item in sorted(campagne.items, key=lambda i: i.id)
                    ]
                )
            ),
        },
        "providers": [
            {"id": p.id, "model": p.model_name, "version": p.model_version,
             "zero_retention": p.zero_retention}
            for p in config.active_providers
        ],
    }


def _reponse_archivee(reponse: ModelResponse) -> dict:
    donnees = reponse.model_dump(mode="json")
    for champ in CHAMPS_NON_REPRODUCTIBLES:
        donnees.pop(champ, None)
    return donnees


def rapport_public(campagne: Campagne) -> dict:
    """Rapport destiné à sortir de la machine : corpus public uniquement.

    Ne contient aucun identifiant ni contenu privé — un contrôle le vérifie
    avant écriture, plutôt que de faire confiance à la construction.
    """
    publics = {
        item.id for item in campagne.items if item.corpus is Corpus.PUBLIC
    }
    jugements_publics = [j for j in campagne.judgments if j.item_id in publics]
    index = {i.id: i for i in campagne.items if i.id in publics}

    return {
        "benchmark_version": campagne.config.benchmark_version,
        "corpus": Corpus.PUBLIC.value,
        "item_count": len(publics),
        "runs_per_item": campagne.config.execution.runs_per_item,
        "models": [
            rapport_modele(jugements_publics, index, model_id)
            for model_id in campagne.model_ids
        ],
        "coverage_plan": coverage_report(
            [i for i in campagne.items if i.corpus is Corpus.PUBLIC],
            campagne.config.plan,
            Corpus.PUBLIC,
        ),
        "quality_assurance": publiable(
            jugements_publics, campagne.annotations, campagne.config.qa_thresholds
        ),
    }


def file_escalade(campagne: Campagne, chemin: Path) -> Path:
    """File de revue humaine : les réponses escaladées, corrigeables à la main.

    Contient le texte des items — elle reste dans le dossier de run, jamais
    publiée. Le CSV s'ouvre directement dans un tableur francophone.
    """
    colonnes = [
        "item_id", "model_id", "run_index", "escalation_reasons",
        "judge_verdict", "judge_confidence", "observed_behavior",
        "expected_behavior", "human_verdict", "annotator", "note",
    ]
    index = campagne.items_by_id
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    with chemin.open("w", encoding="utf-8-sig", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=colonnes, delimiter=";")
        redacteur.writeheader()
        for jugement in sorted(
            (j for j in campagne.judgments if j.escalated),
            key=lambda j: (j.item_id, j.model_id, j.run_index),
        ):
            item = index.get(jugement.item_id)
            redacteur.writerow(
                {
                    "item_id": jugement.item_id,
                    "model_id": jugement.model_id,
                    "run_index": jugement.run_index,
                    "escalation_reasons": " ".join(jugement.escalation_reasons),
                    "judge_verdict": jugement.verdict.value,
                    "judge_confidence": jugement.confidence if jugement.confidence is not None else "",
                    "observed_behavior": jugement.findings.observed_behavior.value,
                    "expected_behavior": item.expected_behavior.value if item else "",
                    "human_verdict": "",
                    "annotator": "",
                    "note": "",
                }
            )
    return chemin


def ecrire_run(
    campagne: Campagne, racine_runs: Path, horodatage: dt.datetime | None = None
) -> Path:
    """Écrit le dossier de run. Refuse d'écraser un run existant."""
    dossier = Path(racine_runs) / nom_dossier(horodatage)
    if dossier.exists():
        raise FileExistsError(
            f"{dossier} existe déjà : un run n'est jamais réécrit en place"
        )

    public = rapport_public(campagne)
    identifiants_prives = campagne.private_ids()

    # Contrôle avant écriture, pas après : un artefact fautif ne doit pas exister.
    assert_no_private_ids(public, identifiants_prives, "public_report.json")
    assert_no_private_content(public, campagne.private_texts(), "public_report.json")

    dossier.mkdir(parents=True)

    ecrire_json(dossier / "config.json", campagne.config.model_dump(mode="json"))
    ecrire_json(dossier / "fingerprints.json", empreintes(campagne))
    ecrire_json(
        dossier / "responses.json",
        [_reponse_archivee(r) for r in campagne.responses],
    )
    ecrire_json(
        dossier / "judgments.json",
        [j.model_dump(mode="json") for j in campagne.judgments],
    )
    ecrire_json(
        dossier / "metrics.json",
        {
            "models": [
                rapport_modele(campagne.judgments, campagne.items_by_id, model_id)
                for model_id in campagne.model_ids
            ]
        },
    )
    ecrire_json(dossier / "public_report.json", public)
    file_escalade(campagne, dossier / "escalations.csv")

    # Télémétrie : utile à l'exploitant, hors du périmètre comparé.
    ecrire_json(
        dossier / "execution.json",
        {
            "responses": len(campagne.responses),
            "errors": sum(1 for r in campagne.responses if r.error),
            "escalated": sum(1 for j in campagne.judgments if j.escalated),
            "run_metadata": {
                cle: meta.model_dump(mode="json") for cle, meta in campagne.metadata.items()
            },
            "latency_ms": {
                f"{r.item_id}/{r.model_id}/{r.run_index}": r.latency_ms
                for r in campagne.responses
                if r.latency_ms is not None
            },
        },
    )

    return dossier


def hash_run(dossier: Path) -> dict[str, str]:
    """Empreinte de chaque fichier comparé : sert à confronter deux runs."""
    return {
        nom: hash_fichier(Path(dossier) / nom)
        for nom in FICHIERS_COMPARES
        if (Path(dossier) / nom).is_file()
    }


def comparer_runs(run_a: Path, run_b: Path) -> list[str]:
    """Fichiers qui diffèrent entre deux runs. Vide = reproductible à l'identique."""
    a, b = hash_run(run_a), hash_run(run_b)
    return sorted({nom for nom in set(a) | set(b) if a.get(nom) != b.get(nom)})
