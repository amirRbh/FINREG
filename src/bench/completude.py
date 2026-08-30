"""Audit de complétude : ce qu'il manque à une règle vérifiée pour ancrer un gold.

L'audit de sources dit qu'une règle cite le bon texte. Il ne dit rien de ce que
ce texte contient **autour** de la règle : les dérogations qui la limitent, les
conditions qui la conditionnent, les renvois sans lesquels elle ne s'applique
pas. Une règle exacte et amputée de ses exceptions est plus dangereuse qu'une
règle fausse : elle a l'air complète.

Ce module cherche donc la **structure juridique** de l'article cité, pas le mot
« exception ». Un texte déroge rarement en s'annonçant : il écrit « par
dérogation », « sans préjudice », « ne s'applique pas », « toutefois », « sauf
si », ou il pose des conditions cumulatives dont l'une manque.

Ce qu'il ne fait pas, et ne peut pas faire :

- **il ne conclut jamais à l'absence d'exception.** Ne pas trouver de dérogation
  dans l'article cité ne prouve pas qu'aucun autre article n'y déroge, ni
  qu'aucun acte ultérieur ne l'a fait. Ce cas ressort en `REQUIRES_HUMAN_REVIEW`,
  jamais en `NONE_IDENTIFIED` ;
- **il n'interprète pas.** Les exceptions qu'il incorpore sont des phrases du
  texte officiel, recopiées, pas des reformulations.

`gold_ready` est le second apport. Une règle peut être juridiquement
irréprochable et rester inutilisable : « le règlement précise les modalités de
l'évaluation » est exact et ne permet de rédiger aucune réponse de référence.
Valider une telle règle sans le dire reviendrait à faire porter l'interprétation
juridique à l'étape de rédaction, là où elle ne serait plus contrôlée.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from src.bench.regles import Rule
from src.bench.rulebook import (
    EXCEPTIONS_ABOUTIES,
    ExceptionsStatus,
    NegativeClaimStatus,
    Priority,
    RuleStatus,
    RuleType,
)
from src.bench.vocabulaires import RegulatoryStatus


class Structure(str, Enum):
    """Structures juridiques qu'un article peut porter, et qu'une règle doit refléter."""

    DEROGATION = "derogation"
    EXCLUSION = "exclusion"
    EXEMPTION = "exemption"
    CONDITIONS_CUMULATIVES = "conditions_cumulatives"
    CONDITIONS_ALTERNATIVES = "conditions_alternatives"
    SEUIL = "seuil"
    DELAI = "delai"
    REGIME_PARTICULIER = "regime_particulier"
    DISPOSITION_TRANSITOIRE = "disposition_transitoire"
    RENVOI = "renvoi"
    DEFINITION_NECESSAIRE = "definition_necessaire"


#: Marques de chaque structure dans un texte réglementaire français. Elles ne
#: cherchent pas le mot « exception » : un texte déroge en écrivant « toutefois »
#: bien plus souvent qu'en s'annonçant comme une exception.
MARQUES: dict[Structure, tuple[str, ...]] = {
    Structure.DEROGATION: (
        r"par dérogation",
        r"\btoutefois\b",
        r"sans préjudice",
        r"\bnéanmoins\b",
        r"il peut être dérogé",
    ),
    Structure.EXCLUSION: (
        r"ne s'appliquen?t? pas",
        r"à l'exception d",
        r"\bhormis\b",
        r"\bexcepté\b",
        r"ne sont pas soumis",
        r"sont exclus",
        r"\bsauf\b",
    ),
    Structure.EXEMPTION: (
        r"n'est pas tenue?",
        r"ne sont pas tenu",
        r"\bdispensée?s?\b",
        r"\bexemptée?s?\b",
        r"peuvent s'abstenir",
        # Une présomption dispense de vérifier : c'est un allègement, même si le
        # texte ne se présente pas comme une exception.
        r"autorisée?s? à présumer",
        r"n'est pas requise?",
        r"peu(?:t|vent) ne pas",
    ),
    Structure.CONDITIONS_CUMULATIVES: (
        r"toutes les conditions suivantes",
        r"les conditions suivantes sont réunies",
        r"critères suivants",
        r"\bcumulativement\b",
        r"ainsi que\b",
    ),
    Structure.CONDITIONS_ALTERNATIVES: (
        r"l'une des conditions suivantes",
        r"l'une quelconque des",
        r"l'un des cas suivants",
        r"selon le cas",
    ),
    Structure.SEUIL: (
        r"\d+\s*%",
        r"\bseuil\b",
        r"\bplafond\b",
        r"au moins \d+",
        r"supérieure? à \d+",
        r"\d[\d  ]*(?:EUR|euros?|€)",
    ),
    Structure.DELAI: (
        r"\d+\s*(?:jours?|mois|ans?|heures?|semaines?)",
        r"dans un délai",
        r"au plus tard",
        r"sans délai",
        r"\bmeilleurs délais\b",
    ),
    Structure.REGIME_PARTICULIER: (
        r"clients? professionnels?",
        r"contreparties? éligibles?",
        r"petites? et moyennes",
        r"microentreprises?",
        r"régime particulier",
        r"proportionnalité",
    ),
    Structure.DISPOSITION_TRANSITOIRE: (
        r"à titre transitoire",
        r"dispositions? transitoires?",
        r"jusqu'au \d",
        r"à compter du \d",
        r"est applicable à partir",
    ),
    Structure.RENVOI: (
        r"conformément à l'article",
        r"visée?s? à l'article",
        r"au sens de l'article",
        r"prévue?s? à l'article",
        r"mentionnée?s? à l'article",
    ),
    Structure.DEFINITION_NECESSAIRE: (
        r"au sens de",
        r"on entend par",
        r"tel(?:le)?s? que défini",
    ),
}

#: Structures qui limitent la portée d'une règle. Ce sont elles qui font une
#: exception au sens du Rulebook — les autres décrivent des conditions.
STRUCTURES_LIMITANTES: frozenset[Structure] = frozenset(
    {Structure.DEROGATION, Structure.EXCLUSION, Structure.EXEMPTION}
)

#: Tournures qui signalent un énoncé qui décrit le texte au lieu de le dire.
#: « Le règlement précise les modalités » est exact et ne permet rien d'écrire.
MARQUES_ABSTRACTION = (
    r"\bmodalités\b",
    r"précise les",
    r"\bencadre\b",
    r"les conditions dans lesquelles",
    r"prévoit des dispositions",
    r"\bdiligences\b",
    r"\bnotamment\b",
    r"\bdivers\b",
    r"un certain nombre",
)

#: Un énoncé exploitable nomme au moins un fait vérifiable : qui doit quoi,
#: sous quel seuil, dans quel délai, ou ce qu'une notion recouvre.
MARQUES_CONCRETES = (
    r"\d",
    r"\bdoit\b|\bdoivent\b",
    r"\bne peut\b|\bne peuvent\b",
    r"\binterdit\b|\binterdi",
    r"\bpublient?\b|\bpublier\b",
    r"\bdéclarent?\b|\bdéclarer\b",
    r"\bconservent?\b|\bconserver\b",
    r"\bnotifient?\b|\bnotifier\b",
    r"on entend par|se définit|est défini",
)

#: En deçà, l'énoncé est trop court pour porter une règle vérifiable.
LONGUEUR_MINIMALE_ENONCE = 80

#: Nombre maximal d'exceptions recopiées depuis le texte officiel. Au-delà, ce
#: n'est plus une liste d'exceptions, c'est une recopie de l'article.
MAX_EXCEPTIONS_INCORPOREES = 6

#: Longueur d'un extrait d'exception. Une phrase de droit peut être longue, mais
#: un extrait qui dépasse cette taille ne se relit plus.
LONGUEUR_EXTRAIT = 400


@dataclass(frozen=True)
class ConstatCompletude:
    """Ce que l'analyse structurelle établit pour une règle."""

    rule_id: str
    domain: str
    priority: str
    #: Structures juridiques trouvées dans l'article cité.
    structures: tuple[Structure, ...] = ()
    #: Phrases du texte officiel qui limitent la portée de la règle, recopiées.
    exceptions_extraites: tuple[str, ...] = ()
    #: Articles auxquels l'article cité renvoie.
    renvois: tuple[str, ...] = ()
    exceptions_status: ExceptionsStatus = ExceptionsStatus.UNKNOWN
    gold_ready: bool = False
    gold_ready_reason: str = ""
    #: Les huit critères de validation, nommés et cochés ou non.
    criteres: dict[str, bool] = field(default_factory=dict)
    #: Les prérequis de `gold_ready` : les huit critères, plus la résolution des
    #: affirmations négatives. Séparés parce qu'une règle peut être juridiquement
    #: établie tout en portant une absence encore à vérifier.
    criteres_gold: dict[str, bool] = field(default_factory=dict)
    statut_propose: RuleStatus = RuleStatus.SOURCE_CHECKED
    motifs: tuple[str, ...] = ()
    temporal_status: str = ""
    cross_reference_checked: bool = False

    @property
    def criteres_manquants(self) -> list[str]:
        return [nom for nom, ok in self.criteres.items() if not ok]

    @property
    def motif(self) -> str:
        return " ; ".join(self.motifs) if self.motifs else ""


