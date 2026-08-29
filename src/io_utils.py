"""Utilitaires d'entrée/sortie.

Toute écriture d'artefact passe par ici : c'est ce qui garantit que deux
exécutions identiques produisent des fichiers identiques octet pour octet
(cf. CLAUDE.md §7 « Auditabilité »).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def json_canonique(donnees: Any) -> str:
    """Sérialise en JSON déterministe : clés triées, UTF-8, saut de ligne final."""
    return json.dumps(donnees, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def ecrire_json(chemin: Path, donnees: Any) -> None:
    """Écrit un JSON déterministe, en créant l'arborescence au besoin."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json_canonique(donnees), encoding="utf-8")


def lire_json(chemin: Path) -> Any:
    return json.loads(chemin.read_text(encoding="utf-8"))


def hash_texte(texte: str) -> str:
    """SHA-256 hexadécimal d'un texte, sur son encodage UTF-8."""
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def hash_json(donnees: Any) -> str:
    """SHA-256 de la forme canonique d'une structure JSON."""
    return hash_texte(json_canonique(donnees))


def hash_fichier(chemin: Path) -> str:
    """SHA-256 du contenu d'un fichier, lu en texte pour être insensible aux fins de ligne."""
    return hash_texte(chemin.read_text(encoding="utf-8"))
