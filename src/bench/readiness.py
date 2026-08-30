"""Écart entre une règle vérifiée et une règle exploitable pour une famille.

Trois seuils se suivent sans se confondre, et l'essentiel de cette phase tient à
ne pas les mélanger :

| Seuil | Ce qu'il affirme |
|---|---|
| `validated` | la règle est juridiquement établie |
| `gold_ready` | on peut en tirer une réponse de référence **sans réinterpréter le droit** |
| `family_ready` | elle peut ancrer une famille de questions du benchmark |

`gold_ready` a d'abord été calculé sur la seule **portance** de l'énoncé — sa
précision. C'était faux, et le chiffre le montrait : quarante et une règles
étaient dites prêtes, dont treize dont la source n'était même pas vérifiée. Un
énoncé parfaitement porteur adossé à une source non consultée ne produit pas un
gold prêt : il produit un gold qui a l'air prêt. `gold_ready` exige donc
désormais la portance **et** ses prérequis probatoires (`PREREQUIS_GOLD`).

`family_ready` ajoute ce que la génération de familles suppose en plus : une
règle réellement `validated`, et de quoi construire des angles — confusions
typiques, pièges, familles candidates. Une règle exacte, précise et sans aucune
confusion documentée n'ancre aucune fausse prémisse crédible.

Les blocages sont **normalisés**. Une catégorie par règle donnerait un rapport
illisible et non comparable d'une passe à l'autre ; neuf catégories couvrent
tout, et le blocage principal est choisi par ordre de fondamentalité — on ne
reproche pas son abstraction à une règle dont la source n'est pas vérifiée.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.bench.completude import ConstatCompletude, PREREQUIS_GOLD
from src.bench.regles import Rule
from src.bench.rulebook import (
    EXCEPTIONS_ABOUTIES,
    ExceptionsStatus,
    NegativeClaimStatus,
    Priority,
    RuleStatus,
)


class BlockerCategory(str, Enum):
    """Catégories normalisées de blocage. Neuf, et pas une par règle."""

    EXCEPTION_UNRESOLVED = "EXCEPTION_UNRESOLVED"
    SOURCE_INCOMPLETE = "SOURCE_INCOMPLETE"
    TEMPORAL_UNRESOLVED = "TEMPORAL_UNRESOLVED"
    RULE_TOO_ABSTRACT = "RULE_TOO_ABSTRACT"
    CROSS_REFERENCE_UNRESOLVED = "CROSS_REFERENCE_UNRESOLVED"
    NEGATIVE_CLAIM_UNRESOLVED = "NEGATIVE_CLAIM_UNRESOLVED"
    SCHEMA_INCOMPLETE = "SCHEMA_INCOMPLETE"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    OTHER = "OTHER"


#: Ordre de fondamentalité : le blocage principal d'une règle est le premier de
#: cette liste qui la concerne. Reprocher son abstraction à une règle dont la
#: source n'est pas vérifiée ferait travailler dans le mauvais ordre.
ORDRE_BLOCAGES: tuple[BlockerCategory, ...] = (
    BlockerCategory.SOURCE_INCOMPLETE,
    BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED,
    BlockerCategory.EXCEPTION_UNRESOLVED,
    BlockerCategory.TEMPORAL_UNRESOLVED,
    BlockerCategory.CROSS_REFERENCE_UNRESOLVED,
    BlockerCategory.RULE_TOO_ABSTRACT,
    BlockerCategory.SCHEMA_INCOMPLETE,
    BlockerCategory.HUMAN_REVIEW_REQUIRED,
    BlockerCategory.OTHER,
)

#: Critère de complétude → catégorie de blocage. La table est explicite pour que
#: l'ajout d'un critère oblige à dire dans quelle catégorie il tombe.
CATEGORIE_PAR_CRITERE: dict[str, BlockerCategory] = {
    "source_primaire_verifiee": BlockerCategory.SOURCE_INCOMPLETE,
    "article_verifie": BlockerCategory.SOURCE_INCOMPLETE,
    "enonce_fidele": BlockerCategory.HUMAN_REVIEW_REQUIRED,
    "exceptions_recherchees": BlockerCategory.EXCEPTION_UNRESOLVED,
    "conditions_capturees": BlockerCategory.SCHEMA_INCOMPLETE,
    "temporalite_etablie": BlockerCategory.TEMPORAL_UNRESOLVED,
    "renvois_verifies": BlockerCategory.CROSS_REFERENCE_UNRESOLVED,
    "affirmations_negatives_resolues": BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED,
    "sans_ambiguite": BlockerCategory.HUMAN_REVIEW_REQUIRED,
}

#: Catégories dont une erreur se paie en pratique : un professionnel qui suit une
#: règle amputée de son exception, appliquée à la mauvaise date, ou fondée sur
#: une absence non vérifiée, agit de travers.
CATEGORIES_DANGEREUSES: frozenset[BlockerCategory] = frozenset(
    {
        BlockerCategory.EXCEPTION_UNRESOLVED,
        BlockerCategory.TEMPORAL_UNRESOLVED,
        BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED,
        BlockerCategory.CROSS_REFERENCE_UNRESOLVED,
    }
)


@dataclass(frozen=True)
class Blocage:
    """Un blocage, sa catégorie, et ce qu'il empêche concrètement."""

    category: BlockerCategory
    critere: str
    explanation: str


