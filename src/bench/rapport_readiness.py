"""Rapports d'exploitabilité : file de revue humaine et synthèse de readiness.

`RULEBOOK_READINESS_SUMMARY.md` s'adresse à la décision : il chiffre l'écart
entre une règle vérifiée et une règle exploitable, et rend une recommandation
déterminée par des seuils, pas par une appréciation.

Il ne produit pas la file de revue : celle-ci appartient au pack d'arbitrage
(`rapport_revue.py`), qui dispose des dispositions de soutien et des
regroupements. Un artefact, un auteur — deux modules qui écriraient le même
fichier finiraient par en donner deux versions.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from src.bench.completude import ConstatCompletude
from src.bench.readiness import (
    BlockerCategory,
    ConstatIntegrite,
    ConstatReadiness,
)
from src.bench.regles import Rule
from src.bench.rulebook import ExceptionsStatus, RuleStatus
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV

SYNTHESE_READINESS = Path("reports/RULEBOOK_READINESS_SUMMARY.md")
MATRICE_READINESS = Path("reports/RULEBOOK_FAMILY_READINESS.csv")

#: Colonnes imposées par la spécification §1.
COLONNES_READINESS = (
    "ID",
    "status",
    "gold_ready",
    "family_ready",
    "family_blocker",
    "blocker_category",
    "explanation",
)

#: Recommandations possibles. Une seule est rendue, par un calcul.
RECOMMANDATIONS = (
    "READY_FOR_FAMILY_GENERATION",
    "READY_AFTER_HUMAN_REVIEW",
    "NOT_READY",
)

#: Catégories de blocage regroupées comme la synthèse les demande.
GROUPES_BLOCAGES: dict[str, tuple[BlockerCategory, ...]] = {
    "exception": (BlockerCategory.EXCEPTION_UNRESOLVED,),
    "temporal": (BlockerCategory.TEMPORAL_UNRESOLVED,),
    "source": (BlockerCategory.SOURCE_INCOMPLETE,),
    "cross_reference": (BlockerCategory.CROSS_REFERENCE_UNRESOLVED,),
    "abstraction": (BlockerCategory.RULE_TOO_ABSTRACT,),
    "other": (
        BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED,
        BlockerCategory.SCHEMA_INCOMPLETE,
        BlockerCategory.HUMAN_REVIEW_REQUIRED,
        BlockerCategory.OTHER,
    ),
}


def _oui(valeur: bool) -> str:
    return "oui" if valeur else "non"


def recommandation(
    etats: list[ConstatReadiness], anomalies: list[ConstatIntegrite]
) -> tuple[str, str]:
    """Recommandation déterministe, et la règle qui l'a produite.

    Aucune appréciation : trois seuils, évalués dans l'ordre. Une anomalie
    d'intégrité prime sur tout — un Rulebook incohérent ne devient pas
    exploitable parce qu'il compte assez de règles prêtes.
    """
    prets = [e for e in etats if e.family_ready]
    bloquants = [e for e in etats if e.priorite_revue in ("P0", "P1")]

    if anomalies:
        return (
            "NOT_READY",
            f"{len(anomalies)} anomalie(s) d'intégrité : un Rulebook incohérent "
            f"n'est pas exploitable, quel que soit le nombre de règles prêtes",
        )
    if not prets:
        return (
            "NOT_READY",
            "aucune règle n'est family_ready : la génération n'aurait rien à ancrer",
        )
    if bloquants:
        return (
            "READY_AFTER_HUMAN_REVIEW",
            f"{len(prets)} règle(s) prêtes, mais {len(bloquants)} arbitrage(s) P0/P1 "
            f"en attente : générer maintenant figerait des familles sur des règles "
            f"dont la portée reste à trancher",
        )
    return (
        "READY_FOR_FAMILY_GENERATION",
        f"{len(prets)} règle(s) family_ready, aucune anomalie d'intégrité, aucun "
        f"arbitrage P0 ou P1 en attente",
    )


def ecrire_matrice_readiness(etats: list[ConstatReadiness], chemin: Path) -> None:
    """Matrice ID × seuils × blocage, une ligne par règle."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(
            flux, fieldnames=list(COLONNES_READINESS), delimiter=SEPARATEUR_CSV
        )
        graveur.writeheader()
        for etat in etats:
            graveur.writerow(
                {
                    "ID": etat.rule_id,
                    "status": etat.status.value,
                    "gold_ready": _oui(etat.gold_ready),
                    "family_ready": _oui(etat.family_ready),
                    "family_blocker": etat.family_blocker,
                    "blocker_category": etat.blocker_category,
                    "explanation": etat.explanation,
                }
            )


