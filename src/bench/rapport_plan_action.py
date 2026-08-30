"""Les quatre artefacts du plan de revue, et ce que chacun refuse de dire.

| Artefact | Lecteur | Ce qu'il porte |
|---|---|---|
| `HUMAN_REVIEW_ACTION_PLAN.md` | qui organise la revue | l'ordre de travail et son rendement |
| `HUMAN_REVIEW_ACTION_PLAN.csv` | l'outillage | une ligne par règle, colonnes fixes |
| `LCBFT_MANUAL_CONSULTATION_PACK.md` | qui ira lire le CMF | ce qu'il faut confirmer, article par article |
| `AMF-R-005-SOURCE-REANCHORING.md` | qui réancrera la source | pourquoi l'URL ne vaut plus, et ce qu'on cherche |

Aucun de ces documents ne prétend avoir lu un texte qu'il n'a pas lu. Le pack
LCB-FT dit exactement l'inverse : il énumère ce qui reste **à confirmer**, et
rappelle que le statut des règles ne bouge pas tant que personne n'a signé.

La projection porte la marque `PROJECTED_ONLY` à chaque fois qu'elle apparaît.
Un chiffre projeté qu'on lirait comme un état ferait croire à un `gold_ready`
que personne n'a accordé.
"""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter
from pathlib import Path

from src.bench.completude import ConstatCompletude
from src.bench.plan_action import (
    ACTIONS_D_ACCES,
    MARQUE_PROJECTION,
    RANGS,
    ActionPrincipale,
    Etape,
    Groupe,
    LigneAction,
    Projection,
    portance_etablie,
)
from src.bench.regles import Rule
from src.bench.relecture import AccesSource
from src.bench.rulebook import NegativeClaimStatus
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV, SEPARATEUR_LISTE

PLAN_ACTION = Path("reports/HUMAN_REVIEW_ACTION_PLAN.md")
PLAN_ACTION_CSV = Path("reports/HUMAN_REVIEW_ACTION_PLAN.csv")
PACK_LCBFT = Path("reports/LCBFT_MANUAL_CONSULTATION_PACK.md")
DOSSIER_REANCRAGE = Path("reports/AMF-R-005-SOURCE-REANCHORING.md")

#: Colonnes imposées par la spécification §1, dans son ordre.
COLONNES_PLAN: tuple[str, ...] = (
    "rule_id",
    "domain",
    "priority",
    "blocker",
    "secondary_blockers",
    "source",
    "article",
    "paragraph",
    "source_access_status",
    "review_cluster",
    "exact_decision_required",
    "required_evidence",
    "proposed_action",
    "expected_status_after_decision",
)


