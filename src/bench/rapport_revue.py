"""Pack de revue : la file P0/P1, le bordereau de décision, l'avancement.

Trois artefacts, et une règle qui les gouverne tous : **rien n'est jamais
pré-rempli à la place du relecteur**. Le bordereau `dossier-revue-p0p1.csv`
porte les colonnes `reviewer_decision`, `reviewer_name`, `review_date`,
`review_notes` et `source_scope` — toutes vides. Le schéma refuse ensuite une
décision d'absence d'exception qui n'attesterait pas le périmètre examiné.

Le regroupement (`review_cluster_id`) est le seul raccourci offert : quand la
même disposition commande le sort de plusieurs règles, le relecteur tranche une
fois. Les règles restent distinctes dans le Rulebook — c'est l'arbitrage qui est
mutualisé, jamais la règle.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from src.bench.dossier_revue import DecisionRevue, DossierRevue
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV

FILE_REVUE = Path("reports/HUMAN_REVIEW_QUEUE.md")
AVANCEMENT_REVUE = Path("reports/HUMAN_REVIEW_PROGRESS.md")
BORDEREAU_REVUE = Path("data/verification/dossier-revue-p0p1.csv")

#: Colonnes du bordereau. Les cinq dernières sont celles du relecteur, et elles
#: sortent vides : c'est tout l'objet de cette phase.
COLONNES_BORDEREAU = (
    "rule_id",
    "priorite",
    "domaine",
    "review_cluster_id",
    "statut_actuel",
    "version_actuelle",
    "blocage",
    "mechanical_proposal",
    "neutral_legal_question",
    "dispositions_a_examiner",
    "source_scope_demande",
    "reviewer_decision",
    "reviewer_name",
    "review_date",
    "review_notes",
    "source_scope",
    "enonce_reformule",
    "exceptions_constatees",
)


def ecrire_bordereau(dossiers: list[DossierRevue], chemin: Path) -> Path:
    """Le bordereau que le relecteur remplit. Aucune décision pré-remplie."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    ordre = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tries = sorted(
        dossiers, key=lambda d: (ordre.get(d.priorite, 9), d.review_cluster_id, d.rule_id)
    )
    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(
            flux, fieldnames=list(COLONNES_BORDEREAU), delimiter=SEPARATEUR_CSV
        )
        graveur.writeheader()
        for dossier in tries:
            graveur.writerow(
                {
                    "rule_id": dossier.rule_id,
                    "priorite": dossier.priorite,
                    "domaine": dossier.domain,
                    "review_cluster_id": dossier.review_cluster_id,
                    "statut_actuel": dossier.status,
                    "version_actuelle": dossier.version,
                    "blocage": dossier.blocker_category,
                    "mechanical_proposal": dossier.mechanical_proposal.value,
                    "neutral_legal_question": dossier.neutral_legal_question,
                    "dispositions_a_examiner": " | ".join(
                        d.article for d in dossier.dispositions
                    ),
                    "source_scope_demande": dossier.source_scope,
                    # Les colonnes du relecteur restent vides, par construction.
                    "reviewer_decision": "",
                    "reviewer_name": "",
                    "review_date": "",
                    "review_notes": "",
                    "source_scope": "",
                    "enonce_reformule": "",
                    "exceptions_constatees": "",
                }
            )
    return chemin