def _proposition(
    etat: ConstatReadiness, regle: Rule, constat: ConstatCompletude | None
) -> str:
    """Une proposition seulement quand elle est mécanique, jamais interprétative."""
    categorie = etat.blocage_principal.category if etat.blocage_principal else None
    if categorie is BlockerCategory.EXCEPTION_UNRESOLVED and constat and constat.exceptions_extraites:
        return (
            "incorporer telles quelles les phrases déjà recopiées du texte officiel, "
            "si elles limitent bien l'obligation que la règle énonce"
        )
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED and constat and constat.renvois:
        return (
            f"rattacher explicitement les articles {', '.join(constat.renvois[:5])} "
            f"à la règle, ou attester qu'ils ne conditionnent pas son application"
        )
    if categorie is BlockerCategory.RULE_TOO_ABSTRACT:
        return (
            "reformuler au plus près de la lettre de l'article, en rattachant chaque "
            "assertion à son paragraphe — ou découper la règle"
        )
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return (
            "consulter le texte hors de cet environnement, puis porter le constat au "
            "dossier de vérification"
        )
    return ""


def _impact(etat: ConstatReadiness, regle: Rule) -> str:
    """Ce que le blocage coûterait s'il n'était pas levé avant la rédaction."""
    categorie = etat.blocage_principal.category if etat.blocage_principal else None
    if categorie is BlockerCategory.EXCEPTION_UNRESOLVED:
        return (
            "les items construits sur cette règle la testeraient comme un absolu : "
            "un modèle qui mentionnerait une dérogation réelle serait compté en erreur"
        )
    if categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED:
        return (
            "une fausse prémisse fondée sur cette absence affirmerait que le texte "
            "ne prévoit rien, sans que rien ne l'atteste"
        )
    if categorie is BlockerCategory.TEMPORAL_UNRESOLVED:
        return (
            "la date d'appréciation des items serait arbitraire, et une réponse "
            "correcte sous une version le serait à tort sous l'autre"
        )
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED:
        return (
            "une réponse de référence pourrait omettre une condition posée par un "
            "article que la règle ne porte pas"
        )
    if categorie is BlockerCategory.RULE_TOO_ABSTRACT:
        return (
            "la rédaction devrait interpréter le droit pour écrire le gold, là où "
            "cette interprétation ne serait plus contrôlée"
        )
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return "aucun item ne pourrait citer sa source, ni être opposé à un audit"
    if categorie is BlockerCategory.SCHEMA_INCOMPLETE:
        return (
            "aucun angle de question ne se déduit de la règle : elle serait exacte "
            "et stérile"
        )
    return "la règle ne peut pas ancrer de famille tant que le point n'est pas tranché"