def ecrire_plan_csv(lignes: list[LigneAction], chemin: Path) -> None:
    """Une ligne par règle P0/P1, colonnes fixes, aucune décision."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(flux, fieldnames=list(COLONNES_PLAN), delimiter=SEPARATEUR_CSV)
        graveur.writeheader()
        for ligne in lignes:
            graveur.writerow(
                {
                    "rule_id": ligne.rule_id,
                    "domain": ligne.domain,
                    "priority": ligne.priority,
                    "blocker": ligne.blocker,
                    "secondary_blockers": SEPARATEUR_LISTE.join(ligne.secondary_blockers),
                    "source": ligne.source,
                    "article": ligne.article,
                    "paragraph": ligne.paragraph,
                    "source_access_status": ligne.source_access_status.value,
                    "review_cluster": ligne.review_cluster,
                    "exact_decision_required": ligne.exact_decision_required,
                    "required_evidence": ligne.required_evidence,
                    "proposed_action": ligne.proposed_action.value,
                    "expected_status_after_decision": ligne.expected_status_after_decision,
                }
            )


# --------------------------------------------------------------------------- #
# Plan d'action
# --------------------------------------------------------------------------- #


def plan_action(
    lignes: list[LigneAction],
    groupes: list[Groupe],
    etapes: list[Etape],
    projection: Projection,
    bloquants: list[str],
    suivante: str,
    empreinte: str,
    jour: dt.date,
) -> str:
    """`reports/HUMAN_REVIEW_ACTION_PLAN.md`."""
    par_action = Counter(ligne.proposed_action.value for ligne in lignes)
    par_priorite = Counter(ligne.priority for ligne in lignes)

    l = [
        "# Plan de revue humaine — P0 / P1",
        "",
        "Le pack d'arbitrage dit quoi trancher, règle par règle. Ce plan dit par où",
        "commencer, et ce que chaque action débloque. Il ne génère aucune famille,",
        "aucune question, et ne modifie aucun statut.",
        "",
        f"**État relu** — audit publié, empreinte `{empreinte}`. Établi le {jour.isoformat()}.",
        "",
        "## Ce qu'il y a à faire",
        "",
        "| Action principale | Règles |",
        "|---|---:|",
    ]
    for action, compte in sorted(par_action.items(), key=lambda kv: (-kv[1], kv[0])):
        l.append(f"| `{action}` | {compte} |")
    l += [
        "",
        f"{len(lignes)} règles — {par_priorite.get('P0', 0)} P0, {par_priorite.get('P1', 0)} P1.",
        "",
    ]

    l += _section_ordre(etapes)
    l += _section_groupes(groupes)
    l += _section_queue(lignes)
    l += _section_projection(projection, groupes)
    l += _section_sortie(bloquants, suivante)
    return "\n".join(l) + "\n"


def _section_ordre(etapes: list[Etape]) -> list[str]:
    """L'ordre d'exécution, et pourquoi il n'est pas l'ordre de gravité."""
    l = [
        "## Ordre d'exécution",
        "",
        "Classé par rendement — règles débloquées par action de revue. **Les priorités",
        "P0/P1 ne sont pas modifiées** : elles disent la gravité d'une erreur, pas",
        "l'ordre du travail. Une consultation qui débloque douze règles passe en tête",
        "parce qu'elle coûte une action pour douze résultats, pas parce qu'elle serait",
        "plus grave qu'un P0 isolé.",
        "",
        "| # | Rang | Action | Objet | Nature | Débloque | Achève |",
        "|---:|---|---|---|---|---:|---:|",
    ]
    for numero, etape in enumerate(etapes, start=1):
        l.append(
            f"| {numero} | {RANGS[etape.rang - 1]} | `{etape.action.value}` | "
            f"`{etape.intitule}` | {etape.nature} | {etape.regles_debloquees} | "
            f"{etape.regles_achevees} |"
        )
    l += [
        "",
        "« Débloque » compte les règles dont l'action lève le blocage principal.",
        "« Achève » compte celles qui, ensuite, ne porteraient plus aucun blocage de",
        "fond — les autres retomberont dans la file avec le blocage suivant.",
        "",
    ]
    return l


def _section_groupes(groupes: list[Groupe]) -> list[str]:
    """Les deux axes de regroupement, qui ne disent pas la même chose."""
    l = [
        "## Regroupements",
        "",
        "Deux axes qu'il ne faut pas confondre. Un **cluster de décision** partage une",
        "question : une seule décision couvre toutes ses règles. Un **lot de lecture**",
        "partage un empêchement : une seule consultation sert tous ses dossiers, mais",
        "chaque règle garde sa décision. Dans les deux cas, les règles restent",
        "distinctes dans le Rulebook — un article porte couramment plusieurs",
        "obligations, et les confondre en effacerait une.",
        "",
        "| cluster_id | Nature | source | article(s) | rules | débloquées | achevées |",
        "|---|---|---|---|---|---:|---:|",
    ]
    for groupe in groupes:
        articles = ", ".join(groupe.articles[:6]) or "—"
        regles = ", ".join(f"`{r}`" for r in groupe.regles)
        l.append(
            f"| `{groupe.identifiant}` | {groupe.nature} | {groupe.source} | {articles} | "
            f"{regles} | {groupe.regles_debloquees} | {groupe.regles_achevees} |"
        )
    l += ["", "### Question unique de chaque regroupement", ""]
    for groupe in groupes:
        l += [
            f"**`{groupe.identifiant}`** ({groupe.regles_debloquees} règles)",
            "",
            f"> {groupe.question_unique}",
            "",
        ]
    return l


def _section_queue(lignes: list[LigneAction]) -> list[str]:
    """La queue complète, par priorité puis domaine."""
    l = [
        "## Queue P0 / P1",
        "",
        "Une entrée par règle. Le détail juridique de chaque dossier — dispositions à",
        "examiner, faits textuels, périmètre — vit dans `HUMAN_REVIEW_P0_P1.md` ; on ne",
        "le recopie pas ici.",
        "",
    ]
    for priorite in ("P0", "P1"):
        concernees = [ligne for ligne in lignes if ligne.priority == priorite]
        if not concernees:
            continue
        l += [f"### {priorite} — {len(concernees)} règles", ""]
        for domaine in sorted({ligne.domain for ligne in concernees}):
            du_domaine = [ligne for ligne in concernees if ligne.domain == domaine]
            l += [
                f"#### {domaine}",
                "",
                "| rule_id | action | blocker | accès | article | cluster | statut projeté |",
                "|---|---|---|---|---|---|---|",
            ]
            for ligne in du_domaine:
                l.append(
                    f"| `{ligne.rule_id}` | `{ligne.proposed_action.value}` | "
                    f"`{ligne.blocker}` | `{ligne.source_access_status.value}` | "
                    f"{ligne.article or '—'} | `{ligne.review_cluster}` | "
                    f"{ligne.expected_status_after_decision} |"
                )
            l.append("")
    return l


def _section_projection(projection: Projection, groupes: list[Groupe]) -> list[str]:
    """Une simulation, marquée comme telle à chaque ligne."""
    l = [
        f"## Simulation — {MARQUE_PROJECTION}",
        "",
        f"**{MARQUE_PROJECTION}.** Rien de ce qui suit n'est un statut. Les seuils se",
        "recalculent en rejouant l'audit sur un Rulebook corrigé ; ils ne se déduisent",
        "pas d'un plan, et aucune décision n'a été rendue à ce jour.",
        "",
        "| Seuil | État réel |",
        "|---|---:|",
        f"| `validated` | {projection.validated} |",
        f"| `gold_ready` | {projection.gold_ready} |",
        f"| `family_ready` | {projection.family_ready} |",
        "",
        f"Si **tous** les arbitrages P0/P1 étaient rendus et signés, "
        f"{projection.eligibles_apres_arbitrage} règle(s) ne porteraient plus de blocage "
        f"de fond, dont {projection.eligibles_avec_portance} dont l'énoncé porte déjà "
        f"assez pour qu'un gold s'y adosse — {MARQUE_PROJECTION}.",
        "",
        "| Si ce regroupement est résolu | Règles concernées | Sans blocage de fond ensuite |",
        "|---|---:|---:|",
    ]
    for groupe in groupes:
        l.append(
            f"| `{groupe.identifiant}` | {groupe.regles_debloquees} | {groupe.regles_achevees} |"
        )
    l += [
        "",
        f"Lecture ({MARQUE_PROJECTION}) : « résolu » veut dire *décision rendue et*",
        "*signée*. Une règle « sans blocage de fond ensuite » devient **éligible** à",
        "`validated` ; elle ne le devient pas d'office, et `gold_ready` reste un calcul",
        "à refaire, jamais un acquis de la décision.",
        "",
    ]
    return l


def _section_sortie(bloquants: list[str], suivante: str) -> list[str]:
    return [
        "## BLOCKING ITEMS",
        "",
        "Ce qui empêche encore `READY_FOR_FAMILY_GENERATION` :",
        "",
        *[f"{numero}. {item}" for numero, item in enumerate(bloquants, start=1)],
        "",
        "## NEXT ACTION",
        "",
        f"> {suivante}",
        "",
    ]


# --------------------------------------------------------------------------- #
# Pack de consultation manuelle LCB-FT
# --------------------------------------------------------------------------- #


def pack_lcbft(
    lignes: list[LigneAction],
    regles: dict[str, Rule],
    obstacles: dict[str, str],
    jour: dt.date,
) -> str:
    """`reports/LCBFT_MANUAL_CONSULTATION_PACK.md` — ce qu'il reste à confirmer.

    Ce document ne rapporte aucun texte : il dit ce que personne n'a pu lire, et
    ce qu'il faudra rapporter pour signer.
    """
    concernees = [
        ligne
        for ligne in lignes
        if ligne.proposed_action in ACTIONS_D_ACCES
        and ligne.source_access_status is AccesSource.REFUS_DE_LA_SOURCE
        and ligne.domain == "LCBFT"
    ]
    obstacle = next((obstacles.get(ligne.rule_id, "") for ligne in concernees), "")

    l = [
        "# LCB-FT — pack de consultation manuelle",
        "",
        f"{len(concernees)} règles adossées au **Code monétaire et financier**, dont le",
        "texte n'a pas pu être lu depuis l'environnement d'exécution.",
        "",
        "> **Aucun de ces textes n'a été consulté.** Ce document n'affirme rien du",
        "> contenu des articles cités : il énumère ce qu'il faudra y vérifier. Le",
        "> statut des règles reste `draft` tant que personne n'a lu et signé.",
        "",
        f"Établi le {jour.isoformat()}.",
        "",
        "## L'empêchement",
        "",
        f"> {obstacle or 'texte primaire non récupéré'}",
        "",
        "Le tunnel réseau s'établit, puis le site répond `403` : le refus vient de la",
        "source, pas de l'environnement. Ouvrir davantage la politique réseau n'y",
        "changerait rien. Les voies restantes : l'API PISTE avec des identifiants, ou",
        "une consultation manuelle.",
        "",
        "## Ce qu'une consultation doit rapporter",
        "",
        "Pour chaque article, et dans cet ordre :",
        "",
        "1. le texte de la disposition **dans sa version applicable**, avec sa date de",
        "   consolidation ;",
        "2. la confirmation — ou l'infirmation — de l'énoncé de la règle ;",
        "3. les dérogations, exclusions et exemptions applicables, **recopiées telles",
        "   quelles** : une exception reformulée est une exception interprétée ;",
        "4. les renvois vers d'autres articles dont l'application dépend ;",
        "5. la signature : `verifie_par` et `date_verification` au dossier de",
        "   vérification. Sans elle, aucune règle ne progresse.",
        "",
    ]

    for ligne in concernees:
        regle = regles[ligne.rule_id]
        l += _fiche_lcbft(ligne, regle)
    return "\n".join(l) + "\n"


def _fiche_lcbft(ligne: LigneAction, regle: Rule) -> list[str]:
    """Une règle du pack : ce qu'on cherche, ce qu'on confirme, ce qui permet de signer."""
    affirmations = [
        claim.claim
        for claim in regle.negative_claims
        if claim.status is NegativeClaimStatus.UNVERIFIED
    ]
    l = [
        f"## `{regle.id}` — {regle.title}",
        "",
        f"- **Article exact** : {regle.source.article}",
        f"- **Disposition** : {regle.source.paragraph or 'article entier — aucun paragraphe désigné'}",
        f"- **Version / date** : version déclarée {regle.source.version_date.isoformat()} ; "
        f"règle applicable depuis le {regle.valid_from.isoformat()}",
        f"- **Statut actuel** : `{regle.status.value}` — inchangé par ce document",
        f"- **Emplacement déclaré** : {regle.source.url or '—'}",
        "",
        "**Énoncé de la règle, tel qu'il est enregistré**",
        "",
        f"> {regle.statement}",
        "",
        "**À confirmer sur le texte**",
        "",
        f"- « {regle.source.article} » porte-t-il bien cette obligation, dans ces termes ?",
        "- l'énoncé en dit-il plus, ou moins, que le texte ?",
        "- la version applicable à la date déclarée est-elle celle qui a été lue ?",
        "",
        "**Exceptions à rechercher**",
        "",
        f"- recherche d'exceptions à ce jour : `{regle.exceptions_status.value}` — "
        f"personne n'a cherché sur le texte",
        "- dérogations, exclusions, exemptions, seuils et régimes particuliers "
        "applicables à cette obligation, dans l'article **et ailleurs dans le code** ;",
        "- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas "
        "trouvé » ne vaut pas « il n'y en a pas ».",
        "",
    ]
    if affirmations:
        l += ["**Affirmations négatives à trancher**", ""]
        l += [f"- « {claim} »" for claim in affirmations]
        l += [""]
    l += [
        "**Résultat attendu pour pouvoir signer**",
        "",
        f"- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode "
        f"`primary_text_review`, `verifie_par` et `date_verification` ;",
        "- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;",
        "- `exceptions_statut` motivé, avec le périmètre couvert.",
        "",
        "---",
        "",
    ]
    return l


# --------------------------------------------------------------------------- #
# Réancrage d'une source
# --------------------------------------------------------------------------- #


def _portance(constat: ConstatCompletude | None) -> str:
    """Ce que l'audit a pu dire de la portance de l'énoncé — souvent : rien.

    Une portance ne se déduit pas d'un texte qu'on n'a pas lu. Dire « non
    établie » sans dire pourquoi laisserait croire à un énoncé jugé faible.
    """
    if constat is None or not constat.gold_ready_reason:
        return (
            "non calculée — la portance s'évalue sur le texte, et le texte n'a pas "
            "été lu"
        )
    if portance_etablie(constat):
        return "l'énoncé porte assez pour qu'un gold s'y adosse, une fois la source établie"
    return f"non établie — motif publié : « {constat.gold_ready_reason} »"


def dossier_reancrage(
    ligne: LigneAction,
    regle: Rule,
    obstacle: str,
    constat: ConstatCompletude | None,
    jour: dt.date,
) -> str:
    """`reports/AMF-R-005-SOURCE-REANCHORING.md`.

    Aucune URL de remplacement n'y est inscrite : en proposer une reviendrait à
    réancrer la règle sans que personne ait constaté que le document s'y trouve.
    """
    return "\n".join(
        [
            f"# `{regle.id}` — réancrage de source",
            "",
            f"Établi le {jour.isoformat()}. **Aucune URL n'est modifiée par ce document**,",
            "et aucune n'y est proposée comme acquise : le réancrage passe par le circuit",
            "de vérification, qui exige une consultation signée.",
            "",
            "## La règle",
            "",
            f"- **Identifiant** : `{regle.id}` — {regle.title}",
            f"- **Statut** : `{regle.status.value}` (inchangé)",
            f"- **Priorité de revue** : {ligne.priority}",
            f"- **Régime** : {regle.regulatory_regime}, applicable depuis le "
            f"{regle.valid_from.isoformat()}",
            "",
            "**Énoncé enregistré**",
            "",
            f"> {regle.statement}",
            "",
            "## URL actuelle",
            "",
            f"> {regle.source.url}",
            "",
            "## Pourquoi elle est invalide",
            "",
            f"> {obstacle or 'texte primaire non récupéré'}",
            "",
            "Ce n'est **pas** un refus d'accès : le serveur répond, et répond que la page",
            "n'existe pas. Le site de l'AMF a réorganisé son espace réglementaire ;",
            "l'URL enregistrée pointe vers un emplacement qui ne sert plus de document.",
            "Une consultation depuis un autre environnement donnerait le même résultat —",
            "il n'y a rien à y lire.",
            "",
            "## Document recherché",
            "",
            f"- **Titre exact tel que la règle le cite** : {regle.source.text}",
            f"- **Ancrage cité** : {regle.source.article}"
            + (f", {regle.source.paragraph}" if regle.source.paragraph else ""),
            f"- **Version déclarée** : {regle.source.version_date.isoformat()}",
            "- **Nature** : acte réglementaire homologué par arrêté, consolidé et publié",
            "  par l'Autorité des marchés financiers ; il se distingue de la doctrine, que",
            "  la règle mentionne précisément pour l'en distinguer.",
            "",
            "## Emplacement probable",
            "",
            "L'espace réglementaire du site de l'AMF (`amf-france.org`) reste joignable :",
            "la doctrine y a été récupérée pour d'autres règles. Le règlement général y",
            "est publié, mais **son emplacement courant n'a pas été constaté** : les deux",
            "chemins essayés rendent 404. Le relecteur doit donc établir l'emplacement,",
            "pas le supposer — et c'est l'emplacement constaté, non celui-ci, qui sera",
            "porté au dossier.",
            "",
            "Deux voies à considérer, dans cet ordre :",
            "",
            "1. la version consolidée publiée par l'AMF elle-même, qui fait foi ;",
            "2. à défaut, le texte homologué tel que publié au *Journal officiel*, qui",
            "   permet d'ancrer un article daté.",
            "",
            "## Méthode de réancrage",
            "",
            "1. constater l'emplacement du document et sa version consolidée ;",
            "2. vérifier que l'ancrage cité — "
            f"« {regle.source.article} » — y existe réellement ; l'audit relève déjà que",
            "   cet ancrage ne désigne aucun article précis, et qu'aucun gold ne pourrait",
            "   citer sa disposition en l'état ;",
            "3. porter au dossier de vérification : URL constatée, version, verdict,",
            "   `verifie_par`, `date_verification` ;",
            "4. appliquer le dossier (`finreg-bench rulebook appliquer-verification`) — la",
            "   correction fait avancer la version de la règle et `supersedes` nomme celle",
            "   qu'elle remplace ;",
            "5. rejouer l'audit, la complétude et l'exploitabilité.",
            "",
            "## Impact sur la règle",
            "",
            f"- **Blocage principal** : `{ligne.blocker}` — {ligne.source_access_status.value}",
            f"- **Action** : `{ligne.proposed_action.value}`",
            f"- **Après réancrage** : {ligne.expected_status_after_decision}",
            "- **Ancrage à découper** : « Règlement général » couvre l'acte entier. Même",
            "  réancrée, la règle ne portera pas de gold tant qu'elle ne citera pas un",
            "  article précis — le réancrage lève l'accès, pas l'imprécision.",
            "",
            f"- **Portance de l'énoncé** : {_portance(constat)}",
            "",
        ]
    )