def structures_presentes(texte: str) -> list[Structure]:
    """Structures juridiques repérées dans un article, dans l'ordre du vocabulaire."""
    trouvees = []
    for structure, marques in MARQUES.items():
        if any(re.search(marque, texte, re.IGNORECASE) for marque in marques):
            trouvees.append(structure)
    return trouvees


def _phrases(texte: str) -> list[str]:
    """Découpe en phrases sans casser sur les abréviations d'articles."""
    protege = re.sub(r"\b(art|par|al|n°)\.\s*", r"\1§ ", texte, flags=re.IGNORECASE)
    return [p.strip().replace("§ ", ". ") for p in re.split(r"(?<=[.;])\s+(?=[A-ZÀ-Ü])", protege)]


def extraire_exceptions(texte: str) -> list[str]:
    """Recopie les phrases du texte officiel qui limitent la portée de la règle.

    Recopier plutôt que reformuler : une exception reformulée est une exception
    interprétée, et l'interprétation n'a pas sa place dans un champ que le gold
    citera. Les extraits sont donc des phrases du texte, tronquées, jamais
    réécrites.
    """
    marques = tuple(m for s in STRUCTURES_LIMITANTES for m in MARQUES[s])
    trouvees: list[str] = []
    for phrase in _phrases(texte):
        if len(phrase) < 40:
            continue
        if any(re.search(marque, phrase, re.IGNORECASE) for marque in marques):
            extrait = phrase[:LONGUEUR_EXTRAIT].strip()
            if extrait and extrait not in trouvees:
                trouvees.append(extrait)
        if len(trouvees) >= MAX_EXCEPTIONS_INCORPOREES:
            break
    return trouvees


