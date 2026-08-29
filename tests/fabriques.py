"""Fabriques d'items pour les tests. Aucun accès réseau, aucun fichier partagé."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ITEM_PUBLIC: dict[str, Any] = {
    "id": "SFDR-0001",
    "corpus": "public",
    "domaine": "SFDR",
    "type": "qualification",
    "difficulte": 2,
    "question": "Un fonds article 8 doit-il publier une part d'investissements durables ?",
    "reponse_reference": "Non, sauf engagement pris dans la documentation précontractuelle.",
    "points_cles": ["article 8 ≠ objectif durable", "annexe II du règlement délégué"],
    "erreurs_disqualifiantes": ["obligation systématique de publier une part minimale"],
    "source": {
        "texte": "Règlement (UE) 2019/2088 (SFDR)",
        "article": "Article 8",
        "url": "https://eur-lex.europa.eu/eli/reg/2019/2088/oj",
        "date_version": "2019-11-27",
        "verifie_par": "A. Rouibah",
        "date_verification": "2026-08-01",
    },
    "date_validite": "2026-12-31",
    "sensible_au_temps": False,
}

ITEM_PRIVE: dict[str, Any] = {
    **copy.deepcopy(ITEM_PUBLIC),
    "id": "PRIV-0001",
    "corpus": "private",
    "domaine": "DORA",
    "source": {
        **copy.deepcopy(ITEM_PUBLIC["source"]),
        "verifie_par": "",
        "date_verification": None,
    },
}


def item(corpus: str = "public", **modifications: Any) -> dict[str, Any]:
    """Un item valide, éventuellement modifié champ par champ."""
    base = copy.deepcopy(ITEM_PUBLIC if corpus == "public" else ITEM_PRIVE)
    for cle, valeur in modifications.items():
        base[cle] = valeur
    return base


def ecrire_corpus(racine: Path, public: list[dict] | None = None,
                  prive: list[dict] | None = None) -> Path:
    """Matérialise un corpus temporaire sur disque et rend sa racine."""
    for nom, contenu in (("public", public), ("private", prive)):
        dossier = racine / nom
        dossier.mkdir(parents=True, exist_ok=True)
        if contenu:
            (dossier / "items.json").write_text(
                json.dumps(contenu, ensure_ascii=False), encoding="utf-8"
            )
    return racine
