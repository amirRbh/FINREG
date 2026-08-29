"""Dérivation du Question Family Map à partir du Rulebook (phase 7).

Ce module transforme `RULE` en `QUESTION FAMILY` → `TWIN GROUP` → blueprints,
**sans rédiger une seule question**. Il ne décide donc jamais du droit : tout ce
qu'il produit est déduit de ce que la règle déclare déjà — son type, ses pièges,
ses confusions typiques, ses exceptions, sa temporalité, ses règles liées.

Trois principes tiennent l'ensemble :

1. **On ne fabrique pas un angle pour remplir un quota.** Une combinaison
   règle × famille dont le score tombe à 0 ou 1 n'entre pas dans la carte ; elle
   reste visible dans la matrice de couverture, comme potentiel non exploité.
2. **L'intérêt d'une question et le droit de la poser sont deux choses.** Une
   famille excellente sur une règle non vérifiée est `blocked`, pas dégradée.
3. **La dérivation est déterministe.** Deux exécutions sur le même Rulebook
   produisent les mêmes familles, dans le même ordre, avec les mêmes
   identifiants : c'est ce qui rend la carte comparable d'une version à l'autre.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass

from src.bench.familles import (
    CODES_FAMILLES,
    CandidateFamily,
    CandidateFamilyStatus,
    CriticalErrorKind,
    FAMILLES_DANGEREUSES,
    FAMILLES_HOLDOUT,
    FamilyKind,
    HoldoutRecommendation,
    ORDRE_FAMILLES,
    PROFILS,
    SCORE_RETENU,
    TemporalBlueprint,
    TwinType,
)
from src.bench.plan import CIBLES_DOMAINES_EXPLICITES_V0, CIBLES_V0, POIDS_TYPES_V0
from src.bench.qc_rulebook import ANCRAGES_IMPRECIS, SEUIL_DOUBLON, proximite_enonces
from src.bench.regles import Rule
from src.bench.rulebook import (
    ExceptionsStatus,
    NegativeClaimStatus,
    Priority,
    RuleStatus,
    RuleType,
)
from src.bench.vocabulaires import (
    Corpus,
    Domain,
    QuestionType,
    ReasoningTrap,
    RegulatoryStatus,
)

#: Nombre d'items qu'une famille est réputée pouvoir engendrer, selon son score.
#: Une estimation de planification, pas une promesse : elle sert uniquement à
#: dire si le Rulebook *permet* la distribution visée (§10).
RENDEMENT_PAR_SCORE: dict[int, int] = {2: 2, 3: 3}

#: Régimes dont la confusion avec un autre est juridiquement plausible, et les
#: marques qui les trahissent dans un énoncé ou une confusion typique.
REGIMES_VOISINS: dict[str, tuple[str, ...]] = {
    "SFDR": ("sfdr", "2019/2088", "article 8", "article 9"),
    "TAXONOMIE": ("taxonomie", "taxonomique", "2020/852"),
    "MIFID2": ("mifid", "2014/65", "adéquation", "gouvernance produit"),
    "AMF": ("amf", "doctrine amf", "position-recommandation"),
    "DORA": ("dora", "2022/2554", "tic ", "ict"),
    "LCBFT": ("lcb-ft", "lcbft", "tracfin", "blanchiment", "vigilance"),
}

#: Préfixe d'identifiant de règle → régime, pour lire une règle liée sans la charger.
PREFIXES_REGIMES: dict[str, str] = {
    "SFDR": "SFDR",
    "TAXO": "TAXONOMIE",
    "MIFID": "MIFID2",
    "AMF": "AMF",
    "DORA": "DORA",
    "LCBFT": "LCBFT",
}

#: Marques d'une computation réelle dans un énoncé. « Ne pas fabriquer
#: artificiellement des calculs » (§3, F3) : sans l'une de ces marques, la
#: famille CALCULATION vaut 0.
MARQUES_CALCUL = re.compile(
    r"(\d+\s*%|\d+\s*(?:jours?|mois|ans?|heures?|semaines?)|"
    r"\d[\d\s ]*(?:euros?|EUR|€)|seuil|plafond|pourcentage|proportion)",
    re.IGNORECASE,
)

#: Marques d'une règle qui se branche selon les faits — matière à réponse conditionnelle.
MARQUES_CONDITION = re.compile(
    r"\b(si\b|lorsqu|sauf|dès lors|à moins|selon que|en cas de|dans le cas où|"
    r"sous réserve|à condition)",
    re.IGNORECASE,
)

#: Marques d'une donnée manquante qui empêche de trancher — matière à abstention.
TYPES_A_FAITS = frozenset(
    {
        RuleType.SCOPE,
        RuleType.CLASSIFICATION,
        RuleType.THRESHOLD,
        RuleType.PROCEDURE,
        RuleType.EXCEPTION,
    }
)


def _sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def _slug(texte: str, longueur: int = 40) -> str:
    """Fragment d'identifiant stable, sans accent ni ponctuation."""
    brut = re.sub(r"[^A-Za-z0-9]+", "-", _sans_accents(texte)).strip("-").upper()
    return brut[:longueur].strip("-") or "NA"


# --------------------------------------------------------------------------- #
# Éligibilité (§2)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Eligibilite:
    """Ce que l'état d'une règle autorise, et ce qu'il réserve.

    Les motifs bloquants interdisent le benchmark final ; les réserves le
    permettent sous condition d'une relecture. Les deux sont dits en français :
    ils sont lus par un humain, pas par le harnais.
    """

    blocages: tuple[str, ...]
    reserves: tuple[str, ...]

    @property
    def statut(self) -> CandidateFamilyStatus:
        if self.blocages:
            return CandidateFamilyStatus.BLOCKED
        if self.reserves:
            return CandidateFamilyStatus.NEEDS_REVIEW
        return CandidateFamilyStatus.READY


