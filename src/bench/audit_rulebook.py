"""Audit du Rulebook contre le texte primaire (phase 6 bis).

Ce module confronte chaque règle à l'acte qu'elle cite, article par article, et
dit ce que cette confrontation établit. Il ne promeut rien : la promotion passe
par le circuit de vérification (`verification.py`), qui exige un vérificateur
nommé. Ici, on rassemble la **preuve** ; là-bas, quelqu'un la signe.

Cette séparation n'est pas une prudence de forme. `RuleStatus.SOURCE_CHECKED`
est défini dans le dépôt comme un statut qui n'est « jamais le résultat d'avoir
trouvé une page web, et jamais un statut qu'un modèle peut s'accorder à
lui-même ». Un audit automatique peut donc établir qu'un article existe, qu'il
dit ce que la règle prétend, et qu'un chiffre s'y trouve — mais pas se délivrer
à lui-même le certificat.

Quatre classements, qui disent chacun une chose différente :

| Classement | Ce qu'il signifie |
|---|---|
| `SOURCE_CHECKED` | un vérificateur nommé a signé — **lu dans le Rulebook, jamais déduit de la preuve** |
| `REQUIRES_HUMAN_REVIEW` | texte récupéré, article trouvé, énoncé corroboré : il ne manque que la signature |
| `DRAFT` | texte récupéré, mais l'article manque ou l'énoncé ne se retrouve pas |
| `BLOCKED` | le texte primaire est hors d'atteinte depuis cet environnement |

`SOURCE_CHECKED` mérite une précision, parce que la distinction est fine et
qu'elle porte tout le verrou. L'audit ne **décerne** jamais ce classement à
partir de sa propre preuve : il le **lit** dans la règle, quand celle-ci porte
déjà un statut promu et une source signée par un vérificateur nommé. Constater
qu'un humain a signé n'est pas signer à sa place. Une règle signée dont l'énoncé
ne se retrouve plus dans le texte redescend d'ailleurs en `DRAFT` : la signature
n'immunise pas contre un texte qui a changé.

`BLOCKED` et `DRAFT` ne se confondent pas : l'un dit « on n'a pas pu regarder »,
l'autre « on a regardé et ça ne va pas ». Les traiter pareil ferait disparaître
la seule information qui dit où porter l'effort.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from src.bench.regles import Rule
from src.bench.rulebook import (
    ExceptionsStatus,
    NegativeClaimStatus,
    RuleStatus,
)
from src.bench.sources_primaires import (
    CITATION_MODIFIEE,
    RecuperationImpossible,
    Recuperateur,
    TextePrimaire,
    celex_consolide,
    celex_de_url,
    celex_du_texte,
    cles_articles,
    extraire_paragraphe,
    recuperateur_http,
    recuperer_page,
    recuperer_texte,
)
from src.bench.verification import Verdict
from src.bench.vocabulaires import RegulatoryStatus


class ClassementAudit(str, Enum):
    """Ce que l'audit établit pour une règle."""

    SOURCE_CHECKED = "SOURCE_CHECKED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    DRAFT = "DRAFT"
    BLOCKED = "BLOCKED"


#: Domaines dont le texte primaire est hors d'atteinte, et pourquoi. Le motif
#: est enregistré tel quel : il devra être réévalué, pas supposé permanent.
SOURCES_HORS_ATTEINTE: dict[str, str] = {
    "legifrance.gouv.fr": (
        "Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire "
        "et financier ne peut pas être consulté ici"
    ),
}

#: Sources institutionnelles atteignables mais qui ne sont pas du droit dur.
#: Une doctrine éclaire l'application d'un texte, elle ne le remplace pas.
SOURCES_DOCTRINALES = ("amf-france.org", "acpr.banque-france.fr", "esma.europa.eu")

#: Au-delà, le vocabulaire de l'énoncé se retrouve dans l'article officiel.
#: En deçà, la règle parle peut-être d'autre chose que l'article qu'elle cite.
SEUIL_CONCORDANCE = 0.45

#: Chiffres porteurs de droit : un seuil, un délai, un montant. Ce sont eux
#: qu'une règle invente le plus facilement, et eux qu'il faut retrouver.
CHIFFRES_PORTEURS = re.compile(
    r"(?<![\w/])(?P<valeur>\d{1,3}(?:[  ]\d{3})*(?:[.,]\d+)?)\s*"
    r"(?P<unite>%|jours?|mois|ans?|années?|heures?|semaines?|euros?|EUR|€)",
    re.IGNORECASE,
)

