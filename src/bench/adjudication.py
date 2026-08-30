"""Dossiers d'arbitrage P0/P1 : transformer une demande de revue en décision tranchable.

La file de revue dit **qu'une** règle demande un juriste. Elle ne dit pas
assez : un relecteur qui l'ouvre doit encore deviner quelle disposition
examiner, quelle exception est suspectée, et ce qu'on attend de lui. Un dossier
d'arbitrage nomme les quatre :

| Champ | Ce qu'il donne au relecteur |
|---|---|
| `dispositions` | ce qu'il doit aller lire, et pourquoi |
| `perimetre_a_examiner` | jusqu'où il doit chercher pour qu'un « rien trouvé » vaille |
| `neutral_legal_question` | la question binaire qu'il tranche |
| `if_exception_exists` / `if_no_exception` | ce que sa réponse changera |

**Deux champs qu'il ne faut jamais mélanger.** `textual_facts` ne porte que ce
qui est écrit dans les sources — l'article existe, telle phrase y figure, telle
signature a été apposée. `interpretive_question` porte ce qui demande un
arbitrage. Les fondre rendrait un fait aussi contestable qu'une lecture, et une
lecture aussi opposable qu'un fait.

`mechanical_proposal` n'est **pas une conclusion juridique** : c'est ce que
l'automate a vu, dit dans un vocabulaire fermé, pour orienter la lecture. Une
règle sans structure limitante repérée ressort
`NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` — ce qui énonce le périmètre déjà
balayé, jamais l'absence d'exception.

Les décisions, elles, ne s'écrivent pas ici : `DecisionAdjudication` est un
schéma de lecture pour ce que le relecteur remplira. Le verrou de la
spécification §11 y est une validation — un `NONE_IDENTIFIED` sans périmètre
attesté est refusé — et non une consigne dans un rapport.
"""

from __future__ import annotations

import datetime as dt
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum

from pydantic import Field, model_validator

from src.bench.completude import PREREQUIS_GOLD, ConstatCompletude
from src.bench.modeles import ModeleStrict
from src.bench.readiness import BlockerCategory, ConstatReadiness
from src.bench.regles import Rule
from src.bench.rulebook import ExceptionsStatus, NegativeClaimStatus

#: Priorités traitées par un pack d'arbitrage. P2 et P3 attendent : arbitrer
#: dans l'ordre de la gravité, c'est refuser de payer une revue au même prix
#: qu'elle coûte peu.
PRIORITES_ARBITREES: tuple[str, ...] = ("P0", "P1")


class PropositionMecanique(str, Enum):
    """Ce que l'automate a vu, dans un vocabulaire fermé. Jamais une conclusion."""

    #: Le périmètre déjà balayé ne contient pas de structure limitante. Ce n'est
    #: pas « il n'y a pas d'exception » : c'est « il n'y en a pas **ici** ».
    NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE = "NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE"
    #: Une structure limitante a été repérée dans le texte : elle vise peut-être
    #: cette règle, peut-être une obligation voisine.
    EXCEPTION_LIKELY = "EXCEPTION_LIKELY"
    #: Quelque chose limite, mais on ne sait pas quoi : renvoi non résolu,
    #: structure sans phrase isolable, ancrage couvrant plusieurs articles.
    EXCEPTION_SCOPE_UNCLEAR = "EXCEPTION_SCOPE_UNCLEAR"
    #: Le blocage n'est pas une exception mais l'énoncé lui-même.
    RULE_NEEDS_REFORMULATION = "RULE_NEEDS_REFORMULATION"
    #: Le périmètre lu ne fonde pas la décision : soit le texte primaire n'a pas
    #: pu être récupéré, soit la question porte sur une absence, qui ne s'établit
    #: pas sur le seul article cité.
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"


class DecisionRelecteur(str, Enum):
    """Les quatre issues d'un arbitrage. Aucune n'est attribuée automatiquement."""

    NONE_IDENTIFIED = "NONE_IDENTIFIED"
    IDENTIFIED_AND_INCORPORATED = "IDENTIFIED_AND_INCORPORATED"
    RULE_REFORMULATED = "RULE_REFORMULATED"
    REQUIRES_FURTHER_REVIEW = "REQUIRES_FURTHER_REVIEW"