def eligibilite_regle(regle: Rule) -> Eligibilite:
    """Conditions d'éligibilité de la spécification §2, appliquées à une règle.

    Une règle `draft` ne produit jamais de famille destinée au benchmark final :
    c'est le même verrou que pour le gold, transporté un cran plus tôt.
    """
    blocages: list[str] = []
    reserves: list[str] = []

    # -- source suffisamment vérifiée --
    if regle.status is RuleStatus.DRAFT:
        blocages.append(
            "règle en « draft » : sa source n'a pas été confrontée au texte primaire"
        )
    elif not regle.is_usable:
        blocages.append(
            f"règle en « {regle.status.value} » : seul « validated » ancre un gold"
        )
    if regle.needs_verification:
        blocages.append(
            f"vérification insuffisante ({regle.verification_method.value})"
        )
    if not regle.source.is_verified:
        blocages.append("source sans vérificateur nommé ni date de vérification")

    # -- temporalité connue --
    if regle.regulatory_status is RegulatoryStatus.PROPOSED:
        blocages.append(
            "réforme proposée : elle ne peut pas être testée comme droit en vigueur"
        )
    if regle.regulatory_status is RegulatoryStatus.REPEALED:
        reserves.append("règle abrogée : exploitable en famille temporelle seulement")

    # -- portée identifiable --
    article = regle.source.article.lower()
    if any(marque in article for marque in ANCRAGES_IMPRECIS):
        reserves.append(
            f"ancrage « {regle.source.article} » : aucun item ne pourra citer un "
            f"article unique"
        )

    # -- absence d'ambiguïté non résolue --
    if regle.exceptions_status is ExceptionsStatus.UNKNOWN:
        reserves.append(
            "exceptions inconnues : la règle se testerait comme un absolu qu'elle "
            "n'est peut-être pas"
        )

    # -- contenu suffisamment précis --
    if not regle.operational_rule.strip():
        reserves.append("aucune traduction opérationnelle : l'application n'est pas cadrée")
    if regle.source.version_date.year < regle.valid_from.year:
        reserves.append(
            f"date de version ({regle.source.version_date.isoformat()}) antérieure à "
            f"l'entrée en vigueur : placeholder à établir"
        )

    return Eligibilite(tuple(blocages), tuple(reserves))


# --------------------------------------------------------------------------- #
# Score de potentiel (§4)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Potentiel:
    """Score 0–3 d'une combinaison règle × famille, et sa justification."""

    score: int
    rationale: str


def _regimes_voisins(regle: Rule) -> list[str]:
    """Régimes avec lesquels la confusion est plausible pour cette règle.

    Trois sources de signal : une règle liée d'un autre régime, une confusion
    typique qui nomme un autre texte, un piège de confusion inter-réglementaire.
    Le régime de la règle elle-même est évidemment exclu.
    """
    propre = regle.regulatory_regime.split("_")[0].upper()
    trouves: set[str] = set()

    for identifiant in regle.related_rules:
        prefixe = identifiant.split("-")[0].upper()
        regime = PREFIXES_REGIMES.get(prefixe)
        if regime and regime != propre and regime != regle.domain.value:
            trouves.add(regime)

    texte = " ".join(regle.common_confusions).lower()
    for regime, marques in REGIMES_VOISINS.items():
        if regime in (propre, regle.domain.value):
            continue
        if any(marque in texte for marque in marques):
            trouves.add(regime)

    return sorted(trouves)