@dataclass(frozen=True)
class ConstatReadiness:
    """L'état d'une règle vis-à-vis des trois seuils, et ce qui la retient."""

    rule_id: str
    domain: str
    status: RuleStatus
    priority: Priority
    gold_ready: bool
    family_ready: bool
    blocages: tuple[Blocage, ...] = ()
    priorite_revue: str = ""
    decision_requise: str = ""
    #: Divergence entre le `gold_ready` stocké sur la règle et le calcul.
    gold_ready_stocke: bool = False

    @property
    def blocage_principal(self) -> Blocage | None:
        for categorie in ORDRE_BLOCAGES:
            for blocage in self.blocages:
                if blocage.category is categorie:
                    return blocage
        return None

    @property
    def blocker_category(self) -> str:
        principal = self.blocage_principal
        return principal.category.value if principal else ""

    @property
    def family_blocker(self) -> str:
        principal = self.blocage_principal
        return principal.critere if principal else ""

    @property
    def explanation(self) -> str:
        principal = self.blocage_principal
        return principal.explanation if principal else ""

    @property
    def demande_arbitrage(self) -> bool:
        return bool(self.decision_requise)


#: Ce qu'une règle doit porter pour qu'on puisse en dériver des angles de
#: question. Une règle exacte et sans aucune confusion documentée n'ancre aucune
#: fausse prémisse crédible : elle est vraie, et muette.
def _matiere_a_familles(regle: Rule) -> bool:
    return bool(
        regle.common_confusions or regle.reasoning_traps or regle.candidate_question_families
    )


