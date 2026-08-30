"""Plan de travail de la revue humaine P0/P1.

Sorties :

- `reports/HUMAN_REVIEW_ACTION_PLAN.md` — l'ordre de travail et son rendement ;
- `reports/HUMAN_REVIEW_ACTION_PLAN.csv` — une ligne par règle, colonnes fixes ;
- `reports/LCBFT_MANUAL_CONSULTATION_PACK.md` — ce qu'il reste à lire dans le CMF ;
- `reports/AMF-R-005-SOURCE-REANCHORING.md` — pourquoi l'URL ne vaut plus.

Le script **ne décide rien, ne promeut rien, ne réécrit aucune règle**. Il ne
touche ni au Rulebook, ni au registre, ni à la carte des familles : il range des
dossiers déjà constitués et calcule ce que chaque action débloquerait.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from src.bench.adjudication import PRIORITES_ARBITREES, preparer
from src.bench.plan_action import (
    ActionPrincipale,
    clusters_de_decision,
    construire_lignes,
    elements_bloquants,
    lots_de_lecture,
    ordre_execution,
    prochaine_action,
    projeter,
)
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.bench.rapport_plan_action import (
    DOSSIER_REANCRAGE,
    PACK_LCBFT,
    PLAN_ACTION,
    PLAN_ACTION_CSV,
    dossier_reancrage,
    ecrire_plan_csv,
    pack_lcbft,
    plan_action,
)
from src.bench.readiness import comparer_au_rejeu, controles_integrite
from src.bench.relecture import relire
from src.bench.rulebook import RuleStatus
from src.bench.verification import REGISTRE_VERIFICATION, charger_registre

#: Règle dont la source est à réancrer et qui a son propre dossier. La liste est
#: explicite : un dossier nominatif ne se crée pas par inadvertance.
REANCRAGES_DOCUMENTES: tuple[str, ...] = ("AMF-R-005",)


def preparer_plan_action(
    racine: Path = RACINE_RULEBOOK,
    plan_chemin: Path = PLAN_ACTION,
    csv_chemin: Path = PLAN_ACTION_CSV,
    lcbft_chemin: Path = PACK_LCBFT,
    reancrage_chemin: Path = DOSSIER_REANCRAGE,
    registre: Path = REGISTRE_VERIFICATION,
    jour: dt.date | None = None,
) -> dict:
    """Écrit les quatre artefacts du plan. Ne modifie aucune règle."""
    jour = jour or dt.date.today()
    regles = charger_rulebook(racine)
    par_id = {r.id: r for r in regles}
    relecture = relire(regles)

    dossiers = preparer(
        regles, relecture.constats, relecture.etats, relecture.extraits, PRIORITES_ARBITREES
    )
    lignes = construire_lignes(dossiers, relecture.acces)
    groupes = lots_de_lecture(lignes) + clusters_de_decision(dossiers, lignes)
    etapes = ordre_execution(lignes, groupes)

    validated = sum(1 for r in regles if r.status is RuleStatus.VALIDATED)
    gold = sum(1 for e in relecture.etats.values() if e.gold_ready)
    family = sum(1 for e in relecture.etats.values() if e.family_ready)
    projection = projeter(lignes, relecture.constats, validated, gold, family)

    entrees = charger_registre(registre)
    anomalies = [
        str(a)
        for a in controles_integrite(regles, relecture.constats, relecture.etats, entrees)
    ]
    bloquants = elements_bloquants(lignes, anomalies, family)
    suivante = prochaine_action(etapes)

    Path(plan_chemin).parent.mkdir(parents=True, exist_ok=True)
    Path(plan_chemin).write_text(
        plan_action(
            lignes, groupes, etapes, projection, bloquants, suivante, relecture.empreinte, jour
        ),
        encoding="utf-8",
    )
    ecrire_plan_csv(lignes, Path(csv_chemin))
    Path(lcbft_chemin).write_text(
        pack_lcbft(lignes, par_id, relecture.obstacles, jour), encoding="utf-8"
    )

    reancrages = 0
    for rule_id in REANCRAGES_DOCUMENTES:
        ligne = next((x for x in lignes if x.rule_id == rule_id), None)
        if ligne is None or ligne.proposed_action is not ActionPrincipale.SOURCE_REANCHORING:
            continue
        Path(reancrage_chemin).write_text(
            dossier_reancrage(
                ligne,
                par_id[rule_id],
                relecture.obstacles.get(rule_id, ""),
                relecture.constats.get(rule_id),
                jour,
            ),
            encoding="utf-8",
        )
        reancrages += 1

    return {
        "regles": len(lignes),
        "par_action": {
            action.value: sum(1 for x in lignes if x.proposed_action is action)
            for action in ActionPrincipale
            if any(x.proposed_action is action for x in lignes)
        },
        "groupes": len(groupes),
        "etapes": len(etapes),
        "lcbft": sum(
            1
            for x in lignes
            if x.domain == "LCBFT" and x.proposed_action is ActionPrincipale.SOURCE_CONSULTATION
        ),
        "reancrages": reancrages,
        "bloquants": bloquants,
        "prochaine_action": suivante,
        "projection": projection,
        "empreinte": relecture.empreinte,
    }


if __name__ == "__main__":
    resultat = preparer_plan_action()
    print(f"{resultat['regles']} règle(s) au plan")
    for action, compte in resultat["par_action"].items():
        print(f"  {action:24s} {compte}")
    print(f"  regroupements : {resultat['groupes']} — étapes : {resultat['etapes']}")
    print(f"  LCB-FT à consulter : {resultat['lcbft']} — réancrages documentés : {resultat['reancrages']}")
    print(f"  PROCHAINE ACTION : {resultat['prochaine_action']}")