def _potentiel(regle: Rule, famille: FamilyKind) -> Potentiel:
    """Score 0–3 de la famille sur cette règle, déduit de ce que la règle déclare."""
    enonce = f"{regle.statement} {regle.operational_rule}"
    confusions = len(regle.common_confusions)
    pieges = set(regle.reasoning_traps)

    if famille is FamilyKind.FACT_RECALL:
        if regle.rule_type in (
            RuleType.DEFINITION,
            RuleType.THRESHOLD,
            RuleType.DEADLINE,
            RuleType.SCOPE,
            RuleType.CLASSIFICATION,
        ):
            return Potentiel(
                3,
                f"règle de type {regle.rule_type.value} : elle porte un élément "
                f"restituable exactement (définition, seuil, délai ou périmètre)",
            )
        if regle.rule_type in (RuleType.OBLIGATION, RuleType.PROHIBITION, RuleType.DISCLOSURE):
            return Potentiel(
                2,
                "l'obligation elle-même se restitue : qui doit quoi, envers qui",
            )
        return Potentiel(
            1,
            f"règle de type {regle.rule_type.value} : la restitution porterait sur "
            f"un dispositif diffus, difficile à noter exactement",
        )

    if famille is FamilyKind.QUALIFICATION:
        if not regle.operational_rule.strip():
            return Potentiel(
                0,
                "aucune traduction opérationnelle : il n'y a rien à appliquer à un cas",
            )
        if regle.rule_type in (
            RuleType.SCOPE,
            RuleType.CLASSIFICATION,
            RuleType.OBLIGATION,
            RuleType.PROHIBITION,
            RuleType.EXCEPTION,
        ):
            return Potentiel(
                3,
                "un cas concret tranche : la règle dit qui est concerné et ce qui "
                "doit être fait, l'application est vérifiable",
            )
        if regle.rule_type is RuleType.DEFINITION:
            return Potentiel(
                1,
                "une définition s'applique mal seule : la qualification dépendrait "
                "d'une règle d'obligation qu'il faudrait joindre",
            )
        return Potentiel(2, "la règle se projette sur un cas, avec une réponse tranchable")

    if famille is FamilyKind.CALCULATION:
        if regle.rule_type in (RuleType.CALCULATION, RuleType.THRESHOLD):
            return Potentiel(
                3,
                f"règle de type {regle.rule_type.value} : la computation est dans la "
                f"règle, pas ajoutée par la question",
            )
        if regle.rule_type is RuleType.DEADLINE and MARQUES_CALCUL.search(enonce):
            return Potentiel(2, "un délai chiffré se calcule à partir d'un fait daté")
        if MARQUES_CALCUL.search(regle.statement):
            return Potentiel(
                1,
                "l'énoncé porte une donnée chiffrée, mais la computation resterait "
                "à inventer autour d'elle",
            )
        return Potentiel(
            0, "aucune computation réelle : un calcul serait fabriqué pour la question"
        )

    if famille is FamilyKind.FALSE_PREMISE:
        if regle.negative_claims:
            return Potentiel(
                3,
                f"{len(regle.negative_claims)} affirmation(s) fausse(s) déjà "
                f"identifiée(s) sur cette règle : la prémisse est prête à être "
                f"réfutée, sous réserve de vérifier l'absence",
            )
        if pieges & {ReasoningTrap.FALSE_THRESHOLD, ReasoningTrap.FALSE_ARTICLE}:
            return Potentiel(
                3,
                "la règle porte un piège d'invention (seuil ou article) : la fausse "
                "prémisse s'écrit directement dessus",
            )
        if confusions:
            return Potentiel(
                2,
                f"{confusions} confusion(s) typique(s) documentée(s) : chacune se "
                f"retourne en prémisse fausse plausible",
            )
        if pieges:
            return Potentiel(
                1,
                "des pièges sont nommés mais aucune confusion documentée : la "
                "prémisse fausse risquerait d'être invraisemblable",
            )
        return Potentiel(0, "ni confusion typique ni piège : rien à contredire de crédible")

    if famille is FamilyKind.TRUE_PREMISE_ADVERSARIAL:
        # §3 : obligatoire dès qu'un jumeau est possible. Le score suit celui de
        # la fausse prémisse — un jumeau ne vaut que ce que vaut son jumeau.
        jumelle = _potentiel(regle, FamilyKind.FALSE_PREMISE)
        if jumelle.score >= SCORE_RETENU:
            return Potentiel(
                jumelle.score,
                "jumeau obligatoire de la fausse prémisse : sans lui, le modèle "
                "apprend « question adversariale ⇒ réfuter » et gagne des points "
                "en réfutant le vrai",
            )
        if regle.rule_type in (RuleType.DEFINITION, RuleType.THRESHOLD, RuleType.SCOPE):
            return Potentiel(
                2,
                "l'énoncé est une affirmation nette : elle se pose telle quelle sous "
                "une forme qui ressemble à un piège sans en être un",
            )
        return Potentiel(
            1, "sans fausse prémisse comparable, la prémisse vraie perd son rôle de contrôle"
        )

    if famille is FamilyKind.CALIBRATED_ABSTENTION:
        if regle.exceptions_status is ExceptionsStatus.UNKNOWN:
            return Potentiel(
                1,
                "exceptions inconnues : on ne peut pas affirmer qu'un cas est "
                "indécidable tant qu'on ignore ce que le texte prévoit",
            )
        if regle.rule_type in TYPES_A_FAITS:
            return Potentiel(
                3,
                f"règle de type {regle.rule_type.value} : elle dépend de faits "
                f"précis, dont l'absence rend la conclusion impossible",
            )
        return Potentiel(
            2, "un cas amputé d'une donnée décisive ne peut pas être tranché sous cette règle"
        )

    if famille is FamilyKind.CONDITIONAL_ANSWER:
        if regle.exceptions_status is ExceptionsStatus.LISTED:
            return Potentiel(
                3,
                "des exceptions listées font des branches : la réponse correcte est "
                "conditionnelle, pas unique",
            )
        if MARQUES_CONDITION.search(enonce):
            return Potentiel(
                2,
                "l'énoncé se branche selon les faits : la bonne réponse dit « si A "
                "alors X, si B alors Y »",
            )
        return Potentiel(
            0, "règle sans branche : une réponse conditionnelle serait un artifice"
        )

    if famille is FamilyKind.TEMPORAL:
        if regle.regulatory_status in (
            RegulatoryStatus.AMENDED,
            RegulatoryStatus.TRANSITIONAL,
            RegulatoryStatus.REPEALED,
        ):
            return Potentiel(
                3,
                f"régime « {regle.regulatory_status.value} » : il existe un avant et "
                f"un après à distinguer",
            )
        if regle.time_sensitive and regle.valid_until is not None:
            return Potentiel(3, "règle datée et bornée : le régime applicable dépend de la date")
        if regle.time_sensitive:
            return Potentiel(
                2,
                "règle marquée sensible au temps : l'entrée en vigueur et le régime "
                "applicable à une date donnée se testent",
            )
        if ReasoningTrap.TEMPORAL_CONFUSION in pieges:
            return Potentiel(
                2, "piège de confusion temporelle documenté sur cette règle"
            )
        return Potentiel(
            0,
            "règle stable et non bornée : une question temporelle porterait sur une "
            "date sans enjeu",
        )

    if famille is FamilyKind.CROSS_REGULATORY:
        voisins = _regimes_voisins(regle)
        if ReasoningTrap.CROSS_REGULATORY_CONFLATION in pieges and voisins:
            return Potentiel(
                3,
                f"confusion inter-réglementaire documentée et régime(s) voisin(s) "
                f"identifié(s) : {', '.join(voisins)}",
            )
        if voisins:
            return Potentiel(
                2,
                f"régime(s) voisin(s) plausible(s) : {', '.join(voisins)} — la "
                f"confusion est juridiquement crédible",
            )
        if ReasoningTrap.CROSS_REGULATORY_CONFLATION in pieges:
            return Potentiel(
                1,
                "piège inter-réglementaire annoncé mais aucun régime voisin nommé : "
                "la confusion resterait abstraite",
            )
        return Potentiel(0, "aucun régime voisin : la confusion ne serait pas plausible")

    if famille is FamilyKind.EXCEPTION:
        if regle.exceptions_status is ExceptionsStatus.LISTED:
            return Potentiel(
                3,
                f"{len(regle.exceptions)} exception(s) listée(s) : la surgénéralisation "
                f"se mesure directement",
            )
        if regle.exceptions_status is ExceptionsStatus.NONE_IDENTIFIED:
            return Potentiel(
                1,
                "aucune exception identifiée : la famille ne pourrait tester qu'une "
                "confirmation d'absence, à sourcer comme connaissance négative",
            )
        return Potentiel(
            0,
            "exceptions inconnues : tester une exception qu'on n'a pas cherchée "
            "reviendrait à l'inventer",
        )

    if famille is FamilyKind.NEGATIVE_ASSERTION:
        if not regle.negative_claims:
            return Potentiel(
                0, "aucune affirmation négative documentée : il n'y a rien à nier"
            )
        verifiees = [
            c
            for c in regle.negative_claims
            if c.status is NegativeClaimStatus.VERIFIED_ABSENT
        ]
        if verifiees:
            return Potentiel(
                3,
                f"{len(verifiees)} absence(s) vérifiée(s) : l'affirmation négative est "
                f"opposable",
            )
        return Potentiel(
            2,
            f"{len(regle.negative_claims)} affirmation(s) négative(s) identifiée(s), "
            f"aucune encore vérifiée absente : la famille est prête mais pas sourçable",
        )

    if famille is FamilyKind.MISSING_INFORMATION:
        if regle.rule_type in TYPES_A_FAITS:
            return Potentiel(
                3,
                f"règle de type {regle.rule_type.value} : on peut nommer exactement "
                f"la donnée qui manque pour conclure",
            )
        if regle.rule_type in (RuleType.OBLIGATION, RuleType.PROCEDURE, RuleType.DISCLOSURE):
            return Potentiel(
                2,
                "l'obligation dépend de faits identifiables : le modèle doit dire "
                "lesquels lui manquent",
            )
        return Potentiel(
            1,
            "la donnée manquante serait difficile à nommer précisément : la demande "
            "d'information resterait vague",
        )

    raise ValueError(f"famille inconnue : {famille}")  # pragma: no cover


