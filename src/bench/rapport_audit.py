"""Rapports de l'audit du Rulebook : matrice, rapport QC, dossier pré-rempli.

Trois artefacts, trois usages :

- `RULEBOOK_VERIFICATION_MATRIX.csv` — une ligne par règle, ce que l'audit a
  établi et d'où ;
- `RULEBOOK_VERIFICATION_QC.md` — ce que l'audit a établi, en clair, anomalies
  comprises ;
- le **dossier pré-rempli**, qui entre directement dans le circuit de
  vérification existant.

Le dossier pré-rempli mérite une explication, parce qu'il porte le verrou du
dépôt. Toutes ses colonnes de constat sont remplies par la machine — verdict
proposé, méthode, énoncé officiel, date de version constatée — **sauf deux** :
`verifie_par` et `date_verification`. Elles restent vides, et le modèle
`Verification` refuse toute promotion sans elles. Le vérificateur n'a donc pas à
refaire le travail de recherche ; il a à le signer, et rien ne peut être promu
tant qu'il ne l'a pas fait. Le verrou n'est pas une consigne dans un rapport :
c'est une validation de schéma qu'aucun chemin ne contourne.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from src.bench.audit_rulebook import (
    SEUIL_CONCORDANCE,
    ClassementAudit,
    ConstatAudit,
)
from src.bench.regles import Rule
from src.bench.rulebook import ExceptionsStatus, Priority, RuleStatus
from src.bench.verification import (
    COLONNES as COLONNES_DOSSIER,
    ENCODAGE_CSV,
    SEPARATEUR_CSV,
    SEPARATEUR_LISTE,
    Verdict,
)

RAPPORT_VERIFICATION = Path("reports/RULEBOOK_VERIFICATION_QC.md")
MATRICE_VERIFICATION = Path("reports/RULEBOOK_VERIFICATION_MATRIX.csv")
DOSSIER_AUDIT = Path("data/verification/dossier-audit.csv")

#: Colonnes de la matrice : celles que la spécification §2 demande, puis la
#: preuve — sans elle, la ligne serait une opinion.
COLONNES_MATRICE = (
    "rule_id",
    "domaine",
    "source",
    "article",
    "version",
    "statut",
    "exceptions",
    "temporalite",
    "probleme",
    "classement",
    "priorite",
    "concordance",
    "article_trouve",
    "chiffres_absents",
    "verdict_propose",
    "celex_consulte",
    "journal_officiel",
    "recupere_depuis",
    "sha256_texte",
)


def ecrire_matrice(constats: list[ConstatAudit], regles: list[Rule], chemin: Path) -> None:
    """Matrice d'audit, aux conventions des artefacts humains du dépôt."""
    priorites = {r.id: r.priority.value for r in regles}
    statuts = {r.id: r.status.value for r in regles}
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(
            flux, fieldnames=list(COLONNES_MATRICE), delimiter=SEPARATEUR_CSV
        )
        graveur.writeheader()
        for constat in constats:
            preuve = constat.preuve
            graveur.writerow(
                {
                    "rule_id": constat.rule_id,
                    "domaine": constat.domain,
                    "source": constat.source_text,
                    "article": constat.article,
                    "version": constat.version_date,
                    "statut": statuts.get(constat.rule_id, ""),
                    "exceptions": constat.exceptions_status,
                    "temporalite": constat.regulatory_status,
                    "probleme": constat.probleme,
                    "classement": constat.classement.value,
                    "priorite": priorites.get(constat.rule_id, ""),
                    "concordance": f"{constat.concordance:.2f}",
                    "article_trouve": "oui" if preuve and preuve.article_found else "non",
                    "chiffres_absents": SEPARATEUR_LISTE.join(constat.missing_figures),
                    "verdict_propose": (
                        constat.verdict_propose.value if constat.verdict_propose else ""
                    ),
                    "celex_consulte": preuve.celex if preuve else "",
                    "journal_officiel": preuve.official_journal if preuve else "",
                    "recupere_depuis": preuve.retrieved_from if preuve else "",
                    "sha256_texte": preuve.sha256 if preuve else "",
                }
            )


