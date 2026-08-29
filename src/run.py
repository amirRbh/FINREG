"""Orchestration d'une exécution complète et écriture du dossier de run.

Chaque exécution produit `runs/AAAA-MM-JJ-HHMM/`, immuable, qui contient tout ce
qu'il faut pour refaire le calcul et le contester : la config gelée, les hashes
des prompts et du corpus, les réponses brutes, les scores détaillés, le résumé
et la file de revue (CLAUDE.md §7).
"""

from __future__ import annotations

import asyncio
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from src.aggregate import AgregatModele, agreger, resume
from src.cache import CacheDisque
from src.io_utils import ecrire_json, hash_fichier, hash_texte
from src.loader import charger_corpus, resume_corpus
from src.providers.base import creer_fournisseur
from src.runner import Runner, lire_prompt_systeme
from src.schema import Config, ConfigFournisseur, Corpus, Item, ReponseBrute, Score
from src.scoring.deterministe import charger_registre, evaluer
from src.scoring.juge import Juge
from src.scoring.revue import detecter_divergences, exporter_csv

FORMAT_DOSSIER = "%Y-%m-%d-%H%M"

#: Fichiers du dossier de run dont le contenu doit être identique d'un run à l'autre.
FICHIERS_REPRODUCTIBLES = (
    "config.json",
    "empreintes.json",
    "reponses.json",
    "scores.json",
    "resume.json",
)


@dataclass
class Execution:
    """Tout ce qu'une exécution a produit, avant écriture."""

    config: Config
    items: list[Item]
    reponses: list[ReponseBrute]
    scores: list[Score]
    agregats: list[AgregatModele]
    empreintes: dict
    nb_entrees_revue: int = 0

    def reponses_par_cle(self) -> dict[tuple[str, str, int], str]:
        return {(r.item_id, r.fournisseur_id, r.index_run): r.texte for r in self.reponses}


def nom_dossier_run(horodatage: dt.datetime | None = None) -> str:
    return (horodatage or dt.datetime.now()).strftime(FORMAT_DOSSIER)


def empreintes(config: Config, items: list[Item]) -> dict:
    """Ce qui identifie l'exécution : prompts, corpus, registre, fournisseurs."""
    return {
        "prompt_systeme": {
            "chemin": config.chemin_prompt_systeme,
            "sha256": hash_fichier(Path(config.chemin_prompt_systeme)),
        },
        "prompt_juge": {
            "chemin": config.chemin_prompt_juge,
            "sha256": hash_fichier(Path(config.chemin_prompt_juge)),
        },
        "registre_references": {
            "chemin": config.chemin_registre,
            "sha256": hash_fichier(Path(config.chemin_registre)),
        },
        "corpus": resume_corpus(items),
        "fournisseurs": [
            {"id": f.id, "modele": f.modele, "zero_retention": f.zero_retention}
            for f in config.fournisseurs_actifs
        ],
    }


async def noter_tout(
    config: Config, items: list[Item], reponses: list[ReponseBrute], juge: Juge
) -> list[Score]:
    """Note chaque réponse : déterministe d'abord, juge ensuite."""
    registre = charger_registre(config.chemin_registre)
    index = {item.id: item for item in items}

    scores: list[Score] = []
    for reponse in sorted(reponses, key=lambda r: (r.item_id, r.fournisseur_id, r.index_run)):
        item = index.get(reponse.item_id)
        if item is None:
            continue
        constat = evaluer(item, reponse.texte, registre)
        scores.append(await juge.noter(item, reponse, constat, config.execution.timeout_s))

    return scores


def executer(
    config: Config,
    racine_projet: Path = Path("."),
    fabrique_fournisseur=creer_fournisseur,
    fabrique_juge=None,
) -> Execution:
    """Exécute le banc de bout en bout, sans rien écrire sur disque hors cache."""
    racine_projet = Path(racine_projet)
    items = charger_corpus(racine_projet / config.racine_corpus, config.corpus)

    prompt_systeme = lire_prompt_systeme(racine_projet / config.chemin_prompt_systeme)
    prompt_juge = lire_prompt_systeme(racine_projet / config.chemin_prompt_juge)

    runner = Runner(
        config,
        prompt_systeme,
        CacheDisque(racine_projet / config.racine_cache, config.corpus),
        fabrique_fournisseur=fabrique_fournisseur,
    )
    resultat = runner.executer(items)

    config_juge = ConfigFournisseur(
        id="juge",
        nom="Juge",
        editeur="interne",
        adaptateur=config.juge.adaptateur,
        modele=config.juge.modele,
        zero_retention=config.juge.zero_retention,
    )
    fournisseur_juge = (fabrique_juge or fabrique_fournisseur)(config_juge)
    juge = Juge(fournisseur_juge, prompt_juge, config.juge.temperature)

    scores = asyncio.run(noter_tout(config, items, resultat.reponses, juge))
    agregats = agreger(config, items, scores)

    return Execution(
        config=config,
        items=items,
        reponses=resultat.reponses,
        scores=scores,
        agregats=agregats,
        empreintes=empreintes(config, items),
    )