# --------------------------------------------------------------------------- #
# Priorité (§5), difficulté (§7), erreurs disqualifiantes (§11)
# --------------------------------------------------------------------------- #

ORDRE_PRIORITES: tuple[Priority, ...] = (
    Priority.LOW,
    Priority.MEDIUM,
    Priority.HIGH,
    Priority.CRITICAL,
)


def _priorite(regle: Rule, famille: FamilyKind) -> Priority:
    """Gravité de l'erreur pour un professionnel, pas intérêt de la question.

    Une famille CRITICAL doit correspondre à une erreur dangereuse en pratique
    (§5) : mal restituer une définition se rattrape, mal qualifier un cas
    conduit à déclarer, publier ou classer de travers.
    """
    rang = ORDRE_PRIORITES.index(regle.priority)
    if famille in FAMILLES_DANGEREUSES:
        return regle.priority
    # Restitution, temporalité, abstention : une erreur y est coûteuse mais elle
    # ne déclenche pas seule un acte fautif.
    return ORDRE_PRIORITES[max(0, rang - 1)]


#: Difficulté de départ de chaque famille, sur l'échelle de la spécification §7.
DIFFICULTE_BASE: dict[FamilyKind, int] = {
    FamilyKind.FACT_RECALL: 1,
    FamilyKind.QUALIFICATION: 3,
    FamilyKind.CALCULATION: 3,
    FamilyKind.FALSE_PREMISE: 4,
    FamilyKind.TRUE_PREMISE_ADVERSARIAL: 4,
    FamilyKind.CALIBRATED_ABSTENTION: 4,
    FamilyKind.CONDITIONAL_ANSWER: 3,
    FamilyKind.TEMPORAL: 4,
    FamilyKind.CROSS_REGULATORY: 5,
    FamilyKind.EXCEPTION: 4,
    FamilyKind.NEGATIVE_ASSERTION: 4,
    FamilyKind.MISSING_INFORMATION: 4,
}

ECHELLE_DIFFICULTE: dict[int, str] = {
    1: "simple restitution",
    2: "restitution + distinction",
    3: "application",
    4: "piège, exception ou temporalité",
    5: "multi-règles, inter-réglementaire ou ambiguïté contrôlée",
}


def _difficulte(regle: Rule, famille: FamilyKind) -> tuple[int, str]:
    """Difficulté prédite 1–5 et sa justification, jamais un chiffre nu."""
    niveau = DIFFICULTE_BASE[famille]
    motifs = [f"socle {niveau} pour {CODES_FAMILLES[famille]} ({ECHELLE_DIFFICULTE[niveau]})"]

    if famille in (FamilyKind.FACT_RECALL, FamilyKind.QUALIFICATION) and regle.common_confusions:
        niveau += 1
        motifs.append(
            f"+1 : {len(regle.common_confusions)} confusion(s) typique(s) — il faut "
            f"restituer *et* distinguer"
        )
    if len(regle.related_rules) >= 3 and famille is not FamilyKind.CROSS_REGULATORY:
        niveau += 1
        motifs.append(
            f"+1 : {len(regle.related_rules)} règles liées — la réponse doit être "
            f"tenue face à des règles voisines"
        )
    if regle.exceptions_status is ExceptionsStatus.LISTED and famille in (
        FamilyKind.QUALIFICATION,
        FamilyKind.FACT_RECALL,
    ):
        niveau += 1
        motifs.append("+1 : la règle porte des exceptions listées, à ne pas omettre")

    niveau = max(1, min(5, niveau))
    motifs.append(f"⇒ {niveau} ({ECHELLE_DIFFICULTE[niveau]})")
    return niveau, " ; ".join(motifs)


def _erreurs_disqualifiantes(regle: Rule, famille: FamilyKind) -> list[CriticalErrorKind]:
    """Catégories d'erreur qui disqualifieraient une réponse à cette famille (§11)."""
    trouvees: set[CriticalErrorKind] = {CriticalErrorKind.INCORRECT_ARTICLE}
    enonce = f"{regle.statement} {regle.operational_rule} {regle.title}".lower()

    if famille in (FamilyKind.FALSE_PREMISE, FamilyKind.NEGATIVE_ASSERTION) or (
        regle.rule_type in (RuleType.THRESHOLD, RuleType.CALCULATION)
    ):
        trouvees.add(CriticalErrorKind.INVENTED_THRESHOLD)
    if regle.rule_type in (RuleType.SCOPE, RuleType.CLASSIFICATION) or famille in (
        FamilyKind.QUALIFICATION,
        FamilyKind.CONDITIONAL_ANSWER,
    ):
        trouvees.add(CriticalErrorKind.WRONG_SCOPE)
    if famille is FamilyKind.CROSS_REGULATORY or _regimes_voisins(regle):
        trouvees.add(CriticalErrorKind.WRONG_REGULATORY_REGIME)
    if famille in (FamilyKind.EXCEPTION, FamilyKind.CONDITIONAL_ANSWER) or (
        regle.exceptions_status is ExceptionsStatus.LISTED
    ):
        trouvees.add(CriticalErrorKind.FAILURE_TO_MENTION_EXCEPTION)
    if regle.rule_type in (RuleType.OBLIGATION, RuleType.PROHIBITION):
        trouvees.add(CriticalErrorKind.INCORRECT_MANDATORY_PROHIBITED)

    if regle.domain is Domain.LCBFT:
        if "politiquement exposé" in enonce or "ppe" in enonce.split():
            trouvees.add(CriticalErrorKind.INCORRECT_PPE_CLASSIFICATION)
        if any(m in enonce for m in ("soupçon", "déclaration", "refus", "relation d'affaires")):
            trouvees.add(CriticalErrorKind.INCORRECT_REFUSAL_CONTINUATION)
    if regle.domain is Domain.DORA and any(
        m in enonce for m in ("incident", "classification", "critique", "tic")
    ):
        trouvees.add(CriticalErrorKind.INCORRECT_ICT_CLASSIFICATION)
    if regle.domain is Domain.SFDR and any(
        m in enonce for m in ("article 8", "article 9", "durable", "durabilité")
    ):
        trouvees.add(CriticalErrorKind.INCORRECT_SUSTAINABILITY_CLASSIFICATION)

    return sorted(trouvees, key=lambda e: e.value)


