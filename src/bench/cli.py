"""CLI de FinReg-FR Bench V0.2."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated

import typer

from src.bench.campagne import executer_campagne
from src.bench.carte_familles import (
    faisabilite_distribution,
    lacunes,
    matrice_couverture,
    redondances,
)
from src.bench.config import BenchConfig
from src.bench.plan import coverage_report
from src.bench.qc_familles import (
    MATRICE_FAMILLES,
    RACINE_FAMILLES,
    RAPPORT_FAMILLES,
    charger_familles,
    ecrire_matrice,
)
from src.bench.qc_familles import controler as controler_familles
from src.bench.qc_familles import erreurs as erreurs_familles
from src.bench.qc_familles import rapport_markdown as rapport_familles
from src.bench.rapport_audit import (
    DOSSIER_AUDIT,
    MATRICE_VERIFICATION,
    RAPPORT_VERIFICATION,
)
from src.bench.rapport_completude import (
    DOSSIER_COMPLETUDE,
    MATRICE_GOLD,
    RAPPORT_COMPLETUDE,
)
from src.bench.rapport_adjudication import (
    DOSSIER_ADJUDICATION,
    PACK_ADJUDICATION,
    PROGRESSION,
)
from src.bench.rapport_plan_action import (
    DOSSIER_REANCRAGE,
    PACK_LCBFT,
    PLAN_ACTION,
    PLAN_ACTION_CSV,
)
from src.bench.rapport_readiness import (
    FILE_REVUE,
    MATRICE_READINESS,
    SYNTHESE_READINESS,
)
from src.bench.qc_rulebook import (
    RACINE_RULEBOOK,
    charger_par_fichier,
    charger_rulebook,
    construire_manifeste,
    controler,
    erreurs,
    rapport_markdown,
)
from src.bench.rapport import comparer_runs, ecrire_run
from src.bench.registre import RegistreInvalide, charger_prive, charger_public
from src.bench.verification import (
    REGISTRE_VERIFICATION,
    VERDICTS_PROMOTEURS,
    VerificationInvalide,
    appliquer,
    ecrire_registre,
    exporter_dossier,
    fusionner_registre,
    lire_dossier,
)
from src.bench.vocabulaires import Corpus
from src.io_utils import ecrire_json, lire_json

app = typer.Typer(help="FinReg-FR Bench V0.2.", no_args_is_help=True)

rulebook = typer.Typer(
    help="Regulatory Rulebook : contrôle qualité et circuit de vérification.",
    no_args_is_help=True,
)
app.add_typer(rulebook, name="rulebook")

familles = typer.Typer(
    help="Question Family Map : dérivation depuis le Rulebook et contrôle qualité.",
    no_args_is_help=True,
)
app.add_typer(familles, name="familles")

RAPPORT_QC = Path("RULEBOOK_QC.md")

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


# -- Rulebook ---------------------------------------------------------------------- #


@rulebook.command("qc")
def rulebook_qc(
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    rapport: Annotated[
        Path, typer.Option("--rapport", help="Rapport Markdown à écrire.")
    ] = RAPPORT_QC,
    ecrire: Annotated[
        bool, typer.Option("--ecrire/--pas-ecrire", help="Réécrire le rapport.")
    ] = False,
) -> None:
    """Contrôle qualité du Rulebook. Sort en erreur si un constat est bloquant."""
    regles = [r for v in charger_par_fichier(racine).values() for r in v]
    constats = controler(regles)
    bloquants = erreurs(constats)

    if ecrire:
        rapport.write_text(rapport_markdown(regles, constats), encoding="utf-8")
        typer.echo(f"Rapport écrit dans {rapport}")

    typer.echo(
        f"{len(regles)} règle(s) — {len(bloquants)} erreur(s), "
        f"{sum(1 for c in constats if c.niveau == 'AVERTISSEMENT')} avertissement(s)"
    )
    typer.echo(
        f"  utilisables pour ancrer un gold : {sum(1 for r in regles if r.is_usable)} / {len(regles)}"
    )
    for constat in bloquants:
        typer.secho(f"  {constat}", fg=typer.colors.RED, err=True)
    if bloquants:
        raise typer.Exit(code=1)


@rulebook.command("exporter-verification")
def rulebook_exporter_verification(
    sortie: Annotated[Path, typer.Option("--sortie", help="Dossier CSV à produire.")],
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    a_verifier: Annotated[
        bool,
        typer.Option(
            "--a-verifier/--toutes",
            help="N'exporter que les règles dont la source n'a pas été consultée.",
        ),
    ] = True,
) -> None:
    """Écrit le dossier de vérification : ce qu'il faut lire, et où le consigner."""
    regles = [r for v in charger_par_fichier(racine).values() for r in v]
    retenues = [r for r in regles if r.needs_verification] if a_verifier else regles
    exporter_dossier(retenues, sortie)
    typer.secho(f"{len(retenues)} règle(s) à vérifier dans {sortie}", fg=typer.colors.GREEN)
    typer.echo("  remplir les colonnes de constat, puis : finreg-bench rulebook appliquer-verification")


