"""Étape 6 — la CLI, de la validation à l'export. Aucun accès réseau."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from typer.testing import CliRunner

from src.cli import app
from src.io_utils import ecrire_json, lire_json
from src.run import ecrire_run, executer
from tests.fabriques import ecrire_corpus, item
from tests.test_aggregate_export import projet_jouet

runner = CliRunner()


def sortie(resultat) -> str:
    """Tout ce que la commande a écrit : les erreurs partent sur la sortie d'erreur."""
    texte = resultat.stdout or ""
    try:
        texte += resultat.stderr or ""
    except ValueError:  # flux non séparés selon la version de click
        pass
    return texte


def projet_avec_config(tmp_path) -> tuple[Path, Path]:
    racine, cfg = projet_jouet(tmp_path)
    chemin = racine / "config.json"
    ecrire_json(chemin, cfg.model_dump(mode="json"))
    return racine, chemin


def test_valider_corpus_correct(tmp_path):
    _, config = projet_avec_config(tmp_path)
    resultat = runner.invoke(app, ["valider", "--config", str(config)])

    assert resultat.exit_code == 0
    assert "valide" in resultat.stdout


def test_valider_sort_en_erreur_et_liste_les_problemes(tmp_path):
    racine, config = projet_avec_config(tmp_path)
    fautif = item(id="A-3")
    fautif["source"]["verifie_par"] = ""
    ecrire_corpus(racine / "corpus", public=[fautif])

    resultat = runner.invoke(app, ["valider", "--config", str(config)])

    assert resultat.exit_code == 1
    assert "verifie_par" in sortie(resultat)


def test_executer_puis_exporter(tmp_path):
    racine, config = projet_avec_config(tmp_path)

    execution = runner.invoke(app, ["executer", "--config", str(config)])
    assert execution.exit_code == 0, execution.stdout
    assert "Run écrit" in execution.stdout

    dossier = next((racine / "runs").iterdir())
    destination = tmp_path / "site"
    export = runner.invoke(app, ["exporter", str(dossier), "--vers", str(destination)])

    assert export.exit_code == 0, export.stdout
    resultats = lire_json(destination / "results.json")
    questions = lire_json(destination / "questions.json")
    assert resultats["nb_questions"] == 2
    assert len(questions) == 2


def test_verifier_reproductibilite(tmp_path):
    racine, config = projet_avec_config(tmp_path)
    _, cfg = projet_jouet(tmp_path / "bis")

    from src.schema import Config

    cfg = Config.model_validate(lire_json(config))
    a = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))
    b = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 16, 9, 5))

    resultat = runner.invoke(app, ["verifier-reproductibilite", str(a), str(b)])
    assert resultat.exit_code == 0, resultat.stdout
    assert "identiques" in resultat.stdout


def test_verifier_reproductibilite_detecte_une_difference(tmp_path):
    racine, config = projet_avec_config(tmp_path)
    from src.schema import Config

    cfg = Config.model_validate(lire_json(config))
    a = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))
    b = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 16, 9, 5))
    (b / "scores.json").write_text("[]\n", encoding="utf-8")

    resultat = runner.invoke(app, ["verifier-reproductibilite", str(a), str(b)])
    assert resultat.exit_code == 1
    assert "scores.json" in sortie(resultat)


def test_revue_reinjectee_prime_sur_le_juge(tmp_path):
    """La boucle complète : exporter la file, corriger, réinjecter, republier."""
    racine, config = projet_avec_config(tmp_path)
    from src.schema import Config

    cfg = Config.model_validate(lire_json(config))
    dossier = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))

    # On fabrique une correction humaine sur un axe, comme si un relecteur l'avait saisie.
    corrections = tmp_path / "corrige.csv"
    corrections.write_text(
        "item_id;fournisseur_id;axe;notes_par_run;ecart;note_humaine;justification_humaine\n"
        "A-1;m-a;exactitude;run 0 : 1 / run 1 : 1;0;2;Vérifié à la main.\n",
        encoding="utf-8-sig",
    )

    reinjection = runner.invoke(
        app, ["revue", "reinjecter", str(dossier), "--csv", str(corrections)]
    )
    assert reinjection.exit_code == 0, reinjection.stdout

    revus = lire_json(dossier / "scores_revus.json")
    corriges = [s for s in revus if s["item_id"] == "A-1" and s["fournisseur_id"] == "m-a"]
    assert corriges and all(s["notes"]["exactitude"] == 2 for s in corriges)
    assert all(s["origine"] == "humain" for s in corriges)

    # Les scores d'origine restent intacts : la pièce initiale n'est pas réécrite.
    origine = lire_json(dossier / "scores.json")
    assert any(s["origine"] != "humain" for s in origine)

    # L'export reprend la version revue.
    destination = tmp_path / "site"
    export = runner.invoke(app, ["exporter", str(dossier), "--vers", str(destination)])
    assert export.exit_code == 0, export.stdout
    assert "revus par un humain" in export.stdout


def test_revue_sans_correction_ne_fait_rien(tmp_path):
    racine, config = projet_avec_config(tmp_path)
    from src.schema import Config

    cfg = Config.model_validate(lire_json(config))
    dossier = ecrire_run(executer(cfg, racine), Path(cfg.racine_runs), dt.datetime(2026, 9, 15, 14, 30))

    resultat = runner.invoke(app, ["revue", "reinjecter", str(dossier)])

    assert resultat.exit_code == 0
    assert "rien à réinjecter" in resultat.stdout
    assert not (dossier / "scores_revus.json").exists()
