"""CLI du harnais FinReg Bench."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated

import typer

from src.export import exporter as exporter_site
from src.io_utils import ecrire_json, lire_json
from src.loader import CorpusInvalide, charger_corpus, resume_corpus
from src.run import (
    charger_run,
    date_execution_du_dossier,
    ecrire_run,
    executer as executer_run,
    hash_run,
)
from src.schema import Config, Corpus, Score
from src.scoring.revue import appliquer_corrections, lire_corrections

app = typer.Typer(help="Harnais d'évaluation FinReg Bench.", no_args_is_help=True)
revue_app = typer.Typer(help="File de revue humaine.", no_args_is_help=True)
app.add_typer(revue_app, name="revue")

CheminConfig = Annotated[Path, typer.Option("--config", help="Fichier de configuration.")]


def _charger_config(chemin: Path, corpus: Corpus | None = None) -> Config:
    config = Config.model_validate(lire_json(chemin))
    if corpus is not None:
        config = config.model_copy(update={"corpus": corpus})
    return config


@app.command()
def valider(
    config: CheminConfig = Path("config.json"),
    corpus: Annotated[Corpus | None, typer.Option(help="Corpus à valider.")] = None,
) -> None:
    """Valide le corpus et affiche toutes les erreurs d'un coup."""
    cfg = _charger_config(config, corpus)
    try:
        items = charger_corpus(Path(cfg.racine_corpus), cfg.corpus)
    except CorpusInvalide as exc:
        typer.secho(f"{len(exc.erreurs)} erreur(s) :", fg=typer.colors.RED, err=True)
        for erreur in exc.erreurs:
            typer.echo(f"  - {erreur}", err=True)
        raise typer.Exit(code=1)

    apercu = resume_corpus(items)
    typer.secho(
        f"Corpus « {cfg.corpus.value} » valide : {apercu['nb_items']} item(s), "
        f"version {apercu['version'][:12]}.",
        fg=typer.colors.GREEN,
    )
    for domaine, nombre in apercu["par_domaine"].items():
        typer.echo(f"  {domaine} : {nombre}")


@app.command()
def executer(
    config: CheminConfig = Path("config.json"),
    corpus: Annotated[Corpus | None, typer.Option(help="Corpus à interroger.")] = None,
) -> None:
    """Exécute le banc et écrit un dossier de run horodaté."""
    cfg = _charger_config(config, corpus)
    execution = executer_run(cfg)
    dossier = ecrire_run(execution, Path(cfg.racine_runs))

    typer.secho(f"Run écrit dans {dossier}", fg=typer.colors.GREEN)
    typer.echo(f"  {len(execution.reponses)} réponse(s), {len(execution.scores)} score(s)")
    typer.echo(f"  {execution.nb_entrees_revue} entrée(s) en revue humaine")
    for rang, agregat in enumerate(execution.agregats, start=1):
        typer.echo(
            f"  {rang}. {agregat.nom} — {agregat.score_global} "
            f"(hallucination de source : {agregat.taux_hallucination_source} %)"
        )


@revue_app.command("exporter")
def revue_exporter(
    run: Annotated[Path, typer.Argument(help="Dossier de run.")],
) -> None:
    """Rappelle où se trouve la file de revue d'un run."""
    chemin = Path(run) / "revue.csv"
    if not chemin.is_file():
        typer.secho(f"Aucune file de revue dans {run}.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    typer.echo(str(chemin))


@revue_app.command("reinjecter")
def revue_reinjecter(
    run: Annotated[Path, typer.Argument(help="Dossier de run.")],
    csv: Annotated[Path, typer.Option("--csv", help="CSV corrigé à la main.")] = None,
) -> None:
    """Applique un CSV corrigé. Les scores d'origine ne sont jamais écrasés."""
    dossier = Path(run)
    source = Path(csv) if csv else dossier / "revue.csv"

    execution = charger_run(dossier)
    corrections = lire_corrections(source)
    if not corrections:
        typer.secho("Aucune note humaine renseignée : rien à réinjecter.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    corriges = appliquer_corrections(execution.scores, corrections)
    ecrire_json(dossier / "scores_revus.json", [s.model_dump(mode="json") for s in corriges])

    from src.aggregate import agreger, resume

    agregats = agreger(execution.config, execution.items, corriges)
    ecrire_json(
        dossier / "resume_revu.json",
        resume(execution.config, execution.items, corriges, agregats, 0),
    )

    typer.secho(
        f"{len(corrections)} correction(s) appliquée(s). "
        f"scores_revus.json et resume_revu.json écrits dans {dossier}.",
        fg=typer.colors.GREEN,
    )


@app.command()
def exporter(
    run: Annotated[Path, typer.Argument(help="Dossier de run à publier.")],
    vers: Annotated[Path, typer.Option("--vers", help="Dossier de destination.")],
) -> None:
    """Génère results.json et questions.json pour le site public."""
    dossier = Path(run)
    execution = charger_run(dossier)

    # Une revue humaine, si elle existe, prime sur la notation automatique.
    revus = dossier / "scores_revus.json"
    if revus.is_file():
        execution.scores = [Score.model_validate(s) for s in lire_json(revus)]
        from src.aggregate import agreger

        execution.agregats = agreger(execution.config, execution.items, execution.scores)
        typer.echo("Scores revus par un humain pris en compte.")

    chemins = exporter_site(
        Path(vers),
        execution.config,
        execution.items,
        execution.scores,
        execution.agregats,
        execution.reponses_par_cle(),
        date_execution_du_dossier(dossier),
    )
    for chemin in chemins:
        typer.secho(f"Écrit : {chemin}", fg=typer.colors.GREEN)


@app.command("verifier-reproductibilite")
def verifier_reproductibilite(
    run_a: Annotated[Path, typer.Argument()],
    run_b: Annotated[Path, typer.Argument()],
) -> None:
    """Compare deux dossiers de run fichier par fichier."""
    a, b = hash_run(Path(run_a)), hash_run(Path(run_b))
    differences = sorted({nom for nom in set(a) | set(b) if a.get(nom) != b.get(nom)})

    if differences:
        typer.secho(f"Runs différents sur : {', '.join(differences)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    typer.secho(f"Runs identiques sur {len(a)} fichier(s).", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
