"""Du dossier d'arbitrage au plan de travail : quoi faire, dans quel ordre, pour quel gain.

Le pack d'arbitrage s'adresse au juriste, règle par règle. Il ne dit pas par où
commencer. Or quarante-quatre décisions ne se valent pas : une seule
consultation du Code monétaire et financier lève le blocage de douze règles,
là où une adjudication d'exception n'en sert qu'une.

Ce module range donc les dossiers en **actions**, et les actions en ordre :

| Regroupement | Ce qu'il économise |
|---|---|
| lot de lecture | un seul document ouvert sert plusieurs dossiers |
| cluster de décision | une seule décision couvre plusieurs règles |

Les deux ne disent pas la même chose et ne se confondent pas. Lire une fois le
règlement SFDR sert six dossiers ; cela n'en tranche aucun. Une décision sur
l'article 25 de MiFID II en tranche quatre d'un coup.

**Rien ici ne promeut quoi que ce soit.** `expected_status_after_decision`
décrit ce qu'une décision *rendue et signée* permettrait, jamais ce qu'elle
produit : le statut se recalcule en rejouant l'audit, il ne se déduit pas d'un
plan. Et sur une règle dont le texte n'a pas pu être lu, ce champ dit ce qu'il
ne sait pas — les blocages qu'un texte encore fermé révélera ne se devinent pas.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.bench.adjudication import Dossier, regroupements
from src.bench.completude import PREFIXE_PORTANCE, ConstatCompletude
from src.bench.readiness import BlockerCategory
from src.bench.relecture import AccesSource


class ActionPrincipale(str, Enum):
    """L'action qui lève le blocage principal. Une seule par règle.

    Une règle peut porter plusieurs blocages ; elle n'a qu'une prochaine étape.
    En nommer deux reviendrait à ne pas dire par où commencer.
    """

    #: Le texte existe mais n'est pas atteignable : il faut aller le lire ailleurs.
    SOURCE_CONSULTATION = "SOURCE_CONSULTATION"
    #: Une dérogation est-elle applicable, ou n'y en a-t-il aucune dans le périmètre ?
    EXCEPTION_ADJUDICATION = "EXCEPTION_ADJUDICATION"
    #: Une absence à établir sur un périmètre, jamais sur un extrait.
    NEGATIVE_CLAIM_REVIEW = "NEGATIVE_CLAIM_REVIEW"
    #: Quelle version fait foi, et à quelle date une question se placerait.
    TEMPORAL_REVIEW = "TEMPORAL_REVIEW"
    #: L'URL enregistrée ne désigne plus de document : la source est à réancrer.
    SOURCE_REANCHORING = "SOURCE_REANCHORING"
    #: L'énoncé lui-même ne tient pas : il se réécrit ou se découpe.
    RULE_REFORMULATION = "RULE_REFORMULATION"
    OTHER = "OTHER"


#: Blocage principal → action, quand l'accès au texte n'impose rien d'autre.
ACTION_PAR_BLOCAGE: dict[BlockerCategory, ActionPrincipale] = {
    BlockerCategory.SOURCE_INCOMPLETE: ActionPrincipale.SOURCE_CONSULTATION,
    BlockerCategory.EXCEPTION_UNRESOLVED: ActionPrincipale.EXCEPTION_ADJUDICATION,
    BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED: ActionPrincipale.NEGATIVE_CLAIM_REVIEW,
    BlockerCategory.TEMPORAL_UNRESOLVED: ActionPrincipale.TEMPORAL_REVIEW,
    BlockerCategory.RULE_TOO_ABSTRACT: ActionPrincipale.RULE_REFORMULATION,
    BlockerCategory.CROSS_REFERENCE_UNRESOLVED: ActionPrincipale.OTHER,
    BlockerCategory.SCHEMA_INCOMPLETE: ActionPrincipale.OTHER,
    BlockerCategory.HUMAN_REVIEW_REQUIRED: ActionPrincipale.OTHER,
    BlockerCategory.OTHER: ActionPrincipale.OTHER,
}

#: Clé interne : le réancrage d'une règle dont l'acte a bien été lu ne demande
#: pas la même preuve que celui d'une URL morte.
_REANCRAGE_SUR_ACTE_LU = "SOURCE_REANCHORING_ACTE_LU"

#: Ce que le relecteur doit rapporter pour que sa décision soit recevable. Sans
#: cette colonne, « revue faite » ne se contrôle pas.
PREUVE_ATTENDUE: dict[ActionPrincipale | str, str] = {
    ActionPrincipale.SOURCE_CONSULTATION: (
        "le texte de la disposition dans sa version applicable, sa référence de "
        "publication, et la signature (verifie_par + date_verification) portée au "
        "dossier de vérification"
    ),
    ActionPrincipale.SOURCE_REANCHORING: (
        "le document réellement en vigueur, son titre exact, sa référence et "
        "l'emplacement constaté — portés au dossier de vérification, jamais "
        "inscrits d'office dans la règle"
    ),
    _REANCRAGE_SUR_ACTE_LU: (
        "l'article précis de l'acte déjà consulté qui porte l'obligation énoncée, "
        "et l'ancrage rectifié — un ancrage qui couvre l'acte entier ne permet à "
        "aucun gold de citer sa disposition"
    ),
    ActionPrincipale.EXCEPTION_ADJUDICATION: (
        "le périmètre réellement examiné (source_scope) et, s'il en existe, les "
        "phrases de dérogation recopiées telles quelles du texte officiel"
    ),
    ActionPrincipale.NEGATIVE_CLAIM_REVIEW: (
        "le périmètre couvert (searched_in) et, si le texte la porte, la "
        "disposition qui contredit l'affirmation (actual_provision)"
    ),
    ActionPrincipale.TEMPORAL_REVIEW: (
        "la version consolidée applicable et sa date, ou l'attestation que la "
        "version déclarée fait foi"
    ),
    ActionPrincipale.RULE_REFORMULATION: (
        "l'énoncé de remplacement, au plus près de la lettre de l'article, ou le "
        "découpage proposé et l'ancrage de chaque règle issue du découpage"
    ),
    ActionPrincipale.OTHER: (
        "la signature du dossier de vérification, et le motif de gold_ready"
    ),
}

#: Blocages qui ne sont pas du travail juridique : la signature les lève, et
#: c'est l'acte même de décider qui la porte.
BLOCAGES_DE_PROCEDURE: frozenset[str] = frozenset({"statut_non_validated"})


@dataclass(frozen=True)
class LigneAction:
    """Une règle, ce qui la bloque, ce qu'on attend, et ce que cela permettrait."""

    rule_id: str
    domain: str
    priority: str
    blocker: str
    secondary_blockers: tuple[str, ...]
    source: str
    article: str
    paragraph: str
    source_access_status: AccesSource
    review_cluster: str
    exact_decision_required: str
    required_evidence: str
    proposed_action: ActionPrincipale
    expected_status_after_decision: str
    #: Vrai si, une fois cette action rendue et signée, plus aucun blocage de
    #: fond ne resterait sur la règle. Sert la projection, jamais un statut.
    acheve_la_regle: bool
    statut_courant: str


