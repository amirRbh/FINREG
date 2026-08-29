"""Chargement et validation du corpus.

La validation rapporte **toutes** les erreurs d'un coup : un corpus se corrige
en une passe, pas erreur après erreur (cf. CLAUDE.md §4).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from src.io_utils import hash_json
from src.schema import Corpus, Item

#: Nom du sous-dossier portant chaque corpus, sous la racine `corpus/`.
DOSSIERS: dict[Corpus, str] = {Corpus.PUBLIC: "public", Corpus.PRIVE: "private"}


@dataclass(frozen=True)
class ErreurCorpus:
    """Une erreur de validation, localisée pour être corrigeable directement."""

    fichier: str
    position: str
    message: str

    def __str__(self) -> str:
        return f"{self.fichier}[{self.position}] : {self.message}"


class CorpusInvalide(Exception):
    """Levée quand au moins un item est invalide. Porte la liste complète."""

    def __init__(self, erreurs: list[ErreurCorpus]) -> None:
        self.erreurs = erreurs
        detail = "\n".join(f"  - {e}" for e in erreurs)
        super().__init__(f"{len(erreurs)} erreur(s) de corpus :\n{detail}")


def _messages_pydantic(exc: ValidationError) -> list[str]:
    messages = []
    for erreur in exc.errors():
        champ = ".".join(str(p) for p in erreur["loc"]) or "(item)"
        messages.append(f"{champ} : {erreur['msg']}")
    return messages


def _items_du_fichier(chemin: Path) -> tuple[list[dict], list[ErreurCorpus]]:
    """Lit un fichier de corpus : soit un item, soit une liste d'items."""
    try:
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [ErreurCorpus(chemin.name, "fichier", f"JSON illisible : {exc}")]

    if isinstance(contenu, dict):
        return [contenu], []
    if isinstance(contenu, list):
        if all(isinstance(brut, dict) for brut in contenu):
            return contenu, []
        return [], [
            ErreurCorpus(chemin.name, "fichier", "la liste doit ne contenir que des objets")
        ]
    return [], [
        ErreurCorpus(chemin.name, "fichier", "attendu : un objet ou une liste d'objets")
    ]


def charger_dossier(dossier: Path, corpus_attendu: Corpus) -> tuple[list[Item], list[ErreurCorpus]]:
    """Charge un dossier de corpus. Ne lève rien : rend les items valides et les erreurs."""
    items: list[Item] = []
    erreurs: list[ErreurCorpus] = []

    if not dossier.is_dir():
        return items, erreurs

    for chemin in sorted(dossier.glob("*.json")):
        bruts, erreurs_fichier = _items_du_fichier(chemin)
        erreurs.extend(erreurs_fichier)

        for index, brut in enumerate(bruts):
            # On repère l'item par son id quand il est lisible, sinon par sa position.
            position = str(brut.get("id") or f"#{index}")
            try:
                item = Item.model_validate(brut)
            except ValidationError as exc:
                erreurs.extend(
                    ErreurCorpus(chemin.name, position, message)
                    for message in _messages_pydantic(exc)
                )
                continue

            if item.corpus is not corpus_attendu:
                # Un item marqué privé posé dans public/ (ou l'inverse) est une
                # erreur bloquante : c'est exactement le genre de glissement que
                # le garde-fou de non-rétention ne pourrait plus rattraper.
                erreurs.append(
                    ErreurCorpus(
                        chemin.name,
                        position,
                        f"corpus déclaré « {item.corpus.value} » "
                        f"dans le dossier « {corpus_attendu.value} »",
                    )
                )
                continue

            items.append(item)

    return items, erreurs


def _erreurs_de_doublons(items: list[Item]) -> list[ErreurCorpus]:
    vus: dict[str, Item] = {}
    erreurs: list[ErreurCorpus] = []
    for item in items:
        if item.id in vus:
            erreurs.append(
                ErreurCorpus(
                    f"corpus/{DOSSIERS[item.corpus]}",
                    item.id,
                    "identifiant en double (les ids sont uniques tous corpus confondus)",
                )
            )
        else:
            vus[item.id] = item
    return erreurs


def charger_corpus(racine: Path, corpus: Corpus | list[Corpus]) -> list[Item]:
    """Charge un ou plusieurs corpus, ou lève `CorpusInvalide` avec toutes les erreurs.

    Les items sont rendus triés par id : le chargement est reproductible quel que
    soit l'ordre de parcours du système de fichiers.
    """
    demandes = [corpus] if isinstance(corpus, Corpus) else list(corpus)

    items: list[Item] = []
    erreurs: list[ErreurCorpus] = []
    for demande in demandes:
        trouves, erreurs_dossier = charger_dossier(racine / DOSSIERS[demande], demande)
        items.extend(trouves)
        erreurs.extend(erreurs_dossier)

    erreurs.extend(_erreurs_de_doublons(items))

    if erreurs:
        raise CorpusInvalide(erreurs)

    return sorted(items, key=lambda item: item.id)


def version_corpus(items: list[Item]) -> str:
    """Hash du corpus effectivement chargé, tracé dans chaque run (CLAUDE.md §7)."""
    return hash_json([item.model_dump(mode="json") for item in sorted(items, key=lambda i: i.id)])


def resume_corpus(items: list[Item]) -> dict:
    """Résumé versionnable du corpus : ce qui identifie le jeu de questions utilisé."""
    return {
        "nb_items": len(items),
        "version": version_corpus(items),
        "ids": [item.id for item in items],
        "par_corpus": {
            corpus.value: sum(1 for i in items if i.corpus is corpus) for corpus in Corpus
        },
        "par_domaine": {
            domaine: sum(1 for i in items if i.domaine == domaine)
            for domaine in sorted({i.domaine for i in items})
        },
    }
