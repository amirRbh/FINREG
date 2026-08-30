"""Les trois artefacts d'un pack d'arbitrage, et la relecture des décisions rendues.

| Artefact | Lecteur | Ce qu'il porte |
|---|---|---|
| `HUMAN_REVIEW_P0_P1.md` | le juriste | un dossier par règle, P0 puis P1, par domaine |
| `dossier-adjudication.csv` | le juriste | les mêmes règles, une ligne à remplir |
| `HUMAN_REVIEW_PROGRESS.md` | la décision | ce qui est tranché, ce qui reste, et l'effet |

Le dossier CSV sort avec ses colonnes de décision **vides**, et le rapport de
progression compte les décisions en relisant ce fichier : tant que personne n'a
rempli une ligne, il affiche zéro. Aucune de ces trois sorties ne peut donc
faire croire qu'un arbitrage a eu lieu.

Le rapport de progression n'annonce jamais d'état « après » : les seuils se
recalculent en rejouant l'audit sur le Rulebook corrigé, pas en projetant ce
qu'une décision produirait. Écrire un « après » prévisionnel reviendrait à
promettre un `gold_ready` que la spécification §14 interdit d'accorder
automatiquement.
"""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter
from pathlib import Path

from src.bench.adjudication import (
    DecisionAdjudication,
    Dossier,
    PRIORITES_ARBITREES,
    regroupements,
)
from src.bench.readiness import BlockerCategory, ConstatReadiness
from src.bench.regles import Rule
from src.bench.rulebook import RuleStatus
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV, SEPARATEUR_LISTE

PACK_ADJUDICATION = Path("reports/HUMAN_REVIEW_P0_P1.md")
PROGRESSION = Path("reports/HUMAN_REVIEW_PROGRESS.md")
DOSSIER_ADJUDICATION = Path("data/verification/dossier-adjudication.csv")

#: Ce que le dossier donne au relecteur — jamais rempli par lui.
COLONNES_CONTEXTE: tuple[str, ...] = (
    "rule_id",
    "review_cluster_id",
    "priorite",
    "domaine",
    "statut",
    "blocage",
    "mechanical_proposal",
    "neutral_legal_question",
    "perimetre_a_examiner",
)
#: Ce que le relecteur rend — jamais rempli par le générateur.
COLONNES_A_REMPLIR: tuple[str, ...] = (
    "reviewer_decision",
    "reviewer_name",
    "review_date",
    "source_scope",
    "exceptions_constatees",
    "enonce_reformule",
    "review_notes",
)
COLONNES = COLONNES_CONTEXTE + COLONNES_A_REMPLIR

#: Longueur des extraits recopiés dans le pack. Au-delà, la fiche cesse d'être
#: lisible ; l'URL de la source y figure toujours pour aller au texte entier.
LONGUEUR_EXTRAIT = 900


# --------------------------------------------------------------------------- #
# Dossier à remplir
# --------------------------------------------------------------------------- #