def _explication(critere: str, regle: Rule, constat: ConstatCompletude) -> str:
    """Ce que le blocage empêche, dit en fonction de la règle concernée."""
    article = regle.source.article or "(article absent)"
    if critere == "source_primaire_verifiee":
        return (
            f"la source n'a pas été confrontée au texte primaire "
            f"({regle.verification_method.value}) : aucune réponse de référence "
            f"ne pourrait être opposée"
        )
    if critere == "article_verifie":
        return f"« {article} » n'a pas été retrouvé dans l'acte cité"
    if critere == "enonce_fidele":
        return "l'énoncé n'est pas corroboré par le texte cité"
    if critere == "exceptions_recherchees":
        return (
            f"recherche d'exceptions « {constat.exceptions_status.value} » : une "
            f"question construite ici testerait la règle comme un absolu"
        )
    if critere == "conditions_capturees":
        return "aucune structure juridique repérée dans l'article : rien à conditionner"
    if critere == "temporalite_etablie":
        return (
            f"temporalité « {constat.temporal_status} » non établie : la date "
            f"d'appréciation de la question serait arbitraire"
        )
    if critere == "renvois_verifies":
        return (
            f"renvois non résolus ({', '.join(constat.renvois[:5]) or 'indéterminés'}) : "
            f"la règle dépend d'articles non consultés"
        )
    if critere == "affirmations_negatives_resolues":
        non_verifiees = [
            c.claim
            for c in regle.negative_claims
            if c.status is NegativeClaimStatus.UNVERIFIED
        ]
        return (
            f"{len(non_verifiees)} affirmation(s) négative(s) non vérifiée(s) : un "
            f"gold affirmerait une absence que rien n'atteste"
        )
    if critere == "sans_ambiguite":
        return "ambiguïté non levée sur la portée de la règle"
    if critere == "statut_non_validated":
        return (
            f"règle en « {regle.status.value} » : seul « validated » ancre une famille"
        )
    if critere == "matiere_a_familles":
        return (
            "ni confusion typique, ni piège, ni famille candidate : la règle est "
            "exacte et muette, aucun angle ne s'en déduit"
        )
    if critere == "portance":
        return constat.gold_ready_reason
    return "blocage non catégorisé"


def evaluer(regle: Rule, constat: ConstatCompletude) -> ConstatReadiness:
    """Situe une règle sur les trois seuils et nomme ce qui la retient."""
    blocages: list[Blocage] = []

    def ajouter(critere: str, categorie: BlockerCategory) -> None:
        blocages.append(Blocage(categorie, critere, _explication(critere, regle, constat)))

    # -- prérequis de gold_ready --
    for critere in PREREQUIS_GOLD:
        if not constat.criteres_gold.get(critere, False):
            ajouter(critere, CATEGORIE_PAR_CRITERE.get(critere, BlockerCategory.OTHER))
    if constat.criteres_gold and not constat.gold_ready and all(
        constat.criteres_gold.get(c, False) for c in PREREQUIS_GOLD
    ):
        # Prérequis tenus mais pas prête : c'est la formulation qui bloque.
        ajouter("portance", BlockerCategory.RULE_TOO_ABSTRACT)
    if not constat.criteres_gold:
        ajouter("source_primaire_verifiee", BlockerCategory.SOURCE_INCOMPLETE)

    gold_ready = constat.gold_ready and not blocages

    # -- ce que family_ready ajoute --
    if regle.status is not RuleStatus.VALIDATED:
        ajouter("statut_non_validated", BlockerCategory.HUMAN_REVIEW_REQUIRED)
    if not _matiere_a_familles(regle):
        ajouter("matiere_a_familles", BlockerCategory.SCHEMA_INCOMPLETE)

    family_ready = gold_ready and not blocages

    return ConstatReadiness(
        rule_id=regle.id,
        domain=regle.domain.value,
        status=regle.status,
        priority=regle.priority,
        gold_ready=gold_ready,
        family_ready=family_ready,
        blocages=tuple(blocages),
        priorite_revue=prioriser(regle, blocages),
        decision_requise=decision_requise(regle, constat, blocages),
        gold_ready_stocke=regle.gold_ready,
    )


# --------------------------------------------------------------------------- #
# Priorisation (§3)
# --------------------------------------------------------------------------- #


def prioriser(regle: Rule, blocages: list[Blocage]) -> str:
    """P0 à P3, déterminé par la gravité de la règle et la nature du blocage.

    P0 n'est pas « urgent » mais « dangereux » : une règle critique dont
    l'exception, la date, le renvoi ou l'absence reste non tranchée produirait un
    item qu'un professionnel pourrait suivre de travers.
    """
    if not blocages:
        return ""
    categories = {b.category for b in blocages}
    dangereux = bool(categories & CATEGORIES_DANGEREUSES)

    if regle.priority is Priority.CRITICAL:
        return "P0" if dangereux else "P1"
    if regle.priority is Priority.HIGH:
        return "P1" if dangereux else "P2"
    if regle.priority is Priority.MEDIUM:
        return "P2" if dangereux else "P3"
    return "P3"


