"""Dossiers d'arbitrage : transformer une demande de revue en décision précise.

La file de revue disait déjà **quoi** trancher. Elle ne disait pas **où
regarder**. Un relecteur à qui l'on demande « cet article comporte-t-il des
dérogations ailleurs dans l'acte ? » doit relire l'acte entier ; ce module va
les chercher pour lui et les lui présente, avec la raison de les suspecter.

Trois séparations que ce module ne franchit jamais :

- **le texte et son interprétation.** `TEXTUAL_FACTS` ne contient que des
  phrases du texte officiel et des constats mécaniques (tel article cite tel
  autre) ; `INTERPRETIVE_QUESTION` porte tout ce qui demande un jugement. Les
  mélanger ferait passer une hypothèse pour un fait établi ;
- **la proposition et la conclusion.** `mechanical_proposal` dit ce que la
  recherche automatique a trouvé, dans le vocabulaire de la recherche, jamais
  dans celui du droit : `EXCEPTION_LIKELY` signifie « une disposition limitante
  cite cet article », pas « il existe une exception » ;
- **le dossier et la règle.** Deux règles peuvent partager un dossier
  (`review_cluster_id`) quand la même disposition commande leur sort. Elles ne
  sont jamais fusionnées dans le Rulebook pour autant : c'est l'arbitrage qui
  est mutualisé, pas la règle.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from src.bench.completude import (
    ConstatCompletude,
    MARQUES,
    STRUCTURES_LIMITANTES,
    Structure,
)
from src.bench.readiness import BlockerCategory, ConstatReadiness
from src.bench.regles import Rule
from src.bench.rulebook import NegativeClaimStatus


class PropositionMecanique(str, Enum):
    """Ce que la recherche automatique a trouvé — jamais ce que le droit dit."""

    NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE = "NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE"
    EXCEPTION_LIKELY = "EXCEPTION_LIKELY"
    EXCEPTION_SCOPE_UNCLEAR = "EXCEPTION_SCOPE_UNCLEAR"
    RULE_NEEDS_REFORMULATION = "RULE_NEEDS_REFORMULATION"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"


class DecisionRevue(str, Enum):
    """Ce que le relecteur peut décider. Jamais renseigné automatiquement."""

    NONE_IDENTIFIED = "NONE_IDENTIFIED"
    IDENTIFIED_AND_INCORPORATED = "IDENTIFIED_AND_INCORPORATED"
    RULE_REFORMULATED = "RULE_REFORMULATED"
    REQUIRES_FURTHER_REVIEW = "REQUIRES_FURTHER_REVIEW"


#: Nombre maximal de dispositions proposées à l'examen. Au-delà, le dossier
#: cesse d'être un point d'entrée et redevient une relecture de l'acte.
MAX_DISPOSITIONS = 6

#: Longueur de l'extrait d'une disposition de soutien.
LONGUEUR_EXTRAIT = 420

#: Marques limitantes, toutes structures confondues.
MARQUES_LIMITANTES: tuple[str, ...] = tuple(
    marque for structure in STRUCTURES_LIMITANTES for marque in MARQUES[structure]
)

#: Une disposition qui déroge à l'acte entier concerne toutes ses règles.
MARQUES_PORTEE_GENERALE = (
    r"présent règlement",
    r"présente directive",
    r"du présent chapitre",
    r"de la présente section",
)


@dataclass(frozen=True)
class DispositionSoutien:
    """Une disposition qui pourrait limiter la portée de la règle."""

    article: str
    #: Pourquoi la recherche l'a retenue — un constat, pas une appréciation.
    motif: str
    #: Ce qui la relie à la règle : citation explicite, ou portée générale.
    relation: str
    extrait: str
    cite_larticle: bool = False


@dataclass(frozen=True)
class DossierRevue:
    """Le dossier soumis au relecteur pour une règle."""

    rule_id: str
    domain: str
    version: int
    status: str
    priorite: str
    statement: str
    source_text: str
    source_article: str
    source_paragraph: str
    source_version_date: str
    source_url: str
    applicable_from: str

    dispositions: tuple[DispositionSoutien, ...] = ()
    textual_facts: tuple[str, ...] = ()
    interpretive_question: str = ""
    neutral_legal_question: str = ""
    mechanical_proposal: PropositionMecanique = (
        PropositionMecanique.EXCEPTION_SCOPE_UNCLEAR
    )
    review_cluster_id: str = ""
    #: Périmètre que le relecteur est prié d'examiner. C'est lui qu'il devra
    #: attester s'il conclut à l'absence d'exception.
    source_scope: str = ""
    if_exception_exists: str = ""
    if_no_exception: str = ""
    blocker_category: str = ""


#: « Les articles 5 à 15 ne s'appliquent pas » : un intervalle cite chacun des
#: articles qu'il couvre. Le lire comme une simple mention ferait manquer la
#: dérogation la plus explicite qu'un acte puisse porter.
INTERVALLE_CITE = re.compile(r"articles?\s+(\d+)\s*(?:à|-|–)\s*(\d+)", re.IGNORECASE)

#: « aux articles 5, 8 et 12 » : une énumération cite chacun d'eux.
ENUMERATION_CITEE = re.compile(
    r"articles?\s+((?:\d+\s*(?:,|et)\s*)+\d+)", re.IGNORECASE
)


def _cite_larticle(texte: str, cle: str) -> bool:
    """Le texte renvoie-t-il explicitement à l'article de la règle ?

    Trois formes de citation, et les trois comptent : la mention directe,
    l'intervalle (« articles 5 à 15 ») et l'énumération (« articles 5, 8 et
    12 »). Ne reconnaître que la première ferait passer pour une dérogation
    générale ce qui est en réalité une exclusion nominative.
    """
    if not cle or not cle.isdigit():
        return bool(cle) and re.search(
            rf"article\s+(?:premier|{re.escape(cle)})\b", texte, re.IGNORECASE
        ) is not None

    numero = int(cle)
    if re.search(rf"article\s+(?:premier|{numero})\b", texte, re.IGNORECASE):
        return True
    for intervalle in INTERVALLE_CITE.finditer(texte):
        debut, fin = int(intervalle.group(1)), int(intervalle.group(2))
        if debut <= numero <= fin:
            return True
    for enumeration in ENUMERATION_CITEE.finditer(texte):
        if numero in {int(n) for n in re.findall(r"\d+", enumeration.group(1))}:
            return True
    return False


def _marques_trouvees(texte: str) -> list[str]:
    return [m for m in MARQUES_LIMITANTES if re.search(m, texte, re.IGNORECASE)]


def _phrases(texte: str) -> list[str]:
    return re.split(r"(?<=[.;])\s+", texte)


def _limite_la_portee_generale(texte: str) -> bool:
    """Une phrase qui limite l'application de l'acte lui-même, pas une autre matière."""
    for phrase in _phrases(texte):
        if not _marques_trouvees(phrase):
            continue
        if any(re.search(m, phrase, re.IGNORECASE) for m in MARQUES_PORTEE_GENERALE):
            return True
    return False


def _extrait_limitant(texte: str) -> str:
    """La première phrase limitante du texte, recopiée."""
    for phrase in _phrases(texte):
        if len(phrase) > 40 and _marques_trouvees(phrase):
            return phrase[:LONGUEUR_EXTRAIT].strip()
    return texte[:LONGUEUR_EXTRAIT].strip()


def dispositions_de_soutien(
    articles: dict[str, str], cle_article: str
) -> list[DispositionSoutien]:
    """Dispositions de l'acte qui pourraient limiter la portée de l'article cité.

    Deux titres à figurer au dossier, et un seul suffit : citer explicitement
    l'article de la règle, ou déroger à l'acte entier. Les dispositions qui
    dérogent à autre chose ne sont pas retenues — un dossier qui listerait tout
    l'acte ne ferait pas gagner de temps au relecteur.

    L'ordre place d'abord ce qui cite l'article : c'est le lien le plus fort que
    la mécanique puisse établir sans lire le droit.
    """
    retenues: list[DispositionSoutien] = []
    for article, texte in articles.items():
        marques = _marques_trouvees(texte)
        if not marques:
            continue
        cite = _cite_larticle(texte, cle_article) and article != cle_article
        # Une portée générale ne se déduit pas de la coexistence de deux formules
        # quelque part dans l'article : il faut que la limitation porte **sur** la
        # portée. On l'exige donc dans la même phrase, sans quoi une définition
        # employant « exempté » passerait pour une dérogation à l'acte entier.
        generale = _limite_la_portee_generale(texte)
        if article == cle_article:
            relation = "disposition interne à l'article cité par la règle"
        elif cite:
            relation = f"cette disposition cite explicitement l'article {cle_article}"
        elif generale:
            relation = "cette disposition déroge à l'acte entier, donc potentiellement à cet article"
        else:
            continue

        retenues.append(
            DispositionSoutien(
                article=f"Article {article}",
                motif=(
                    "porte une formule limitante : "
                    + ", ".join(sorted({m.strip('\\b') for m in marques})[:3])
                ),
                relation=relation,
                extrait=_extrait_limitant(texte),
                cite_larticle=cite,
            )
        )

    def rang(disposition: DispositionSoutien) -> tuple:
        interne = disposition.relation.startswith("disposition interne")
        return (0 if disposition.cite_larticle else 1 if interne else 2, disposition.article)

    return sorted(retenues, key=rang)[:MAX_DISPOSITIONS]


def _faits_textuels(
    regle: Rule, constat: ConstatCompletude, dispositions: list[DispositionSoutien]
) -> list[str]:
    """Uniquement ce qui est écrit ou mécaniquement constaté. Aucun jugement."""
    faits = [
        f"L'acte cité est « {regle.source.text} », consulté dans sa version du "
        f"{regle.source.version_date.isoformat()}.",
        f"L'ancrage déclaré est « {regle.source.article} »"
        + (f", {regle.source.paragraph}." if regle.source.paragraph else "."),
    ]
    if constat.criteres.get("article_verifie"):
        faits.append("Cet article a été retrouvé dans le texte officiel récupéré.")
    else:
        faits.append("Cet article n'a pas été retrouvé dans le texte officiel récupéré.")
    if constat.structures:
        faits.append(
            "Structures juridiques relevées dans l'article : "
            + ", ".join(s.value for s in constat.structures)
            + "."
        )
    else:
        faits.append("Aucune structure limitante n'a été relevée dans l'article lui-même.")
    if constat.renvois:
        faits.append(
            "L'article renvoie aux articles " + ", ".join(constat.renvois[:8]) + "."
        )
    for disposition in dispositions:
        faits.append(
            f"{disposition.article} — {disposition.motif} ; "
            f"{disposition.relation}."
        )
    for revendication in regle.negative_claims:
        faits.append(
            f"La règle porte une affirmation négative, à l'état "
            f"« {revendication.status.value} » : « {revendication.claim} »."
        )
    return faits


def _question_neutre(
    regle: Rule, constat: ConstatCompletude, dispositions: list[DispositionSoutien],
    categorie: str,
) -> str:
    """Une question binaire, tranchable sur le texte, sans conseil juridique."""
    article = regle.source.article
    acte = regle.source.text

    if categorie == BlockerCategory.EXCEPTION_UNRESOLVED.value:
        if dispositions:
            citees = ", ".join(d.article for d in dispositions[:3])
            return (
                f"{citees} constitue(nt)-t-il(s) une exception applicable à "
                f"« {article} » de {acte}, ou s'agit-il d'obligations distinctes "
                f"sans incidence sur la portée de la règle {regle.id} ?"
            )
        return (
            f"L'acte {acte} comporte-t-il, en dehors de « {article} », une "
            f"disposition qui déroge à cette obligation, ou aucune disposition de "
            f"cet acte n'en limite-t-elle la portée ?"
        )
    if categorie == BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED.value:
        claims = [
            c.claim for c in regle.negative_claims if c.status is NegativeClaimStatus.UNVERIFIED
        ]
        objet = claims[0] if claims else "l'affirmation négative portée par la règle"
        return (
            f"« {objet} » est-il absent de l'intégralité de {acte} dans la version "
            f"consultée, ou une disposition de cet acte le prévoit-elle ?"
        )
    if categorie == BlockerCategory.TEMPORAL_UNRESOLVED.value:
        return (
            f"La version de {acte} qui fait foi pour la règle {regle.id} est-elle "
            f"celle consultée le {regle.source.version_date.isoformat()}, ou une "
            f"version consolidée postérieure s'applique-t-elle ?"
        )
    if categorie == BlockerCategory.SOURCE_INCOMPLETE.value:
        return (
            f"« {article} » de {acte} existe-t-il dans la version applicable et "
            f"énonce-t-il ce que la règle {regle.id} affirme, ou l'ancrage doit-il "
            f"être corrigé ?"
        )
    if categorie == BlockerCategory.RULE_TOO_ABSTRACT.value:
        return (
            f"L'énoncé de la règle {regle.id} peut-il être reformulé au plus près "
            f"de la lettre de « {article} », ou la règle doit-elle être découpée en "
            f"plusieurs règles distinctes ?"
        )
    return (
        f"Le blocage constaté sur la règle {regle.id} peut-il être levé en l'état "
        f"du texte de {acte}, ou une information extérieure est-elle nécessaire ?"
    )


def _proposition(
    constat: ConstatCompletude, dispositions: list[DispositionSoutien], categorie: str
) -> PropositionMecanique:
    """Ce que la recherche a trouvé, dit dans le vocabulaire de la recherche."""
    if categorie == BlockerCategory.SOURCE_INCOMPLETE.value:
        return PropositionMecanique.INSUFFICIENT_SOURCE
    if categorie == BlockerCategory.RULE_TOO_ABSTRACT.value:
        return PropositionMecanique.RULE_NEEDS_REFORMULATION
    if any(d.cite_larticle for d in dispositions):
        return PropositionMecanique.EXCEPTION_LIKELY
    if dispositions:
        return PropositionMecanique.EXCEPTION_SCOPE_UNCLEAR
    if constat.structures and any(s in STRUCTURES_LIMITANTES for s in constat.structures):
        return PropositionMecanique.EXCEPTION_SCOPE_UNCLEAR
    return PropositionMecanique.NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE


def _perimetre(regle: Rule, dispositions: list[DispositionSoutien]) -> str:
    """Ce que le relecteur devra attester avoir examiné pour conclure à l'absence."""
    morceaux = [
        f"{regle.source.text}, version du {regle.source.version_date.isoformat()}",
        f"article cité : {regle.source.article}",
    ]
    if dispositions:
        morceaux.append(
            "dispositions à examiner : " + ", ".join(d.article for d in dispositions)
        )
    else:
        morceaux.append("acte entier, à défaut de disposition limitante identifiée")
    return " ; ".join(morceaux)