def ecrire_dossier(dossiers: list[Dossier], chemin: Path) -> None:
    """Une ligne par règle, colonnes de décision vides.

    Le générateur n'écrit rien dans `COLONNES_A_REMPLIR` : c'est ce qui empêche
    un arbitrage de naître d'une valeur par défaut.
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(flux, fieldnames=list(COLONNES), delimiter=SEPARATEUR_CSV)
        graveur.writeheader()
        for dossier in dossiers:
            ligne = {colonne: "" for colonne in COLONNES}
            ligne.update(
                {
                    "rule_id": dossier.rule_id,
                    "review_cluster_id": dossier.review_cluster_id,
                    "priorite": dossier.priorite_revue,
                    "domaine": dossier.domain,
                    "statut": dossier.current_status,
                    "blocage": dossier.blocage_categorie.value,
                    "mechanical_proposal": dossier.mechanical_proposal.value,
                    "neutral_legal_question": dossier.neutral_legal_question,
                    "perimetre_a_examiner": dossier.perimetre_a_examiner,
                }
            )
            graveur.writerow(ligne)


def lire_decisions(chemin: Path) -> list[DecisionAdjudication]:
    """Relit les décisions rendues. Lecture tout ou rien, comme la vérification.

    Une ligne dont la décision est vide n'est pas une décision : elle est
    ignorée. Une ligne remplie mais irrecevable arrête la lecture — un dossier
    à moitié valide appliqué à moitié laisserait le Rulebook dans un état que
    personne n'a arbitré.
    """
    chemin = Path(chemin)
    if not chemin.exists():
        return []
    decisions: list[DecisionAdjudication] = []
    erreurs: list[str] = []
    with chemin.open("r", encoding=ENCODAGE_CSV, newline="") as flux:
        for ligne in csv.DictReader(flux, delimiter=SEPARATEUR_CSV):
            if not (ligne.get("reviewer_decision") or "").strip():
                continue
            brut = {
                "rule_id": (ligne.get("rule_id") or "").strip(),
                "reviewer_decision": ligne["reviewer_decision"].strip(),
                "reviewer_name": (ligne.get("reviewer_name") or "").strip(),
                "review_date": (ligne.get("review_date") or "").strip() or None,
                "review_notes": (ligne.get("review_notes") or "").strip(),
                "source_scope": (ligne.get("source_scope") or "").strip(),
                "exceptions_constatees": [
                    e.strip()
                    for e in (ligne.get("exceptions_constatees") or "").split(SEPARATEUR_LISTE)
                    if e.strip()
                ],
                "enonce_reformule": (ligne.get("enonce_reformule") or "").strip(),
            }
            try:
                decisions.append(DecisionAdjudication.model_validate(brut))
            except Exception as exc:
                erreurs.append(f"{brut['rule_id'] or '(sans identifiant)'} : {exc}")
    if erreurs:
        raise ValueError(
            "dossier d'arbitrage irrecevable, rien n'est retenu :\n  " + "\n  ".join(erreurs)
        )
    return decisions


# --------------------------------------------------------------------------- #
# Pack de revue
# --------------------------------------------------------------------------- #


def _fiche(dossier: Dossier) -> list[str]:
    """Un dossier rendu en Markdown, dans l'ordre où il se lit."""
    lignes = [
        f"#### `{dossier.rule_id}` — {dossier.domain} · {dossier.priorite_revue} · "
        f"`review_cluster_id` : `{dossier.review_cluster_id}`",
        "",
        "**RULE**",
        "",
        f"- ID : `{dossier.rule_id}`",
        f"- Domaine : {dossier.domain}",
        f"- Version : v{dossier.version}",
        f"- Statut courant : `{dossier.current_status}`",
        f"- Blocage : `{dossier.blocage_categorie.value}` ({dossier.blocage})",
        "",
        "**CURRENT STATEMENT**",
        "",
        f"> {dossier.current_statement}",
        "",
        "**PRIMARY SOURCE**",
        "",
        f"- Texte : {dossier.source_texte}",
        f"- Article : {dossier.source_article or '—'}",
        f"- Paragraphe : {dossier.source_paragraphe or '—'}",
        f"- Version du texte déclarée : {dossier.source_version}",
        f"- Date d'application de la règle : {dossier.source_date_applicable}",
        f"- URL : {dossier.source_url or '—'}",
        "",
    ]
    if dossier.extrait_officiel:
        lignes += [
            "**Extrait officiel**",
            "",
            f"> {dossier.extrait_officiel[:LONGUEUR_EXTRAIT]}",
            "",
        ]
    lignes += ["**SUPPORTING PROVISION**", ""]
    for disposition in dossier.dispositions:
        lignes += [
            f"- **{disposition.reference}**",
            f"  - Pourquoi elle est potentiellement pertinente : {disposition.pertinence}",
            f"  - Relation avec la règle : {disposition.relation}",
        ]
    lignes += [
        "",
        f"**Périmètre à examiner** — {dossier.perimetre_a_examiner}",
        "",
        "**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources",
        "",
    ]
    lignes += [f"- {fait}" for fait in dossier.textual_facts]
    lignes += [
        "",
        "**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain",
        "",
        f"{dossier.interpretive_question}",
        "",
        "**NEUTRAL_LEGAL_QUESTION**",
        "",
        f"> {dossier.neutral_legal_question}",
        "",
        f"**mechanical_proposal** — `{dossier.mechanical_proposal.value}` "
        f"(aide à la lecture, jamais une conclusion juridique)",
        "",
    ]
    if dossier.blocages_restants:
        lignes += [
            "**Autres blocages de la règle** — trancher celui-ci ne les lève pas",
            "",
        ]
        lignes += [f"- {blocage}" for blocage in dossier.blocages_restants]
        lignes += [""]
    lignes += [
        "**IMPACT SUR LE BENCHMARK**",
        "",
        f"- `if_exception_exists` — {dossier.if_exception_exists}",
        f"- `if_no_exception` — {dossier.if_no_exception}",
        "",
        "**DÉCISION DU RELECTEUR** — à remplir dans "
        "`data/verification/dossier-adjudication.csv`",
        "",
        "| Champ | Valeur |",
        "|---|---|",
        "| `reviewer_decision` | |",
        "| `reviewer_name` | |",
        "| `review_date` | |",
        "| `source_scope` | |",
        "| `review_notes` | |",
        "",
        "---",
        "",
    ]
    return lignes