def renvois_de(texte: str) -> list[str]:
    """Articles auxquels le texte renvoie — ceux sans lesquels la règle est incomplète."""
    trouves: set[str] = set()
    for marque in MARQUES[Structure.RENVOI]:
        for coincidence in re.finditer(marque + r"\s*(?:premier|\d+[a-z]*)", texte, re.IGNORECASE):
            numero = re.search(r"(premier|\d+[a-z]*)$", coincidence.group(0), re.IGNORECASE)
            if numero:
                trouves.add("1" if numero.group(1).lower() == "premier" else numero.group(1))
    return sorted(trouves, key=lambda n: (len(n), n))


def evaluer_portance(regle: Rule) -> tuple[bool, str]:
    """L'énoncé est-il assez précis pour qu'on en tire une réponse de référence ?

    La **portance** ne dit rien de la véracité ni de la complétude : elle dit si
    la formulation permet d'écrire un gold sans rouvrir le texte et sans trancher
    une question de droit. C'est une condition de `gold_ready`, pas `gold_ready`
    lui-même — un énoncé peut être parfaitement porteur et reposer sur une source
    non vérifiée.
    """
    enonce = regle.statement
    motifs: list[str] = []

    if len(enonce) < LONGUEUR_MINIMALE_ENONCE:
        motifs.append("énoncé trop court pour porter une règle vérifiable")

    abstraites = [
        m for m in MARQUES_ABSTRACTION if re.search(m, enonce, re.IGNORECASE)
    ]
    concretes = [m for m in MARQUES_CONCRETES if re.search(m, enonce, re.IGNORECASE)]

    if not concretes:
        motifs.append(
            "l'énoncé ne nomme ni obligation, ni seuil, ni délai, ni définition : "
            "rien de vérifiable à opposer à une réponse"
        )
    if abstraites and len(concretes) <= 1:
        lisibles = ", ".join(m.strip("\\b").replace("\\b", "") for m in abstraites[:3])
        motifs.append(
            f"l'énoncé décrit le texte au lieu de le dire ({lisibles}) : une réponse "
            f"de référence devrait réinterpréter le droit pour être écrite"
        )
    if not regle.source.article.strip():
        motifs.append("aucun article à citer dans la réponse de référence")

    if motifs:
        return False, " ; ".join(motifs)

    return True, (
        f"énoncé porteur d'un fait vérifiable, ancré sur « {regle.source.article} » "
        f"({len(enonce)} caractères)"
    )