def exporter_dossier_prerempli(
    constats: list[ConstatAudit], regles: list[Rule], chemin: Path
) -> Path:
    """Dossier de vérification pré-rempli par l'audit, **sans la signature**.

    `verifie_par` et `date_verification` restent vides à dessein : ce sont elles
    que le schéma exige pour promouvoir une règle. Le vérificateur lit l'extrait
    officiel reporté en commentaire, et signe — ou corrige.
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
            preuve = constat.preuve
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
                    "url": preuve.retrieved_from if preuve else regle.source.url,
                    "version_date_declaree": regle.source.version_date.isoformat(),
                    "enonce_actuel": regle.statement,
                    "exceptions_statut_actuel": regle.exceptions_status.value,
                    # Constats de la machine : tout est proposé, rien n'est signé.
                    "verdict": (
                        constat.verdict_propose.value if constat.verdict_propose else ""
                    ),
                    "methode": (
                        "primary_text_fetched"
                        if constat.classement is not ClassementAudit.BLOCKED
                        else ""
                    ),
                    "statut_vise": (
                        RuleStatus.SOURCE_CHECKED.value
                        if constat.verdict_propose is Verdict.CONFIRME
                        else ""
                    ),
                    "commentaire": _commentaire(constat),
                }
            )
            graveur.writerow(ligne)
    return chemin


def _commentaire(constat: ConstatAudit) -> str:
    """Ce que le vérificateur doit lire avant de signer : la preuve, puis les réserves."""
    morceaux: list[str] = []
    if constat.preuve and constat.preuve.paragraph_excerpt:
        morceaux.append(f"TEXTE OFFICIEL — {constat.preuve.paragraph_excerpt[:600]}")
    elif constat.preuve and constat.preuve.excerpt:
        morceaux.append(f"TEXTE OFFICIEL — {constat.preuve.excerpt[:600]}")
    if constat.problemes:
        morceaux.append("RÉSERVES — " + " ; ".join(constat.problemes))
    return " || ".join(morceaux)


def _anomalies(constats: list[ConstatAudit]) -> list[tuple[str, str]]:
    return [(c.rule_id, p) for c in constats for p in c.problemes]


def rapport_markdown(constats: list[ConstatAudit], regles: list[Rule]) -> str:
    """`reports/RULEBOOK_VERIFICATION_QC.md` : ce que l'audit a établi, sans arrondi."""
    par_id = {r.id: r for r in regles}
    par_classement = Counter(c.classement.value for c in constats)
    actes = sorted({c.preuve.celex for c in constats if c.preuve and c.preuve.celex})
    articles_trouves = sum(1 for c in constats if c.preuve and c.preuve.article_found)
    negatives_examinees = sum(c.negative_claims_checked for c in constats)
    negatives_absentes = sum(c.negative_claims_absent for c in constats)
    temporelles = sum(1 for r in regles if r.time_sensitive)
    exceptions_connues = sum(
        1 for r in regles if r.exceptions_status is not ExceptionsStatus.UNKNOWN
    )
    anomalies = _anomalies(constats)

    lignes = [
        "# Rulebook — audit de vérification contre le texte primaire",
        "",
        "Rapport généré par `src/bench/rapport_audit.py`. Il dit, règle par règle,",
        "ce que la confrontation au texte officiel a établi — et ce qu'elle n'a pas",
        "pu établir.",
        "",
        "## Ce que cet audit fait, et ce qu'il ne fait pas",
        "",
        "L'audit **récupère le texte primaire authentique**, le découpe par article,",
        "et confronte chaque règle à l'article qu'elle cite. Il n'attribue jamais le",
        "statut `source_checked` : le dépôt définit ce statut comme n'étant « jamais",
        "un statut qu'un modèle peut s'accorder à lui-même ». Une règle dont tout est",
        "corroboré est donc classée `REQUIRES_HUMAN_REVIEW` — il ne lui manque que la",
        "signature d'un vérificateur nommé.",
        "",
        "Cette signature ne demande pas de refaire le travail : le dossier",
        "`data/verification/dossier-audit.csv` est pré-rempli avec le verdict proposé,",
        "la méthode et l'extrait officiel. Seules `verifie_par` et `date_verification`",
        "sont vides — et le schéma `Verification` refuse toute promotion sans elles.",
        "",
        "```sh",
        "# remplir verifie_par et date_verification, puis :",
        "finreg-bench rulebook appliquer-verification data/verification/dossier-audit.csv",
        "```",
        "",
        "## Voies d'accès aux sources primaires",
        "",
        "Ce que l'environnement d'exécution permet réellement, mesuré et non supposé :",
        "",
        "| Voie | État | Conséquence |",
        "|---|---|---|",
        "| `publications.europa.eu` (CELLAR) | texte authentique du *Journal officiel*, "
        "découpé par article | **voie retenue pour le droit de l'Union** |",
        "| `eur-lex.europa.eu` | HTTP 200 mais sert la page d'accueil du JO | inutilisable |",
        "| `legifrance.gouv.fr` | HTTP 403 | Code monétaire et financier hors d'atteinte |",
        "| `amf-france.org` | page réelle | doctrine AMF atteignable |",
        "",
        "> Un `200` qui rend une page d'accueil est plus dangereux qu'un `403` : il se",
        "> lit comme un succès. Chaque récupération est donc validée sur son contenu —",
        "> langue attendue, articles découpables — et jamais sur son code de retour.",
        "",
        "## Synthèse",
        "",
        f"- règles examinées : **{len(constats)}**",
        f"- `SOURCE_CHECKED` : **{par_classement.get('SOURCE_CHECKED', 0)}**",
        f"- `REQUIRES_HUMAN_REVIEW` : **{par_classement.get('REQUIRES_HUMAN_REVIEW', 0)}**",
        f"- `DRAFT` : **{par_classement.get('DRAFT', 0)}**",
        f"- `BLOCKED` : **{par_classement.get('BLOCKED', 0)}**",
        "",
        f"- sources primaires effectivement consultées : **{len(actes)}** "
        f"({', '.join(f'`{a}`' for a in actes) or '—'})",
        f"- articles retrouvés dans le texte officiel : **{articles_trouves} / {len(constats)}**",
        f"- affirmations négatives examinées : **{negatives_examinees}**, "
        f"dont corroborées absentes : **{negatives_absentes}**",
        f"- règles sensibles au temps : **{temporelles}**",
        f"- règles dont les exceptions sont renseignées : "
        f"**{exceptions_connues} / {len(regles)}**",
        f"- anomalies relevées : **{len(anomalies)}**",
        "",
        f"Seuil de concordance retenu : **{SEUIL_CONCORDANCE:.0%}** du vocabulaire de",
        "l'énoncé retrouvé dans l'article officiel. Ce n'est pas une mesure de vérité —",
        "un énoncé peut être faux avec un vocabulaire parfaitement couvert — mais une",
        "mesure de **rattachement** : elle attrape la règle qui cite un article parlant",
        "d'autre chose.",
        "",
        "## Classement par domaine",
        "",
        "| Domaine | Règles | Human review | Draft | Blocked |",
        "|---|---:|---:|---:|---:|",
    ]

    for domaine in sorted({c.domain for c in constats}):
        concernes = [c for c in constats if c.domain == domaine]
        lignes.append(
            f"| {domaine} | {len(concernes)} | "
            f"{sum(1 for c in concernes if c.classement is ClassementAudit.REQUIRES_HUMAN_REVIEW)} | "
            f"{sum(1 for c in concernes if c.classement is ClassementAudit.DRAFT)} | "
            f"{sum(1 for c in concernes if c.classement is ClassementAudit.BLOCKED)} |"
        )

    lignes += [
        "",
        "## Audit des règles",
        "",
        "Ordre de priorité de la spécification §3 : les critiques d'abord, puis les",
        "exceptions inconnues, puis les affirmations négatives.",
        "",
        "| ID | Domaine | Source | Article | Version | Statut | Exceptions | Temporalité | Problème |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for constat in constats:
        regle = par_id[constat.rule_id]
        probleme = constat.probleme or "—"
        lignes.append(
            f"| `{constat.rule_id}` | {constat.domain} | {constat.source_text[:34]} | "
            f"{constat.article} | {constat.version_date} | {constat.classement.value} | "
            f"{constat.exceptions_status} | {constat.regulatory_status} | "
            f"{probleme[:190]} |"
        )

    lignes += ["", "## Anomalies", ""]
    groupes: dict[str, list[str]] = {}
    for rule_id, anomalie in anomalies:
        cle = _famille_anomalie(anomalie)
        groupes.setdefault(cle, []).append(f"`{rule_id}` : {anomalie}")
    for cle, elements in sorted(groupes.items(), key=lambda kv: -len(kv[1])):
        lignes += [f"### {cle} — {len(elements)}", ""]
        lignes += [f"- {e}" for e in elements[:25]]
        if len(elements) > 25:
            lignes.append(f"- … et {len(elements) - 25} autre(s)")
        lignes.append("")

    lignes += [
        "## Règles critiques restant à trancher",
        "",
    ]
    critiques = [
        c
        for c in constats
        if par_id[c.rule_id].priority is Priority.CRITICAL
        and c.classement is not ClassementAudit.REQUIRES_HUMAN_REVIEW
    ]
    if critiques:
        lignes += ["| ID | Classement | Pourquoi |", "|---|---|---|"]
        for constat in critiques:
            lignes.append(
                f"| `{constat.rule_id}` | {constat.classement.value} | "
                f"{(constat.probleme or '—')[:170]} |"
            )
    else:
        lignes.append("Aucune : toutes les règles critiques sont corroborées.")
    lignes.append("")

    return "\n".join(lignes) + "\n"


#: Regroupement des anomalies par nature, pour que le rapport se lise.
_FAMILLES_ANOMALIES = (
    ("Source primaire hors d'atteinte", ("hors d'atteinte", "403", "non récupéré", "HTTP")),
    ("Article introuvable dans l'acte cité", ("introuvable",)),
    ("Énoncé peu corroboré", ("peu corroboré",)),
    ("Chiffre non retrouvé", ("chiffre",)),
    ("Exceptions jamais cherchées", ("exceptions jamais",)),
    ("Affirmation négative", ("affirmation négative",)),
    ("Source doctrinale", ("doctrinale",)),
    ("Temporalité", ("proposed", "version invraisemblable")),
)


def _famille_anomalie(anomalie: str) -> str:
    for libelle, marques in _FAMILLES_ANOMALIES:
        if any(marque in anomalie for marque in marques):
            return libelle
    return "Autres"
