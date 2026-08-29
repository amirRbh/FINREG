"""Étape 3 — runner, cache, reprise, débit. Aucun accès réseau."""

from __future__ import annotations

import asyncio

import pytest

from src.cache import CacheDisque, hash_prompt
from src.limiteur import LimiteurDebit
from src.providers.base import Requete
from src.providers.fake import FauxFournisseur
from src.runner import Runner, lire_prompt_systeme
from src.schema import Config, ConfigExecution, ConfigFournisseur, Corpus, Item
from src.securite import PrivateCorpusLeakError
from tests.fabriques import item

PROMPT = "Tu es un assistant de conformité.\n"


def config(**modifications) -> Config:
    base = {
        "corpus": Corpus.PUBLIC,
        "fournisseurs": [
            ConfigFournisseur(
                id="f-a", nom="Modèle A", editeur="Éditeur A",
                adaptateur="fake", modele="modele-a", zero_retention=True,
            )
        ],
        "execution": ConfigExecution(nb_runs=3, concurrence=2, requetes_par_minute=100000),
    }
    base.update(modifications)
    return Config(**base)


class FabriqueTracante:
    """Fabrique de fournisseurs qui conserve les instances pour les inspecter."""

    def __init__(self):
        self.instances: dict[str, FauxFournisseur] = {}

    def __call__(self, config_fournisseur):
        if config_fournisseur.id not in self.instances:
            self.instances[config_fournisseur.id] = FauxFournisseur(config_fournisseur)
        return self.instances[config_fournisseur.id]

    @property
    def total_appels(self) -> int:
        return sum(f.nb_appels for f in self.instances.values())


def runner(tmp_path, cfg=None, fabrique=None, corpus=Corpus.PUBLIC):
    cfg = cfg or config()
    return Runner(
        cfg,
        PROMPT,
        CacheDisque(tmp_path / "cache", corpus),
        fabrique_fournisseur=fabrique or FabriqueTracante(),
    )


def items_publics(n=2) -> list[Item]:
    return [
        Item.model_validate(item(id=f"PUB-{i}", question=f"Question numéro {i} ?"))
        for i in range(n)
    ]


def test_trois_executions_par_item_et_par_fournisseur(tmp_path):
    fabrique = FabriqueTracante()
    resultat = runner(tmp_path, fabrique=fabrique).executer(items_publics(2))

    assert len(resultat.reponses) == 2 * 3
    assert sorted({r.index_run for r in resultat.reponses}) == [0, 1, 2]
    assert fabrique.total_appels == 6


def test_temperature_zero_transmise(tmp_path):
    fabrique = FabriqueTracante()
    runner(tmp_path, fabrique=fabrique).executer(items_publics(1))

    appels = fabrique.instances["f-a"].appels
    assert appels and all(a.temperature == 0.0 for a in appels)


def test_le_prompt_systeme_est_le_meme_pour_tous(tmp_path):
    fabrique = FabriqueTracante()
    runner(tmp_path, fabrique=fabrique).executer(items_publics(2))

    assert {a.prompt_systeme for a in fabrique.instances["f-a"].appels} == {PROMPT}


def test_seconde_execution_ne_rappelle_pas_le_fournisseur(tmp_path):
    """Le cache disque : on ne repaie jamais deux fois la même requête."""
    items = items_publics(2)

    fabrique1 = FabriqueTracante()
    premier = runner(tmp_path, fabrique=fabrique1).executer(items)
    assert fabrique1.total_appels == 6
    assert premier.nb_depuis_cache == 0

    fabrique2 = FabriqueTracante()
    second = runner(tmp_path, fabrique=fabrique2).executer(items)
    assert fabrique2.total_appels == 0
    assert second.nb_depuis_cache == 6

    assert [r.texte for r in premier.reponses] == [r.texte for r in second.reponses]


def test_reprise_apres_interruption(tmp_path):
    """Une exécution interrompue ne refait que ce qui manque."""
    items = items_publics(3)

    partielle = FabriqueTracante()
    partielle.instances["f-a"] = FauxFournisseur(config().fournisseurs[0])
    partielle.instances["f-a"].questions_en_echec = {"Question numéro 2"}

    premier = runner(tmp_path, fabrique=partielle).executer(items)
    assert premier.nb_erreurs == 3  # les 3 runs de l'item interrompu

    reprise = FabriqueTracante()
    second = runner(tmp_path, fabrique=reprise).executer(items)

    assert second.nb_erreurs == 0
    assert reprise.total_appels == 3  # seuls les manquants sont rejoués
    assert second.nb_depuis_cache == 6


def test_une_erreur_nest_pas_mise_en_cache(tmp_path):
    fabrique = FabriqueTracante()
    fabrique.instances["f-a"] = FauxFournisseur(config().fournisseurs[0])
    fabrique.instances["f-a"].questions_en_echec = {"Question numéro 0"}

    resultat = runner(tmp_path, fabrique=fabrique).executer(items_publics(1))

    assert resultat.nb_erreurs == 3
    assert all(r.texte == "" for r in resultat.reponses)
    assert all("échec simulé" in (r.erreur or "") for r in resultat.reponses)