#: Abréviations de catégorie pour l'identifiant de regroupement. Deux règles ne
#: partagent un dossier que si elles posent la même question sur la même
#: disposition : la catégorie fait donc partie de la clé.
ABREVIATION_CATEGORIE: dict[BlockerCategory, str] = {
    BlockerCategory.EXCEPTION_UNRESOLVED: "EXC",
    BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED: "NEG",
    BlockerCategory.CROSS_REFERENCE_UNRESOLVED: "RNV",
    BlockerCategory.TEMPORAL_UNRESOLVED: "TMP",
    BlockerCategory.SOURCE_INCOMPLETE: "SRC",
    BlockerCategory.RULE_TOO_ABSTRACT: "ABS",
    BlockerCategory.SCHEMA_INCOMPLETE: "SCH",
    BlockerCategory.HUMAN_REVIEW_REQUIRED: "HRV",
    BlockerCategory.OTHER: "AUT",
}


@dataclass(frozen=True)
class DispositionExaminee:
    """Une disposition que le relecteur doit aller lire, et ce qu'on en attend."""

    reference: str
    #: Pourquoi elle est potentiellement pertinente — un constat, pas une lecture.
    pertinence: str
    #: Sa relation supposée avec la règle : exception, condition, régime particulier…
    relation: str


@dataclass(frozen=True)
class Dossier:
    """Un arbitrage à rendre : la règle, ce qu'on sait, et la question exacte.

    Les champs de décision n'existent pas ici. Un dossier qui porterait un
    `reviewer_decision` pourrait le porter pré-rempli, et l'arbitrage humain
    deviendrait une case à cocher sur un avis déjà écrit — c'est
    `DecisionAdjudication`, relu depuis le dossier rempli, qui les porte.
    """

    rule_id: str
    domain: str
    version: int
    current_status: str
    current_statement: str

    source_texte: str
    source_article: str
    source_paragraphe: str
    source_version: str
    source_date_applicable: str
    source_url: str

    priorite_revue: str
    blocage: str
    blocage_categorie: BlockerCategory
    review_cluster_id: str

    dispositions: tuple[DispositionExaminee, ...]
    perimetre_a_examiner: str
    textual_facts: tuple[str, ...]
    interpretive_question: str
    neutral_legal_question: str
    mechanical_proposal: PropositionMecanique
    if_exception_exists: str
    if_no_exception: str
    #: Les autres blocages de la règle. La question porte sur le plus fondamental,
    #: mais la priorité P0 tient souvent à l'un de ceux-là : les taire ferait
    #: croire qu'une règle est réglée dès que sa source est établie.
    blocages_restants: tuple[str, ...] = ()
    extrait_officiel: str = ""


# --------------------------------------------------------------------------- #
# Identifiant de regroupement
# --------------------------------------------------------------------------- #

CELEX = re.compile(r"\b([13]\d{4}[A-Z]\d{4})\b")
#: Référence de doctrine (« DOC-2020-03 ») : elle identifie une position AMF
#: aussi précisément qu'un CELEX identifie un acte de l'Union.
REFERENCE_DOCTRINE = re.compile(r"\bDOC-\d{4}-\d{2}\b", re.IGNORECASE)
#: Mots vides d'un intitulé d'acte : ils n'y distinguent rien.
MOTS_VIDES = frozenset(
    {"DE", "DU", "DES", "LA", "LE", "LES", "ET", "L", "D", "UE", "N", "AU", "AUX"}
)


def _sans_accent(texte: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texte) if unicodedata.category(c) != "Mn"
    )


