"""Dossier de consultation d'un lot, et sa feuille de décision.

Sorties, pour `LOT-CMF` :

- `reports/LOT_CMF_REVIEW_DOSSIER.md` — une fiche par règle, deux décisions
  attendues, et ce qu'une preuve suffisante doit rapporter ;
- `data/verification/dossier-lot-cmf.csv` — le dossier de vérification restreint
  aux règles du lot, **colonnes de décision vides**.

Le script ne lit aucun texte primaire, ne décide rien, ne promeut rien. La
feuille de décision est celle du circuit de vérification déjà en place : c'est
lui, et lui seul, qui écrit au registre append-only.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from src.bench.adjudication import PRIORITES_ARBITREES, preparer
from src.bench.plan_action import (
    clusters_de_decision,
    construire_lignes,
    lots_de_lecture,
)
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.bench.rapport_lot import dossier_de_lot
from src.bench.relecture import relire
from src.bench.verification import exporter_dossier

DOSSIER_LOT_CMF = Path("reports/LOT_CMF_REVIEW_DOSSIER.md")
FEUILLE_LOT_CMF = Path("data/verification/dossier-lot-cmf.csv")


def preparer_lot(
    identifiant: str = "LOT-CMF",
    racine: Path = RACINE_RULEBOOK,
    dossier_chemin: Path = DOSSIER_LOT_CMF,
    feuille_chemin: Path = FEUILLE_LOT_CMF,
    jour: dt.date | None = None,
) -> dict:
    """Écrit le dossier du lot et sa feuille de décision vierge."""
    jour = jour or dt.date.today()
    regles = charger_rulebook(racine)
    par_id = {r.id: r for r in regles}
    relecture = relire(regles)

    dossiers = preparer(
        regles, relecture.constats, relecture.etats, relecture.extraits, PRIORITES_ARBITREES
    )
    lignes = construire_lignes(dossiers, relecture.acces)
    groupes = lots_de_lecture(lignes) + clusters_de_decision(dossiers, lignes)

    groupe = next((g for g in groupes if g.identifiant == identifiant), None)
    if groupe is None:
        connus = ", ".join(g.identifiant for g in groupes)
        raise ValueError(f"lot « {identifiant} » inconnu — lots et clusters : {connus}")

    du_lot = [ligne for ligne in lignes if ligne.rule_id in groupe.regles]
    obstacle = next(
        (relecture.obstacles.get(ligne.rule_id, "") for ligne in du_lot if relecture.obstacles.get(ligne.rule_id)),
        "",
    )

    # La feuille de décision est le dossier de vérification du circuit existant :
    # une seconde feuille ferait exister deux chemins vers le registre.
    exporter_dossier([par_id[ligne.rule_id] for ligne in du_lot], Path(feuille_chemin))

    Path(dossier_chemin).parent.mkdir(parents=True, exist_ok=True)
    Path(dossier_chemin).write_text(
        dossier_de_lot(
            identifiant,
            groupe.source,
            obstacle,
            du_lot,
            par_id,
            relecture.constats,
            str(feuille_chemin),
            jour,
        ),
        encoding="utf-8",
    )

    return {
        "lot": identifiant,
        "source": groupe.source,
        "regles": [ligne.rule_id for ligne in du_lot],
        "articles": sorted({ligne.article for ligne in du_lot if ligne.article}),
        "statuts": sorted({par_id[ligne.rule_id].status.value for ligne in du_lot}),
        "exceptions_statuts": sorted(
            {par_id[ligne.rule_id].exceptions_status.value for ligne in du_lot}
        ),
        "empreinte": relecture.empreinte,
    }


if __name__ == "__main__":
    resultat = preparer_lot()
    print(f"{resultat['lot']} — {len(resultat['regles'])} règle(s) : {resultat['source']}")
    for rule_id in resultat["regles"]:
        print(f"  {rule_id}")
    print(f"  statuts : {resultat['statuts']} — exceptions : {resultat['exceptions_statuts']}")
