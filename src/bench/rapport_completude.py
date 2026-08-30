"""Rapports de l'audit de complétude : QC, matrice de gold-readiness, dossier.

Trois artefacts, comme pour l'audit de sources — et pour la même raison : ce qui
est établi (`RULEBOOK_COMPLETENESS_QC.md`), ce qui est chiffré ligne à ligne
(`RULEBOOK_GOLD_READINESS.csv`), et ce qui reste à décider (le dossier de
vérification pré-rempli, sans signature).

Le rapport insiste sur une distinction que le décompte seul effacerait : une
règle peut être **validée et inutilisable**. Compter les `validated` sans
compter les `gold_ready` donnerait un faux sentiment de complétude — c'est
exactement ce que la spécification de cette phase interdit.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from src.bench.completude import ConstatCompletude, Structure
from src.bench.regles import Rule
from src.bench.rulebook import ExceptionsStatus, Priority, RuleStatus
from src.bench.verification import (
    COLONNES as COLONNES_DOSSIER,
    ENCODAGE_CSV,
    SEPARATEUR_CSV,
    SEPARATEUR_LISTE,
    Verdict,
)

RAPPORT_COMPLETUDE = Path("reports/RULEBOOK_COMPLETENESS_QC.md")
MATRICE_GOLD = Path("reports/RULEBOOK_GOLD_READINESS.csv")
DOSSIER_COMPLETUDE = Path("data/verification/dossier-completude.csv")

#: Colonnes imposées par la spécification §11, dans son ordre.
COLONNES_GOLD = (
    "ID",
    "domain",
    "status",
    "gold_ready",
    "exceptions_status",
    "temporal_status",
    "source_verified",
    "article_verified",
    "cross_reference_checked",
    "human_review_required",
    "reason",
)


def _oui(valeur: bool) -> str:
    return "oui" if valeur else "non"


def ecrire_matrice_gold(
    constats: list[ConstatCompletude], regles: list[Rule], chemin: Path
) -> None:
    """Matrice de gold-readiness, une ligne par règle."""
    par_id = {r.id: r for r in regles}
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(
            flux, fieldnames=list(COLONNES_GOLD), delimiter=SEPARATEUR_CSV
        )
        graveur.writeheader()
        for constat in constats:
            regle = par_id[constat.rule_id]
            humain = constat.statut_propose is RuleStatus.REQUIRES_HUMAN_REVIEW or (
                constat.exceptions_status is ExceptionsStatus.REQUIRES_HUMAN_REVIEW
            )
            graveur.writerow(
                {
                    "ID": constat.rule_id,
                    "domain": constat.domain,
                    "status": constat.statut_propose.value,
                    "gold_ready": _oui(constat.gold_ready),
                    "exceptions_status": constat.exceptions_status.value,
                    "temporal_status": constat.temporal_status,
                    "source_verified": _oui(regle.source.is_verified),
                    "article_verified": _oui(constat.criteres.get("article_verifie", False)),
                    "cross_reference_checked": _oui(constat.cross_reference_checked),
                    "human_review_required": _oui(humain),
                    "reason": constat.gold_ready_reason
                    if not constat.gold_ready
                    else constat.motif,
                }
            )


def exporter_dossier_completude(
    constats: list[ConstatCompletude], regles: list[Rule], chemin: Path
) -> Path:
    """Dossier pré-rempli de la passe de complétude, **sans la signature**.

    Même verrou que pour l'audit de sources : `verifie_par` et
    `date_verification` restent vides, et le schéma refuse toute promotion sans
    elles. Ce qui change ici, c'est ce que le dossier propose — non plus « la
    source dit bien cela », mais « voici les dispositions limitantes recopiées
    du texte officiel, et voici si la règle porte un gold ».
    """
    par_id = {r.id: r for r in regles}
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(
            flux, fieldnames=list(COLONNES_DOSSIER), delimiter=SEPARATEUR_CSV
        )
        graveur.writeheader()
        for constat in constats:
            regle = par_id[constat.rule_id]
            ligne = {colonne: "" for colonne in COLONNES_DOSSIER}
            ligne.update(
                {
                    "rule_id": regle.id,
                    "domaine": regle.domain.value,
                    "type": regle.rule_type.value,
                    "priorite": regle.priority.value,
                    "statut_actuel": regle.status.value,
                    "texte_source": regle.source.text,
                    "article": regle.source.article,
                    "url": regle.source.url,
                    "version_date_declaree": regle.source.version_date.isoformat(),
                    "enonce_actuel": regle.statement,
                    "exceptions_statut_actuel": regle.exceptions_status.value,
                    "commentaire": _commentaire(constat),
                }
            )
            if constat.statut_propose is RuleStatus.VALIDATED:
                ligne.update(
                    {
                        "verdict": Verdict.CONFIRME.value,
                        "methode": regle.verification_method.value,
                        "statut_vise": RuleStatus.VALIDATED.value,
                        "exceptions_statut": constat.exceptions_status.value,
                        "exceptions_constatees": SEPARATEUR_LISTE.join(
                            constat.exceptions_extraites
                        ),
                        "gold_ready": _oui(constat.gold_ready),
                        "gold_ready_motif": constat.gold_ready_reason,
                    }
                )
            graveur.writerow(ligne)
    return chemin


def _commentaire(constat: ConstatCompletude) -> str:
    morceaux = [f"STRUCTURES — {', '.join(s.value for s in constat.structures) or 'aucune'}"]
    if constat.criteres_manquants:
        morceaux.append("CRITÈRES MANQUANTS — " + ", ".join(constat.criteres_manquants))
    if constat.motifs:
        morceaux.append("CONSTATS — " + constat.motif)
    return " || ".join(morceaux)[:2000]


def rapport_markdown(constats: list[ConstatCompletude], regles: list[Rule]) -> str:
    """`reports/RULEBOOK_COMPLETENESS_QC.md`."""
    par_id = {r.id: r for r in regles}
    statuts = Counter(c.statut_propose.value for c in constats)
    exceptions = Counter(c.exceptions_status.value for c in constats)
    prets = [c for c in constats if c.gold_ready]
    utilisables = [
        c
        for c in constats
        if c.statut_propose is RuleStatus.VALIDATED and c.gold_ready
    ]
    arbitrage = [
        c
        for c in constats
        if c.statut_propose is RuleStatus.REQUIRES_HUMAN_REVIEW
        or c.exceptions_status is ExceptionsStatus.REQUIRES_HUMAN_REVIEW
    ]
    modifiees = [c for c in constats if c.exceptions_extraites]

    lignes = [
        "# Rulebook — audit de complétude et de gold-readiness",
        "",
        "Rapport généré par `src/bench/rapport_completude.py`. L'audit de sources",
        "établissait qu'une règle cite le bon texte ; celui-ci examine ce que ce texte",
        "contient **autour** d'elle — dérogations, conditions, renvois, temporalité —",
        "et si ce qu'elle en dit suffit à écrire une réponse de référence.",
        "",
        "## Deux choses à ne pas confondre",
        "",
        "`validated` dit que la règle est juridiquement établie. `gold_ready` dit",
        "qu'elle est assez précise pour qu'on en tire une réponse de référence **sans",
        "nouvelle interprétation juridique**. Les deux sont indépendants : « le",
        "règlement précise les modalités de l'évaluation » peut être parfaitement exact",
        "et ne rien permettre de rédiger.",
        "",
        "Ne compter que les `validated` donnerait un faux sentiment de complétude. La",
        "seule population utile à la génération de familles est **`validated` ET",
        "`gold_ready`**.",
        "",
        "## Synthèse",
        "",
        f"- règles examinées : **{len(constats)}**",
        f"- `validated` : **{statuts.get('validated', 0)}**",
        f"- `source_checked` : **{statuts.get('source_checked', 0)}**",
        f"- `requires_human_review` : **{statuts.get('requires_human_review', 0)}**",
        f"- `draft` : **{statuts.get('draft', 0)}**",
        "",
        f"- `gold_ready` : **{len(prets)}**",
        f"- non `gold_ready` : **{len(constats) - len(prets)}**",
        f"- **utilisables pour la génération de familles** "
        f"(`validated` et `gold_ready`) : **{len(utilisables)}**",
        "",
        "### Recherche d'exceptions",
        "",
        f"- `none_identified` : **{exceptions.get('none_identified', 0)}**",
        f"- `identified_and_incorporated` : "
        f"**{exceptions.get('identified_and_incorporated', 0)}**",
        f"- `identified_but_not_incorporated` : "
        f"**{exceptions.get('identified_but_not_incorporated', 0)}**",
        f"- `not_applicable` : **{exceptions.get('not_applicable', 0)}**",
        f"- `requires_human_review` : **{exceptions.get('requires_human_review', 0)}**",
        f"- `unknown` : **{exceptions.get('unknown', 0)}**",
        "",
        "> **`none_identified` n'est jamais attribué par cette passe.** Ne pas trouver",
        "> de dérogation dans l'article cité ne prouve pas qu'aucun autre article n'y",
        "> déroge, ni qu'aucun acte ultérieur ne l'a fait. Ce cas ressort en",
        "> `requires_human_review` : c'est un juriste qui peut conclure à l'absence,",
        "> pas une recherche de motifs.",
        "",
        "## Structures juridiques trouvées dans les textes cités",
        "",
        "| Structure | Règles concernées |",
        "|---|---:|",
    ]
    presentes = Counter(s.value for c in constats for s in c.structures)
    for structure in Structure:
        lignes.append(f"| {structure.value} | {presentes.get(structure.value, 0)} |")

    lignes += [
        "",
        "## Critères de validation non remplis",
        "",
        "Les huit critères de la spécification §4. Un seul manquant suffit à refuser",
        "la validation.",
        "",
        "| Critère | Règles bloquées |",
        "|---|---:|",
    ]
    manquants = Counter(m for c in constats for m in c.criteres_manquants)
    for critere, nombre in sorted(manquants.items(), key=lambda kv: -kv[1]):
        lignes.append(f"| `{critere}` | {nombre} |")

    lignes += [
        "",
        "## Règles utilisables pour la génération de familles",
        "",
    ]
    if utilisables:
        lignes += ["| ID | Domaine | Priorité | Exceptions |", "|---|---|---|---|"]
        for constat in utilisables:
            lignes.append(
                f"| `{constat.rule_id}` | {constat.domain} | {constat.priority} | "
                f"{constat.exceptions_status.value} |"
            )
    else:
        lignes.append("Aucune. Aucune famille ne peut encore être finalisée.")

    lignes += [
        "",
        f"## Règles modifiées ({len(modifiees)})",
        "",
        "Exceptions recopiées depuis le texte officiel — recopiées, jamais",
        "reformulées : une exception reformulée est une exception interprétée.",
        "Chaque incorporation **reversionne** la règle, sans écraser l'ancienne.",
        "",
    ]
    if modifiees:
        lignes += ["| ID | Dispositions incorporées |", "|---|---:|"]
        for constat in modifiees:
            lignes.append(
                f"| `{constat.rule_id}` | {len(constat.exceptions_extraites)} |"
            )
    else:
        lignes.append("Aucune.")

    lignes += [
        "",
        f"## Règles nécessitant un arbitrage humain ({len(arbitrage)})",
        "",
        "| ID | Priorité | Pourquoi |",
        "|---|---|---|",
    ]
    for constat in arbitrage[:60]:
        raison = constat.motif or constat.gold_ready_reason
        lignes.append(
            f"| `{constat.rule_id}` | {constat.priority} | {raison[:150]} |"
        )
    if len(arbitrage) > 60:
        lignes.append(f"| … | | et {len(arbitrage) - 60} autre(s) |")

    non_prets = [c for c in constats if not c.gold_ready]
    lignes += [
        "",
        f"## Règles non `gold_ready` ({len(non_prets)})",
        "",
        "Elles peuvent être juridiquement exactes : ce qui leur manque est la",
        "précision, pas la véracité.",
        "",
        "| ID | Priorité | Pourquoi |",
        "|---|---|---|",
    ]
    for constat in non_prets[:60]:
        lignes.append(
            f"| `{constat.rule_id}` | {constat.priority} | "
            f"{constat.gold_ready_reason[:150]} |"
        )
    if len(non_prets) > 60:
        lignes.append(f"| … | | et {len(non_prets) - 60} autre(s) |")

    critiques = [
        c
        for c in constats
        if par_id[c.rule_id].priority is Priority.CRITICAL
        and c.statut_propose is not RuleStatus.VALIDATED
    ]
    lignes += [
        "",
        f"## Règles CRITICAL non validées ({len(critiques)})",
        "",
        "Contrôle renforcé de la spécification §9 : une règle critique n'est validée",
        "que si ses exceptions **et** ses renvois sont établis.",
        "",
    ]
    lignes += [f"- `{c.rule_id}` : {(c.motif or '—')[:170]}" for c in critiques[:40]]
    if len(critiques) > 40:
        lignes.append(f"- … et {len(critiques) - 40} autre(s)")

    lignes += [
        "",
        "## Ce que cette passe n'a pas fait",
        "",
        "- elle n'a promu aucune règle d'elle-même : le dossier",
        "  `data/verification/dossier-completude.csv` est pré-rempli **sans**",
        "  `verifie_par` ni `date_verification`, et le schéma refuse toute promotion",
        "  sans elles ;",
        "- elle n'a écrasé aucun énoncé : toute incorporation reversionne ;",
        "- elle n'a conclu à aucune absence d'exception.",
        "",
    ]
    return "\n".join(lignes) + "\n"