def _acte_normalise(regle: Rule) -> str:
    """Le CELEX de l'acte s'il existe, sinon sa référence, sinon ses initiales.

    Le CELEX est ce qui identifie un acte sans ambiguïté : deux règles qui le
    partagent citent le même texte, quelle que soit la façon dont leur `source`
    l'intitule. À défaut — doctrine nationale, code — l'abrégé doit rester
    stable et reconnaissable : « Code monétaire et financier » donne `CMF`, pas
    trois mots tronqués au hasard.
    """
    for candidat in (regle.source.url, regle.source.text):
        trouve = CELEX.search(candidat or "")
        if trouve:
            return trouve.group(1)
    reference = REFERENCE_DOCTRINE.search(regle.source.text or "")
    if reference:
        return reference.group(0).upper()
    mots = [
        mot
        for mot in re.findall(r"[A-Za-z0-9]+", _sans_accent(regle.source.text).upper())
        if mot not in MOTS_VIDES
    ]
    if not mots:
        return "ACTE"
    return "".join(mot[0] for mot in mots)[:8]


def _ancrage_normalise(article: str) -> str:
    """« Article 25 » → `ART25` ; « Article L. 561-2 » → `ARTL561-2`."""
    nettoye = re.sub(r"^\s*articles?\s*", "", _sans_accent(article or ""), flags=re.IGNORECASE)
    nettoye = re.sub(r"[^A-Za-z0-9-]+", "-", nettoye).strip("-").upper()
    return f"ART{nettoye[:24].rstrip('-')}" if nettoye else "ACTE"


def cluster_id(regle: Rule, categorie: BlockerCategory) -> str:
    """Regroupe les règles qui posent la même question sur la même disposition.

    Le regroupement ne fusionne rien : les règles restent distinctes dans le
    Rulebook, et chacune garde sa décision. Il évite seulement de faire trancher
    trois fois le même point à propos du même article.
    """
    return (
        f"CL-{_acte_normalise(regle)}-{_ancrage_normalise(regle.source.article)}-"
        f"{ABREVIATION_CATEGORIE.get(categorie, 'AUT')}"
    )


# --------------------------------------------------------------------------- #
# Ce que le relecteur doit aller lire
# --------------------------------------------------------------------------- #


def dispositions_a_examiner(
    regle: Rule, constat: ConstatCompletude, par_id: dict[str, Rule]
) -> tuple[DispositionExaminee, ...]:
    """Les dispositions susceptibles de limiter, conditionner ou déplacer la règle.

    Aucune n'est présentée comme une exception : elles sont **candidates**, et
    la raison donnée est toujours un constat de l'automate — une structure
    repérée, un renvoi relevé, un article voisin cité par une autre règle.
    """
    dispositions: list[DispositionExaminee] = []

    for phrase in constat.exceptions_extraites:
        dispositions.append(
            DispositionExaminee(
                reference=f"{regle.source.article} — phrase recopiée du texte officiel",
                pertinence=(
                    f"porte une structure limitante repérée par l'analyse : "
                    f"« {phrase[:220]} »"
                ),
                relation="limite peut-être la portée de l'obligation énoncée",
            )
        )

    for renvoi in constat.renvois:
        dispositions.append(
            DispositionExaminee(
                reference=f"Article {renvoi} de {regle.source.text}",
                pertinence=f"{regle.source.article} y renvoie explicitement",
                relation="peut conditionner l'application de la règle",
            )
        )

    for autre_id in regle.related_rules:
        autre = par_id.get(autre_id)
        if autre is None or autre.source.article == regle.source.article:
            continue
        dispositions.append(
            DispositionExaminee(
                reference=f"{autre.source.article} de {autre.source.text} (règle {autre_id})",
                pertinence=(
                    f"règle rattachée du Rulebook, sur une autre disposition : "
                    f"« {autre.title} »"
                ),
                relation="régime voisin, susceptible de poser une exception ou un cas particulier",
            )
        )

    for secondaire in regle.secondary_sources:
        dispositions.append(
            DispositionExaminee(
                reference=secondaire,
                pertinence="source secondaire citée par la règle",
                relation="peut signaler une condition d'application non portée par l'énoncé",
            )
        )

    if not dispositions:
        dispositions.append(
            DispositionExaminee(
                reference=f"{regle.source.text} — hors {regle.source.article}",
                pertinence=(
                    "l'analyse n'a repéré aucune disposition candidate dans l'article "
                    "cité : il n'y a donc rien à confirmer, seulement un périmètre à balayer"
                ),
                relation="périmètre de recherche, aucune disposition désignée",
            )
        )
    return tuple(dispositions)


