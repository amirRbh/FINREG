"""V0.2 phases 10-12 — runner, rapports, reproductibilité, jeu synthétique."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.bench.campagne import SyntheticJudge, executer_campagne
from src.bench.cli import app
from src.bench.config import BenchConfig, ExecutionConfig, ProviderConfig
from src.bench.fournisseurs import SyntheticProvider
from src.bench.isolation import PrivateLeakError
from src.bench.items import Item
from src.bench.rapport import Campagne, comparer_runs, ecrire_run, rapport_public
from src.bench.registre import charger_public
from src.bench.reponses import ModelResponse
from src.bench.runner import BenchRunner, lire_prompt_systeme, verifier_non_retention
from src.bench.vocabulaires import Corpus
from src.cache import CacheDisque
from src.io_utils import lire_json
from src.securite import PrivateCorpusLeakError
from tests.bench.fabriques import ecrire_corpus, ecrire_referentiel, item

SYNTH = Path("fixtures/synthetic")
PROMPT = "Prompt système synthétique.\n"

runner_cli = CliRunner()


def provider(id="p-a", zero_retention=False, **kw) -> ProviderConfig:
    base = {
        "id": id, "name": "Modèle", "provider": "local", "model_name": id,
        "model_version": "1", "adapter": "synthetic", "zero_retention": zero_retention,
    }
    base.update(kw)
    return ProviderConfig(**base)


def config(**kw) -> BenchConfig:
    base = {
        "benchmark_version": "v0.2-test",
        "corpus": Corpus.PUBLIC,
        "providers": [provider()],
        "execution": ExecutionConfig(runs_per_item=3, concurrency=2, requests_per_minute=100000),
    }
    base.update(kw)
    return BenchConfig(**base)


class Fabrique:
    def __init__(self):
        self.instances: dict[str, SyntheticProvider] = {}

    def __call__(self, config_fournisseur):
        if config_fournisseur.id not in self.instances:
            self.instances[config_fournisseur.id] = SyntheticProvider(config_fournisseur)
        return self.instances[config_fournisseur.id]

    @property
    def total(self) -> int:
        return sum(p.call_count for p in self.instances.values())


def items(n=2) -> list[Item]:
    return [
        Item.model_validate(item(base_id=f"SYNTH-{i}", question=f"Question numéro {i} ?"))
        for i in range(n)
    ]


def runner(tmp_path, cfg=None, fabrique=None, corpus=Corpus.PUBLIC):
    return BenchRunner(
        cfg or config(), PROMPT, CacheDisque(tmp_path / "cache", corpus),
        fabrique=fabrique or Fabrique(),
    )


# -- phase 10 : runner ---------------------------------------------------------- #


def test_execution_produit_trois_runs(tmp_path):
    fabrique = Fabrique()
    resultat = runner(tmp_path, fabrique=fabrique).execute(items(2))

    assert len(resultat.responses) == 6
    assert sorted({r.run_index for r in resultat.responses}) == [0, 1, 2]
    assert fabrique.total == 6
    assert all(a.temperature == 0.0 for a in fabrique.instances["p-a"].calls)


def test_metadonnees_de_run_completes(tmp_path):
    resultat = runner(tmp_path).execute(items(1))
    meta = resultat.metadata["p-a"]

    assert meta.model_name == "p-a"
    assert meta.model_version == "1"
    assert meta.provider == "local"
    assert meta.temperature == 0.0
    assert meta.benchmark_version == "v0.2-test"
    assert len(meta.system_prompt_sha256) == 64


def test_le_cache_evite_de_repayer(tmp_path):
    jeu = items(2)
    premier = Fabrique()
    runner(tmp_path, fabrique=premier).execute(jeu)
    assert premier.total == 6

    second = Fabrique()
    resultat = runner(tmp_path, fabrique=second).execute(jeu)
    assert second.total == 0
    assert resultat.from_cache == 6


def test_reprise_apres_interruption(tmp_path):
    jeu = items(3)
    partielle = Fabrique()
    partielle.instances["p-a"] = SyntheticProvider(provider())
    partielle.instances["p-a"].failing = {"Question numéro 2"}

    premier = runner(tmp_path, fabrique=partielle).execute(jeu)
    assert premier.errors == 3

    reprise = Fabrique()
    second = runner(tmp_path, fabrique=reprise).execute(jeu)
    assert second.errors == 0
    assert reprise.total == 3  # seuls les manquants sont rejoués


def test_une_erreur_nest_pas_une_mauvaise_reponse(tmp_path):
    fabrique = Fabrique()
    fabrique.instances["p-a"] = SyntheticProvider(provider())
    fabrique.instances["p-a"].failing = {"Question numéro 0"}

    resultat = runner(tmp_path, fabrique=fabrique).execute(items(1))
    assert resultat.errors == 3
    assert all(not r.is_usable for r in resultat.responses)


def test_concurrence_bornee(tmp_path):
    execution = runner(tmp_path)
    execution.execute(items(5))
    assert execution.max_concurrency_seen <= 2


def test_ordre_des_reponses_stable(tmp_path):
    jeu = items(4)
    a = runner(tmp_path / "a").execute(jeu)
    b = runner(tmp_path / "b").execute(jeu)
    cles = lambda r: [(x.item_id, x.model_id, x.run_index) for x in r.responses]
    assert cles(a) == cles(b) == sorted(cles(a))


# -- phase 10 : garde-fou de non-rétention ---------------------------------------- #


def test_corpus_prive_vers_fournisseur_non_conforme_ne_declenche_aucun_appel(tmp_path):
    cfg = config(corpus=Corpus.PRIVE, providers=[provider(zero_retention=False)])
    fabrique = Fabrique()
    execution = runner(tmp_path, cfg=cfg, fabrique=fabrique, corpus=Corpus.PRIVE)
    prives = [Item.model_validate(item(base_id="SYNTH-P", corpus="private"))]

    with pytest.raises(PrivateCorpusLeakError):
        execution.execute(prives)

    assert fabrique.total == 0


def test_corpus_prive_vers_fournisseur_conforme_sexecute(tmp_path):
    cfg = config(corpus=Corpus.PRIVE, providers=[provider(zero_retention=True)])
    execution = runner(tmp_path, cfg=cfg, corpus=Corpus.PRIVE)
    resultat = execution.execute([Item.model_validate(item(base_id="SYNTH-P", corpus="private"))])
    assert len(resultat.responses) == 3


@pytest.mark.parametrize("valeur", [None, "true", 1, "1", []])
def test_zero_retention_non_booleen_vaut_refus(valeur):
    assert provider(zero_retention=valeur).zero_retention is False


def test_le_message_de_refus_ne_divulgue_aucun_contenu():
    prive = Item.model_validate(item(corpus="private", question="SECRET-SYNTH"))
    fournisseur = SyntheticProvider(provider(zero_retention=False))

    with pytest.raises(PrivateCorpusLeakError) as exc:
        verifier_non_retention([prive], fournisseur)

    assert "SECRET-SYNTH" not in str(exc.value)


# -- phase 11 : dossier de run ------------------------------------------------------ #


def campagne_synthetique(tmp_path, corpus_prive=None) -> Campagne:
    ref = ecrire_referentiel(tmp_path / "registry")
    ecrire_corpus(tmp_path / "corpus", public=[item()], prive=corpus_prive)
    registre = charger_public(ref, tmp_path / "corpus")

    cfg = config(
        registry_root=str(ref),
        corpus_root=str(tmp_path / "corpus"),
        system_prompt_path=str(SYNTH / "prompts" / "system-v1.txt"),
        cache_root=str(tmp_path / ".cache"),
        runs_root=str(tmp_path / "runs"),
    )
    return executer_campagne(cfg, Path("."), juge=SyntheticJudge())


def test_le_dossier_de_run_contient_tout(tmp_path):
    dossier = ecrire_run(
        campagne_synthetique(tmp_path), tmp_path / "runs", dt.datetime(2026, 9, 1, 10, 0)
    )

    assert dossier.name == "2026-09-01-1000"
    for fichier in (
        "config.json", "fingerprints.json", "responses.json", "judgments.json",
        "metrics.json", "public_report.json", "escalations.csv", "execution.json",
    ):
        assert (dossier / fichier).is_file(), fichier

    empreintes = lire_json(dossier / "fingerprints.json")
    assert len(empreintes["system_prompt"]["sha256"]) == 64
    assert len(empreintes["corpus"]["sha256"]) == 64
    assert empreintes["benchmark_version"] == "v0.2-test"


def test_un_run_nest_jamais_reecrit(tmp_path):
    horodatage = dt.datetime(2026, 9, 1, 10, 0)
    ecrire_run(campagne_synthetique(tmp_path), tmp_path / "runs", horodatage)

    with pytest.raises(FileExistsError):
        ecrire_run(campagne_synthetique(tmp_path), tmp_path / "runs", horodatage)


def test_deux_runs_identiques_produisent_les_memes_fichiers(tmp_path):
    """La reproductibilité à l'identique : ce qui rend le rapport opposable."""
    a = ecrire_run(campagne_synthetique(tmp_path), tmp_path / "runs", dt.datetime(2026, 9, 1, 10, 0))
    b = ecrire_run(campagne_synthetique(tmp_path), tmp_path / "runs", dt.datetime(2026, 9, 2, 15, 30))

    assert a.name != b.name
    assert comparer_runs(a, b) == []


