"""Génère le Question Family Map à partir du Rulebook (phase 7).

Le script ne décide rien : tout ce qu'il écrit est dérivé de `data/rules/`. Le
relancer après une vérification du Rulebook suffit à mettre la carte à jour —
les familles dont la règle a été promue passent d'elles-mêmes de `blocked` à
`ready`, sans qu'on les réécrive.

Sorties :

- `data/families/<domaine>-families.json` — les familles candidates ;
- `data/families/family-manifest.json` — le récapitulatif chiffré ;
- `reports/FAMILY_MAP_QC.md` — le contrôle qualité, les lacunes, les redondances ;
- `reports/FAMILY_COVERAGE_MATRIX.csv` — la matrice DOMAIN × RULE × FAMILY.

Aucune question n'est rédigée ici (phase 7 §17).
"""

from __future__ import annotations

from pathlib import Path

from src.bench.carte_familles import (
    deriver_familles,
    faisabilite_distribution,
    lacunes,
    matrice_couverture,
    redondances,
)
from src.bench.qc_familles import (
    MATRICE_FAMILLES,
    RACINE_FAMILLES,
    RAPPORT_FAMILLES,
    construire_manifeste,
    controler,
    ecrire_carte,
    ecrire_matrice,
    erreurs,
    rapport_markdown,
)
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.io_utils import ecrire_json


def generer(
    racine_regles: Path = RACINE_RULEBOOK,
    racine_familles: Path = RACINE_FAMILLES,
    rapport: Path = RAPPORT_FAMILLES,
    matrice: Path = MATRICE_FAMILLES,
) -> dict:
    """Dérive, contrôle et écrit la carte. Rend le manifeste."""
    regles = charger_rulebook(racine_regles)
    familles = deriver_familles(regles)

    comptes = ecrire_carte(familles, racine_familles)
    manifeste = construire_manifeste(familles, regles, comptes)
    ecrire_json(Path(racine_familles) / "family-manifest.json", manifeste)

    constats = controler(familles, regles)
    Path(rapport).parent.mkdir(parents=True, exist_ok=True)
    Path(rapport).write_text(rapport_markdown(familles, regles, constats), encoding="utf-8")
    ecrire_matrice(matrice_couverture(regles, familles), Path(matrice))

    return manifeste | {
        "number_of_findings": len(constats),
        "number_of_blocking_findings": len(erreurs(constats)),
        "coverage_gaps": lacunes(regles, familles),
        "redundancy": redondances(familles, regles),
        "distribution": faisabilite_distribution(familles),
    }


if __name__ == "__main__":
    resultat = generer()
    print(f"{resultat['number_of_families']} famille(s) écrites dans {RACINE_FAMILLES}")
    print(f"  règles exploitées : {resultat['number_of_rules_with_family']} / {resultat['number_of_rules']}")
    print(f"  prêtes : {resultat['number_ready']} — bloquées : {resultat['number_blocked']}")
    print(f"  constats : {resultat['number_of_findings']} dont {resultat['number_of_blocking_findings']} bloquant(s)")