def perimetre_a_examiner(regle: Rule, categorie: BlockerCategory) -> str:
    """Le périmètre dont la couverture rend un « rien trouvé » opposable.

    Sans lui, `none_identified` signifierait « je n'ai pas vu », ce que le
    Rulebook refuse depuis le début pour les affirmations négatives.
    """
    acte = regle.source.text
    article = regle.source.article or "l'article cité"
    version = regle.source.version_date.isoformat()
    if categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED:
        return (
            f"{acte} entier dans sa version applicable au {version}, et non le seul "
            f"{article} : une absence ne s'établit pas sur un extrait"
        )
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED:
        return f"les articles auxquels {article} renvoie, dans {acte} au {version}"
    if categorie is BlockerCategory.TEMPORAL_UNRESOLVED:
        return (
            f"les versions successives de {acte} couvrant {article}, et la date de "
            f"consolidation applicable"
        )
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return (
            f"{article} de {acte}, consulté hors de cet environnement d'exécution "
            f"(le texte primaire n'y est pas atteignable)"
        )
    return (
        f"{acte} entier au {version} — articles autres que {article} compris — ainsi "
        f"que les actes délégués et d'exécution pris sur son fondement"
    )


# --------------------------------------------------------------------------- #
# Faits, question binaire, question interprétative
# --------------------------------------------------------------------------- #


def faits_textuels(
    regle: Rule, constat: ConstatCompletude, extrait: str
) -> tuple[str, ...]:
    """Uniquement ce qui est écrit — dans les sources ou dans le registre.

    Rien de ce qui figure ici ne demande une lecture : un fait qui se discute
    n'est pas un fait, c'est la question posée plus bas.
    """
    faits: list[str] = []
    if regle.source.is_verified:
        faits.append(
            f"source consultée et signée le {regle.source.verification_date} par "
            f"{regle.source.verified_by} (méthode : {regle.verification_method.value})"
        )
    else:
        faits.append("aucune consultation signée de la source primaire")

    if constat.criteres:
        faits.append(
            f"« {regle.source.article} » "
            + ("existe dans l'acte cité" if constat.criteres.get("article_verifie") else "n'a pas été retrouvé dans l'acte cité")
        )
        faits.append(
            "le vocabulaire de l'énoncé "
            + ("se retrouve dans l'article" if constat.criteres.get("enonce_fidele") else "ne se retrouve pas dans l'article")
        )
    else:
        faits.append("le texte de l'article n'a pas pu être lu : aucun critère n'a été coché")

    if constat.structures:
        faits.append(
            "structures juridiques repérées dans l'article : "
            + ", ".join(s.value for s in constat.structures)
        )
    else:
        faits.append("aucune structure juridique repérée dans l'article cité")

    if constat.exceptions_extraites:
        faits.append(
            f"{len(constat.exceptions_extraites)} phrase(s) limitante(s) recopiée(s) "
            f"telles quelles du texte officiel"
        )
    if constat.renvois:
        faits.append("renvois relevés dans l'article : " + ", ".join(constat.renvois))

    faits.append(f"recherche d'exceptions à ce jour : « {constat.exceptions_status.value} »")
    faits.append(
        f"statut réglementaire « {regle.regulatory_status.value} », en vigueur depuis le "
        f"{regle.valid_from.isoformat()}"
        + (f", jusqu'au {regle.valid_until.isoformat()}" if regle.valid_until else "")
    )

    en_suspens = [c for c in regle.negative_claims if c.status is NegativeClaimStatus.UNVERIFIED]
    for claim in en_suspens:
        faits.append(f"affirmation négative non vérifiée : « {claim.claim[:200]} »")

    faits.append(
        f"extrait officiel disponible ({len(extrait)} caractères)"
        if extrait
        else "aucun extrait officiel disponible : le texte n'a pas été récupéré"
    )
    return tuple(faits)


