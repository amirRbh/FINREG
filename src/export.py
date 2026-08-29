"""Export vers le site public.

Génère `results.json` et `questions.json` au format lu par FinReg Compass
(`src/lib/finreg.ts`), en n'incluant **que** les items du corpus public.
Un item privé dans un export est un bug bloquant : l'export lève plutôt que
d'écrire (CLAUDE.md §8).
"""

from __future__ import annotations

import datetime as dt
from collections import defaultdict
from pathlib import Path

from src.aggregate import AgregatModele
from src.io_utils import ecrire_json
from src.schema import Config, Corpus, Flag, Item, Score

#: Signalements que le site sait libeller. Les autres ne sont pas publiés.
FLAGS_PUBLIES: tuple[Flag, ...] = (
    Flag.HALLUCINATION_SOURCE,
    Flag.SOURCING_INCOMPLET,
    Flag.SURCONFIANCE,
    Flag.ABSTENTION,
    Flag.ERREUR_DISQUALIFIANTE,
)


class ExportInvalide(RuntimeError):
    """L'export refuse d'écrire un fichier destiné à être publié en l'état."""


def _verifier_publiable(items: list[Item], config: Config) -> None:
    prives = [item.id for item in items if item.corpus is not Corpus.PUBLIC]
    if prives:
        raise ExportInvalide(
            f"{len(prives)} item(s) non publics dans l'export : {sorted(prives)[:5]}. "
            "L'export ne publie que le corpus public."
        )

    inconnus = sorted(
        {item.domaine for item in items if item.domaine not in config.domaines_publics}
    )
    if inconnus:
        raise ExportInvalide(
            f"domaines inconnus du site public : {inconnus}. "
            f"Domaines déclarés : {sorted(config.domaines_publics)}."
        )


def _run_representatif(runs: list[Score]) -> Score:
    """Le run médian en note, choisi de façon déterministe.

    Publier le meilleur run flatterait le modèle, publier le pire l'accablerait :
    on publie celui du milieu, et l'écart-type dit à côté ce qu'il en coûte.
    """
    tries = sorted(runs, key=lambda s: (s.total(), s.index_run))
    return tries[(len(tries) - 1) // 2]


def _note_publiee(runs: list[Score]) -> int:
    """Note 0–10 attendue par le site : moyenne des runs, ramenée sur 10."""
    from src.schema import NOTE_MAX

    moyenne = sum(s.total() for s in runs) / len(runs)
    return round(10 * moyenne / NOTE_MAX)


def _flags_publies(runs: list[Score]) -> list[str]:
    """Union des signalements sur l'ensemble des runs, dans un ordre stable.

    Un défaut apparu sur un seul run reste un défaut : on ne le lisse pas.
    """
    presents = {flag for score in runs for flag in score.flags}
    return [flag.value for flag in FLAGS_PUBLIES if flag in presents]


def construire_questions(
    items: list[Item], scores: list[Score], reponses_par_cle: dict[tuple[str, str, int], str]
) -> list[dict]:
    groupes: dict[tuple[str, str], list[Score]] = defaultdict(list)
    for score in scores:
        groupes[(score.item_id, score.fournisseur_id)].append(score)

    sortie: list[dict] = []
    for item in sorted(items, key=lambda i: i.id):
        reponses_modeles: dict[str, dict] = {}
        for (item_id, fournisseur_id), runs in groupes.items():
            if item_id != item.id:
                continue
            runs = sorted(runs, key=lambda s: s.index_run)
            representatif = _run_representatif(runs)
            reponses_modeles[fournisseur_id] = {
                "texte": reponses_par_cle.get(
                    (item_id, fournisseur_id, representatif.index_run), ""
                ),
                "score": _note_publiee(runs),
                "flags": _flags_publies(runs),
            }

        sortie.append(
            {
                "id": item.id,
                "domaine": item.domaine,
                "type": item.type.value,
                "difficulte": item.difficulte,
                "question": item.question,
                "reponse_reference": item.reponse_reference,
                "source": {
                    "texte": item.source.texte,
                    "article": item.source.article,
                    "url": item.source.url,
                },
                "reponses_modeles": dict(sorted(reponses_modeles.items())),
            }
        )

    return sortie


def construire_resultats(
    agregats: list[AgregatModele],
    nb_questions: int,
    nb_runs: int,
    date_execution: dt.date,
) -> dict:
    return {
        "date_execution": date_execution.isoformat(),
        "nb_questions": nb_questions,
        "nb_runs": nb_runs,
        "modeles": [
            {
                "id": a.fournisseur_id,
                "nom": a.nom,
                "editeur": a.editeur,
                "score_global": a.score_global,
                "taux_hallucination_source": a.taux_hallucination_source,
                "taux_abstention_correcte": a.taux_abstention_correcte,
                "ecart_type": a.ecart_type,
                "scores_domaines": a.scores_domaines,
                "scores_axes": a.scores_axes,
            }
            for a in agregats
        ],
    }


def exporter(
    destination: Path,
    config: Config,
    items: list[Item],
    scores: list[Score],
    agregats: list[AgregatModele],
    reponses_par_cle: dict[tuple[str, str, int], str],
    date_execution: dt.date,
) -> list[Path]:
    """Écrit results.json et questions.json. Rend les chemins écrits."""
    publics = [item for item in items if item.corpus is Corpus.PUBLIC]
    _verifier_publiable(publics, config)

    ids_publics = {item.id for item in publics}
    scores_publics = [s for s in scores if s.item_id in ids_publics]

    destination = Path(destination)
    chemin_resultats = destination / "results.json"
    chemin_questions = destination / "questions.json"

    ecrire_json(
        chemin_resultats,
        construire_resultats(
            agregats, len(publics), config.execution.nb_runs, date_execution
        ),
    )
    ecrire_json(
        chemin_questions,
        construire_questions(publics, scores_publics, reponses_par_cle),
    )

    return [chemin_resultats, chemin_questions]