def action_principale(dossier: Dossier, acces: AccesSource) -> ActionPrincipale:
    """L'action qui lève le blocage principal, corrigée par l'état d'accès.

    Un blocage de source ne dit pas *pourquoi* le texte manque, et les trois cas
    n'appellent pas le même travail :

    - la source refuse (403 après tunnel établi) : il faut aller lire ailleurs ;
    - l'URL ne désigne plus rien (404) : la source se réancre ;
    - l'acte a bien été récupéré : alors ce n'est pas l'accès qui bloque mais
      l'ancrage — « Ensemble de la directive » ne désigne aucune disposition, et
      l'article cité peut aussi ne pas exister dans l'acte cité. Envoyer
      quelqu'un consulter un texte déjà consulté ne lèverait rien.
    """
    if dossier.blocage_categorie is BlockerCategory.SOURCE_INCOMPLETE:
        if acces is AccesSource.REFUS_DE_LA_SOURCE or acces is AccesSource.INDETERMINE:
            return ActionPrincipale.SOURCE_CONSULTATION
        return ActionPrincipale.SOURCE_REANCHORING
    if (
        dossier.blocage_categorie is BlockerCategory.HUMAN_REVIEW_REQUIRED
        and dossier.blocage == "enonce_fidele"
    ):
        return ActionPrincipale.RULE_REFORMULATION
    return ACTION_PAR_BLOCAGE.get(dossier.blocage_categorie, ActionPrincipale.OTHER)


def preuve_requise(action: ActionPrincipale, acces: AccesSource) -> str:
    """Ce qu'il faut rapporter pour que la décision soit recevable.

    Un réancrage sur un acte déjà lu ne demande pas de retrouver un document :
    il demande de nommer l'article.
    """
    if action is ActionPrincipale.SOURCE_REANCHORING and acces is AccesSource.TEXTE_RECUPERE:
        return PREUVE_ATTENDUE[_REANCRAGE_SUR_ACTE_LU]
    return PREUVE_ATTENDUE[action]