def question_neutre(regle: Rule, constat: ConstatCompletude, categorie: BlockerCategory) -> str:
    """UNE question, binaire, tranchable sur le texte, sans conseil juridique."""
    acte = regle.source.text
    article = regle.source.article or "l'article cité"

    if categorie is BlockerCategory.EXCEPTION_UNRESOLVED:
        if constat.exceptions_status is ExceptionsStatus.IDENTIFIED_BUT_NOT_INCORPORATED:
            return (
                f"Les structures limitantes repérées dans {article} de {acte} "
                f"restreignent-elles l'obligation qu'énonce {regle.id}, ou visent-elles "
                f"une obligation distincte posée par le même article ?"
            )
        return (
            f"Une dérogation, exclusion, exemption ou condition applicable à {regle.id} "
            f"existe-t-elle dans le périmètre indiqué — {article}, un autre article de "
            f"{acte}, ou un acte pris sur son fondement — ou n'en existe-t-il aucune "
            f"dans ce périmètre ?"
        )
    if categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED:
        claims = [c.claim for c in regle.negative_claims if c.status is NegativeClaimStatus.UNVERIFIED]
        affirmation = claims[0] if claims else "l'affirmation négative portée par la règle"
        return (
            f"« {affirmation[:200]} » : cette disposition est-elle absente de {acte} "
            f"dans le périmètre indiqué, ou une disposition la porte-t-elle ?"
        )
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED:
        renvois = ", ".join(constat.renvois[:5]) or "auxquels l'article renvoie"
        return (
            f"Les articles {renvois} conditionnent-ils l'application de {regle.id}, ou "
            f"s'agit-il de renvois sans incidence sur la portée de la règle ?"
        )
    if categorie is BlockerCategory.TEMPORAL_UNRESOLVED:
        return (
            f"La version de {acte} qui fait foi pour {regle.id} est-elle celle déclarée "
            f"au {regle.source.version_date.isoformat()}, ou une version consolidée "
            f"postérieure s'applique-t-elle à {article} ?"
        )
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return (
            f"Le texte de {article} de {acte}, consulté hors de cet environnement, "
            f"soutient-il l'énoncé de {regle.id}, ou l'énoncé vise-t-il une autre "
            f"disposition ?"
        )
    if categorie is BlockerCategory.RULE_TOO_ABSTRACT:
        return (
            f"L'énoncé de {regle.id} peut-il être reformulé au plus près de la lettre "
            f"de {article} sans ajouter d'interprétation, ou la règle doit-elle être "
            f"découpée en plusieurs règles ancrées chacune sur leur paragraphe ?"
        )
    if categorie is BlockerCategory.HUMAN_REVIEW_REQUIRED:
        return (
            f"L'énoncé de {regle.id} est-il soutenu par {article} de {acte} tel qu'il "
            f"est rédigé, ou doit-il être corrigé avant toute validation ?"
        )
    return (
        f"Le blocage « {categorie.value} » sur {regle.id} tient-il à l'énoncé de la "
        f"règle, ou à ce que le Rulebook n'a pas encore établi de son texte ?"
    )


def question_interpretative(regle: Rule, categorie: BlockerCategory) -> str:
    """Ce que l'automate ne peut pas trancher, et pourquoi il ne le peut pas."""
    if categorie is BlockerCategory.EXCEPTION_UNRESOLVED:
        return (
            "Déterminer si une disposition limitante vise l'obligation énoncée ici ou "
            "une obligation voisine relève d'une lecture juridique : l'analyse ne "
            "compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle "
            "obligation une dérogation se rapporte."
        )
    if categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED:
        return (
            "Établir qu'une disposition est absente suppose d'avoir couvert un périmètre "
            "et de l'attester : l'analyse peut dire qu'elle n'a pas trouvé, jamais que "
            "cela n'existe pas."
        )
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED:
        return (
            "Savoir si un renvoi conditionne l'application de la règle ou l'accompagne "
            "sans la restreindre demande de lire les deux articles ensemble — l'analyse "
            "relève le renvoi, elle n'en pèse pas la portée."
        )
    if categorie is BlockerCategory.TEMPORAL_UNRESOLVED:
        return (
            "Choisir la version applicable engage la date à laquelle une question se "
            "placera : l'analyse constate qu'aucune consolidation ne correspond à la "
            "date déclarée, elle ne désigne pas celle qui fait foi."
        )
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return (
            "Le texte primaire n'est pas atteignable depuis cet environnement : aucune "
            "vérification mécanique n'est possible, et la consultation doit être faite "
            "puis signée par un humain."
        )
    if categorie is BlockerCategory.RULE_TOO_ABSTRACT:
        return (
            "Reformuler au plus près de la lettre suppose de décider ce que l'énoncé "
            "doit conserver : l'analyse mesure la portance d'une formulation, elle "
            "n'écrit pas celle qui la remplacerait."
        )
    return (
        "Le passage à « validated » engage la responsabilité de qui l'atteste : "
        "aucun automate ne se l'accorde."
    )