#: Mots trop courts pour porter du sens : ils gonfleraient la concordance.
_MOT = re.compile(r"[0-9a-zà-ÿ]+", re.IGNORECASE)


def _mots_signifiants(texte: str) -> set[str]:
    return {m.lower() for m in _MOT.findall(texte.replace("’", "'")) if len(m) > 4}


def couverture_lexicale(enonce: str, officiel: str) -> float:
    """Part du vocabulaire de l'énoncé qui se retrouve dans le texte officiel.

    Ce n'est pas une mesure de vérité : un énoncé peut être faux avec un
    vocabulaire parfaitement couvert. C'est une mesure de **rattachement** —
    elle attrape la règle qui cite un article parlant d'autre chose, ce qu'un
    humain mettrait longtemps à repérer sur 58 règles.
    """
    mots = _mots_signifiants(enonce)
    if not mots:
        return 0.0
    presents = _mots_signifiants(officiel)
    return len(mots & presents) / len(mots)


def chiffres_de(texte: str) -> list[str]:
    """Seuils, délais et montants cités, normalisés pour être comparés."""
    trouves = []
    for marque in CHIFFRES_PORTEURS.finditer(texte):
        valeur = re.sub(r"[  ]", "", marque.group("valeur")).replace(",", ".")
        # « 30.0 » et « 30 » sont le même seuil ; « 30 » et « 3 » ne le sont pas.
        # Ne retirer les zéros que derrière une virgule décimale.
        if "." in valeur:
            valeur = valeur.rstrip("0").rstrip(".")
        unite = marque.group("unite").lower().rstrip("s")
        unite = {"euro": "eur", "€": "eur", "année": "an"}.get(unite, unite)
        trouves.append(f"{valeur} {unite}")
    return sorted(set(trouves))


@dataclass(frozen=True)
class PreuveArticle:
    """Ce qui a été effectivement lu, et d'où. Rejouable par un tiers."""

    celex: str
    article_key: str
    article_found: bool
    retrieved_from: str
    sha256: str
    official_journal: str
    excerpt: str = ""
    paragraph_excerpt: str = ""


@dataclass(frozen=True)
class ConstatAudit:
    """Le résultat de la confrontation d'une règle à son texte primaire."""

    rule_id: str
    domain: str
    source_text: str
    article: str
    paragraph: str
    version_date: str
    classement: ClassementAudit
    exceptions_status: str
    regulatory_status: str
    concordance: float = 0.0
    missing_figures: tuple[str, ...] = ()
    problemes: tuple[str, ...] = ()
    verdict_propose: Verdict | None = None
    preuve: PreuveArticle | None = None
    negative_claims_checked: int = 0
    negative_claims_absent: int = 0

    @property
    def probleme(self) -> str:
        """Les anomalies en une cellule, pour la matrice."""
        return " ; ".join(self.problemes) if self.problemes else ""


def _hote_hors_atteinte(url: str) -> str | None:
    for hote, motif in SOURCES_HORS_ATTEINTE.items():
        if hote in url:
            return motif
    return None


def _verifier_affirmations_negatives(
    regle: Rule, texte: TextePrimaire
) -> tuple[int, int, list[str]]:
    """Cherche chaque affirmation négative dans **l'acte entier**, pas dans un extrait.

    La spécification est explicite : ne pas trouver X dans un extrait ne prouve
    rien. Le périmètre de recherche est donc l'acte complet, et il est consigné
    tel quel — c'est ce qui rend l'absence opposable plutôt que supposée.
    """
    absentes = 0
    notes: list[str] = []
    corpus = texte.text.lower()
    for revendication in regle.negative_claims:
        chiffres = chiffres_de(revendication.claim)
        introuvables = [c for c in chiffres if c.split()[0] not in corpus]
        if chiffres and len(introuvables) == len(chiffres):
            absentes += 1
            notes.append(
                f"affirmation négative « {revendication.claim[:60]}… » : aucun de ses "
                f"chiffres ({', '.join(chiffres)}) ne figure dans l'acte "
                f"{texte.celex} — absence corroborée sur l'acte entier"
            )
        elif not chiffres:
            notes.append(
                f"affirmation négative « {revendication.claim[:60]}… » : sans chiffre "
                f"à chercher, l'absence ne peut pas être établie mécaniquement"
            )
    return len(regle.negative_claims), absentes, notes