def test_la_latence_ne_rend_pas_deux_runs_differents(tmp_path):
    """La latence décrit l'exécution, pas la réponse : elle sort du périmètre comparé."""
    dossier = ecrire_run(
        campagne_synthetique(tmp_path), tmp_path / "runs", dt.datetime(2026, 9, 1, 10, 0)
    )
    archivees = lire_json(dossier / "responses.json")
    assert all("latency_ms" not in r for r in archivees)
    assert "latency_ms" in lire_json(dossier / "execution.json")


def test_la_file_descalade_est_corrigeable_a_la_main(tmp_path):
    dossier = ecrire_run(
        campagne_synthetique(tmp_path), tmp_path / "runs", dt.datetime(2026, 9, 1, 10, 0)
    )
    contenu = (dossier / "escalations.csv").read_text(encoding="utf-8-sig")
    assert "item_id;model_id;run_index;escalation_reasons" in contenu
    assert "human_verdict" in contenu


# -- phase 11 : rapport public --------------------------------------------------------- #


def test_le_rapport_public_exclut_le_prive():
    public = Item.model_validate(item())
    prive = Item.model_validate(item(base_id="SYNTH-P", corpus="private", question="SECRET-SYNTH"))
    campagne = Campagne(
        config=config(), items=[public, prive], responses=[], judgments=[]
    )
    rendu = json.dumps(rapport_public(campagne), ensure_ascii=False)

    assert rendu.count("SYNTH-P") == 0
    assert "SECRET-SYNTH" not in rendu