# --------------------------------------------------------------------------- #
# Ce que le relecteur doit trancher (§2)
# --------------------------------------------------------------------------- #


def decision_requise(
    regle: Rule, constat: ConstatCompletude, blocages: list[Blocage]
) -> str:
    """La question exacte posée au relecteur, jamais « revue requise ».

    Une file d'attente qui dit « à revoir » ne se traite pas : elle se contemple.
    Chaque ligne nomme donc la disposition, l'acte, et l'alternative à trancher.
    """
    if not blocages:
        return ""
    principal = None
    for categorie in ORDRE_BLOCAGES:
        for blocage in blocages:
            if blocage.category is categorie:
                principal = blocage
                break
        if principal:
            break
    if principal is None:  # pragma: no cover - blocages non vide
        return ""

    article = regle.source.article or "l'article cité"
    acte = regle.source.text
    categorie = principal.category

    if categorie is BlockerCategory.EXCEPTION_UNRESOLVED:
        if constat.exceptions_status is ExceptionsStatus.REQUIRES_HUMAN_REVIEW:
            return (
                f"Le relecteur humain doit décider si {article} de {acte} comporte "
                f"des dérogations, exclusions ou exemptions que la recherche "
                f"automatique n'a pas repérées — y compris posées par un autre "
                f"article ou un acte ultérieur — et, s'il n'y en a aucune, "
                f"l'attester en portant « none_identified »."
            )
        return (
            f"Le relecteur humain doit décider si les dispositions limitantes "
            f"repérées dans {article} de {acte} doivent être incorporées à la "
            f"règle, ou si elles concernent une autre obligation que celle "
            f"qu'elle énonce."
        )
    if categorie is BlockerCategory.NEGATIVE_CLAIM_UNRESOLVED:
        claims = [
            c.claim for c in regle.negative_claims if c.status is NegativeClaimStatus.UNVERIFIED
        ]
        exemple = claims[0][:90] if claims else "l'affirmation négative portée par la règle"
        return (
            f"Le relecteur humain doit décider si « {exemple} » est réellement "
            f"absent de {acte}, en indiquant le périmètre consulté — un extrait ne "
            f"suffit pas à établir une absence."
        )
    if categorie is BlockerCategory.TEMPORAL_UNRESOLVED:
        return (
            f"Le relecteur humain doit décider quelle version de {acte} fait foi "
            f"pour cette règle (statut « {constat.temporal_status} »), et à quelle "
            f"date une question devrait se placer."
        )
    if categorie is BlockerCategory.CROSS_REFERENCE_UNRESOLVED:
        renvois = ", ".join(constat.renvois[:5]) or "non identifiés"
        return (
            f"Le relecteur humain doit décider si les renvois de {article} "
            f"(articles {renvois}) sont indispensables à l'application de la règle, "
            f"et si leur contenu doit y être rattaché."
        )
    if categorie is BlockerCategory.SOURCE_INCOMPLETE:
        return (
            f"Le relecteur humain doit décider comment établir {article} de {acte}, "
            f"dont le texte primaire n'est pas atteignable depuis l'environnement "
            f"d'exécution."
        )
    if categorie is BlockerCategory.RULE_TOO_ABSTRACT:
        return (
            f"Le relecteur humain doit décider si l'énoncé peut être reformulé au "
            f"plus près de la lettre de {article}, ou si la règle doit être "
            f"découpée en plusieurs règles plus précises."
        )
    if categorie is BlockerCategory.SCHEMA_INCOMPLETE:
        return (
            f"Le relecteur humain doit décider quelles confusions typiques et quels "
            f"pièges cette règle permet de tester — sans eux, aucun angle de "
            f"question ne s'en déduit."
        )
    if categorie is BlockerCategory.HUMAN_REVIEW_REQUIRED:
        if principal.critere == "enonce_fidele":
            return (
                f"Le relecteur humain doit décider si l'énoncé de la règle est "
                f"soutenu par {article} de {acte}, ou s'il vise en réalité une "
                f"autre disposition."
            )
        return (
            f"Le relecteur humain doit décider si la règle peut passer "
            f"« validated » en l'état, ou ce qui manque encore pour l'y porter."
        )
    return (
        f"Le relecteur humain doit décider comment lever le blocage "
        f"« {principal.critere} » sur cette règle."
    )