@rulebook.command("appliquer-verification")
def rulebook_appliquer_verification(
    dossier: Annotated[Path, typer.Argument(help="Dossier de vérification rempli.")],
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    registre: Annotated[
        Path, typer.Option("--registre", help="Registre de vérification.")
    ] = REGISTRE_VERIFICATION,
    rapport: Annotated[
        Path, typer.Option("--rapport", help="Rapport Markdown à réécrire.")
    ] = RAPPORT_QC,
) -> None:
    """Réinjecte les constats. Rien n'est écrit si un seul constat est irrecevable."""
    try:
        verifications = lire_dossier(dossier)
    except VerificationInvalide as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not verifications:
        typer.secho("Aucun verdict renseigné : rien à appliquer.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    par_fichier = charger_par_fichier(racine)
    toutes = [r for v in par_fichier.values() for r in v]
    connus = {r.id for r in toutes}

    try:
        # Validation d'ensemble avant toute écriture : un identifiant inconnu ou
        # une promotion irrecevable doit arrêter le lot entier.
        appliquer(toutes, verifications)
    except VerificationInvalide as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    appliquees: list = []
    compte_par_fichier: dict[str, int] = {}
    for chemin, regles in par_fichier.items():
        ids = {r.id for r in regles}
        resultat = appliquer(regles, [v for v in verifications if v.rule_id in ids])
        ecrire_json(chemin, [r.model_dump(mode="json") for r in resultat])
        appliquees.extend(resultat)
        compte_par_fichier[chemin.stem] = len(resultat)

    ecrire_registre(fusionner_registre(verifications, registre), registre)
    ecrire_json(racine / "rulebook-manifest.json", construire_manifeste(appliquees, compte_par_fichier))
    rapport.write_text(
        rapport_markdown(appliquees, controler(appliquees)), encoding="utf-8"
    )

    promues = sum(1 for v in verifications if v.verdict in VERDICTS_PROMOTEURS)
    typer.secho(
        f"{len(verifications)} constat(s) appliqué(s), {promues} promotion(s).",
        fg=typer.colors.GREEN,
    )
    typer.echo(f"  utilisables pour ancrer un gold : {sum(1 for r in appliquees if r.is_usable)} / {len(appliquees)}")
    typer.echo(f"  registre : {registre}")
    inconnus = {v.rule_id for v in verifications} - connus
    for identifiant in sorted(inconnus):  # pragma: no cover - déjà refusé plus haut
        typer.secho(f"  règle inconnue ignorée : {identifiant}", fg=typer.colors.YELLOW)


@rulebook.command("auditer")
def rulebook_auditer(
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    rapport: Annotated[
        Path, typer.Option("--rapport", help="Rapport d'audit à écrire.")
    ] = RAPPORT_VERIFICATION,
    matrice: Annotated[
        Path, typer.Option("--matrice", help="Matrice d'audit CSV à écrire.")
    ] = MATRICE_VERIFICATION,
    dossier: Annotated[
        Path, typer.Option("--dossier", help="Dossier de vérification pré-rempli.")
    ] = DOSSIER_AUDIT,
) -> None:
    """Confronte chaque règle à son texte primaire. Ne promeut rien.

    L'audit rassemble la preuve ; la promotion reste au circuit de vérification,
    qui exige un vérificateur nommé. Le dossier produit est pré-rempli sauf
    « verifie_par » et « date_verification » : le schéma refuse toute promotion
    tant qu'elles sont vides.
    """
    from scripts.auditer_rulebook import auditer_et_rapporter

    resultat = auditer_et_rapporter(racine, rapport, matrice, dossier)
    typer.secho(f"{resultat['rules']} règle(s) auditées", fg=typer.colors.GREEN)
    for classement, nombre in resultat["by_classification"].items():
        typer.echo(f"  {classement:24} {nombre}")
    typer.echo(
        f"  {len(resultat['acts_consulted'])} acte(s) consulté(s), "
        f"{resultat['articles_found']} article(s) retrouvé(s), "
        f"{resultat['anomalies']} anomalie(s)"
    )
    typer.echo(f"  rapport : {resultat['report']} — matrice : {resultat['matrix']}")
    typer.echo(f"  dossier à signer : {resultat['dossier']}")
    typer.secho(
        "  aucune règle promue : renseigner verifie_par et date_verification, "
        "puis « finreg-bench rulebook appliquer-verification »",
        fg=typer.colors.YELLOW,
    )


@rulebook.command("completude")
def rulebook_completude(
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    rapport: Annotated[
        Path, typer.Option("--rapport", help="Rapport de complétude à écrire.")
    ] = RAPPORT_COMPLETUDE,
    matrice: Annotated[
        Path, typer.Option("--matrice", help="Matrice de gold-readiness CSV.")
    ] = MATRICE_GOLD,
    dossier: Annotated[
        Path, typer.Option("--dossier", help="Dossier de vérification pré-rempli.")
    ] = DOSSIER_COMPLETUDE,
) -> None:
    """Cherche la structure juridique des articles cités : exceptions, conditions, renvois.

    Ne promeut rien. Une règle peut être validée et rester inutilisable : c'est
    ce que « gold_ready » dit, et c'est ce qui empêche un faux sentiment de
    complétude.
    """
    from scripts.auditer_completude import auditer_completude

    resultat = auditer_completude(racine, rapport, matrice, dossier)
    typer.secho(f"{resultat['rules']} règle(s) examinées", fg=typer.colors.GREEN)
    for statut, nombre in resultat["by_status"].items():
        typer.echo(f"  {statut:24} {nombre}")
    typer.echo(f"  gold_ready : {resultat['gold_ready']}")
    typer.echo(
        f"  utilisables pour les familles (validated ET gold_ready) : "
        f"{resultat['usable_for_families']}"
    )
    typer.echo(f"  rapport : {resultat['report']} — matrice : {resultat['matrix']}")
    typer.secho(
        "  aucune règle promue : renseigner verifie_par et date_verification, "
        "puis « finreg-bench rulebook appliquer-verification »",
        fg=typer.colors.YELLOW,
    )


@rulebook.command("readiness")
def rulebook_readiness(
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    synthese: Annotated[
        Path, typer.Option("--synthese", help="Synthèse d'exploitabilité.")
    ] = SYNTHESE_READINESS,
    file_revue: Annotated[
        Path, typer.Option("--file-revue", help="File de revue humaine.")
    ] = FILE_REVUE,
    matrice: Annotated[
        Path, typer.Option("--matrice", help="Matrice de readiness CSV.")
    ] = MATRICE_READINESS,
) -> None:
    """Situe chaque règle sur les trois seuils et rend une recommandation.

    Sort en erreur si la recommandation n'est pas `READY_FOR_FAMILY_GENERATION` :
    la génération de familles ne doit pas pouvoir démarrer sur un Rulebook
    incohérent ou dont les arbitrages critiques sont en attente.
    """
    from scripts.auditer_readiness import auditer_readiness

    resultat = auditer_readiness(racine, synthese, file_revue, matrice)
    typer.secho(f"{resultat['rules']} règle(s)", fg=typer.colors.GREEN)
    typer.echo(f"  gold_ready   : {resultat['gold_ready']}")
    typer.echo(f"  family_ready : {resultat['family_ready']}")
    typer.echo(
        f"  intégrité : {resultat['integrity_passed']} passé(s), "
        f"{resultat['integrity_failed']} échoué(s)"
    )
    for anomalie in resultat["anomalies"]:
        typer.secho(f"    {anomalie}", fg=typer.colors.RED, err=True)
    couleur = (
        typer.colors.GREEN
        if resultat["recommendation"] == "READY_FOR_FAMILY_GENERATION"
        else typer.colors.YELLOW
    )
    typer.secho(f"  {resultat['recommendation']} — {resultat['reason']}", fg=couleur)
    if resultat["recommendation"] != "READY_FOR_FAMILY_GENERATION":
        raise typer.Exit(code=1)



@rulebook.command("adjudication")
def rulebook_adjudication(
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    pack_chemin: Annotated[
        Path, typer.Option("--pack", help="Pack de revue P0/P1.")
    ] = PACK_ADJUDICATION,
    dossier: Annotated[
        Path, typer.Option("--dossier", help="Dossier d'arbitrage à remplir.")
    ] = DOSSIER_ADJUDICATION,
    progression_chemin: Annotated[
        Path, typer.Option("--progression", help="Rapport de progression.")
    ] = PROGRESSION,
) -> None:
    """Prépare les dossiers d'arbitrage P0 puis P1. Ne décide rien, ne promeut rien.

    Le dossier CSV sort avec ses colonnes de décision vides ; s'il en porte déjà,
    il n'est pas réécrit — regénérer un pack ne doit jamais effacer un arbitrage
    rendu.
    """
    from scripts.preparer_adjudication import preparer_adjudication

    resultat = preparer_adjudication(racine, pack_chemin, dossier, progression_chemin)
    typer.secho(f"{resultat['dossiers']} dossier(s) d'arbitrage", fg=typer.colors.GREEN)
    for priorite, compte in resultat["par_priorite"].items():
        typer.echo(f"  {priorite} : {compte}")
    typer.echo(f"  questions distinctes : {resultat['questions_distinctes']}")
    typer.echo(f"  regroupements (>1 règle) : {resultat['regroupements']}")
    typer.echo(f"  décisions déjà rendues : {resultat['decisions_rendues']}")
    if resultat["dossier_preserve"]:
        typer.secho(
            "  dossier conservé en l'état : il porte des décisions",
            fg=typer.colors.YELLOW,
        )
    typer.echo(f"  empreinte de l'audit relu : {resultat['empreinte']}")


@rulebook.command("plan-action")
def rulebook_plan_action(
    racine: Annotated[Path, typer.Option("--racine", help="Dossier des règles.")] = RACINE_RULEBOOK,
    plan: Annotated[Path, typer.Option("--plan", help="Plan de revue.")] = PLAN_ACTION,
    plan_csv: Annotated[
        Path, typer.Option("--plan-csv", help="Queue P0/P1 en CSV.")
    ] = PLAN_ACTION_CSV,
    lcbft: Annotated[
        Path, typer.Option("--lcbft", help="Pack de consultation manuelle LCB-FT.")
    ] = PACK_LCBFT,
    reancrage: Annotated[
        Path, typer.Option("--reancrage", help="Dossier de réancrage de source.")
    ] = DOSSIER_REANCRAGE,
) -> None:
    """Range les arbitrages P0/P1 en actions et calcule l'ordre de travail.

    Ne décide rien, ne promeut rien, n'écrit ni règle, ni registre, ni famille.
    """
    from scripts.preparer_plan_action import preparer_plan_action

    resultat = preparer_plan_action(racine, plan, plan_csv, lcbft, reancrage)
    typer.secho(f"{resultat['regles']} règle(s) au plan", fg=typer.colors.GREEN)
    for action, compte in resultat["par_action"].items():
        typer.echo(f"  {action:24s} {compte}")
    typer.echo(f"  regroupements : {resultat['groupes']} — étapes : {resultat['etapes']}")
    typer.echo(
        f"  LCB-FT à consulter : {resultat['lcbft']} — "
        f"réancrages documentés : {resultat['reancrages']}"
    )
    for item in resultat["bloquants"]:
        typer.secho(f"  BLOQUANT — {item}", fg=typer.colors.YELLOW)
    typer.secho(f"  PROCHAINE ACTION — {resultat['prochaine_action']}", fg=typer.colors.CYAN)

# -- Question Family Map ------------------------------------------------------------ #


@familles.command("generer")
def familles_generer(
    racine_regles: Annotated[
        Path, typer.Option("--racine-regles", help="Dossier des règles.")
    ] = RACINE_RULEBOOK,
    racine: Annotated[
        Path, typer.Option("--racine", help="Dossier de sortie de la carte.")
    ] = RACINE_FAMILLES,
    rapport: Annotated[
        Path, typer.Option("--rapport", help="Rapport Markdown à écrire.")
    ] = RAPPORT_FAMILLES,
    matrice: Annotated[
        Path, typer.Option("--matrice", help="Matrice de couverture CSV à écrire.")
    ] = MATRICE_FAMILLES,
) -> None:
    """Dérive la carte des familles depuis le Rulebook, avec son QC et sa matrice."""
    from scripts.generer_familles import generer

    resultat = generer(racine_regles, racine, rapport, matrice)
    typer.secho(
        f"{resultat['number_of_families']} famille(s) écrite(s) dans {racine}",
        fg=typer.colors.GREEN,
    )
    typer.echo(
        f"  règles exploitées : {resultat['number_of_rules_with_family']} / "
        f"{resultat['number_of_rules']} "
        f"(dont {resultat['number_of_usable_rules']} utilisable(s) pour un gold)"
    )
    typer.echo(f"  prêtes : {resultat['number_ready']} — bloquées : {resultat['number_blocked']}")
    typer.echo(f"  rapport : {rapport} — matrice : {matrice}")
    if resultat["number_of_blocking_findings"]:
        raise typer.Exit(code=1)


@familles.command("qc")
def familles_qc(
    racine: Annotated[Path, typer.Option("--racine", help="Dossier de la carte.")] = RACINE_FAMILLES,
    racine_regles: Annotated[
        Path, typer.Option("--racine-regles", help="Dossier des règles.")
    ] = RACINE_RULEBOOK,
    rapport: Annotated[
        Path, typer.Option("--rapport", help="Rapport Markdown à écrire.")
    ] = RAPPORT_FAMILLES,
    ecrire: Annotated[
        bool, typer.Option("--ecrire/--pas-ecrire", help="Réécrire le rapport.")
    ] = False,
) -> None:
    """Contrôle qualité de la carte. Sort en erreur si un constat est bloquant."""
    carte = charger_familles(racine)
    regles = charger_rulebook(racine_regles)
    constats = controler_familles(carte, regles)
    bloquants = erreurs_familles(constats)

    if ecrire:
        Path(rapport).parent.mkdir(parents=True, exist_ok=True)
        Path(rapport).write_text(rapport_familles(carte, regles, constats), encoding="utf-8")
        typer.echo(f"Rapport écrit dans {rapport}")

    trous = lacunes(regles, carte)
    doubles = redondances(carte, regles)
    distribution = faisabilite_distribution(carte)

    typer.echo(
        f"{len(carte)} famille(s) — {len(bloquants)} erreur(s), "
        f"{sum(1 for c in constats if c.niveau == 'AVERTISSEMENT')} avertissement(s)"
    )
    typer.echo(f"  prêtes pour le benchmark : {sum(1 for f in carte if f.is_ready)} / {len(carte)}")
    typer.echo(f"  règles sans famille intéressante : {len(trous['rules_without_family'])}")
    typer.echo(f"  doublons réels : {doubles['number_redundant']}")
    typer.echo(
        f"  distribution visée atteignable : "
        f"{'oui' if distribution['achievable'] else 'non'}"
    )
    for constat in bloquants:
        typer.secho(f"  {constat}", fg=typer.colors.RED, err=True)
    if bloquants:
        raise typer.Exit(code=1)


@familles.command("exporter-matrice")
def familles_exporter_matrice(
    sortie: Annotated[Path, typer.Option("--sortie", help="Matrice CSV à produire.")] = MATRICE_FAMILLES,
    racine: Annotated[Path, typer.Option("--racine", help="Dossier de la carte.")] = RACINE_FAMILLES,
    racine_regles: Annotated[
        Path, typer.Option("--racine-regles", help="Dossier des règles.")
    ] = RACINE_RULEBOOK,
) -> None:
    """Écrit la matrice DOMAIN × RULE × FAMILY × TRAP × DIFFICULTY."""
    regles = charger_rulebook(racine_regles)
    lignes = matrice_couverture(regles, charger_familles(racine))
    ecrire_matrice(lignes, sortie)
    typer.secho(f"{len(lignes)} ligne(s) écrites dans {sortie}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