@dataclass(frozen=True)
class TexteDeLaRegle:
    """Le texte officiel d'une règle, et les dispositions qu'elle cite.

    Extrait de l'audit de sources pour être partagé avec l'audit de complétude :
    deux résolutions concurrentes du même acte finiraient par diverger, et la
    seconde passe vérifierait une autre version du droit que la première.
    """

    texte: TextePrimaire | None
    article: str = ""
    trouvees: tuple[str, ...] = ()
    manquantes: tuple[str, ...] = ()
    cles: tuple[str, ...] = ()
    celex_url: str | None = None
    celex_cite: str | None = None
    doctrinale: bool = False
    consolidation_manquante: str = ""
    echec: str = ""


def texte_de_la_regle(
    regle: Rule, recuperateur: Recuperateur = recuperateur_http, cache=None
) -> TexteDeLaRegle:
    """Résout l'acte cité, le récupère, et isole les dispositions citées.

    L'URL et la citation ne désignent pas toujours le même acte : une règle
    pointe volontiers l'acte **modificatif** alors qu'elle énonce l'acte modifié.
    On vérifie contre l'acte cité, qui est celui dont la règle parle. Et une
    règle qui énonce un texte « modifié » est cherchée dans sa version
    consolidée : la confronter à l'acte d'origine lui reprocherait de ne pas
    contenir une disposition ajoutée depuis.
    """
    celex_url = celex_de_url(regle.source.url)
    celex_cite = celex_du_texte(regle.source.text)
    doctrinale = any(hote in regle.source.url for hote in SOURCES_DOCTRINALES)
    celex = celex_cite or celex_url

    if celex is None and not doctrinale:
        return TexteDeLaRegle(
            None,
            celex_url=celex_url,
            celex_cite=celex_cite,
            echec="URL sans identifiant CELEX ni source institutionnelle reconnue",
        )

    consolidation_manquante = ""
    texte = None
    if celex is not None and CITATION_MODIFIEE.search(regle.source.text):
        vise = celex_consolide(celex, regle.source.version_date)
        if vise is not None:
            try:
                texte = recuperer_texte(vise, "FRA", recuperateur, cache)
            except RecuperationImpossible:
                consolidation_manquante = vise

    if texte is None:
        try:
            texte = (
                recuperer_page(regle.source.url, recuperateur, cache)
                if celex is None
                else recuperer_texte(celex, "FRA", recuperateur, cache)
            )
        except RecuperationImpossible as exc:
            return TexteDeLaRegle(
                None,
                celex_url=celex_url,
                celex_cite=celex_cite,
                doctrinale=doctrinale,
                consolidation_manquante=consolidation_manquante,
                echec=f"texte primaire non récupéré : {exc}",
            )

    cles = cles_articles(regle.source.article) if texte.articles else []
    trouvees = [c for c in cles if c in texte.articles]
    manquantes = [c for c in cles if c not in texte.articles]
    return TexteDeLaRegle(
        texte=texte,
        article=" ".join(texte.articles[c] for c in trouvees),
        trouvees=tuple(trouvees),
        manquantes=tuple(manquantes),
        cles=tuple(cles),
        celex_url=celex_url,
        celex_cite=celex_cite,
        doctrinale=doctrinale,
        consolidation_manquante=consolidation_manquante,
    )