def synthese(
    etats: list[ConstatReadiness],
    regles: list[Rule],
    anomalies: list[ConstatIntegrite],
    tests_integrite: tuple[int, int],
) -> str:
    """`reports/RULEBOOK_READINESS_SUMMARY.md`, dans la forme demandée."""
    statuts = Counter(r.status.value for r in regles)
    par_priorite = Counter(e.priorite_revue for e in etats if e.demande_arbitrage)
    blocages = Counter()
    for etat in etats:
        principal = etat.blocage_principal
        if principal is None:
            continue
        for groupe, categories in GROUPES_BLOCAGES.items():
            if principal.category in categories:
                blocages[groupe] += 1
                break

    verdict, motif = recommandation(etats, anomalies)
    passes, echoues = tests_integrite

    lignes = [
        "# Rulebook — synthèse d'exploitabilité",
        "",
        "```",
        "Rulebook",
        f"  {len(regles)} total",
        "",
        "Status",
        f"  validated:      {statuts.get('validated', 0)}",
        f"  source_checked: {statuts.get('source_checked', 0)}",
        f"  draft:          {statuts.get('draft', 0)}",
        "",
        "Readiness",
        f"  gold_ready:     {sum(1 for e in etats if e.gold_ready)}",
        f"  family_ready:   {sum(1 for e in etats if e.family_ready)}",
        "",
        "Blockers",
        f"  exception:       {blocages.get('exception', 0)}",
        f"  temporal:        {blocages.get('temporal', 0)}",
        f"  source:          {blocages.get('source', 0)}",
        f"  cross_reference: {blocages.get('cross_reference', 0)}",
        f"  abstraction:     {blocages.get('abstraction', 0)}",
        f"  other:           {blocages.get('other', 0)}",
        "",
        "Human review",
        f"  P0: {par_priorite.get('P0', 0)}",
        f"  P1: {par_priorite.get('P1', 0)}",
        f"  P2: {par_priorite.get('P2', 0)}",
        f"  P3: {par_priorite.get('P3', 0)}",
        "",
        "Critical integrity tests",
        f"  passed: {passes}",
        f"  failed: {echoues}",
        "",
        "Recommendation",
        f"  {verdict}",
        "```",
        "",
        f"**{verdict}** — {motif}.",
        "",
        "## Les trois seuils, et pourquoi ils diffèrent",
        "",
        "| Seuil | Ce qu'il affirme | Ce qu'il exige en plus |",
        "|---|---|---|",
        "| `validated` | la règle est juridiquement établie | les huit critères de "
        "validation |",
        "| `gold_ready` | on peut en tirer une réponse de référence sans "
        "réinterpréter le droit | portance de l'énoncé **et** prérequis probatoires |",
        "| `family_ready` | elle peut ancrer une famille de questions | statut "
        "`validated` **et** de quoi construire des angles |",
        "",
        "## Correction apportée à `gold_ready`",
        "",
        "`gold_ready` était calculé sur la seule précision de l'énoncé. Le chiffre",
        "le trahissait : quarante et une règles étaient dites prêtes, dont treize",
        "dont la source n'était pas vérifiée. Un énoncé porteur adossé à une source",
        "non consultée ne donne pas un gold prêt, il donne un gold qui a l'air prêt.",
        "",
        "`gold_ready` exige désormais, en plus de la portance : source primaire",
        "vérifiée, article retrouvé, recherche d'exceptions aboutie, temporalité",
        "établie, renvois vérifiés, affirmations négatives résolues. **La logique a",
        "été corrigée, pas le rapport.**",
        "",
        "## Blocages, par catégorie normalisée",
        "",
        "| Catégorie | Règles | Ce qu'elle recouvre |",
        "|---|---:|---|",
    ]

    descriptions = {
        BlockerCategory.SOURCE_INCOMPLETE: "source non consultée, ou article non retrouvé",
        BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED: "une absence affirmée sans être attestée",
        BlockerCategory.EXCEPTION_UNRESOLVED: "dérogations non tranchées",
        BlockerCategory.TEMPORAL_UNRESOLVED: "version applicable non établie",
        BlockerCategory.CROSS_REFERENCE_UNRESOLVED: "renvois non résolus",
        BlockerCategory.RULE_TOO_ABSTRACT: "énoncé qui décrit le texte au lieu de le dire",
        BlockerCategory.SCHEMA_INCOMPLETE: "rien à quoi accrocher un angle de question",
        BlockerCategory.HUMAN_REVIEW_REQUIRED: "une décision humaine reste à porter",
        BlockerCategory.OTHER: "hors des catégories ci-dessus",
    }
    detail = Counter(
        e.blocage_principal.category for e in etats if e.blocage_principal is not None
    )
    for categorie in BlockerCategory:
        lignes.append(
            f"| `{categorie.value}` | {detail.get(categorie, 0)} | "
            f"{descriptions[categorie]} |"
        )

    ecart = [e for e in etats if e.gold_ready and not e.family_ready]
    lignes += [
        "",
        f"## `gold_ready` sans `family_ready` ({len(ecart)})",
        "",
    ]
    if ecart:
        lignes += ["| ID | Blocage | Catégorie | Explication |", "|---|---|---|---|"]
        for etat in ecart:
            lignes.append(
                f"| `{etat.rule_id}` | `{etat.family_blocker}` | "
                f"`{etat.blocker_category}` | {etat.explanation[:130]} |"
            )
    else:
        lignes.append(
            "Aucune : toute règle prête pour un gold l'est aussi pour une famille. "
            "L'écart observé auparavant venait du calcul de `gold_ready`, corrigé "
            "depuis."
        )

    lignes += ["", "## Anomalies d'intégrité", ""]
    if anomalies:
        lignes += ["| Contrôle | Règle | Message |", "|---|---|---|"]
        for anomalie in anomalies:
            lignes.append(
                f"| `{anomalie.controle}` | `{anomalie.rule_id}` | {anomalie.message} |"
            )
    else:
        lignes.append("Aucune.")
    lignes.append("")

    return "\n".join(lignes) + "\n"