def test_cle_de_cache_sur_prompt_modele_et_index(tmp_path):
    """Changer l'un des trois éléments de la clé invalide l'entrée."""
    cache = CacheDisque(tmp_path, Corpus.PUBLIC)
    empreinte = hash_prompt(PROMPT, "Question ?")
    cache.ecrire(empreinte, "modele-a", 0, "texte")

    assert cache.lire(empreinte, "modele-a", 0) == "texte"
    assert cache.lire(empreinte, "modele-a", 1) is None
    assert cache.lire(empreinte, "modele-b", 0) is None
    assert cache.lire(hash_prompt(PROMPT, "Autre ?"), "modele-a", 0) is None


def test_le_prompt_systeme_fait_partie_de_la_cle(tmp_path):
    """Changer le prompt système invalide tout le cache : sinon le run n'est pas honnête."""
    items = items_publics(1)
    runner(tmp_path, fabrique=FabriqueTracante()).executer(items)

    fabrique = FabriqueTracante()
    autre = Runner(
        config(), PROMPT + "\nConsigne ajoutée.",
        CacheDisque(tmp_path / "cache", Corpus.PUBLIC),
        fabrique_fournisseur=fabrique,
    )
    autre.executer(items)
    assert fabrique.total_appels == 3


def test_les_caches_sont_cloisonnes_par_corpus(tmp_path):
    cache_public = CacheDisque(tmp_path, Corpus.PUBLIC)
    cache_prive = CacheDisque(tmp_path, Corpus.PRIVE)
    empreinte = hash_prompt(PROMPT, "Question ?")

    cache_prive.ecrire(empreinte, "modele-a", 0, "réponse issue du privé")

    assert cache_public.lire(empreinte, "modele-a", 0) is None
    assert cache_prive.lire(empreinte, "modele-a", 0) == "réponse issue du privé"


def test_la_concurrence_est_bornee(tmp_path):
    cfg = config(execution=ConfigExecution(nb_runs=3, concurrence=2, requetes_par_minute=100000))
    execution = runner(tmp_path, cfg=cfg, fabrique=FabriqueTracante())
    execution.executer(items_publics(5))

    assert execution.concurrence_max_observee <= 2


def test_corpus_prive_vers_fournisseur_non_conforme_ne_declenche_aucun_appel(tmp_path):
    """Le garde-fou coupe avant même la construction du prompt."""
    cfg = config(
        corpus=Corpus.PRIVE,
        fournisseurs=[
            ConfigFournisseur(
                id="f-a", nom="Modèle A", editeur="Éditeur A",
                adaptateur="fake", modele="modele-a", zero_retention=False,
            )
        ],
    )
    fabrique = FabriqueTracante()
    execution = runner(tmp_path, cfg=cfg, fabrique=fabrique, corpus=Corpus.PRIVE)
    prives = [Item.model_validate(item("private", id="PRIV-1"))]

    with pytest.raises(PrivateCorpusLeakError):
        execution.executer(prives)

    assert fabrique.total_appels == 0


def test_corpus_prive_vers_fournisseur_conforme_sexecute(tmp_path):
    cfg = config(
        corpus=Corpus.PRIVE,
        fournisseurs=[
            ConfigFournisseur(
                id="f-a", nom="Modèle A", editeur="Éditeur A",
                adaptateur="fake", modele="modele-a", zero_retention=True,
            )
        ],
    )
    execution = runner(tmp_path, cfg=cfg, corpus=Corpus.PRIVE)
    resultat = execution.executer([Item.model_validate(item("private", id="PRIV-1"))])

    assert len(resultat.reponses) == 3


def test_ordre_des_reponses_stable(tmp_path):
    """L'ordonnancement concurrent ne doit pas transparaître dans les artefacts."""
    items = items_publics(4)
    premier = runner(tmp_path / "a", fabrique=FabriqueTracante()).executer(items)
    second = runner(tmp_path / "b", fabrique=FabriqueTracante()).executer(items)

    cles = lambda r: [(x.item_id, x.fournisseur_id, x.index_run) for x in r.reponses]
    assert cles(premier) == cles(second) == sorted(cles(premier))


def test_limiteur_espace_les_acquisitions():
    """Débit vérifié sur une horloge simulée : les tests ne dorment jamais."""
    temps = {"maintenant": 0.0}
    attentes: list[float] = []

    async def dormir(duree):
        attentes.append(duree)
        temps["maintenant"] += duree

    async def scenario():
        limiteur = LimiteurDebit(60, horloge=lambda: temps["maintenant"], dormir=dormir)
        for _ in range(4):
            await limiteur.acquerir()

    asyncio.run(scenario())

    assert attentes == [pytest.approx(1.0), pytest.approx(1.0), pytest.approx(1.0)]


def test_prompt_systeme_vide_refuse(tmp_path):
    chemin = tmp_path / "vide.txt"
    chemin.write_text("   \n", encoding="utf-8")

    with pytest.raises(ValueError, match="vide"):
        lire_prompt_systeme(chemin)


def test_prompt_systeme_versionne_est_lisible():
    from pathlib import Path

    texte = lire_prompt_systeme(Path("prompts/system.txt"))
    assert "réglementation financière" in texte