def _impacts(regle: Rule, categorie: str) -> tuple[str, str]:
    """Ce que chaque issue changerait pour les futurs items — sans les concevoir."""
    if categorie == BlockerCategory.EXCEPTION_UNRESOLVED.value:
        return (
            "les items devront poser le cas sous condition, et une réponse qui "
            "omettrait l'exception deviendra une erreur disqualifiante ; une famille "
            "« exception » deviendra possible sur cette règle",
            "les items pourront poser la règle comme un absolu, et une réponse qui "
            "inventerait une dérogation deviendra une erreur disqualifiante",
        )
    if categorie == BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED.value:
        return (
            "l'affirmation négative tombe : aucune fausse prémisse ne pourra être "
            "construite sur cette absence, et la règle devra dire ce que le texte "
            "prévoit réellement",
            "l'absence devient opposable et pourra fonder une fausse prémisse, avec "
            "le périmètre de recherche cité en source",
        )
    if categorie == BlockerCategory.TEMPORAL_UNRESOLVED.value:
        return (
            "les items devront porter une date d'appréciation explicite, et une "
            "famille temporelle deviendra possible",
            "les items pourront omettre la date, la règle étant stable sur la période",
        )
    if categorie == BlockerCategory.SOURCE_INCOMPLETE.value:
        return (
            "l'ancrage sera corrigé et les items citeront la disposition exacte",
            "la règle restera inexploitable : aucun item ne pourra citer sa source",
        )
    if categorie == BlockerCategory.RULE_TOO_ABSTRACT.value:
        return (
            "la règle reformulée pourra porter une réponse de référence vérifiable",
            "la règle restera vraie et inexploitable pour un gold",
        )
    return (
        "la règle deviendra exploitable pour ancrer des familles",
        "la règle restera bloquée en l'état",
    )