# --------------------------------------------------------------------------- #
# Pièges, abstention, temporalité
# --------------------------------------------------------------------------- #

#: Piège retenu pour une fausse prémisse, par ordre de préférence : d'abord ceux
#: qui affirment une disposition inexistante, ensuite les confusions de fond.
PREFERENCE_PIEGES: tuple[ReasoningTrap, ...] = (
    ReasoningTrap.FALSE_THRESHOLD,
    ReasoningTrap.FALSE_ARTICLE,
    ReasoningTrap.SCOPE_CONFUSION,
    ReasoningTrap.CONCEPT_CONFLATION,
    ReasoningTrap.DEFINITION_DRIFT,
    ReasoningTrap.TEMPORAL_CONFUSION,
    ReasoningTrap.OVERGENERALIZATION,
    ReasoningTrap.EXCEPTION_OMISSION,
    ReasoningTrap.CAUSAL_INFERENCE,
    ReasoningTrap.CROSS_REGULATORY_CONFLATION,
)


def _piege(regle: Rule, famille: FamilyKind) -> ReasoningTrap:
    """Piège mesuré par la famille. `NONE` quand la famille n'en contient pas."""
    pieges = set(regle.reasoning_traps)

    if famille is FamilyKind.NEGATIVE_ASSERTION:
        return ReasoningTrap.NEGATIVE_ASSERTION
    if famille is FamilyKind.FALSE_PREMISE:
        for candidat in PREFERENCE_PIEGES:
            if candidat in pieges:
                return candidat
        # Une fausse prémisse doit nommer un piège : à défaut, la confusion de
        # concept est le défaut le plus neutre.
        return ReasoningTrap.CONCEPT_CONFLATION
    if famille is FamilyKind.TEMPORAL:
        return ReasoningTrap.TEMPORAL_CONFUSION
    if famille is FamilyKind.CROSS_REGULATORY:
        return ReasoningTrap.CROSS_REGULATORY_CONFLATION
    if famille is FamilyKind.EXCEPTION:
        return ReasoningTrap.OVERGENERALIZATION
    if famille in (FamilyKind.CALIBRATED_ABSTENTION, FamilyKind.MISSING_INFORMATION):
        return ReasoningTrap.MISSING_INFORMATION
    return ReasoningTrap.NONE


def _abstention_focus(regle: Rule, famille: FamilyKind) -> list[str]:
    """Ce que le modèle doit réclamer, nommément, pour réussir l'abstention.

    Ce ne sont pas encore les `missing_information` d'un item : ce sont les
    catégories de faits que la règle rend décisives, et sur lesquelles la
    question sera construite.
    """
    if famille not in (FamilyKind.CALIBRATED_ABSTENTION, FamilyKind.MISSING_INFORMATION):
        return []

    besoins = [
        f"les faits qui déclenchent l'application de « {regle.title} » "
        f"({regle.source.article})"
    ]
    if regle.rule_type in (RuleType.SCOPE, RuleType.CLASSIFICATION):
        besoins.append("la qualification exacte de l'entité ou du produit concerné")
    if regle.rule_type in (RuleType.THRESHOLD, RuleType.CALCULATION):
        besoins.append("les données chiffrées permettant de situer le cas par rapport au seuil")
    if regle.rule_type in (RuleType.DEADLINE, RuleType.PROCEDURE):
        besoins.append("la date de l'événement déclencheur et l'état de la procédure")
    if regle.exceptions_status is ExceptionsStatus.LISTED:
        besoins.append("les éléments permettant d'écarter ou de retenir une exception")
    if regle.time_sensitive:
        besoins.append("la date à laquelle la situation doit être appréciée")
    return besoins


def _temporal_blueprint(regle: Rule) -> TemporalBlueprint:
    """Ancrage temporel d'une famille temporelle (§13)."""
    precedent = ""
    transition = ""
    if regle.regulatory_status is RegulatoryStatus.AMENDED:
        precedent = f"{regle.regulatory_regime} (version antérieure à la modification)"
        transition = "le texte a été modifié : la réponse dépend de la version applicable"
    elif regle.regulatory_status is RegulatoryStatus.TRANSITIONAL:
        transition = "régime transitoire : la réponse dépend de la date d'appréciation"
    elif regle.valid_until is not None:
        transition = (
            f"la règle cesse de s'appliquer le {regle.valid_until.isoformat()} : "
            f"le régime postérieur doit être identifié"
        )
    else:
        transition = (
            f"entrée en vigueur au {regle.valid_from.isoformat()} : avant cette date, "
            f"la règle ne s'applique pas"
        )

    return TemporalBlueprint(
        target_date=regle.valid_from,
        applicable_regime=regle.regulatory_regime,
        text_version_date=regle.source.version_date,
        previous_regime=precedent,
        transition=transition,
        regulatory_status=regle.regulatory_status,
    )


# --------------------------------------------------------------------------- #
# Redondance (§8)
# --------------------------------------------------------------------------- #


