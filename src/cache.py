"""Cache disque des réponses de modèle.

Indexé sur `(hash du prompt, modèle, index du run)` : on ne repaie jamais deux
fois la même requête, et une exécution interrompue reprend là où elle s'est
arrêtée (CLAUDE.md §5).

Les caches sont cloisonnés par corpus : une réponse issue du corpus privé ne
peut pas se retrouver dans un artefact public.
"""

from __future__ import annotations

import re
from pathlib import Path

from src.io_utils import ecrire_json, hash_texte, lire_json
from src.schema import Corpus

SEPARATEUR_PROMPT = "\n\n===QUESTION===\n\n"


def hash_prompt(prompt_systeme: str, question: str) -> str:
    """Empreinte du prompt complet réellement envoyé au modèle."""
    return hash_texte(prompt_systeme + SEPARATEUR_PROMPT + question)


def _slug(valeur: str) -> str:
    """Nom de dossier sûr, dérivé d'un identifiant de modèle."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", valeur).strip("_") or "modele"


class CacheDisque:
    def __init__(self, racine: Path, corpus: Corpus) -> None:
        self.racine = Path(racine) / corpus.value
        self.corpus = corpus
        self.lectures = 0
        self.ecritures = 0

    def chemin(self, empreinte: str, modele: str, index_run: int) -> Path:
        # Deux niveaux de sous-dossiers : un corpus de plusieurs milliers d'items
        # ne fait pas un dossier illisible.
        return self.racine / _slug(modele) / empreinte[:2] / f"{empreinte}-{index_run}.json"

    def lire(self, empreinte: str, modele: str, index_run: int) -> str | None:
        chemin = self.chemin(empreinte, modele, index_run)
        if not chemin.is_file():
            return None
        contenu = lire_json(chemin)
        # Une entrée dont la clé ne correspond pas est ignorée plutôt que servie :
        # mieux vaut repayer une requête que noter la mauvaise réponse.
        if (
            contenu.get("hash_prompt") != empreinte
            or contenu.get("modele") != modele
            or contenu.get("index_run") != index_run
        ):
            return None
        self.lectures += 1
        return contenu["texte"]

    def ecrire(self, empreinte: str, modele: str, index_run: int, texte: str) -> None:
        ecrire_json(
            self.chemin(empreinte, modele, index_run),
            {
                "hash_prompt": empreinte,
                "modele": modele,
                "index_run": index_run,
                "texte": texte,
            },
        )
        self.ecritures += 1


class CacheMemoire(CacheDisque):
    """Même interface, sans disque. Réservé aux tests qui n'ont pas besoin de persistance."""

    def __init__(self, corpus: Corpus = Corpus.PUBLIC) -> None:
        self.corpus = corpus
        self.entrees: dict[tuple[str, str, int], str] = {}
        self.lectures = 0
        self.ecritures = 0

    def lire(self, empreinte: str, modele: str, index_run: int) -> str | None:
        texte = self.entrees.get((empreinte, modele, index_run))
        if texte is not None:
            self.lectures += 1
        return texte

    def ecrire(self, empreinte: str, modele: str, index_run: int, texte: str) -> None:
        self.entrees[(empreinte, modele, index_run)] = texte
        self.ecritures += 1
