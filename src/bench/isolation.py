"""Garde-fous d'isolation du corpus privé.

Le privé est l'actif commercial : il n'est jamais publié, jamais journalisé en
clair, jamais présent dans un artefact public. Le code ne peut pas rendre une
fuite impossible, mais il peut la rendre bruyante à chaque endroit où elle
pourrait se produire.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

from src.bench.vocabulaires import Corpus


class PrivateLeakError(RuntimeError):
    """Du contenu ou un identifiant privé a été trouvé là où il ne doit pas être.

    Le message ne cite jamais le contenu fautif — seulement des identifiants et
    l'endroit où ils ont été trouvés. Une erreur finit dans un journal.
    """


def _texte_de(charge: Any) -> str:
    if isinstance(charge, (str, bytes)):
        return charge.decode("utf-8", "replace") if isinstance(charge, bytes) else charge
    if isinstance(charge, Path):
        return charge.read_text(encoding="utf-8")
    return json.dumps(charge, ensure_ascii=False, default=str)


def assert_no_private_ids(
    charge: Any, private_ids: Iterable[str], ou: str = "artefact"
) -> None:
    """Refuse un artefact qui contient un identifiant privé.

    Cherche aussi les identifiants sans suffixe de version : `SFDR-0042` doit être
    détecté même si le privé contient `SFDR-0042-v2`.
    """
    texte = _texte_de(charge)
    trouves: set[str] = set()

    for identifiant in private_ids:
        for forme in {identifiant, re.sub(r"-v\d+$", "", identifiant)}:
            if not forme:
                continue
            if re.search(rf"(?<![\w-]){re.escape(forme)}(?![\w-])", texte):
                trouves.add(identifiant)

    if trouves:
        raise PrivateLeakError(
            f"{len(trouves)} identifiant(s) du corpus privé présents dans {ou} : "
            f"{sorted(trouves)[:5]}. Aucun contenu privé ne doit sortir."
        )


def assert_no_private_content(charge: Any, textes_prives: Iterable[str], ou: str = "artefact") -> None:
    """Refuse un artefact qui contient un fragment de texte privé.

    Complète le contrôle par identifiant : un export peut recopier une question
    sans son identifiant.
    """
    texte = _texte_de(charge)
    nombre = sum(
        1 for fragment in textes_prives if fragment.strip() and fragment.strip() in texte
    )
    if nombre:
        raise PrivateLeakError(
            f"{nombre} fragment(s) de contenu privé présents dans {ou}. "
            "Le contenu fautif n'est pas reproduit ici volontairement."
        )


def assert_private_is_gitignored(racine: Path, chemin_prive: str = "corpus/private/") -> None:
    """Vérifie que le dossier privé est bien exclu du versionnement."""
    gitignore = Path(racine) / ".gitignore"
    if not gitignore.is_file():
        raise PrivateLeakError(f"aucun .gitignore à la racine {racine}")

    lignes = {
        ligne.strip().rstrip("/")
        for ligne in gitignore.read_text(encoding="utf-8").splitlines()
        if ligne.strip() and not ligne.strip().startswith("#")
    }
    if chemin_prive.rstrip("/") not in lignes:
        raise PrivateLeakError(
            f"{chemin_prive} n'est pas dans {gitignore} : le corpus privé pourrait "
            "être versionné par accident"
        )


def assert_no_private_tracked_by_git(racine: Path, chemin_prive: str = "corpus/private") -> list[str]:
    """Rend la liste des fichiers privés suivis par git. Vide = conforme."""
    import subprocess

    resultat = subprocess.run(
        ["git", "-C", str(racine), "ls-files", "--", chemin_prive],
        capture_output=True,
        text=True,
        check=False,
    )
    suivis = [ligne for ligne in resultat.stdout.splitlines() if ligne.strip()]
    if suivis:
        raise PrivateLeakError(
            f"{len(suivis)} fichier(s) du corpus privé suivis par git : {suivis[:3]}"
        )
    return suivis


def redact_for_log(items: Iterable[Any]) -> list[dict]:
    """Forme journalisable d'un lot d'items : identifiants et métadonnées seulement."""
    return [item.redacted() for item in items]


def public_only(items: Iterable[Any]) -> list[Any]:
    """Ne garde que le public. Le point de passage unique avant tout export."""
    return [item for item in items if item.corpus is Corpus.PUBLIC]