def _fiche(dossier: DossierRevue) -> list[str]:
    """Un dossier, dans la forme demandée par la spécification §3."""
    lignes = [
        f"### `{dossier.rule_id}` — {dossier.domain} · {dossier.priorite} · "
        f"cluster `{dossier.review_cluster_id}`",
        "",
        "**RULE**",
        "",
        f"- ID : `{dossier.rule_id}`",
        f"- Domain : {dossier.domain}",
        f"- Version : v{dossier.version}",
        f"- Current status : `{dossier.status}`",
        "",
        "**CURRENT STATEMENT**",
        "",
        f"> {dossier.statement}",
        "",
        "**PRIMARY SOURCE**",
        "",
        f"- Texte : {dossier.source_text}",
        f"- Article : {dossier.source_article}",
        f"- Paragraphe : {dossier.source_paragraph or '—'}",
        f"- Version consultée : {dossier.source_version_date}",
        f"- Date applicable : {dossier.applicable_from}",
        f"- URL : {dossier.source_url}",
        "",
        "**SUPPORTING PROVISION**",
        "",
    ]
    if dossier.dispositions:
        for disposition in dossier.dispositions:
            lignes += [
                f"- **{disposition.article}**",
                f"  - Pourquoi elle est potentiellement pertinente : {disposition.motif}",
                f"  - Relation avec la règle : {disposition.relation}",
                f"  - Extrait : « {disposition.extrait} »",
            ]
    else:
        lignes.append(
            "- Aucune disposition limitante de cet acte ne cite l'article de la règle "
            "ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le "
            "périmètre à examiner reste l'acte complet."
        )
    lignes += [
        "",
        "**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté",
        "",
    ]
    lignes += [f"- {fait}" for fait in dossier.textual_facts]
    lignes += [
        "",
        "**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain",
        "",
        f"- {dossier.interpretive_question}",
        "",
        "**NEUTRAL_LEGAL_QUESTION**",
        "",
        f"> {dossier.neutral_legal_question}",
        "",
        f"**mechanical_proposal** : `{dossier.mechanical_proposal.value}` — proposition "
        f"de recherche, jamais une conclusion juridique.",
        "",
        "**IMPACT SUR LE BENCHMARK**",
        "",
        f"- `if_exception_exists` : {dossier.if_exception_exists}",
        f"- `if_no_exception` : {dossier.if_no_exception}",
        "",
        "**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)",
        "",
        f"> {dossier.source_scope}",
        "",
        "**DÉCISION DU RELECTEUR** — à remplir dans "
        "`data/verification/dossier-revue-p0p1.csv`",
        "",
        "| champ | valeur |",
        "|---|---|",
        "| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · "
        "`RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |",
        "| `reviewer_name` | |",
        "| `review_date` | |",
        "| `review_notes` | |",
        "| `source_scope` | |",
        "",
        "---",
        "",
    ]
    return lignes