def test_un_identifiant_prive_dans_le_rapport_bloque_lecriture(tmp_path, monkeypatch):
    """Le contrôle passe avant l'écriture : un artefact fautif ne doit pas exister."""
    prive = Item.model_validate(item(base_id="SYNTH-P", corpus="private"))
    campagne = Campagne(config=config(), items=[prive], responses=[], judgments=[])

    monkeypatch.setattr(
        "src.bench.rapport.rapport_public", lambda c: {"fuite": "SYNTH-P-v1"}
    )
    with pytest.raises(PrivateLeakError):
        ecrire_run(campagne, tmp_path / "runs", dt.datetime(2026, 9, 1, 10, 0))

    assert not (tmp_path / "runs" / "2026-09-01-1000").exists()


# -- phase 12 : jeu synthétique ---------------------------------------------------------- #


def test_le_jeu_synthetique_est_valide():
    registre = charger_public(SYNTH / "registry", SYNTH / "corpus")
    assert len(registre.items) == 9
    assert registre.private_ids() == []


def test_le_jeu_synthetique_couvre_les_six_types():
    registre = charger_public(SYNTH / "registry", SYNTH / "corpus")
    types = {i.question_type.value for i in registre.items}
    assert types == {
        "fact", "qualification", "calculation",
        "false_premise", "true_premise_adversarial", "calibrated_abstention",
    }