def concept_teste(regle: Rule) -> str:
    """Le concept qu'une famille de cette règle mettra à l'épreuve.

    Formulé comme la spécification l'illustre — « Article 9 = objectif
    d'investissement durable » — pour qu'un humain voie d'un coup d'œil que deux
    familles testent la même chose.
    """
    return f"{regle.source.article} = {regle.title}"


def groupe_redondance(regle: Rule) -> str:
    """Clé de regroupement des familles qui testent le même concept.

    Deux règles du même domaine, du même article et du même type portent le même
    concept : leurs familles se comparent, et une collision sur la même famille
    est une redondance à trancher.
    """
    return f"RG-{regle.domain.value}-{_slug(regle.source.article, 24)}-{regle.rule_type.value}"


# --------------------------------------------------------------------------- #
# Dérivation
# --------------------------------------------------------------------------- #


def _construire(regle: Rule, famille: FamilyKind, potentiel: Potentiel) -> CandidateFamily:
    """Assemble le blueprint d'une famille, sans rédiger de question."""
    profil = PROFILS[famille]
    eligibilite = eligibilite_regle(regle)
    blocages = list(eligibilite.blocages)
    reserves = list(eligibilite.reserves)

    # Blocages propres à la famille : ils s'ajoutent à ceux de la règle.
    if famille is FamilyKind.EXCEPTION and regle.exceptions_status is ExceptionsStatus.UNKNOWN:
        blocages.append(
            "famille EXCEPTION sur une règle dont les exceptions n'ont pas été cherchées"
        )
    if famille is FamilyKind.NEGATIVE_ASSERTION:
        if not any(
            c.status is NegativeClaimStatus.VERIFIED_ABSENT for c in regle.negative_claims
        ):
            blocages.append(
                "affirmation négative non vérifiée absente : « je n'ai pas trouvé » "
                "n'est pas « cela n'existe pas »"
            )
    if famille is FamilyKind.FALSE_PREMISE and _piege(regle, famille) in (
        ReasoningTrap.FALSE_THRESHOLD,
        ReasoningTrap.FALSE_ARTICLE,
    ):
        reserves.append(
            "piège d'invention : l'item exigera une vérification négative (searched_in, "
            "version consultée, vérificateur)"
        )

    statut = (
        CandidateFamilyStatus.BLOCKED
        if blocages
        else CandidateFamilyStatus.NEEDS_REVIEW
        if reserves
        else CandidateFamilyStatus.READY
    )

    piege = _piege(regle, famille)
    difficulte, motif_difficulte = _difficulte(regle, famille)
    voisins = _regimes_voisins(regle) if famille is FamilyKind.CROSS_REGULATORY else []

    holdout = (
        HoldoutRecommendation.PRIVATE_PREFERRED
        if famille in FAMILLES_HOLDOUT or difficulte >= 4
        else HoldoutRecommendation.EITHER
    )

    return CandidateFamily(
        id=f"{regle.id}-{CODES_FAMILLES[famille]}",
        rule_id=regle.id,
        domain=regle.domain,
        family_kind=famille,
        family_code=CODES_FAMILLES[famille],
        concept_tested=concept_teste(regle),
        redundancy_group_id=groupe_redondance(regle),
        family_score=potentiel.score,
        family_rationale=potentiel.rationale,
        priority=_priorite(regle, famille),
        predicted_difficulty=difficulte,
        difficulty_rationale=motif_difficulte,
        question_type=profil.question_type,
        expected_behavior=profil.expected_behavior,
        answerability=profil.answerability,
        reasoning_trap=(
            ReasoningTrap.NONE
            if profil.question_type is QuestionType.TRUE_PREMISE_ADVERSARIAL
            else piege
        ),
        mimicked_trap=(
            _piege(regle, FamilyKind.FALSE_PREMISE)
            if profil.question_type is QuestionType.TRUE_PREMISE_ADVERSARIAL
            else None
        ),
        requires_negative_claim=(
            profil.question_type is QuestionType.FALSE_PREMISE
            and piege
            in (
                ReasoningTrap.FALSE_THRESHOLD,
                ReasoningTrap.FALSE_ARTICLE,
                ReasoningTrap.NEGATIVE_ASSERTION,
            )
        ),
        abstention_focus=_abstention_focus(regle, famille),
        cross_regulatory_with=voisins,
        candidate_disqualifying_errors=_erreurs_disqualifiantes(regle, famille),
        temporal_blueprint=(
            _temporal_blueprint(regle) if famille is FamilyKind.TEMPORAL else None
        ),
        source=regle.source.model_copy(deep=True),
        regulatory_regime=regle.regulatory_regime,
        regulatory_status=regle.regulatory_status,
        candidate_family_status=statut,
        blocking_reasons=blocages,
        review_reasons=[] if blocages else reserves,
        public_eligible=True,
        private_eligible=True,
        holdout_recommendation=holdout,
    )


def potentiel_complet(regle: Rule) -> dict[FamilyKind, Potentiel]:
    """Score des douze familles sur une règle, y compris les scores 0 et 1.

    Rien n'est jeté : ce que la carte ne retient pas reste visible dans la
    matrice de couverture, comme potentiel non exploité.
    """
    return {famille: _potentiel(regle, famille) for famille in ORDRE_FAMILLES}


def deriver_familles(regles: list[Rule]) -> list[CandidateFamily]:
    """Familles retenues (score ≥ 2) pour toutes les règles, jumeaux appariés."""
    familles: list[CandidateFamily] = []
    for regle in sorted(regles, key=lambda r: r.id):
        scores = potentiel_complet(regle)
        for famille in ORDRE_FAMILLES:
            potentiel = scores[famille]
            if potentiel.score >= SCORE_RETENU:
                familles.append(_construire(regle, famille, potentiel))
    return apparier_jumeaux(familles)


# --------------------------------------------------------------------------- #
# Jumeaux (§6)
# --------------------------------------------------------------------------- #

#: Piège de la fausse prémisse → nature du couple, quand elle est déterminante.
TYPE_JUMEAU_PAR_PIEGE: dict[ReasoningTrap, TwinType] = {
    ReasoningTrap.TEMPORAL_CONFUSION: TwinType.TEMPORAL_TWIN,
    ReasoningTrap.SCOPE_CONFUSION: TwinType.SCOPE_TWIN,
    ReasoningTrap.EXCEPTION_OMISSION: TwinType.EXCEPTION_TWIN,
    ReasoningTrap.OVERGENERALIZATION: TwinType.EXCEPTION_TWIN,
}