def proposition_mecanique(
    constat: ConstatCompletude, categorie: BlockerCategory
) -> PropositionMecanique:
    """Ce que l'automate a vu, traduit dans le vocabulaire fermé. Pas une conclusion."""
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return PropositionMecanique.INSUFFICIENT_SOURCE
    if categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED:
        return PropositionMecanique.INSUFFICIENT_SOURCE
    if categorie is BlockerCategory.RULE_TOO_ABSTRACT:
        return PropositionMecanique.RULE_NEEDS_REFORMULATION
    if categorie is BlockerCategory.HUMAN_REVIEW_REQUIRED:
        return PropositionMecanique.RULE_NEEDS_REFORMULATION
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED:
        return PropositionMecanique.EXCEPTION_SCOPE_UNCLEAR
    if categorie is BlockerCategory.TEMPORAL_UNRESOLVED:
        return PropositionMecanique.EXCEPTION_SCOPE_UNCLEAR
    if categorie is BlockerCategory.EXCEPTION_UNRESOLVED:
        if constat.exceptions_status is ExceptionsStatus.IDENTIFIED_BUT_NOT_INCORPORATED:
            return PropositionMecanique.EXCEPTION_LIKELY
        if constat.exceptions_status is ExceptionsStatus.UNKNOWN:
            return PropositionMecanique.INSUFFICIENT_SOURCE
        return PropositionMecanique.NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE
    return PropositionMecanique.EXCEPTION_SCOPE_UNCLEAR


def impacts(regle: Rule, categorie: BlockerCategory) -> tuple[str, str]:
    """Ce que chaque issue changerait pour les futurs items — sans les concevoir."""
    suite = (
        f"la règle est reversionnée (v{regle.version + 1}, `supersedes` nommant la "
        f"version remplacée) et tout item déjà ancré dessus est à reversionner"
    )
    if categorie is BlockerCategory.EXCEPTION_UNRESOLVED:
        return (
            f"l'exception est recopiée dans `exceptions`, `exceptions_status` passe à "
            f"« identified_and_incorporated » et {suite} ; un item qui testerait la "
            f"règle comme un absolu compterait en erreur un modèle qui mentionne la "
            f"dérogation",
            "`exceptions_status` passe à « none_identified » avec le périmètre attesté ; "
            "la règle peut alors porter des items qui la testent sans réserve, et "
            "`gold_ready` est recalculé — il ne devient pas vrai pour autant",
        )
    if categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED:
        return (
            f"l'affirmation passe « present_contrary » : la fausse prémisse prévue "
            f"était vraie, l'item l'aurait comptée à l'envers, et {suite}",
            "l'affirmation passe « verified_absent » avec `searched_in` : elle peut "
            "porter une fausse prémisse opposable",
        )
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED:
        return (
            f"le renvoi conditionne la règle : son contenu doit être rattaché à "
            f"l'énoncé, et {suite}",
            "les renvois sont attestés sans incidence : la règle s'applique telle "
            "qu'énoncée et `renvois_verifies` est tenu",
        )
    if categorie is BlockerCategory.TEMPORAL_UNRESOLVED:
        return (
            f"une version consolidée postérieure fait foi : la date d'appréciation des "
            f"items change, et {suite}",
            "la version déclarée fait foi : les items se placent à cette date sans "
            "réserve",
        )
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return (
            f"le texte consulté contredit l'énoncé : {suite}",
            "le texte consulté soutient l'énoncé : la consultation est portée au "
            "dossier de vérification et la règle peut progresser",
        )
    if categorie is BlockerCategory.RULE_TOO_ABSTRACT:
        return (
            f"la règle est reformulée ou découpée : {suite}, et chaque règle issue du "
            f"découpage cite son propre paragraphe",
            "l'énoncé est tenu pour assez porteur : un gold peut s'y adosser sans "
            "réinterpréter le droit",
        )
    return (
        f"la règle est corrigée avant validation : {suite}",
        "la règle est validée en l'état, et son exploitabilité est recalculée",
    )