def _index(dossiers: list[Dossier]) -> list[str]:
    """Table de navigation : de quoi retrouver un dossier, pas de quoi le trancher."""
    lignes = [
        "| ID | Domaine | Ancrage | Blocage | Proposition mécanique | Regroupement |",
        "|---|---|---|---|---|---|",
    ]
    for dossier in dossiers:
        lignes.append(
            f"| `{dossier.rule_id}` | {dossier.domain} | {dossier.source_article or '—'} | "
            f"`{dossier.blocage_categorie.value}` | `{dossier.mechanical_proposal.value}` | "
            f"`{dossier.review_cluster_id}` |"
        )
    lignes.append("")
    return lignes


def _section_priorite(priorite: str, dossiers: list[Dossier], intitule: str) -> list[str]:
    """Une priorité, classée par domaine puis par ID."""
    concernes = [d for d in dossiers if d.priorite_revue == priorite]
    if not concernes:
        return []
    lignes = [f"## {priorite} — {intitule} ({len(concernes)} règles)", ""]
    lignes += _index(concernes)
    for domaine in sorted({d.domain for d in concernes}):
        du_domaine = [d for d in concernes if d.domain == domaine]
        lignes += [f"### {domaine} — {len(du_domaine)} règle(s)", ""]
        for dossier in du_domaine:
            lignes += _fiche(dossier)
    return lignes


def pack(dossiers: list[Dossier], empreinte: str, artefacts: tuple[str, ...], jour: dt.date) -> str:
    """`reports/HUMAN_REVIEW_P0_P1.md` — les P0, puis les P1."""
    par_priorite = Counter(d.priorite_revue for d in dossiers)
    clusters = regroupements(dossiers)

    lignes = [
        "# Arbitrage humain — pack P0 / P1",
        "",
        "Ce document ne génère aucune question, aucune famille, aucun item : il",
        "prépare des décisions. Chaque dossier nomme la disposition à examiner, le",
        "périmètre qui rend une absence opposable, la question binaire à trancher, et",
        "ce que chaque issue changerait.",
        "",
        "**Il ne donne aucun conseil juridique.** `TEXTUAL_FACTS` ne porte que ce qui",
        "est écrit dans les sources ; `INTERPRETIVE_QUESTION` porte ce qui demande un",
        "arbitrage. `mechanical_proposal` dit ce que l'automate a vu — jamais ce que",
        "le droit dit.",
        "",
        f"**État relu** — audit du Rulebook publié, empreinte `{empreinte}`. "
        f"Préparé le {jour.isoformat()}.",
        "",
        "Artefacts relus :",
        "",
    ]
    lignes += [f"- `{a}`" for a in artefacts]
    lignes += [
        "",
        "## Ce qu'il y a à trancher",
        "",
        "| Priorité | Ce qu'elle signifie | Règles |",
        "|---|---|---:|",
        f"| **P0** | une erreur ici serait dangereuse pour un professionnel | "
        f"{par_priorite.get('P0', 0)} |",
        f"| **P1** | affecte la validité du benchmark | {par_priorite.get('P1', 0)} |",
        "",
        f"Total : **{len(dossiers)}** dossiers, regroupés en "
        f"**{len({d.review_cluster_id for d in dossiers})}** questions distinctes.",
        "",
        "P2 et P3 ne figurent pas ici : on arbitre dans l'ordre de la gravité.",
        "",
    ]
    lignes += _section_regroupements(clusters)
    lignes += _section_lots(dossiers)
    lignes += _section_priorite("P0", dossiers, "REVIEW REQUIRED")
    lignes += _section_priorite("P1", dossiers, "REVIEW REQUIRED")
    lignes += _section_tracabilite()
    return "\n".join(lignes) + "\n"