def _type_jumeau(
    fausse: CandidateFamily | None, vraie: CandidateFamily | None
) -> TwinType:
    """Nature du couple.

    Quand le piège de la fausse prémisse désigne la variable qui change
    (temporalité, périmètre, exception), c'est elle qui nomme le couple. Sinon,
    le couple est nommé par son ancre — la famille au meilleur score, la fausse
    prémisse en cas d'égalité.
    """
    if fausse is not None and vraie is not None:
        specifique = TYPE_JUMEAU_PAR_PIEGE.get(fausse.reasoning_trap)
        if specifique is not None:
            return specifique
        return (
            TwinType.TRUE_FALSE
            if vraie.family_score > fausse.family_score
            else TwinType.FALSE_TRUE
        )
    if fausse is not None:
        return TwinType.FALSE_MISSING
    return TwinType.TRUE_MISSING


def apparier_jumeaux(familles: list[CandidateFamily]) -> list[CandidateFamily]:
    """Apparie chaque fausse prémisse avec son contrôle, règle par règle.

    Ordre de recherche : d'abord la prémisse vraie adversariale — c'est elle qui
    mesure si le modèle a vérifié la prémisse plutôt qu'appris à réfuter. À
    défaut, une famille d'information manquante : le couple mesure alors la
    frontière entre « c'est faux » et « il me manque de quoi trancher ».
    """
    par_regle: dict[str, dict[FamilyKind, CandidateFamily]] = defaultdict(dict)
    for famille in familles:
        par_regle[famille.rule_id][famille.family_kind] = famille

    apparies: dict[str, CandidateFamily] = {}
    for rule_id in sorted(par_regle):
        parkinds = par_regle[rule_id]
        fausse = parkinds.get(FamilyKind.FALSE_PREMISE)
        vraie = parkinds.get(FamilyKind.TRUE_PREMISE_ADVERSARIAL)
        manquante = parkinds.get(FamilyKind.MISSING_INFORMATION) or parkinds.get(
            FamilyKind.CALIBRATED_ABSTENTION
        )

        if fausse is not None and vraie is not None:
            couple = (fausse, vraie)
            type_jumeau = _type_jumeau(fausse, vraie)
        elif fausse is not None and manquante is not None:
            couple = (fausse, manquante)
            type_jumeau = _type_jumeau(fausse, None)
        elif vraie is not None and manquante is not None:
            couple = (vraie, manquante)
            type_jumeau = _type_jumeau(None, vraie)
        else:
            continue

        groupe = f"TG-{rule_id}"
        gauche, droite = couple
        apparies[gauche.id] = gauche.model_copy(
            update={
                "twin_candidate": True,
                "twin_group_id": groupe,
                "twin_type": type_jumeau,
                "twin_partner_id": droite.id,
            }
        )
        apparies[droite.id] = droite.model_copy(
            update={
                "twin_candidate": True,
                "twin_group_id": groupe,
                "twin_type": type_jumeau,
                "twin_partner_id": gauche.id,
            }
        )

    return [apparies.get(f.id, f) for f in familles]


# --------------------------------------------------------------------------- #
# Matrice de couverture (§9) et distribution visée (§10)
# --------------------------------------------------------------------------- #


def matrice_couverture(regles: list[Rule], familles: list[CandidateFamily]) -> list[dict]:
    """DOMAIN × RULE × FAMILY × TRAP × DIFFICULTY, potentiel non retenu compris.

    Une ligne par combinaison règle × famille : c'est ce qui permet de voir non
    seulement ce que la carte contient, mais ce qu'elle a écarté et pourquoi.
    """
    retenues = {(f.rule_id, f.family_kind): f for f in familles}
    lignes: list[dict] = []

    for regle in sorted(regles, key=lambda r: r.id):
        scores = potentiel_complet(regle)
        for famille in ORDRE_FAMILLES:
            potentiel = scores[famille]
            retenue = retenues.get((regle.id, famille))
            lignes.append(
                {
                    "domain": regle.domain.value,
                    "rule_id": regle.id,
                    "rule_type": regle.rule_type.value,
                    "rule_status": regle.status.value,
                    "rule_priority": regle.priority.value,
                    "family_code": CODES_FAMILLES[famille],
                    "family_kind": famille.value,
                    "family_id": retenue.id if retenue else "",
                    "family_score": potentiel.score,
                    "retained": bool(retenue),
                    "question_type": PROFILS[famille].question_type.value,
                    "reasoning_trap": (
                        retenue.reasoning_trap.value if retenue else _piege(regle, famille).value
                    ),
                    "predicted_difficulty": (
                        retenue.predicted_difficulty
                        if retenue
                        else _difficulte(regle, famille)[0]
                    ),
                    "priority": (
                        retenue.priority.value if retenue else _priorite(regle, famille).value
                    ),
                    "candidate_family_status": (
                        retenue.candidate_family_status.value if retenue else "not_retained"
                    ),
                    "twin_group_id": (retenue.twin_group_id or "") if retenue else "",
                    "twin_type": (
                        retenue.twin_type.value if retenue and retenue.twin_type else ""
                    ),
                    "concept_tested": concept_teste(regle),
                    "redundancy_group_id": groupe_redondance(regle),
                    "family_rationale": potentiel.rationale,
                }
            )
    return lignes


