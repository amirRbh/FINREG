"""Dossier d'un lot de consultation : ce que le relecteur doit lire, et rendre.

Un lot rassemble les règles qu'un seul document, une fois ouvert, sert toutes.
Ce n'est pas un cluster de décision : chacune garde sa décision, et le dossier
en énumère deux par règle — l'énoncé est-il soutenu par le texte, et le texte
comporte-t-il des dérogations. La seconde ne se déduit jamais de la première :
confirmer un énoncé ne dit rien des exceptions qui le limitent ailleurs.

**Ce document n'a lu aucun texte.** Il ne dit pas ce que les articles
contiennent : il dit ce qu'il faudra y vérifier, et ce qu'une réponse devra
rapporter pour être recevable. Les statuts ne bougent pas.

Le vocabulaire de décision du relecteur se reporte sur le circuit de
vérification, qui existe déjà et qui est le seul chemin vers le registre
append-only. Inventer un second circuit ferait exister deux vérités.
"""

from __future__ import annotations

import datetime as dt

from src.bench.adjudication import question_neutre
from src.bench.completude import ConstatCompletude
from src.bench.plan_action import LigneAction
from src.bench.readiness import BlockerCategory
from src.bench.regles import Rule
from src.bench.rulebook import NegativeClaimStatus
from src.bench.verification import COLONNES_A_REMPLIR

#: Le vocabulaire demandé par la revue, et sa traduction exacte dans le circuit
#: de vérification. La colonne « ce qu'il faut écrire » est ce qui rend la
#: décision applicable : sans elle, chaque relecteur inventerait son encodage.
CORRESPONDANCE_DECISIONS: tuple[tuple[str, str, str], ...] = (
    (
        "NONE_IDENTIFIED",
        "aucune dérogation dans le périmètre examiné",
        "`verdict=confirme` · `exceptions_statut=none_identified` · "
        "`perimetre_exceptions` **obligatoire**",
    ),
    (
        "IDENTIFIED_AND_INCORPORATED",
        "des dérogations existent et sont recopiées dans la règle",
        "`verdict=confirme` · `exceptions_statut=identified_and_incorporated` · "
        "`exceptions_constatees` (extraits officiels) · `perimetre_exceptions` · "
        "`version_date_constatee`",
    ),
    (
        "REQUIRES_CORRECTION",
        "le texte dit autre chose : l'énoncé est rectifié",
        "`verdict=corrige` · `enonce_corrige` **obligatoire** — la règle est "
        "reversionnée, `supersedes` nomme la version remplacée",
    ),
    (
        "REJECTED",
        "le texte contredit la règle, ou la disposition citée n'existe pas",
        "`verdict=refute` · `commentaire` **obligatoire** — la règle reste `draft`, "
        "rien n'est promu",
    ),
    (
        "(consultée sans conclure)",
        "texte introuvable, version incertaine : la consultation est consignée",
        "`verdict=non_verifiable` · `commentaire` — la règle reste `draft`",
    ),
)


def dossier_de_lot(
    identifiant: str,
    source: str,
    obstacle: str,
    lignes: list[LigneAction],
    regles: dict[str, Rule],
    constats: dict[str, ConstatCompletude],
    chemin_csv: str,
    jour: dt.date,
) -> str:
    """Le dossier d'un lot : l'empêchement, le protocole, puis une fiche par règle."""
    l = [
        f"# {identifiant} — dossier de consultation",
        "",
        f"{len(lignes)} règles adossées à **{source}**, dont le texte primaire n'a pas",
        "pu être lu depuis l'environnement d'exécution.",
        "",
        "> **Aucun de ces textes n'a été consulté.** Ce document n'affirme rien de leur",
        "> contenu : il énumère ce qu'il faudra y vérifier. Aucun statut ne bouge, et",
        "> aucune décision n'est pré-remplie — y compris par défaut.",
        "",
        f"Établi le {jour.isoformat()}.",
        "",
        "## L'empêchement",
        "",
        f"> {obstacle or 'texte primaire non récupéré'}",
        "",
        "Le tunnel réseau s'établit, puis la source répond `403` : le refus vient du",
        "site, pas de l'environnement d'exécution. Ouvrir davantage la politique réseau",
        "n'y changerait rien. Restent l'API PISTE avec des identifiants, ou une",
        "consultation manuelle.",
        "",
        "## Deux décisions par règle, jamais une",
        "",
        "Chaque fiche pose **deux** questions distinctes, et confirmer la première ne",
        "répond pas à la seconde :",
        "",
        "1. **l'énoncé** est-il soutenu par la disposition citée, telle qu'elle est",
        "   rédigée dans la version applicable ?",
        "2. **les exceptions** : cette disposition, ou une autre du même code, la",
        "   limite-t-elle ?",
        "",
        "Une règle confirmée dont les exceptions restent `unknown` ne devient pas",
        "`validated` : elle se testerait comme un absolu qu'elle n'est peut-être pas.",
        "",
        "## Comment rendre une décision",
        "",
        f"Les décisions se portent dans `{chemin_csv}` — une ligne par règle, colonnes",
        "de décision vides à ce jour. Le vocabulaire de la revue s'y traduit ainsi :",
        "",
        "| Décision | Ce qu'elle affirme | Ce qu'il faut écrire |",
        "|---|---|---|",
    ]
    for decision, sens, encodage in CORRESPONDANCE_DECISIONS:
        l.append(f"| `{decision}` | {sens} | {encodage} |")

    l += [
        "",
        "**Toute décision doit être signée** : `verifie_par` et `date_verification`.",
        "Le schéma refuse une promotion sans elles — ce n'est pas une consigne, c'est",
        "une validation. Il refuse aussi un `none_identified` sans",
        "`perimetre_exceptions` : « je n'ai pas trouvé » ne vaut pas « il n'y en a",
        "pas », et une recherche automatique infructueuse ne fait jamais passer",
        "`unknown` à `none_identified`.",
        "",
        "Une ligne laissée vide n'est pas une décision : elle est ignorée. Un dossier",
        "dont une ligne est irrecevable ne s'applique pas à moitié.",
        "",
        "Colonnes à remplir : "
        + ", ".join(f"`{colonne}`" for colonne in COLONNES_A_REMPLIR)
        + ".",
        "",
        "## Les règles du lot",
        "",
    ]
    for ligne in lignes:
        l += _fiche(ligne, regles[ligne.rule_id], constats.get(ligne.rule_id))
    return "\n".join(l) + "\n"