def _section_regroupements(clusters: dict[str, list[Dossier]]) -> list[str]:
    """Les questions qui se posent plusieurs fois, pour ne les trancher qu'une."""
    if not clusters:
        return []
    lignes = [
        f"## Regroupements — {len(clusters)} questions partagées",
        "",
        "Plusieurs règles peuvent dépendre de la même disposition et poser la même",
        "question. Une décision unique peut alors couvrir tout le groupe.",
        "",
        "**Le regroupement ne fusionne rien.** Les règles restent distinctes dans le",
        "Rulebook, et chacune garde sa décision, son énoncé et sa version : un article",
        "porte couramment plusieurs obligations, et les confondre en effacerait une.",
        "",
        "| Regroupement | Règles | Question partagée |",
        "|---|---|---|",
    ]
    for cluster, groupe in clusters.items():
        ids = ", ".join(f"`{d.rule_id}`" for d in groupe)
        lignes.append(f"| `{cluster}` | {ids} | {groupe[0].neutral_legal_question} |")
    lignes.append("")
    return lignes


def _section_lots(dossiers: list[Dossier]) -> list[str]:
    """Les règles bloquées sur la même source inaccessible.

    Ce n'est **pas** un regroupement de questions : chacune porte sur son propre
    article et garde sa décision. C'est un lot de consultation — une seule
    sortie hors de cet environnement couvre les douze, et le dire évite douze
    déplacements pour un seul texte.
    """
    par_source: dict[str, list[Dossier]] = {}
    for dossier in dossiers:
        if dossier.blocage_categorie is BlockerCategory.SOURCE_INCOMPLETE:
            par_source.setdefault(dossier.source_texte, []).append(dossier)
    lots = {source: groupe for source, groupe in sorted(par_source.items()) if len(groupe) > 1}
    if not lots:
        return []

    lignes = [
        f"## Lots de consultation — {len(lots)} source"
        + ("s" if len(lots) > 1 else "")
        + " hors d'atteinte",
        "",
        "Ces règles ne posent pas la même question : elles butent sur le même",
        "empêchement. Le texte primaire n'est pas atteignable depuis l'environnement",
        "d'exécution, et chacune attend la lecture de **son** article. Une seule",
        "consultation de la source couvre tout le lot ; les décisions restent",
        "individuelles.",
        "",
        "| Source | Règles | Articles à lire |",
        "|---|---|---|",
    ]
    for source, groupe in lots.items():
        ids = ", ".join(f"`{d.rule_id}`" for d in groupe)
        articles = ", ".join(sorted({d.source_article for d in groupe if d.source_article}))
        lignes.append(f"| {source} | {ids} | {articles} |")
    lignes.append("")
    return lignes


def _section_tracabilite() -> list[str]:
    """Ce qu'une décision devient, et ce qu'elle déclenche."""
    return [
        "## Traçabilité",
        "",
        "Une décision rendue s'enregistre au registre append-only",
        "`data/verification/rulebook-ledger.json`, qui se rejoue dans l'ordre. Une",
        "décision n'écrase jamais la précédente : elle s'y ajoute.",
        "",
        "| Champ du registre | Provenance |",
        "|---|---|",
        "| `rule_id` | le dossier |",
        "| `previous_status`, `previous_version` | l'état du Rulebook au moment de la décision |",
        "| `decision` | `reviewer_decision` |",
        "| `new_version` | avancée seulement si l'énoncé ou les exceptions changent |",
        "| `reviewer`, `review_date` | `reviewer_name`, `review_date` |",
        "| `review_notes` | `review_notes` |",
        "| `source_scope` | `source_scope` — obligatoire pour `NONE_IDENTIFIED` |",
        "",
        "### Après chaque décision appliquée",
        "",
        "Une décision humaine ne rend pas une règle exploitable. Elle lève un",
        "blocage ; les seuils se recalculent, ils ne se déduisent pas :",
        "",
        "1. revalider la règle (`finreg-bench rulebook qc`) ;",
        "2. recalculer la gold-readiness (`rulebook completude`) ;",
        "3. recalculer la family-readiness (`rulebook readiness`) ;",
        "4. rejouer les contrôles d'intégrité, registre compris ;",
        "5. n'écrire au registre qu'ensuite.",
        "",
        "Une règle ne passe `validated` qu'après décision humaine, et seulement si",
        "`exception_status` vaut `NONE_IDENTIFIED` — périmètre attesté — ou",
        "`IDENTIFIED_AND_INCORPORATED` — exceptions recopiées. Un `gold_ready` ne",
        "s'accorde jamais par le fait qu'une décision a été rendue.",
        "",
    ]