def auditer_regle(
    regle: Rule,
    recuperateur: Recuperateur = recuperateur_http,
    cache=None,
) -> ConstatAudit:
    """Confronte une règle à son texte primaire et rend le constat.

    Ne lève jamais : une source inaccessible est un résultat d'audit, pas un
    échec du programme. Un audit qui s'arrête à la première source injoignable
    ne dirait rien des cinquante-sept autres règles.
    """
    commun = dict(
        rule_id=regle.id,
        domain=regle.domain.value,
        source_text=regle.source.text,
        article=regle.source.article,
        paragraph=regle.source.paragraph,
        version_date=regle.source.version_date.isoformat(),
        exceptions_status=regle.exceptions_status.value,
        regulatory_status=regle.regulatory_status.value,
    )
    problemes: list[str] = []

    if regle.regulatory_status is RegulatoryStatus.PROPOSED:
        problemes.append(
            "règle déclarée « proposed » : une réforme proposée n'est pas du droit "
            "applicable et ne peut pas être vérifiée comme tel"
        )

    motif = _hote_hors_atteinte(regle.source.url)
    if motif is not None:
        return ConstatAudit(
            **commun,
            classement=ClassementAudit.BLOCKED,
            problemes=tuple([motif, *problemes]),
            verdict_propose=None,
        )

    # -- quel acte la règle prétend-elle énoncer ? --
    # L'URL et la citation ne désignent pas toujours le même acte : une règle
    # pointe volontiers l'acte **modificatif** alors qu'elle énonce l'acte
    # modifié. On vérifie contre l'acte cité, qui est celui dont la règle parle.
    celex_url = celex_de_url(regle.source.url)
    celex_cite = celex_du_texte(regle.source.text)
    doctrinale = any(hote in regle.source.url for hote in SOURCES_DOCTRINALES)

    if celex_url and celex_cite and celex_url != celex_cite:
        problemes.append(
            f"l'URL désigne l'acte {celex_url} alors que la source cite {celex_cite} : "
            f"vérification conduite contre l'acte cité"
        )
    celex = celex_cite or celex_url

    if celex is None and not doctrinale:
        return ConstatAudit(
            **commun,
            classement=ClassementAudit.BLOCKED,
            problemes=tuple(
                ["URL sans identifiant CELEX ni source institutionnelle reconnue", *problemes]
            ),
        )

    # -- récupération --
    # Une règle qui énonce un texte « modifié » énonce la version consolidée :
    # la vérifier contre l'acte d'origine reviendrait à lui reprocher de ne pas
    # contenir une disposition ajoutée depuis. On tente donc la consolidation à
    # la date déclarée par la règle, et l'on dit ce qui manque quand elle échoue.
    consolidation_demandee = celex is not None and bool(
        CITATION_MODIFIEE.search(regle.source.text)
    )
    texte = None
    if consolidation_demandee:
        vise = celex_consolide(celex, regle.source.version_date)
        if vise is not None:
            try:
                texte = recuperer_texte(vise, "FRA", recuperateur, cache)
            except RecuperationImpossible:
                problemes.append(
                    f"la source dit l'acte modifié, mais aucune version consolidée "
                    f"au {regle.source.version_date.isoformat()} n'existe "
                    f"({vise}) : la date de consolidation applicable doit être "
                    f"établie, sans quoi la règle est vérifiée contre le texte d'origine"
                )

    if texte is None:
        try:
            texte = (
                recuperer_page(regle.source.url, recuperateur, cache)
                if celex is None
                else recuperer_texte(celex, "FRA", recuperateur, cache)
            )
        except RecuperationImpossible as exc:
            return ConstatAudit(
                **commun,
                classement=ClassementAudit.BLOCKED,
                problemes=tuple([f"texte primaire non récupéré : {exc}", *problemes]),
            )

    # -- quelles dispositions la règle cite-t-elle ? --
    # Une doctrine n'est pas découpée en articles : lui chercher un « article 3 »
    # reviendrait à lui reprocher de ne pas être un règlement. La confrontation
    # porte alors sur la page entière, et la réserve doctrinale ci-dessous dit
    # ce que cette preuve vaut.
    cles = cles_articles(regle.source.article) if texte.articles else []
    if not cles and texte.articles:
        problemes.append(
            f"ancrage « {regle.source.article} » : aucun article désigné, la règle "
            f"est vérifiée contre l'acte entier et aucun gold ne pourra citer sa "
            f"disposition"
        )
    elif len(cles) > 1:
        problemes.append(
            f"ancrage « {regle.source.article} » : {len(cles)} articles couverts "
            f"({', '.join(cles)}), à découper avant qu'un gold puisse le citer"
        )

    trouvees = [c for c in cles if c in texte.articles]
    manquantes = [c for c in cles if c not in texte.articles]
    # Une citation qui vise plusieurs articles est imprécise, pas fausse : il
    # suffit qu'une des dispositions citées existe pour que l'ancrage tienne.
    article_texte = " ".join(texte.articles[c] for c in trouvees)
    trouve = bool(trouvees) if cles else bool(texte.text)

    if manquantes and texte.articles:
        problemes.append(
            f"article(s) {', '.join(manquantes)} introuvable(s) dans l'acte "
            f"{texte.celex or 'consulté'} ({len(texte.articles)} articles découpés)"
        )

    # Ancrage global ou doctrine : la référence est le texte entier. C'est moins
    # précis, et c'est précisément ce que l'anomalie ci-dessus signale.
    reference = article_texte or texte.text

    concordance = couverture_lexicale(regle.statement, reference) if reference else 0.0
    if reference and concordance < SEUIL_CONCORDANCE:
        problemes.append(
            f"énoncé peu corroboré par le texte cité ({concordance:.0%} du "
            f"vocabulaire retrouvé) : la règle parle peut-être d'autre chose"
        )

    attendus = chiffres_de(regle.statement)
    absents = tuple(c for c in attendus if c.split()[0] not in reference.replace(" ", " "))
    if absents:
        problemes.append(
            f"chiffre(s) non retrouvé(s) dans le texte officiel : {', '.join(absents)}"
        )

    verifiees, absentes, notes = (
        _verifier_affirmations_negatives(regle, texte) if texte.articles else (0, 0, [])
    )
    problemes.extend(notes)

    if regle.exceptions_status is ExceptionsStatus.UNKNOWN:
        problemes.append(
            "exceptions jamais cherchées : à trancher entre « listed » et "
            "« none_identified » avant toute validation"
        )

    if doctrinale:
        problemes.append(
            "source doctrinale : elle éclaire l'application d'un texte, elle ne "
            "vaut pas preuve principale pour une disposition législative"
        )

    # -- classement --
    # Une signature déjà portée par la règle se lit ; elle ne se déduit jamais de
    # la preuve. Et elle ne protège pas un énoncé que le texte ne corrobore plus.
    deja_signee = regle.status is not RuleStatus.DRAFT and regle.source.is_verified

    if manquantes and not trouvees:
        classement = ClassementAudit.DRAFT
        verdict = Verdict.REFUTE
    elif reference and concordance >= SEUIL_CONCORDANCE and not absents:
        classement = (
            ClassementAudit.SOURCE_CHECKED
            if deja_signee
            else ClassementAudit.REQUIRES_HUMAN_REVIEW
        )
        verdict = Verdict.CONFIRME
    elif reference:
        classement = ClassementAudit.DRAFT
        verdict = Verdict.CORRIGE
    else:
        classement = ClassementAudit.DRAFT
        verdict = Verdict.NON_VERIFIABLE

    cle = trouvees[0] if trouvees else ""
    extrait = article_texte[:1500]
    return ConstatAudit(
        **commun,
        classement=classement,
        concordance=round(concordance, 3),
        missing_figures=absents,
        problemes=tuple(problemes),
        verdict_propose=verdict,
        negative_claims_checked=verifiees,
        negative_claims_absent=absentes,
        preuve=PreuveArticle(
            celex=texte.celex,
            article_key=cle,
            article_found=trouve,
            retrieved_from=texte.retrieved_from,
            sha256=texte.sha256,
            official_journal=texte.official_journal,
            excerpt=extrait,
            paragraph_excerpt=extraire_paragraphe(article_texte, regle.source.paragraph)[:1200],
        ),
    )


def auditer(
    regles: list[Rule], recuperateur: Recuperateur = recuperateur_http, cache=None
) -> list[ConstatAudit]:
    """Audite toutes les règles, dans l'ordre de priorité de la spécification §3.

    On vérifie d'abord ce dont l'erreur coûte le plus cher : les règles
    critiques, puis celles dont les exceptions sont inconnues, puis celles qui
    portent une affirmation négative.
    """
    return [auditer_regle(regle, recuperateur, cache) for regle in ordre_de_priorite(regles)]


def ordre_de_priorite(regles: list[Rule]) -> list[Rule]:
    """Ordre de passage : le coût d'une erreur d'abord, l'identifiant ensuite."""

    def rang(regle: Rule) -> tuple:
        return (
            0 if regle.priority.value == "CRITICAL" else 1,
            0 if regle.exceptions_status is ExceptionsStatus.UNKNOWN else 1,
            0 if regle.negative_claims else 1,
            regle.id,
        )

    return sorted(regles, key=rang)
