"""CLI de FinReg-FR Bench V0.2."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated

import typer

from src.bench.campagne import executer_campagne
from src.bench.config import BenchConfig
from src.bench.plan import coverage_report
from src.bench.rapport import comparer_runs, ecrire_run
from src.bench.registre import RegistreInvalide, charger_prive, charger_public
from src.bench.vocabulaires import Corpus
from src.io_utils import lire_json

app = typer.Typer(help="FinReg-FR Bench V0.2.", no_args_is_help=True)

CheminConfig = Annotated[Path, typer.Option("--config", help="Fichier de configuration.")]


def _config(chemin: Path) -> BenchConfig:
    return BenchConfig.model_validate(lire_json(chemin))


@app.command()
def valider(config: CheminConfig) -> None:
    """Valide la hiérarchie et le corpus, en rapportant toutes les anomalies."""
    cfg = _config(config)
    try:
        if cfg.corpus is Corpus.PRIVE:
            registre = charger_prive(
                Path(cfg.registry_root), Path(cfg.corpus_root), je_confirme_usage_local=True
            )
        else:
            registre = charger_public(Path(cfg.registry_root), Path(cfg.corpus_root))
    except RegistreInvalide as exc:
        typer.secho(f"{len(exc.erreurs)} anomalie(s) :", fg=typer.colors.RED, err=True)
        for erreur in exc.erreurs:
            typer.echo(f"  - {erreur}", err=True)
        raise typer.Exit(code=1)

    typer.secho(
        f"Registre valide : {len(registre.rules)} règle(s), {len(registre.families)} famille(s), "
        f"{len(registre.items)} item(s).",
        fg=typer.colors.GREEN,
    )
    rapport = coverage_report(registre.items, cfg.plan, cfg.corpus)
    typer.echo(f"  couverture : {rapport['actual_total']} / {rapport['target_total']} visés")
    for ligne in rapport["by_domain"]:
        typer.echo(f"    {ligne['key']:8} {ligne['actual']:4} / {ligne['target']:4}  ({ligne['gap']:+d})")


@app.command()
def executer(config: CheminConfig) -> None:
    """Exécute la campagne et écrit un dossier de run horodaté."""
    cfg = _config(config)
    campagne = executer_campagne(cfg)
    dossier = ecrire_run(campagne, Path(cfg.runs_root))

    escalades = sum(1 for j in campagne.judgments if j.escalated)
    typer.secho(f"Run écrit dans {dossier}", fg=typer.colors.GREEN)
    typer.echo(f"  {len(campagne.responses)} réponse(s), {len(campagne.judgments)} jugement(s)")
    typer.echo(f"  {escalades} escalade(s) en revue humaine")

    from src.bench.metriques import rapport_modele

    for model_id in campagne.model_ids:
        metriques = rapport_modele(campagne.judgments, campagne.items_by_id, model_id)["metrics"]
        for cle in ("accuracy_answered", "coverage", "source_hallucination_rate"):
            m = metriques[cle]
            typer.echo(
                f"  {model_id:10} {m['name']:28} {m['value_pct']} % "
                f"({m['numerator']}/{m['denominator']})"
            )


@app.command("verifier-reproductibilite")
def verifier_reproductibilite(
    run_a: Annotated[Path, typer.Argument()], run_b: Annotated[Path, typer.Argument()]
) -> None:
    """Compare deux dossiers de run fichier par fichier."""
    differences = comparer_runs(run_a, run_b)
    if differences:
        typer.secho(
            f"Runs différents sur : {', '.join(differences)}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)
    typer.secho("Runs identiques sur tous les fichiers comparés.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