# --------------------------------------------------------------------------- #
# Progression
# --------------------------------------------------------------------------- #


def progression(
    dossiers: list[Dossier],
    decisions: list[DecisionAdjudication],
    regles: list[Rule],
    etats: dict[str, ConstatReadiness],
    jour: dt.date,
) -> str:
    """`reports/HUMAN_REVIEW_PROGRESS.md` — ce qui est tranché, ce qui reste."""
    tranchees = {d.rule_id for d in decisions}
    par_priorite = {
        priorite: [d for d in dossiers if d.priorite_revue == priorite]
        for priorite in PRIORITES_ARBITREES
    }
    validated = sum(1 for r in regles if r.status is RuleStatus.VALIDATED)
    gold = sum(1 for e in etats.values() if e.gold_ready)
    family = sum(1 for e in etats.values() if e.family_ready)
    clusters = {d.review_cluster_id for d in dossiers}
    clusters_tranches = {d.review_cluster_id for d in dossiers if d.rule_id in tranchees}

    lignes = [
        "# Arbitrage humain — progression",
        "",
        f"Au {jour.isoformat()}. Les décisions sont comptées en relisant",
        "`data/verification/dossier-adjudication.csv` : une ligne vide n'est pas une",
        "décision, et aucune n'est écrite par le générateur.",
        "",
        "## Avancement",
        "",
        "| Priorité | Total | Arbitrées | Restantes |",
        "|---|---:|---:|---:|",
    ]
    for priorite in PRIORITES_ARBITREES:
        total = len(par_priorite[priorite])
        faites = sum(1 for d in par_priorite[priorite] if d.rule_id in tranchees)
        lignes.append(f"| {priorite} | {total} | {faites} | {total - faites} |")
    lignes += [
        "",
        f"Regroupements : {len(clusters_tranches)} tranché(s) sur {len(clusters)}.",
        "",
        "## Effet sur les seuils",
        "",
        "| Seuil | Avant | Après |",
        "|---|---:|---|",
        f"| `validated` | {validated} | — |",
        f"| `gold_ready` | {gold} | — |",
        f"| `family_ready` | {family} | — |",
        "",
        "La colonne « après » reste vide tant que les décisions n'ont pas été",
        "appliquées puis l'audit rejoué. Un « après » prévisionnel serait un",
        "`gold_ready` accordé par anticipation — ce que la spécification interdit.",
        "",
        "## Ce qui reste bloqué",
        "",
        "| Blocage | P0 | P1 |",
        "|---|---:|---:|",
    ]
    categories = sorted({d.blocage_categorie.value for d in dossiers})
    for categorie in categories:
        compte = {
            priorite: sum(
                1
                for d in par_priorite[priorite]
                if d.blocage_categorie.value == categorie and d.rule_id not in tranchees
            )
            for priorite in PRIORITES_ARBITREES
        }
        lignes.append(
            f"| `{categorie}` | {compte['P0']} | {compte['P1']} |"
        )
    lignes += [
        "",
        "## Après chaque décision",
        "",
        "1. revalider la règle ; 2. recalculer la gold-readiness ; 3. recalculer la",
        "family-readiness ; 4. rejouer les contrôles d'intégrité ; 5. écrire au",
        "registre append-only. Dans cet ordre, et jamais l'un sans les autres.",
        "",
    ]
    return "\n".join(lignes) + "\n"