# --------------------------------------------------------------------------- #
# Intégrité des données (§7)
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ConstatIntegrite:
    """Une incohérence entre ce que le Rulebook affirme et ce qu'il porte."""

    controle: str
    rule_id: str
    message: str

    def __str__(self) -> str:
        return f"[{self.controle}] {self.rule_id} — {self.message}"


def rejouer_le_registre(initiales: list[Rule], registre: list) -> dict[str, Rule]:
    """Rejoue tout le registre sur un Rulebook initial et rend l'état obtenu.

    Comptabiliser les reversionnements à partir des entrées prises isolément ne
    marche pas : une entrée ne reversionne que si elle ajoute réellement quelque
    chose à l'état du moment. Deux applications successives du même constat ne
    font donc avancer la version qu'une fois. Seul le rejeu dit la vérité — et
    c'est aussi lui qui attrape la résurrection d'une formulation antérieure.
    """
    from src.bench.verification import appliquer

    connus = {r.id for r in initiales}
    pertinentes = [v for v in registre if v.rule_id in connus]
    return {r.id: r for r in appliquer(initiales, pertinentes, historique=True)}


#: Champs comparés au rejeu. L'énoncé et la version en sont le cœur : c'est leur
#: divergence qui signale qu'une ancienne formulation validée a ressuscité.
CHAMPS_REJOUES: tuple[str, ...] = (
    "version",
    "supersedes",
    "statement",
    "status",
    "exceptions_status",
    "exceptions",
    "gold_ready",
)


def _empreinte_rejeu(regle: Rule) -> dict:
    donnees = {champ: getattr(regle, champ) for champ in CHAMPS_REJOUES}
    donnees["status"] = regle.status.value
    donnees["exceptions_status"] = regle.exceptions_status.value
    donnees["source"] = {
        "article": regle.source.article,
        "paragraph": regle.source.paragraph,
        "url": regle.source.url,
        "version_date": regle.source.version_date.isoformat(),
        "verified_by": regle.source.verified_by,
        "verification_date": (
            regle.source.verification_date.isoformat()
            if regle.source.verification_date
            else None
        ),
    }
    return donnees


def comparer_au_rejeu(
    livrees: list[Rule], initiales: list[Rule], registre: list
) -> list[ConstatIntegrite]:
    """Le Rulebook livré est-il exactement ce que le registre reconstruit ?

    C'est le contrôle qui couvre à lui seul « une ancienne version validée alors
    qu'une plus récente existe », « une modification d'énoncé sans nouvelle
    version » et « une nouvelle version sans entrée au registre » : les trois
    sont des divergences entre le livré et le rejoué.
    """
    try:
        rejouees = rejouer_le_registre(initiales, registre)
    except Exception as exc:  # le registre ne se rejoue pas : c'est déjà l'anomalie
        return [
            ConstatIntegrite(
                "registre_non_rejouable", "*", f"le registre ne se rejoue pas : {exc}"
            )
        ]

    anomalies: list[ConstatIntegrite] = []
    for regle in livrees:
        attendue = rejouees.get(regle.id)
        if attendue is None:
            anomalies.append(
                ConstatIntegrite(
                    "regle_hors_registre", regle.id,
                    "la règle livrée n'existe pas dans le Rulebook reconstruit",
                )
            )
            continue
        obtenu, espere = _empreinte_rejeu(regle), _empreinte_rejeu(attendue)
        if obtenu != espere:
            differents = sorted(k for k in obtenu if obtenu[k] != espere[k])
            anomalies.append(
                ConstatIntegrite(
                    "rejeu_divergent", regle.id,
                    f"le registre reconstruit une règle différente de celle livrée "
                    f"(champs : {', '.join(differents)}) — une formulation "
                    f"antérieure a pu survivre à une correction",
                )
            )
    return anomalies