def _blocages_de_fond(dossier: Dossier) -> tuple[str, ...]:
    """Les blocages restants qui demandent autre chose qu'une signature."""
    return tuple(
        blocage
        for blocage in dossier.blocages_restants
        if not any(procedure in blocage for procedure in BLOCAGES_DE_PROCEDURE)
    )


def portance_etablie(constat: ConstatCompletude) -> bool:
    """L'énoncé porte-t-il assez pour qu'un gold s'y adosse ?

    Le calcul a déjà eu lieu à l'audit ; on le relit dans son motif plutôt que
    de le refaire, pour que deux réponses ne puissent pas diverger.
    """
    return constat.gold_ready or constat.gold_ready_reason.startswith(PREFIXE_PORTANCE)


def statut_projete(
    dossier: Dossier, acces: AccesSource, restants: tuple[str, ...]
) -> str:
    """Ce qu'une décision rendue **et signée** permettrait — jamais ce qu'elle produit."""
    if acces is not AccesSource.TEXTE_RECUPERE:
        return (
            f"`{dossier.current_status}` → `source_checked` si la consultation est "
            f"signée. Les blocages que le texte révélera ne sont pas connus avant "
            f"lecture : l'audit les fera apparaître, ils ne se devinent pas ici"
        )
    if dossier.blocage_categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return (
            f"statut inchangé (`{dossier.current_status}`) tant que l'ancrage ne "
            f"désigne pas une disposition ; une fois l'article cité, l'audit rejoué "
            f"dira ce qui reste — il ne se devine pas ici"
        )
    if restants:
        return (
            f"statut inchangé (`{dossier.current_status}`) : {len(restants)} blocage(s) "
            f"de fond resteraient après cette décision"
        )
    return (
        f"`{dossier.current_status}` → `validated` possible si la décision est signée ; "
        f"`gold_ready` est alors recalculé, il n'est pas accordé par la décision"
    )


def construire_lignes(
    dossiers: list[Dossier],
    acces: dict[str, AccesSource],
) -> list[LigneAction]:
    """Une ligne par dossier P0/P1, dans l'ordre du pack."""
    lignes: list[LigneAction] = []
    for dossier in dossiers:
        etat_acces = acces.get(dossier.rule_id, AccesSource.INDETERMINE)
        action = action_principale(dossier, etat_acces)
        restants = _blocages_de_fond(dossier)
        lignes.append(
            LigneAction(
                rule_id=dossier.rule_id,
                domain=dossier.domain,
                priority=dossier.priorite_revue,
                blocker=dossier.blocage_categorie.value,
                secondary_blockers=dossier.blocages_restants,
                source=dossier.source_texte,
                article=dossier.source_article,
                paragraph=dossier.source_paragraphe,
                source_access_status=etat_acces,
                review_cluster=dossier.review_cluster_id,
                exact_decision_required=dossier.neutral_legal_question,
                required_evidence=preuve_requise(action, etat_acces),
                proposed_action=action,
                expected_status_after_decision=statut_projete(dossier, etat_acces, restants),
                acheve_la_regle=(etat_acces is AccesSource.TEXTE_RECUPERE and not restants),
                statut_courant=dossier.current_status,
            )
        )
    return lignes


# --------------------------------------------------------------------------- #
# Regroupements : ce qu'une seule action sert
# --------------------------------------------------------------------------- #

#: Actions qui butent sur l'accès au texte : elles se regroupent par document,
#: puisque c'est le document qu'il faut aller chercher.
ACTIONS_D_ACCES: frozenset[ActionPrincipale] = frozenset(
    {ActionPrincipale.SOURCE_CONSULTATION, ActionPrincipale.SOURCE_REANCHORING}
)


@dataclass(frozen=True)
class Groupe:
    """Un ensemble de règles qu'une seule action sert, et ce qu'elle leur fait."""

    identifiant: str
    nature: str
    action: ActionPrincipale
    source: str
    articles: tuple[str, ...]
    regles: tuple[str, ...]
    question_unique: str
    #: Règles dont l'action lève le blocage principal.
    regles_debloquees: int
    #: Règles qui, après cette action, ne porteraient plus aucun blocage de fond.
    regles_achevees: int