#: Prérequis probatoires de `gold_ready`, dans l'ordre où ils se lisent. Un
#: énoncé porteur ne suffit pas : écrire une réponse de référence sur une source
#: non vérifiée, une exception inconnue ou une temporalité incertaine reviendrait
#: à faire porter le doute au gold, là où il ne se verrait plus.
PREREQUIS_GOLD: tuple[str, ...] = (
    "source_primaire_verifiee",
    "article_verifie",
    "exceptions_recherchees",
    "temporalite_etablie",
    "renvois_verifies",
    "affirmations_negatives_resolues",
)


def affirmations_negatives_resolues(regle: Rule) -> bool:
    """Une règle qui porte une affirmation négative non vérifiée n'est pas prête.

    « Je n'ai pas trouvé » n'est pas « cela n'existe pas » : tant qu'une
    affirmation négative reste `unverified`, le gold qu'elle porterait
    affirmerait une absence que rien n'atteste.
    """
    return all(
        revendication.status is not NegativeClaimStatus.UNVERIFIED
        for revendication in regle.negative_claims
    )


def evaluer_temporalite(regle: Rule) -> tuple[str, bool]:
    """État temporel de la règle, et si cet état est établi.

    Une réforme proposée n'est jamais du droit applicable ; une règle modifiée
    dont on ignore la version consolidée ne se teste pas non plus.
    """
    statut = regle.regulatory_status
    if statut is RegulatoryStatus.PROPOSED:
        return "PROPOSED", False
    if statut is RegulatoryStatus.REPEALED:
        return "REPEALED", regle.valid_until is not None
    if statut is RegulatoryStatus.TRANSITIONAL:
        return "TRANSITIONAL", regle.valid_until is not None
    if statut is RegulatoryStatus.AMENDED:
        # Un texte modifié n'est établi que si la version consultée est
        # postérieure à la modification qu'il porte.
        return "AMENDED", regle.source.version_date >= regle.valid_from
    etabli = regle.source.version_date >= regle.valid_from or not regle.time_sensitive
    return "IN_FORCE", etabli