# --------------------------------------------------------------------------- #
# Construction du pack
# --------------------------------------------------------------------------- #


def _blocages_restants(
    constat: ConstatCompletude, etat: ConstatReadiness, principal
) -> tuple[str, ...]:
    """Les autres blocages, dédoublonnés — et rien qui n'ait été réellement constaté.

    Quand le texte n'a pas pu être lu, aucun prérequis n'a été évalué : les
    afficher comme autant de blocages distincts ferait passer des conséquences
    d'une source manquante pour des constats propres (« 0 affirmation négative
    non vérifiée » en est le cas caricatural). Il n'en reste alors que ce qui se
    lit sur la règle elle-même.
    """
    texte_non_lu = not constat.criteres_gold
    vus: set[tuple[str, str]] = set()
    restants: list[str] = []
    for blocage in etat.blocages:
        if blocage is principal:
            continue
        if texte_non_lu and blocage.critere in PREREQUIS_GOLD:
            continue
        cle = (blocage.category.value, blocage.critere)
        if cle in vus:
            continue
        vus.add(cle)
        restants.append(f"`{blocage.category.value}` ({blocage.critere}) — {blocage.explanation}")
    return tuple(restants)


def construire(
    regle: Rule,
    constat: ConstatCompletude,
    etat: ConstatReadiness,
    extrait: str,
    par_id: dict[str, Rule],
) -> Dossier:
    """Un dossier d'arbitrage pour une règle, sans aucun champ de décision."""
    principal = etat.blocage_principal
    categorie = principal.category if principal else BlockerCategory.OTHER
    si_exception, si_aucune = impacts(regle, categorie)
    restants = _blocages_restants(constat, etat, principal)
    return Dossier(
        rule_id=regle.id,
        domain=regle.domain.value,
        version=regle.version,
        current_status=regle.status.value,
        current_statement=regle.statement,
        source_texte=regle.source.text,
        source_article=regle.source.article,
        source_paragraphe=regle.source.paragraph,
        source_version=regle.source.version_date.isoformat(),
        source_date_applicable=regle.valid_from.isoformat(),
        source_url=regle.source.url,
        priorite_revue=etat.priorite_revue,
        blocage=etat.family_blocker,
        blocage_categorie=categorie,
        review_cluster_id=cluster_id(regle, categorie),
        dispositions=dispositions_a_examiner(regle, constat, par_id),
        perimetre_a_examiner=perimetre_a_examiner(regle, categorie),
        textual_facts=faits_textuels(regle, constat, extrait),
        interpretive_question=question_interpretative(regle, categorie),
        neutral_legal_question=question_neutre(regle, constat, categorie),
        mechanical_proposal=proposition_mecanique(constat, categorie),
        if_exception_exists=si_exception,
        if_no_exception=si_aucune,
        blocages_restants=restants,
        extrait_officiel=extrait,
    )