def _cluster(regle: Rule, dispositions: list[DispositionSoutien], categorie: str) -> str:
    """Identifiant de dossier partagé par les règles qui posent la même question.

    Deux règles du même acte, bloquées pour la même raison, et dont l'examen
    porte sur les mêmes dispositions, appellent un seul arbitrage. Les regrouper
    évite au relecteur de trancher trois fois la même chose — sans jamais fusionner
    les règles elles-mêmes.
    """
    acte = re.sub(r"[^A-Za-z0-9]+", "-", regle.source.text)[:28].strip("-").upper()
    cible = "-".join(d.article.replace("Article ", "A") for d in dispositions) or "AUCUNE"
    court = {
        BlockerCategory.EXCEPTION_UNRESOLVED.value: "EXC",
        BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED.value: "NEG",
        BlockerCategory.TEMPORAL_UNRESOLVED.value: "TMP",
        BlockerCategory.SOURCE_INCOMPLETE.value: "SRC",
        BlockerCategory.RULE_TOO_ABSTRACT.value: "ABS",
    }.get(categorie, "AUT")
    return f"CL-{court}-{acte}-{cible}"[:80]


def construire_dossier(
    regle: Rule,
    constat: ConstatCompletude,
    etat: ConstatReadiness,
    articles: dict[str, str],
    cle_article: str,
) -> DossierRevue:
    """Assemble le dossier d'arbitrage d'une règle."""
    categorie = etat.blocker_category
    dispositions = dispositions_de_soutien(articles, cle_article) if articles else []
    si_exception, si_aucune = _impacts(regle, categorie)

    return DossierRevue(
        rule_id=regle.id,
        domain=regle.domain.value,
        version=regle.version,
        status=regle.status.value,
        priorite=etat.priorite_revue,
        statement=regle.statement,
        source_text=regle.source.text,
        source_article=regle.source.article,
        source_paragraph=regle.source.paragraph,
        source_version_date=regle.source.version_date.isoformat(),
        source_url=regle.source.url,
        applicable_from=regle.valid_from.isoformat(),
        dispositions=tuple(dispositions),
        textual_facts=tuple(_faits_textuels(regle, constat, dispositions)),
        interpretive_question=etat.decision_requise,
        neutral_legal_question=_question_neutre(regle, constat, dispositions, categorie),
        mechanical_proposal=_proposition(constat, dispositions, categorie),
        review_cluster_id=_cluster(regle, dispositions, categorie),
        source_scope=_perimetre(regle, dispositions),
        if_exception_exists=si_exception,
        if_no_exception=si_aucune,
        blocker_category=categorie,
    )
