"""Préparation du pack d'arbitrage P0/P1.

Sorties :

- `reports/HUMAN_REVIEW_P0_P1.md` — un dossier par règle, P0 puis P1 ;
- `data/verification/dossier-adjudication.csv` — les mêmes règles, à remplir ;
- `reports/HUMAN_REVIEW_PROGRESS.md` — ce qui est tranché, ce qui reste.

Le script **ne décide rien** et ne promeut aucune règle : il prépare. Les
colonnes de décision sortent vides, et le rapport de progression les recompte à
chaque passe. L'application des décisions est un autre circuit — celui de la
vérification, qui exige une signature.

Les constats sont **relus** des artefacts d'audit publiés, non refaits : le
texte primaire n'est pas atteignable depuis cet environnement, et une passe qui
ne peut pas lire le texte ne doit rien constater de neuf. La relecture refuse
d'écrire si elle ne reproduit pas le blocage que l'audit avait publié.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from src.bench.adjudication import PRIORITES_ARBITREES, preparer, regroupements
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.bench.rapport_adjudication import (
    DOSSIER_ADJUDICATION,
    PACK_ADJUDICATION,
    PROGRESSION,
    ecrire_dossier,
    lire_decisions,
    pack,
    progression,
)
from src.bench.relecture import relire


def preparer_adjudication(
    racine: Path = RACINE_RULEBOOK,
    pack_chemin: Path = PACK_ADJUDICATION,
    dossier_chemin: Path = DOSSIER_ADJUDICATION,
    progression_chemin: Path = PROGRESSION,
    priorites: tuple[str, ...] = PRIORITES_ARBITREES,
    jour: dt.date | None = None,
) -> dict:
    """Écrit le pack, le dossier à remplir et la progression. Ne décide rien."""
    jour = jour or dt.date.today()
    regles = charger_rulebook(racine)
    relecture = relire(regles)

    dossiers = preparer(
        regles, relecture.constats, relecture.etats, relecture.extraits, priorites
    )

    # Les décisions déjà rendues sont relues avant réécriture : réécrire le
    # dossier ne doit pas effacer un arbitrage. S'il en porte, on ne le touche
    # pas — le pack et la progression, eux, se régénèrent.
    decisions = lire_decisions(dossier_chemin)
    if not decisions:
        ecrire_dossier(dossiers, Path(dossier_chemin))

    Path(pack_chemin).parent.mkdir(parents=True, exist_ok=True)
    Path(pack_chemin).write_text(
        pack(dossiers, relecture.empreinte, relecture.artefacts, jour), encoding="utf-8"
    )
    Path(progression_chemin).write_text(
        progression(dossiers, decisions, regles, relecture.etats, jour), encoding="utf-8"
    )

    return {
        "dossiers": len(dossiers),
        "par_priorite": {
            priorite: sum(1 for d in dossiers if d.priorite_revue == priorite)
            for priorite in priorites
        },
        "regroupements": len(regroupements(dossiers)),
        "questions_distinctes": len({d.review_cluster_id for d in dossiers}),
        "decisions_rendues": len(decisions),
        "empreinte": relecture.empreinte,
        "dossier_preserve": bool(decisions),
    }


if __name__ == "__main__":
    resultat = preparer_adjudication()
    print(f"{resultat['dossiers']} dossier(s) d'arbitrage")
    for priorite, compte in resultat["par_priorite"].items():
        print(f"  {priorite} : {compte}")
    print(f"  questions distinctes : {resultat['questions_distinctes']}")
    print(f"  regroupements (>1 règle) : {resultat['regroupements']}")
    print(f"  décisions déjà rendues : {resultat['decisions_rendues']}")
    print(f"  empreinte de l'audit relu : {resultat['empreinte']}")