def _fiche(ligne: LigneAction, regle: Rule, constat: ConstatCompletude | None) -> list[str]:
    """Une règle du lot, dans l'ordre où le relecteur en a besoin."""
    en_suspens = [
        claim.claim
        for claim in regle.negative_claims
        if claim.status is NegativeClaimStatus.UNVERIFIED
    ]
    question_exceptions = (
        question_neutre(regle, constat, BlockerCategory.EXCEPTION_UNRESOLVED)
        if constat is not None
        else ""
    )

    l = [
        f"### `{regle.id}` — {regle.title}",
        "",
        f"**Énoncé actuel (v{regle.version})**",
        "",
        f"> {regle.statement}",
        "",
        "**Source, article, disposition attendue**",
        "",
        f"- Texte : {regle.source.text}",
        f"- Article : {regle.source.article}",
        f"- Disposition attendue : "
        + (regle.source.paragraph or "article entier — aucun paragraphe désigné"),
        f"- Emplacement déclaré : {regle.source.url or '—'}",
        f"- Type de règle : `{regle.rule_type.value}` · priorité `{regle.priority.value}` "
        f"· revue {ligne.priority}",
        "",
        "**Version / date pertinente**",
        "",
        f"- Version déclarée dans la règle : {regle.source.version_date.isoformat()}",
        f"- Règle applicable depuis le {regle.valid_from.isoformat()}"
        + (f", jusqu'au {regle.valid_until.isoformat()}" if regle.valid_until else ""),
        f"- Régime : {regle.regulatory_regime} · statut réglementaire "
        f"`{regle.regulatory_status.value}`",
        "- La version à lire est celle applicable à la date ci-dessus ; si la",
        "  consolidation consultée diffère, c'est elle qu'il faut porter au dossier",
        "  (`version_date_constatee`).",
        "",
        "**Questions exactes à trancher**",
        "",
        f"1. {ligne.exact_decision_required}",
    ]
    if question_exceptions:
        l.append(f"2. {question_exceptions}")
    l += [
        "",
        "**Exceptions à rechercher**",
        "",
        f"- état actuel : `{regle.exceptions_status.value}` — personne n'a cherché sur "
        f"le texte, et aucune recherche automatique n'a pu avoir lieu ;",
        "- dérogations, exclusions, exemptions, seuils et régimes particuliers "
        "applicables à **cette** obligation ;",
        f"- dans {regle.source.article}, mais aussi ailleurs dans l'acte et dans les "
        f"textes pris pour son application — une dérogation s'écrit rarement dans "
        f"l'article qu'elle limite ;",
        "- périmètre à attester quelle que soit la conclusion.",
        "",
    ]
    if en_suspens:
        l += ["**Affirmations négatives portées par la règle**", ""]
        l += [f"- « {claim} » — à confirmer ou à contredire sur le texte" for claim in en_suspens]
        l += [""]
    if regle.common_confusions:
        l += ["**Confusions typiques déjà consignées** (à confirmer ou infirmer)", ""]
        l += [f"- {confusion}" for confusion in regle.common_confusions]
        l += [""]
    l += [
        "**Ce qui constitue une preuve suffisante**",
        "",
        f"- {ligne.required_evidence} ;",
        "- pour les exceptions : les phrases limitantes **recopiées telles quelles** du "
        "texte officiel — une exception reformulée est une exception interprétée ;",
        "- pour une absence : le périmètre exact examiné (articles, acte, version), "
        "porté dans `perimetre_exceptions` ;",
        "- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.",
        "",
        "**Décision actuellement manquante**",
        "",
        f"- **consultation de la source** : aucune. `{regle.source.article}` n'a jamais "
        f"été lu ; `verification_method` vaut `{regle.verification_method.value}` et la "
        f"règle reste `{regle.status.value}` ;",
        f"- **recherche d'exceptions** : aucune. `exceptions_status` vaut "
        f"`{regle.exceptions_status.value}` ;",
        "- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.",
        "",
        "---",
        "",
    ]
    return l