def analyser(
    regle: Rule,
    article: str,
    acte: str = "",
    article_verifie: bool = False,
    concordance: float = 0.0,
) -> ConstatCompletude:
    """Analyse la structure de l'article cité et ce qu'elle exige de la règle.

    `article` est le texte officiel de la disposition citée ; `acte` celui de
    l'acte entier, pour les renvois. Sans texte, l'analyse ne conclut rien : une
    règle dont la source est hors d'atteinte reste `unknown`, elle ne devient
    pas « sans exception ».
    """
    commun = dict(rule_id=regle.id, domain=regle.domain.value, priority=regle.priority.value)
    temporal, temporel_etabli = evaluer_temporalite(regle)

    if not article.strip():
        return ConstatCompletude(
            **commun,
            exceptions_status=ExceptionsStatus.UNKNOWN,
            statut_propose=regle.status,
            motifs=(
                "texte de l'article non disponible : la structure juridique n'a pas "
                "pu être examinée, et une absence d'exception ne se suppose pas",
            ),
            temporal_status=temporal,
        )

    structures = structures_presentes(article)
    limitantes = [s for s in structures if s in STRUCTURES_LIMITANTES]
    extraits = extraire_exceptions(article) if limitantes else []
    renvois = renvois_de(article)
    motifs: list[str] = []

    # -- statut des exceptions --
    if limitantes and extraits:
        exceptions_status = ExceptionsStatus.IDENTIFIED_AND_INCORPORATED
        motifs.append(
            f"{len(extraits)} disposition(s) limitante(s) recopiée(s) du texte "
            f"officiel ({', '.join(s.value for s in limitantes)})"
        )
    elif limitantes:
        exceptions_status = ExceptionsStatus.IDENTIFIED_BUT_NOT_INCORPORATED
        motifs.append(
            f"structures limitantes repérées ({', '.join(s.value for s in limitantes)}) "
            f"sans phrase isolable : à incorporer à la main"
        )
    else:
        # Le point dur de la phase : ne rien trouver n'est pas trouver qu'il n'y a rien.
        exceptions_status = ExceptionsStatus.REQUIRES_HUMAN_REVIEW
        motifs.append(
            "aucune structure limitante dans l'article cité — ce qui ne prouve pas "
            "qu'aucun autre article n'y déroge : « none_identified » demande un juriste"
        )

    # -- renvois --
    renvois_verifies = bool(renvois) and bool(acte)
    if renvois and not acte:
        motifs.append(
            f"{len(renvois)} renvoi(s) vers d'autres articles, non résolus faute de "
            f"disposer de l'acte entier"
        )
    elif renvois:
        motifs.append(f"renvois vérifiés dans l'acte : articles {', '.join(renvois[:8])}")
    else:
        renvois_verifies = True  # rien à vérifier

    if not temporel_etabli:
        motifs.append(f"temporalité non établie (statut « {temporal} »)")

    portance, motif_portance = evaluer_portance(regle)

    # -- les huit critères de la spécification §4 --
    criteres = {
        "source_primaire_verifiee": regle.source.is_verified,
        "article_verifie": article_verifie,
        "enonce_fidele": concordance >= 0.45,
        "exceptions_recherchees": exceptions_status in EXCEPTIONS_ABOUTIES,
        "conditions_capturees": bool(structures),
        "temporalite_etablie": temporel_etabli,
        "renvois_verifies": renvois_verifies,
        "sans_ambiguite": portance or exceptions_status in EXCEPTIONS_ABOUTIES,
    }
    # La résolution des affirmations négatives est un prérequis de `gold_ready`,
    # pas un neuvième critère de validation : une règle peut être juridiquement
    # établie tout en portant une absence encore à vérifier.
    criteres_gold = dict(criteres)
    criteres_gold["affirmations_negatives_resolues"] = affirmations_negatives_resolues(regle)

    # `gold_ready` exige la portance **et** ses prérequis probatoires. Ne demander
    # que la portance rendait « prête » une règle dont la source n'était même pas
    # vérifiée : le doute passait alors du Rulebook au gold, où plus personne ne
    # l'aurait vu.
    manquants = [nom for nom in PREREQUIS_GOLD if not criteres_gold.get(nom, False)]
    gold_ready = portance and not manquants
    if not portance:
        motif_gold = motif_portance
    elif manquants:
        motif_gold = (
            f"énoncé porteur, mais prérequis non tenus : {', '.join(manquants)}"
        )
    else:
        motif_gold = motif_portance

    # -- statut proposé --
    if regle.status is RuleStatus.DRAFT:
        statut = RuleStatus.DRAFT
    elif all(criteres.values()):
        statut = RuleStatus.VALIDATED
    elif not criteres["enonce_fidele"]:
        # Le texte ne soutient pas ce que la règle affirme : c'est un blocage de
        # fond, pas une information manquante.
        statut = RuleStatus.REQUIRES_HUMAN_REVIEW
        motifs.append("l'énoncé n'est pas corroboré par le texte cité")
    else:
        statut = RuleStatus.SOURCE_CHECKED

    if regle.priority is Priority.CRITICAL and statut is RuleStatus.VALIDATED:
        # §9 : contrôle renforcé. Une règle critique validée sans exceptions
        # abouties ou sans renvois vérifiés ferait porter le risque au gold.
        if not (criteres["exceptions_recherchees"] and criteres["renvois_verifies"]):
            statut = RuleStatus.SOURCE_CHECKED
            motifs.append(
                "règle CRITICAL : contrôle renforcé, validation refusée tant que "
                "exceptions et renvois ne sont pas tous deux établis"
            )

    return ConstatCompletude(
        **commun,
        structures=tuple(structures),
        exceptions_extraites=tuple(extraits),
        renvois=tuple(renvois),
        exceptions_status=exceptions_status,
        gold_ready=gold_ready,
        gold_ready_reason=motif_gold,
        criteres=criteres,
        criteres_gold=criteres_gold,
        statut_propose=statut,
        motifs=tuple(motifs),
        temporal_status=temporal,
        cross_reference_checked=renvois_verifies,
    )