def controles_integrite(
    regles: list[Rule],
    constats: dict[str, ConstatCompletude],
    readiness: dict[str, ConstatReadiness],
    registre: list,
) -> list[ConstatIntegrite]:
    """Les sept contrôles d'intégrité, appliqués au Rulebook livré.

    Ils portent sur des incohérences qu'aucun rapport ne doit pouvoir masquer :
    une règle qui se dit prête sans l'être, une version qui n'a pas laissé de
    trace, un énoncé validé que sa source ne soutient pas. C'est la résurrection
    d'une ancienne formulation validée qui a motivé le lot — elle s'était
    réellement produite.
    """
    anomalies: list[ConstatIntegrite] = []
    par_regle: dict[str, list] = {}
    for entree in registre:
        par_regle.setdefault(entree.rule_id, []).append(entree)

    for regle in regles:
        constat = constats.get(regle.id)
        etat = readiness.get(regle.id)
        entrees = par_regle.get(regle.id, [])
        # (c) prête sans source
        if regle.gold_ready and not regle.source.is_verified:
            anomalies.append(
                ConstatIntegrite(
                    "gold_ready_sans_source", regle.id,
                    "gold_ready alors que la source n'est pas vérifiée",
                )
            )
        # (d) prête avec des exceptions non abouties
        if regle.gold_ready and regle.exceptions_status not in EXCEPTIONS_ABOUTIES:
            anomalies.append(
                ConstatIntegrite(
                    "gold_ready_exceptions_inconnues", regle.id,
                    f"gold_ready alors que la recherche d'exceptions vaut "
                    f"« {regle.exceptions_status.value} »",
                )
            )
        # (c bis) prête alors qu'une affirmation négative reste en suspens
        if regle.gold_ready and any(
            c.status is NegativeClaimStatus.UNVERIFIED for c in regle.negative_claims
        ):
            anomalies.append(
                ConstatIntegrite(
                    "gold_ready_affirmation_negative", regle.id,
                    "gold_ready alors qu'une affirmation négative reste non vérifiée",
                )
            )
        # (b) validée avec un énoncé que sa source ne soutient pas
        if (
            regle.status is RuleStatus.VALIDATED
            and constat is not None
            and constat.criteres
            and not constat.criteres.get("enonce_fidele", True)
        ):
            anomalies.append(
                ConstatIntegrite(
                    "validee_non_corroboree", regle.id,
                    "règle validée dont l'énoncé n'est pas corroboré par sa source",
                )
            )
        # divergence entre le gold_ready stocké et le calcul
        if etat is not None and regle.gold_ready != etat.gold_ready:
            anomalies.append(
                ConstatIntegrite(
                    "gold_ready_divergent", regle.id,
                    f"gold_ready stocké « {regle.gold_ready} » alors que le calcul "
                    f"donne « {etat.gold_ready} » : {etat.explanation}",
                )
            )
        # (e) prête pour une famille sans être prête pour un gold
        if etat is not None and etat.family_ready and not etat.gold_ready:
            anomalies.append(
                ConstatIntegrite(
                    "family_ready_sans_gold_ready", regle.id,
                    "family_ready sans gold_ready : impossible par construction",
                )
            )

    return anomalies
