"""Exécution des appels modèles.

Trois exécutions par item, température 0, prompt système unique et versionné,
appels concurrents sous limite de débit, cache disque et reprise après
interruption (CLAUDE.md §5).

Le garde-fou de non-rétention est appelé **avant** toute construction de prompt :
si un item privé vise un fournisseur non conforme, aucune requête n'est même
assemblée (CLAUDE.md §3).
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from src.cache import CacheDisque, hash_prompt
from src.limiteur import LimiteurDebit
from src.providers.base import Fournisseur, Requete, creer_fournisseur
from src.schema import Config, ConfigFournisseur, Corpus, Item, ReponseBrute
from src.securite import verifier_lot


@dataclass
class ResultatExecution:
    reponses: list[ReponseBrute] = field(default_factory=list)
    nb_appels_reseau: int = 0
    nb_depuis_cache: int = 0
    nb_erreurs: int = 0

    def par_item(self) -> dict[tuple[str, str, int], ReponseBrute]:
        return {(r.item_id, r.fournisseur_id, r.index_run): r for r in self.reponses}


def lire_prompt_systeme(chemin: Path) -> str:
    """Le prompt système est un fichier versionné, jamais une chaîne en dur."""
    texte = Path(chemin).read_text(encoding="utf-8")
    if not texte.strip():
        raise ValueError(f"prompt système vide : {chemin}")
    return texte


class Runner:
    def __init__(
        self,
        config: Config,
        prompt_systeme: str,
        cache: CacheDisque,
        fabrique_fournisseur: Callable[[ConfigFournisseur], Fournisseur] = creer_fournisseur,
        limiteur: LimiteurDebit | None = None,
    ) -> None:
        self.config = config
        self.prompt_systeme = prompt_systeme
        self.cache = cache
        self.fabrique_fournisseur = fabrique_fournisseur
        self.limiteur = limiteur or LimiteurDebit(config.execution.requetes_par_minute)
        self._semaphore = asyncio.Semaphore(config.execution.concurrence)
        #: Concurrence réellement atteinte, pour vérifier la limite en test.
        self.concurrence_max_observee = 0
        self._en_vol = 0

    # ------------------------------------------------------------------ #
    # Contrôle préalable
    # ------------------------------------------------------------------ #

    def _controler_avant_tout_appel(
        self, items: list[Item], fournisseurs: dict[str, Fournisseur]
    ) -> None:
        """Vérifie le lot entier contre chaque destinataire. Lève avant tout prompt."""
        for fournisseur in fournisseurs.values():
            verifier_lot(items, fournisseur)

    # ------------------------------------------------------------------ #
    # Exécution
    # ------------------------------------------------------------------ #

    async def _appeler(
        self, fournisseur: Fournisseur, item: Item, index_run: int
    ) -> ReponseBrute:
        empreinte = hash_prompt(self.prompt_systeme, item.question)

        cache = self.cache.lire(empreinte, fournisseur.modele, index_run)
        if cache is not None:
            return ReponseBrute(
                item_id=item.id,
                fournisseur_id=fournisseur.id,
                modele=fournisseur.modele,
                index_run=index_run,
                hash_prompt=empreinte,
                texte=cache,
                depuis_cache=True,
            )

        requete = Requete(
            prompt_systeme=self.prompt_systeme,
            question=item.question,
            temperature=self.config.execution.temperature,
        )

        await self.limiteur.acquerir()
        async with self._semaphore:
            self._en_vol += 1
            self.concurrence_max_observee = max(self.concurrence_max_observee, self._en_vol)
            debut = time.monotonic()
            try:
                texte = await asyncio.wait_for(
                    fournisseur.completer(requete, self.config.execution.timeout_s),
                    timeout=self.config.execution.timeout_s,
                )
            except Exception as exc:  # tracé, pas masqué : le run reste exploitable
                return ReponseBrute(
                    item_id=item.id,
                    fournisseur_id=fournisseur.id,
                    modele=fournisseur.modele,
                    index_run=index_run,
                    hash_prompt=empreinte,
                    texte="",
                    erreur=f"{type(exc).__name__}: {exc}",
                    latence_ms=int((time.monotonic() - debut) * 1000),
                )
            finally:
                self._en_vol -= 1

        latence_ms = int((time.monotonic() - debut) * 1000)
        # On n'écrit au cache qu'un appel réussi : une erreur ne doit pas être rejouée.
        self.cache.ecrire(empreinte, fournisseur.modele, index_run, texte)
        return ReponseBrute(
            item_id=item.id,
            fournisseur_id=fournisseur.id,
            modele=fournisseur.modele,
            index_run=index_run,
            hash_prompt=empreinte,
            texte=texte,
            latence_ms=latence_ms,
        )

    async def executer_async(self, items: list[Item]) -> ResultatExecution:
        fournisseurs = {
            config.id: self.fabrique_fournisseur(config)
            for config in self.config.fournisseurs_actifs
        }
        self._controler_avant_tout_appel(items, fournisseurs)

        taches = [
            self._appeler(fournisseur, item, index_run)
            for item in items
            for fournisseur in fournisseurs.values()
            for index_run in range(self.config.execution.nb_runs)
        ]
        reponses = await asyncio.gather(*taches)

        # Ordre stable, indépendant de l'ordonnancement : le run est reproductible.
        reponses = sorted(reponses, key=lambda r: (r.item_id, r.fournisseur_id, r.index_run))

        return ResultatExecution(
            reponses=list(reponses),
            nb_appels_reseau=sum(1 for r in reponses if not r.depuis_cache and not r.erreur),
            nb_depuis_cache=sum(1 for r in reponses if r.depuis_cache),
            nb_erreurs=sum(1 for r in reponses if r.erreur),
        )

    def executer(self, items: list[Item]) -> ResultatExecution:
        return asyncio.run(self.executer_async(items))


def corpus_des_items(items: list[Item]) -> Corpus:
    """Corpus effectif d'un lot ; privé dès qu'un seul item l'est."""
    return Corpus.PRIVE if any(item.est_prive for item in items) else Corpus.PUBLIC