def preparer(
    regles: list[Rule],
    constats: dict[str, ConstatCompletude],
    etats: dict[str, ConstatReadiness],
    extraits: dict[str, str],
    priorites: tuple[str, ...] = PRIORITES_ARBITREES,
) -> list[Dossier]:
    """Les dossiers des priorités demandées, classés par priorité, domaine puis ID."""
    par_id = {r.id: r for r in regles}
    ordre = {p: i for i, p in enumerate(priorites)}
    dossiers = [
        construire(regle, constats[regle.id], etats[regle.id], extraits.get(regle.id, ""), par_id)
        for regle in regles
        if etats[regle.id].priorite_revue in priorites
    ]
    return sorted(
        dossiers, key=lambda d: (ordre[d.priorite_revue], d.domain, d.rule_id)
    )


def regroupements(dossiers: list[Dossier]) -> dict[str, list[Dossier]]:
    """Les regroupements de plus d'un dossier, dans l'ordre des identifiants.

    Un regroupement partage une **question**, jamais une règle : chaque règle
    garde sa décision, son énoncé et sa version. Fusionner les règles ferait
    disparaître des obligations distinctes derrière un article commun.
    """
    par_cluster: dict[str, list[Dossier]] = {}
    for dossier in dossiers:
        par_cluster.setdefault(dossier.review_cluster_id, []).append(dossier)
    return {c: d for c, d in sorted(par_cluster.items()) if len(d) > 1}


# --------------------------------------------------------------------------- #
# Ce que le relecteur rend (§7, §11)
# --------------------------------------------------------------------------- #


class DecisionAdjudication(ModeleStrict):
    """Une décision humaine, relue depuis le dossier rempli.

    Le schéma porte le verrou de la spécification §11 : un « je n'ai pas trouvé
    d'exception » n'est recevable que si le périmètre réellement examiné est
    attesté. C'est la même règle que pour les affirmations négatives, et elle
    est ici une validation — pas une consigne dans un rapport.
    """

    rule_id: str = Field(min_length=1)
    reviewer_decision: DecisionRelecteur
    reviewer_name: str = ""
    review_date: dt.date | None = None
    review_notes: str = ""
    #: Le périmètre réellement examiné. Obligatoire pour `NONE_IDENTIFIED`.
    source_scope: str = ""
    #: Les exceptions constatées, recopiées du texte officiel, jamais reformulées.
    exceptions_constatees: list[str] = Field(default_factory=list)
    #: L'énoncé de remplacement, pour une reformulation.
    enonce_reformule: str = ""

    @model_validator(mode="after")
    def _une_decision_est_signee(self) -> DecisionAdjudication:
        if not self.reviewer_name.strip() or self.review_date is None:
            raise ValueError(
                f"{self.rule_id} : une décision d'arbitrage exige reviewer_name et "
                f"review_date — une décision anonyme n'est opposable à personne"
            )
        return self

    @model_validator(mode="after")
    def _absence_attestee(self) -> DecisionAdjudication:
        if self.reviewer_decision is DecisionRelecteur.NONE_IDENTIFIED and not self.source_scope.strip():
            raise ValueError(
                f"{self.rule_id} : « NONE_IDENTIFIED » exige source_scope — sans le "
                f"périmètre examiné, « je n'ai pas trouvé » ne vaut pas « il n'y en a pas »"
            )
        return self

    @model_validator(mode="after")
    def _incorporer_c_est_ecrire(self) -> DecisionAdjudication:
        if self.reviewer_decision is DecisionRelecteur.IDENTIFIED_AND_INCORPORATED and not [
            e for e in self.exceptions_constatees if e.strip()
        ]:
            raise ValueError(
                f"{self.rule_id} : « IDENTIFIED_AND_INCORPORATED » exige les exceptions "
                f"recopiées du texte officiel — incorporer une exception, c'est l'écrire"
            )
        if self.reviewer_decision is DecisionRelecteur.RULE_REFORMULATED and not self.enonce_reformule.strip():
            raise ValueError(
                f"{self.rule_id} : « RULE_REFORMULATED » exige enonce_reformule"
            )
        if self.reviewer_decision is DecisionRelecteur.REQUIRES_FURTHER_REVIEW and not self.review_notes.strip():
            raise ValueError(
                f"{self.rule_id} : « REQUIRES_FURTHER_REVIEW » exige review_notes — "
                f"renvoyer un dossier sans dire ce qui manque ne le fait pas avancer"
            )
        return self