def file_de_revue(dossiers: list[DossierRevue]) -> str:
    """`reports/HUMAN_REVIEW_QUEUE.md` — P0 d'abord, par domaine puis identifiant."""
    par_priorite: dict[str, list[DossierRevue]] = defaultdict(list)
    for dossier in dossiers:
        par_priorite[dossier.priorite].append(dossier)

    clusters = defaultdict(list)
    for dossier in dossiers:
        clusters[dossier.review_cluster_id].append(dossier.rule_id)
    partages = {c: r for c, r in clusters.items() if len(r) > 1}

    lignes = [
        "# Rulebook — file de revue humaine (P0 / P1)",
        "",
        "Chaque dossier dit **quelle disposition examiner**, **quelle exception est",
        "suspectée**, **quelle formulation est concernée** et **quelle décision est",
        "attendue**. Le relecteur n'a rien à deviner.",
        "",
        "**Ce document ne donne aucun conseil juridique.** Il sépare strictement ce",
        "qui est écrit dans le texte (`TEXTUAL_FACTS`) de ce qui demande un arbitrage",
        "(`INTERPRETIVE_QUESTION`). La `mechanical_proposal` dit ce que la recherche",
        "automatique a trouvé, dans son propre vocabulaire — `EXCEPTION_LIKELY`",
        "signifie « une disposition limitante cite cet article », pas « il existe une",
        "exception ».",
        "",
        "## Ce qui est demandé",
        "",
        f"- dossiers P0 : **{len(par_priorite.get('P0', []))}**",
        f"- dossiers P1 : **{len(par_priorite.get('P1', []))}**",
        f"- arbitrages distincts après regroupement : **{len(clusters)}**",
        f"- groupes couvrant plusieurs règles : **{len(partages)}**",
        "",
        "Une décision d'absence d'exception (`NONE_IDENTIFIED`) n'est acceptée que si",
        "le champ `source_scope` atteste le périmètre réellement examiné. Le schéma",
        "la refuse sinon : « je n'ai pas trouvé » n'est pas « cela n'existe pas ».",
        "",
    ]

    if partages:
        lignes += [
            "## Arbitrages mutualisés",
            "",
            "Ces règles dépendent de la même disposition : une seule décision les",
            "couvre toutes. Les règles ne sont pas fusionnées pour autant — seul le",
            "dossier l'est.",
            "",
            "| Cluster | Règles | Nombre |",
            "|---|---|---:|",
        ]
        for cluster, regles in sorted(partages.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            lignes.append(
                f"| `{cluster}` | {', '.join(f'`{r}`' for r in sorted(regles))} | "
                f"{len(regles)} |"
            )
        lignes.append("")

    for priorite in ("P0", "P1"):
        concernes = par_priorite.get(priorite, [])
        if not concernes:
            continue
        lignes += [
            f"## {priorite} — REVIEW REQUIRED ({len(concernes)} règles)",
            "",
        ]
        par_domaine: dict[str, list[DossierRevue]] = defaultdict(list)
        for dossier in concernes:
            par_domaine[dossier.domain].append(dossier)
        for domaine in sorted(par_domaine):
            lignes += [f"### Domaine {domaine}", ""]
            for dossier in sorted(par_domaine[domaine], key=lambda d: d.rule_id):
                lignes.extend(_fiche(dossier))

    return "\n".join(lignes) + "\n"


def avancement(
    dossiers: list[DossierRevue],
    decisions: dict[str, str],
    avant: dict[str, int],
    apres: dict[str, int],
) -> str:
    """`reports/HUMAN_REVIEW_PROGRESS.md` — ce qui est tranché, ce qui reste."""
    par_priorite = Counter(d.priorite for d in dossiers)
    traites = Counter(
        d.priorite for d in dossiers if decisions.get(d.rule_id)
    )

    lignes = [
        "# Rulebook — avancement de la revue humaine",
        "",
        "```",
        f"P0 total     : {par_priorite.get('P0', 0)}",
        f"P0 reviewed  : {traites.get('P0', 0)}",
        f"P0 remaining : {par_priorite.get('P0', 0) - traites.get('P0', 0)}",
        "",
        f"P1 total     : {par_priorite.get('P1', 0)}",
        f"P1 reviewed  : {traites.get('P1', 0)}",
        f"P1 remaining : {par_priorite.get('P1', 0) - traites.get('P1', 0)}",
        "```",
        "",
        "## Effet sur l'exploitabilité",
        "",
        "| | avant | après |",
        "|---|---:|---:|",
        f"| `validated` | {avant.get('validated', 0)} | {apres.get('validated', 0)} |",
        f"| `gold_ready` | {avant.get('gold_ready', 0)} | {apres.get('gold_ready', 0)} |",
        f"| `family_ready` | {avant.get('family_ready', 0)} | {apres.get('family_ready', 0)} |",
        "",
    ]
    if not any(decisions.values()):
        lignes += [
            "Aucune décision n'a encore été portée : le bordereau",
            "`data/verification/dossier-revue-p0p1.csv` sort avec ses colonnes de",
            "décision vides, comme prévu. Les colonnes « après » reproduisent donc",
            "l'état actuel.",
            "",
        ]
    lignes += [
        "## Après chaque décision appliquée",
        "",
        "L'application d'un bordereau rejoue toute la chaîne, dans cet ordre :",
        "",
        "1. la règle est revalidée par le schéma ;",
        "2. la gold-readiness est recalculée, jamais héritée de la décision ;",
        "3. la family-readiness est recalculée ;",
        "4. les contrôles d'intégrité sont réexécutés ;",
        "5. le registre append-only enregistre la décision, sans écraser la précédente.",
        "",
        "Une décision humaine ne vaut donc jamais `gold_ready` par elle-même : elle",
        "lève un blocage, et le calcul dit ensuite ce que la règle est devenue.",
        "",
    ]
    return "\n".join(lignes) + "\n"


def lire_bordereau(chemin: Path) -> dict[str, dict[str, str]]:
    """Relit les décisions portées au bordereau, sans rien interpréter."""
    chemin = Path(chemin)
    if not chemin.is_file():
        return {}
    with chemin.open(encoding=ENCODAGE_CSV, newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=SEPARATEUR_CSV))
    return {
        ligne["rule_id"]: ligne
        for ligne in lignes
        if (ligne.get("reviewer_decision") or "").strip()
    }


#: Décision du relecteur → constat de vérification. Le pont entre deux
#: vocabulaires : celui de l'arbitrage et celui du registre.
CORRESPONDANCE_DECISIONS: dict[DecisionRevue, tuple[str, str | None]] = {
    DecisionRevue.NONE_IDENTIFIED: ("confirme", "none_identified"),
    DecisionRevue.IDENTIFIED_AND_INCORPORATED: (
        "confirme",
        "identified_and_incorporated",
    ),
    DecisionRevue.RULE_REFORMULATED: ("corrige", None),
    DecisionRevue.REQUIRES_FURTHER_REVIEW: ("non_verifiable", None),
}