def lots_de_lecture(lignes: list[LigneAction]) -> list[Groupe]:
    """Les règles dont le texte primaire n'est pas atteignable, par document.

    Ce n'est pas un cluster de décision : ces règles ne posent pas la même
    question, elles butent sur le même empêchement. Une consultation du document
    les sert toutes ; les décisions restent individuelles.
    """
    par_source: dict[str, list[LigneAction]] = {}
    for ligne in lignes:
        if ligne.proposed_action is ActionPrincipale.SOURCE_CONSULTATION:
            par_source.setdefault(ligne.source, []).append(ligne)

    groupes: list[Groupe] = []
    for source, membres in sorted(par_source.items()):
        # Un lot suppose plusieurs dossiers : une règle seule n'économise rien,
        # et l'annoncer comme un lot gonflerait le rendement affiché.
        if len(membres) < 2:
            continue
        groupes.append(
            Groupe(
                identifiant="LOT-" + _abreger(source),
                nature="lot de lecture",
                action=ActionPrincipale.SOURCE_CONSULTATION,
                source=source,
                articles=tuple(sorted({m.article for m in membres if m.article})),
                regles=tuple(m.rule_id for m in membres),
                question_unique=(
                    f"Le texte de {source} confirme-t-il les énoncés des règles du lot, "
                    f"article par article ? Une consultation sert tout le lot ; chaque "
                    f"règle garde sa décision."
                ),
                regles_debloquees=len(membres),
                regles_achevees=sum(1 for m in membres if m.acheve_la_regle),
            )
        )
    return groupes


def clusters_de_decision(dossiers: list[Dossier], lignes: list[LigneAction]) -> list[Groupe]:
    """Les clusters déjà définis : une seule décision couvre plusieurs règles."""
    par_id = {ligne.rule_id: ligne for ligne in lignes}
    groupes: list[Groupe] = []
    for cluster, membres in regroupements(dossiers).items():
        concernees = [par_id[d.rule_id] for d in membres if d.rule_id in par_id]
        groupes.append(
            Groupe(
                identifiant=cluster,
                nature="cluster de décision",
                action=(
                    concernees[0].proposed_action
                    if concernees
                    else ActionPrincipale.EXCEPTION_ADJUDICATION
                ),
                source=membres[0].source_texte,
                articles=tuple(sorted({d.source_article for d in membres if d.source_article})),
                regles=tuple(d.rule_id for d in membres),
                question_unique=membres[0].neutral_legal_question,
                regles_debloquees=len(membres),
                regles_achevees=sum(1 for m in concernees if m.acheve_la_regle),
            )
        )
    return groupes


def _abreger(intitule: str) -> str:
    """Initiales des mots significatifs d'un intitulé d'acte."""
    import re
    import unicodedata

    sans_accent = "".join(
        c for c in unicodedata.normalize("NFD", intitule) if unicodedata.category(c) != "Mn"
    )
    vides = {"DE", "DU", "DES", "LA", "LE", "LES", "ET", "L", "D", "UE", "N", "AU", "AUX"}
    mots = [m for m in re.findall(r"[A-Za-z0-9]+", sans_accent.upper()) if m not in vides]
    return "".join(m[0] for m in mots)[:8] or "ACTE"


# --------------------------------------------------------------------------- #
# Ordre d'exécution (§6)
# --------------------------------------------------------------------------- #

#: Les cinq rangs de la spécification, dans l'ordre. Le rang prime toujours sur
#: le nombre de règles : une décision individuelle P0, même isolée, passe avant
#: n'importe quel P1.
RANGS: tuple[str, ...] = (
    "consultation débloquant plusieurs règles",
    "cluster de décision commun",
    "correction de source (réancrage, ou consultation isolée)",
    "décision individuelle P0",
    "décision individuelle P1",
)


@dataclass(frozen=True)
class Etape:
    """Une étape du plan : ce qu'on fait, sur quoi, et ce que cela débloque."""

    rang: int
    intitule: str
    nature: str
    action: ActionPrincipale
    regles: tuple[str, ...]
    regles_debloquees: int
    regles_achevees: int

    @property
    def rendement(self) -> float:
        """Règles débloquées par action de revue. Le critère du §6."""
        return float(self.regles_debloquees)