def test_le_jeu_synthetique_contient_un_gold_versionne():
    registre = charger_public(SYNTH / "registry", SYNTH / "corpus")
    versions = sorted(i.version for i in registre.items if i.base_id == "SYNTH-VERS-01")
    assert versions == [1, 2]
    assert registre.latest_versions()["SYNTH-VERS-01"].version == 2


def test_le_jeu_synthetique_ninvente_aucun_droit():
    """Tout doit être reconnaissable comme fictif."""
    contenu = (SYNTH / "corpus" / "public" / "items.json").read_text(encoding="utf-8")
    donnees = json.loads(contenu)

    assert all(i["base_id"].startswith("SYNTH-") for i in donnees)
    assert all("example.invalid" in i["source"]["url"] for i in donnees)
    assert all("synthétique" in i["source"]["text"].lower() for i in donnees)


def test_le_jeu_synthetique_est_hors_du_corpus_reel():
    """Il ne doit pas pouvoir être chargé à la place du corpus réel."""
    assert not (Path("corpus") / "public" / "items.json").exists()
    assert SYNTH.is_dir() and not str(SYNTH).startswith("corpus")


def test_campagne_complete_sur_le_jeu_synthetique(tmp_path):
    cfg = BenchConfig.model_validate(lire_json(SYNTH / "config.json")).model_copy(
        update={"cache_root": str(tmp_path / ".cache"), "runs_root": str(tmp_path / "runs")}
    )
    campagne = executer_campagne(cfg, Path("."), juge=SyntheticJudge())

    assert len(campagne.responses) == 9 * 2 * 3
    assert len(campagne.judgments) == len(campagne.responses)
    assert campagne.model_ids == ["synth-a", "synth-b"]

    dossier = ecrire_run(campagne, tmp_path / "runs", dt.datetime(2026, 9, 1, 10, 0))
    rapport = lire_json(dossier / "public_report.json")

    assert rapport["item_count"] == 9
    assert len(rapport["models"]) == 2
    for modele in rapport["models"]:
        for metrique in modele["metrics"].values():
            assert "denominator" in metrique and "definition" in metrique


# -- CLI ------------------------------------------------------------------------------------- #


def test_cli_valider():
    resultat = runner_cli.invoke(app, ["valider", "--config", str(SYNTH / "config.json")])
    assert resultat.exit_code == 0, resultat.stdout
    assert "Registre valide" in resultat.stdout


def test_cli_executer_puis_comparer(tmp_path):
    cfg = json.loads((SYNTH / "config.json").read_text(encoding="utf-8"))
    cfg["cache_root"] = str(tmp_path / ".cache")
    cfg["runs_root"] = str(tmp_path / "runs")
    chemin = tmp_path / "config.json"
    chemin.write_text(json.dumps(cfg), encoding="utf-8")

    execution = runner_cli.invoke(app, ["executer", "--config", str(chemin)])
    assert execution.exit_code == 0, execution.stdout
    assert "Run écrit" in execution.stdout

    dossier = next((tmp_path / "runs").iterdir())
    comparaison = runner_cli.invoke(
        app, ["verifier-reproductibilite", str(dossier), str(dossier)]
    )
    assert comparaison.exit_code == 0
    assert "identiques" in comparaison.stdout