def faisabilite_distribution(
    familles: list[CandidateFamily], corpus: Corpus = Corpus.PUBLIC
) -> dict:
    """Le Rulebook permet-il réellement la distribution visée (§10) ?

    Le rendement par famille est une hypothèse de planification (2 items pour un
    score 2, 3 pour un score 3), pas une promesse. Elle est affichée pour qu'on
    puisse la contester plutôt que la subir.
    """
    cible_totale = CIBLES_V0[corpus.value]
    par_type: Counter[str] = Counter()
    for famille in familles:
        par_type[famille.question_type.value] += RENDEMENT_PAR_SCORE.get(
            famille.family_score, 0
        )

    lignes = []
    for type_question, poids in sorted(POIDS_TYPES_V0.items()):
        cible = round(cible_totale * poids)
        possible = par_type.get(type_question, 0)
        lignes.append(
            {
                "question_type": type_question,
                "target_share": poids,
                "target_items": cible,
                "families": sum(
                    1 for f in familles if f.question_type.value == type_question
                ),
                "estimated_items": possible,
                "gap": possible - cible,
                "achievable": possible >= cible,
            }
        )

    par_domaine = []
    cibles_domaines = CIBLES_DOMAINES_EXPLICITES_V0.get(corpus.value, {})
    for domaine in sorted(d.value for d in Domain):
        concernees = [f for f in familles if f.domain.value == domaine]
        possible = sum(RENDEMENT_PAR_SCORE.get(f.family_score, 0) for f in concernees)
        cible = cibles_domaines.get(domaine, 0)
        par_domaine.append(
            {
                "domain": domaine,
                "target_items": cible,
                "families": len(concernees),
                "estimated_items": possible,
                "gap": possible - cible,
                "achievable": possible >= cible,
            }
        )

    return {
        "corpus": corpus.value,
        "target_total": cible_totale,
        "estimated_items_total": sum(
            RENDEMENT_PAR_SCORE.get(f.family_score, 0) for f in familles
        ),
        "yield_hypothesis": {str(k): v for k, v in sorted(RENDEMENT_PAR_SCORE.items())},
        "by_question_type": lignes,
        "by_domain": par_domaine,
        "achievable": all(ligne["achievable"] for ligne in lignes),
    }


def lacunes(regles: list[Rule], familles: list[CandidateFamily]) -> dict:
    """Ce que la carte ne couvre pas : familles absentes, règles inexploitées, jumeaux manquants."""
    par_regle: dict[str, list[CandidateFamily]] = defaultdict(list)
    for famille in familles:
        par_regle[famille.rule_id].append(famille)

    sans_famille = sorted(r.id for r in regles if not par_regle.get(r.id))

    presentes = {f.family_kind for f in familles}
    familles_absentes = [f.value for f in ORDRE_FAMILLES if f not in presentes]

    pieges_presents = {f.reasoning_trap.value for f in familles} | {
        f.mimicked_trap.value for f in familles if f.mimicked_trap
    }
    pieges_absents = sorted(
        t.value for t in ReasoningTrap if t is not ReasoningTrap.NONE and t.value not in pieges_presents
    )

    fausses_sans_jumeau = sorted(
        f.id
        for f in familles
        if f.family_kind is FamilyKind.FALSE_PREMISE and not f.twin_candidate
    )

    par_domaine_famille: dict[str, set[str]] = defaultdict(set)
    for famille in familles:
        par_domaine_famille[famille.domain.value].add(famille.family_kind.value)
    manques_par_domaine = {
        domaine.value: sorted(
            f.value for f in ORDRE_FAMILLES if f.value not in par_domaine_famille[domaine.value]
        )
        for domaine in Domain
    }

    charge = Counter(f.rule_id for f in familles)
    return {
        "rules_without_family": sans_famille,
        "missing_family_kinds": familles_absentes,
        "missing_traps": pieges_absents,
        "false_premises_without_twin": fausses_sans_jumeau,
        "missing_family_kinds_by_domain": manques_par_domaine,
        "most_exploited_rules": [
            {"rule_id": rid, "families": n} for rid, n in charge.most_common(5)
        ],
        "least_exploited_rules": [
            {"rule_id": rid, "families": charge.get(rid, 0)}
            for rid in sorted(r.id for r in regles)
            if charge.get(rid, 0) <= 1
        ],
    }


def redondances(familles: list[CandidateFamily], regles: list[Rule]) -> dict:
    """Groupes de redondance, et collisions à trancher (§8).

    Deux familles du même groupe qui mesurent la même chose de la même façon
    sont candidates à la redondance. Mais partager un article ne suffit pas :
    un article porte couramment plusieurs obligations distinctes, et le QC du
    Rulebook a déjà tranché cette question — c'est la **proximité des énoncés**
    qui sépare le vrai doublon du simple ancrage commun. La carte applique la
    même règle, avec le même seuil, pour ne pas dire deux choses différentes du
    même Rulebook.
    """
    par_id = {r.id: r for r in regles}
    groupes: dict[str, list[CandidateFamily]] = defaultdict(list)
    for famille in familles:
        groupes[famille.redundancy_group_id].append(famille)

    collisions = []
    for groupe, membres in sorted(groupes.items()):
        vus: dict[tuple[str, str], list[CandidateFamily]] = defaultdict(list)
        for famille in membres:
            vus[(famille.family_kind.value, famille.reasoning_trap.value)].append(famille)
        for (kind, piege), concernees in sorted(vus.items()):
            if len(concernees) < 2:
                continue
            ordonnees = sorted(concernees, key=lambda f: f.id)
            for suivante in ordonnees[1:]:
                premiere = ordonnees[0]
                gauche, droite = par_id.get(premiere.rule_id), par_id.get(suivante.rule_id)
                proximite = (
                    proximite_enonces(gauche.statement, droite.statement)
                    if gauche is not None and droite is not None
                    else 1.0
                )
                collisions.append(
                    {
                        "redundancy_group_id": groupe,
                        "family_kind": kind,
                        "reasoning_trap": piege,
                        "family_ids": [premiere.id, suivante.id],
                        "rule_ids": sorted({premiere.rule_id, suivante.rule_id}),
                        "statement_proximity": round(proximite, 3),
                        # Même ancrage, mêmes mots : les deux familles ne
                        # différeraient que par la formulation.
                        "redundant": proximite >= SEUIL_DOUBLON,
                        "concepts": sorted({premiere.concept_tested, suivante.concept_tested}),
                    }
                )

    return {
        "groups": [
            {
                "redundancy_group_id": groupe,
                "families": len(membres),
                "rules": sorted({f.rule_id for f in membres}),
                "concepts": sorted({f.concept_tested for f in membres}),
            }
            for groupe, membres in sorted(groupes.items())
            if len({f.rule_id for f in membres}) > 1
        ],
        "collisions": collisions,
        "number_of_groups": len(groupes),
        "number_redundant": sum(1 for c in collisions if c["redundant"]),
        "proximity_threshold": SEUIL_DOUBLON,
    }