def ecrire_run(
    execution: Execution, racine_runs: Path, horodatage: dt.datetime | None = None
) -> Path:
    """Écrit le dossier de run. Refuse d'écraser un run existant."""
    dossier = Path(racine_runs) / nom_dossier_run(horodatage)
    if dossier.exists():
        raise FileExistsError(
            f"le dossier de run {dossier} existe déjà : un run n'est jamais réécrit en place"
        )
    dossier.mkdir(parents=True)

    entrees_revue = detecter_divergences(
        execution.scores,
        seuil=execution.config.juge.seuil_ecart_revue,
        items={item.id: item for item in execution.items},
    )
    execution.nb_entrees_revue = len(entrees_revue)

    ecrire_json(dossier / "config.json", execution.config.model_dump(mode="json"))
    ecrire_json(dossier / "empreintes.json", execution.empreintes)
    ecrire_json(
        dossier / "reponses.json",
        [r.pour_archive() for r in execution.reponses],
    )
    # Télémétrie d'exécution : utile à l'exploitant, hors du périmètre comparé.
    ecrire_json(
        dossier / "execution.json",
        {
            "nb_reponses": len(execution.reponses),
            "nb_depuis_cache": sum(1 for r in execution.reponses if r.depuis_cache),
            "nb_erreurs": sum(1 for r in execution.reponses if r.erreur),
            "latence_ms": {
                r.item_id + "/" + r.fournisseur_id + "/" + str(r.index_run): r.latence_ms
                for r in execution.reponses
                if r.latence_ms is not None
            },
        },
    )
    ecrire_json(
        dossier / "scores.json", [s.model_dump(mode="json") for s in execution.scores]
    )
    ecrire_json(
        dossier / "resume.json",
        resume(
            execution.config,
            execution.items,
            execution.scores,
            execution.agregats,
            len(entrees_revue),
        ),
    )
    exporter_csv(entrees_revue, dossier / "revue.csv")

    return dossier


def charger_run(dossier: Path) -> Execution:
    """Relit un dossier de run pour réinjecter une revue ou refaire un export."""
    from src.io_utils import lire_json

    dossier = Path(dossier)
    config = Config.model_validate(lire_json(dossier / "config.json"))
    reponses = [ReponseBrute.model_validate(r) for r in lire_json(dossier / "reponses.json")]
    scores = [Score.model_validate(s) for s in lire_json(dossier / "scores.json")]
    empreintes_run = lire_json(dossier / "empreintes.json")

    items = charger_corpus(Path(config.racine_corpus), config.corpus)
    version_attendue = empreintes_run.get("corpus", {}).get("version")
    version_actuelle = resume_corpus(items)["version"]
    if version_attendue and version_attendue != version_actuelle:
        raise ValueError(
            f"le corpus a changé depuis le run {dossier.name} "
            f"(attendu {version_attendue[:12]}, trouvé {version_actuelle[:12]}). "
            "Rejouez le run plutôt que de mélanger deux versions de corpus."
        )

    return Execution(
        config=config,
        items=items,
        reponses=reponses,
        scores=scores,
        agregats=agreger(config, items, scores),
        empreintes=empreintes_run,
    )


def date_execution_du_dossier(dossier: Path) -> dt.date:
    """La date de publication vient du nom du dossier, pas de l'horloge courante."""
    return dt.datetime.strptime(Path(dossier).name, FORMAT_DOSSIER).date()


def hash_run(dossier: Path) -> dict[str, str]:
    """Empreinte de chaque fichier reproductible : sert à comparer deux runs."""
    return {
        nom: hash_texte((Path(dossier) / nom).read_text(encoding="utf-8"))
        for nom in FICHIERS_REPRODUCTIBLES
        if (Path(dossier) / nom).is_file()
    }