def ordre_execution(lignes: list[LigneAction], groupes: list[Groupe]) -> list[Etape]:
    """Le plan, du rendement le plus élevé au plus faible, à rang égal.

    Les priorités P0/P1 ne sont pas touchées : elles fixent la gravité, pas
    l'ordre d'exécution. Une consultation qui débloque douze règles passe avant
    une décision P0 isolée parce qu'elle coûte le même travail pour douze fois
    le résultat — pas parce qu'elle serait plus grave.
    """
    etapes: list[Etape] = []
    servies: set[str] = set()

    for groupe in groupes:
        rang = 1 if groupe.nature == "lot de lecture" else 2
        etapes.append(
            Etape(
                rang=rang,
                intitule=groupe.identifiant,
                nature=groupe.nature,
                action=groupe.action,
                regles=groupe.regles,
                regles_debloquees=groupe.regles_debloquees,
                regles_achevees=groupe.regles_achevees,
            )
        )
        servies.update(groupe.regles)

    for ligne in lignes:
        if ligne.rule_id in servies:
            continue
        if ligne.proposed_action in ACTIONS_D_ACCES:
            # Travail sur la source, hors lot : réancrage, ou consultation isolée.
            rang = 3
        elif ligne.priority == "P0":
            rang = 4
        else:
            rang = 5
        etapes.append(
            Etape(
                rang=rang,
                intitule=ligne.rule_id,
                nature="décision individuelle",
                action=ligne.proposed_action,
                regles=(ligne.rule_id,),
                regles_debloquees=1,
                regles_achevees=1 if ligne.acheve_la_regle else 0,
            )
        )

    return sorted(etapes, key=lambda e: (e.rang, -e.regles_debloquees, e.intitule))


# --------------------------------------------------------------------------- #
# Projection (§7) — jamais un statut
# --------------------------------------------------------------------------- #

MARQUE_PROJECTION = "PROJECTED_ONLY"


@dataclass(frozen=True)
class Projection:
    """Ce qu'une résolution *permettrait*. Aucun statut n'en découle."""

    validated: int
    gold_ready: int
    family_ready: int
    #: Règles P0/P1 qui, leur décision rendue et signée, ne porteraient plus de
    #: blocage de fond.
    eligibles_apres_arbitrage: int
    #: Parmi elles, celles dont l'énoncé porte déjà assez pour un gold.
    eligibles_avec_portance: int


def projeter(
    lignes: list[LigneAction],
    constats: dict[str, ConstatCompletude],
    validated: int,
    gold_ready: int,
    family_ready: int,
) -> Projection:
    """Compte ce que les arbitrages rendraient éligible — sans rien promettre."""
    achevees = [ligne for ligne in lignes if ligne.acheve_la_regle]
    return Projection(
        validated=validated,
        gold_ready=gold_ready,
        family_ready=family_ready,
        eligibles_apres_arbitrage=len(achevees),
        eligibles_avec_portance=sum(
            1
            for ligne in achevees
            if ligne.rule_id in constats and portance_etablie(constats[ligne.rule_id])
        ),
    )


# --------------------------------------------------------------------------- #
# Critères de sortie (§8)
# --------------------------------------------------------------------------- #


def elements_bloquants(
    lignes: list[LigneAction], anomalies: list[str], family_ready: int
) -> list[str]:
    """Ce qui empêche encore `READY_FOR_FAMILY_GENERATION`, du plus lourd au plus léger."""
    bloquants: list[str] = []
    if anomalies:
        bloquants.append(
            f"{len(anomalies)} anomalie(s) d'intégrité du Rulebook : un Rulebook "
            f"incohérent n'est pas exploitable, quel que soit le nombre de règles prêtes"
        )
    if not family_ready:
        bloquants.append("aucune règle family_ready : la génération n'aurait rien à ancrer")

    p0 = sum(1 for ligne in lignes if ligne.priority == "P0")
    p1 = sum(1 for ligne in lignes if ligne.priority == "P1")
    if p0 or p1:
        bloquants.append(
            f"{p0 + p1} arbitrage(s) en attente ({p0} P0, {p1} P1) : générer maintenant "
            f"figerait des familles sur des règles dont la portée reste à trancher"
        )

    sans_texte = [ligne for ligne in lignes if ligne.source_access_status is not AccesSource.TEXTE_RECUPERE]
    if sans_texte:
        sources = sorted({ligne.source for ligne in sans_texte})
        bloquants.append(
            f"{len(sans_texte)} règle(s) dont le texte primaire n'a pas été lu "
            f"({', '.join(sources)}) : aucune réponse de référence ne pourrait leur "
            f"être opposée"
        )
    return bloquants


def prochaine_action(etapes: list[Etape]) -> str:
    """Une seule action concrète, la première du plan."""
    if not etapes:
        return "aucune : plus aucun arbitrage P0 ou P1 n'est en attente"
    premiere = etapes[0]
    return (
        f"{premiere.action.value} sur {premiere.intitule} "
        f"({premiere.nature}) — {premiere.regles_debloquees} règle(s) débloquée(s) : "
        f"{', '.join(premiere.regles)}"
    )
