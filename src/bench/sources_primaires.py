"""Récupération du texte primaire officiel, pour confronter le Rulebook à la lettre.

Le Rulebook interdit de promouvoir une règle sur la foi d'une page web qui la
mentionne. Ce module ne récupère donc **que** des textes qui font droit :

- **CELLAR** (`publications.europa.eu`), le dépôt de l'Office des publications
  de l'Union : il sert le texte tel qu'il a paru au *Journal officiel*, en XML
  balisé par article, langue par langue. C'est la source authentique, pas une
  reproduction.
- Les sites institutionnels français pour la doctrine (AMF), quand elle n'a pas
  d'équivalent au JO.

Ce que ce module a établi sur l'environnement d'exécution, et qui explique sa
forme :

| Voie | État | Conséquence |
|---|---|---|
| `eur-lex.europa.eu` | **200 trompeur** : sert la page d'accueil du JO | inutilisable |
| `publications.europa.eu` (CELLAR) | texte authentique du JO | **voie retenue** |
| `legifrance.gouv.fr` | 403 | Code monétaire et financier hors d'atteinte |
| `amf-france.org` | page réelle | doctrine AMF atteignable |

Un `200` qui rend une page d'accueil est plus dangereux qu'un `403` : il se lit
comme un succès. Chaque récupération est donc **validée sur son contenu** — la
langue attendue, l'acte attendu — et non sur son code de retour.

Aucun appel réseau n'est fait depuis les tests : le récupérateur est injecté
(`Recuperateur`), et la suite de tests en fournit un faux.
"""

from __future__ import annotations

import datetime as dt
import glob
import html
import io
import re
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from src.io_utils import ecrire_json, hash_texte, lire_json

#: Le cache vit hors du dépôt : c'est une copie de travail d'un texte officiel,
#: pas un artefact du projet. `.cache/` est déjà ignoré par git.
CACHE_PRIMAIRE = Path(".cache/primary")

RACINE_CELLAR = "http://publications.europa.eu/resource"

#: Identifiant CELEX tel qu'il apparaît dans une URL EUR-Lex.
CELEX_DANS_URL = re.compile(r"CELEX[:%]?(?:3A)?\s*(?P<celex>[0-9][0-9A-Z-]{6,})", re.IGNORECASE)

#: Formats de manifestation exploitables, dans l'ordre de préférence : Formex
#: balisé, puis rendu XHTML du JO. Le format `01` est le PDF — authentique mais
#: non découpable sans océrisation, donc écarté.
FORMATS_MANIFESTATION = ("02", "03")

#: Manifestations à sonder : l'index encode la langue dans l'ordre alphabétique
#: des codes ISO, et il glisse donc selon les langues dont l'acte dispose. Le
#: français tombe sur 9 dans le régime à 24 langues, sur 8 pour un acte antérieur
#: à l'entrée du croate. On sonde ces valeurs d'abord, les autres ensuite — et
#: on **valide toujours sur le texte** : un index n'est pas une preuve.
INDICES_PROBABLES = (9, 8, 10, 7, 11)
INDICES_MANIFESTATION = tuple(
    f"{i:04d}" for i in INDICES_PROBABLES + tuple(
        j for j in range(1, 26) if j not in INDICES_PROBABLES
    )
)

#: Marques qui attestent qu'un texte est bien en français. Un index de
#: manifestation n'est jamais cru sur parole.
MARQUES_FRANCAIS = (
    "parlement européen",
    "considérant",
    "le présent règlement",
    "la présente directive",
    "journal officiel",
)

MARQUES_ANGLAIS = ("european parliament", "whereas", "this regulation", "this directive")

LANGUES = {"FRA": MARQUES_FRANCAIS, "ENG": MARQUES_ANGLAIS}

#: Un acte de l'Union porte son année dans son numéro : « 32019R2088 » = 2019/2088.
CELEX_STRUCTURE = re.compile(
    r"^(?P<secteur>\d)(?P<annee>\d{4})(?P<type>[A-Z])(?P<numero>\d{4})$"
)
#: Version consolidée : « 02019R2088-20200712 ».
CELEX_CONSOLIDE = re.compile(
    r"^0(?P<annee>\d{4})(?P<type>[A-Z])(?P<numero>\d{4})-(?P<date>\d{8})$"
)


class RecuperationImpossible(RuntimeError):
    """Le texte primaire n'a pas pu être obtenu, ou n'est pas celui attendu.

    Levée aussi — et surtout — quand la réponse est un succès HTTP qui ne
    contient pas le texte demandé : c'est le cas le plus trompeur.
    """


@dataclass(frozen=True)
class Reponse:
    """Ce qu'une récupération rend. `url` est l'URL **finale**, redirections suivies.

    L'URL finale n'est pas un détail : CELLAR résout un CELEX en redirigeant vers
    l'identifiant de la ressource. Lire cet identifiant dans le corps RDF plutôt
    que dans la redirection reviendrait à prendre le premier document cité par le
    graphe pour l'acte demandé.
    """

    status: int
    content: bytes
    url: str


class Recuperateur(Protocol):
    """Ce que le module attend du réseau, et rien de plus.

    Le réduire à cette signature est ce qui permet aux tests de tourner sans
    réseau, comme la règle non négociable du dépôt l'exige.
    """

    def __call__(self, url: str, entetes: dict[str, str]) -> Reponse:
        ...  # pragma: no cover - protocole


def recuperateur_http(url: str, entetes: dict[str, str]) -> Reponse:
    """Récupérateur réel. Jamais utilisé par les tests."""
    requete = urllib.request.Request(url, headers=entetes)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return Reponse(reponse.status, reponse.read(), reponse.geturl())


@dataclass(frozen=True)
class TextePrimaire:
    """Un texte officiel effectivement récupéré, et de quoi le réopposer.

    `sha256` et `retrieved_from` sont ce qui rend la consultation vérifiable par
    un tiers : on peut refaire la récupération et comparer.
    """

    celex: str
    language: str
    retrieved_from: str
    text: str
    sha256: str
    byte_size: int
    #: Référence du Journal officiel, lue dans le document lui-même.
    official_journal: str = ""
    articles: dict[str, str] = field(default_factory=dict)

    @property
    def is_authentic(self) -> bool:
        """Un texte vide ou minuscule n'est pas un texte : c'est une page d'erreur."""
        return len(self.text) > 2000 and bool(self.articles)


def celex_de_url(url: str) -> str | None:
    """Identifiant CELEX porté par une URL EUR-Lex, s'il y en a un."""
    trouve = CELEX_DANS_URL.search(url)
    return trouve.group("celex").upper() if trouve else None


#: « Règlement (UE) 2019/2088 », « Directive 2014/65/UE », « Règlement délégué
#: (UE) 2017/565 » : l'acte cité en toutes lettres dans la source d'une règle.
ACTE_EN_TOUTES_LETTRES = re.compile(
    r"(?P<nature>règlement|directive)[^,;.]{0,40}?"
    r"(?:\(UE\)\s*)?(?P<annee>(?:19|20)\d{2})/(?P<numero>\d{1,4})",
    re.IGNORECASE,
)


def celex_du_texte(source: str) -> str | None:
    """Identifiant CELEX de l'acte cité en toutes lettres, s'il est reconnaissable.

    Une règle cite parfois un acte dans `source.text` et pointe une URL vers un
    autre — typiquement l'acte **modificatif** plutôt que l'acte modifié. Savoir
    lire l'acte dans la citation permet de vérifier la règle contre le texte
    qu'elle prétend énoncer, au lieu d'échouer sur celui que l'URL désigne.
    """
    trouve = ACTE_EN_TOUTES_LETTRES.search(source.replace("\u00a0", " "))
    if trouve is None:
        return None
    type_acte = "L" if trouve.group("nature").lower().startswith("directive") else "R"
    return f"3{trouve.group('annee')}{type_acte}{int(trouve.group('numero')):04d}"


#: La citation dit-elle que l'acte a été modifié ? Une règle qui énonce une
#: disposition introduite par un acte modificatif ne se vérifie pas contre le
#: texte d'origine : il faut la version consolidée.
CITATION_MODIFIEE = re.compile(r"\bmodifié?e?\b|\bconsolidée?\b", re.IGNORECASE)


def celex_consolide(celex: str, date: dt.date) -> str | None:
    """CELEX de la version consolidée d'un acte à une date donnée.

    CELLAR n'expose pas de « dernière version consolidée » sans date : il faut
    nommer la consolidation. C'est une contrainte utile — elle force à dire de
    quelle version du droit on parle, ce qu'une règle sensible au temps doit de
    toute façon préciser.
    """
    structure = CELEX_STRUCTURE.match(celex)
    if structure is None:
        return None
    return (
        f"0{structure.group('annee')}{structure.group('type')}"
        f"{structure.group('numero')}-{date.strftime('%Y%m%d')}"
    )


#: Marques d'un ancrage qui vise l'acte entier plutôt qu'une disposition.
ANCRAGE_GLOBAL = re.compile(r"\bensemble\b|\bintégralité\b", re.IGNORECASE)

#: « Articles 8 à 13 » : un intervalle d'articles.
INTERVALLE_ARTICLES = re.compile(r"(?P<debut>\d+)\s*(?:à|-|–)\s*(?P<fin>\d+)")

#: Référence d'acte à écarter avant de lire des numéros d'article : sans cela,
#: « article 54 du règlement 2017/565 » livrerait aussi 2017 et 565.
REFERENCE_ACTE = re.compile(r"\(?\bUE\b\)?\s*\d{4}/\d{1,4}|\b\d{4}/\d{1,4}\b")


def cles_articles(libelle: str) -> list[str]:
    """Articles désignés par un libellé d'ancrage, intervalles et listes compris.

    Rend une liste vide quand l'ancrage vise l'acte entier : il n'y a alors pas
    d'article à retrouver, et prétendre le contraire ferait échouer la règle sur
    une disposition qu'elle n'a jamais prétendu citer.
    """
    if ANCRAGE_GLOBAL.search(libelle):
        return []
    nettoye = REFERENCE_ACTE.sub(" ", libelle)
    cles: list[str] = []
    for intervalle in INTERVALLE_ARTICLES.finditer(nettoye):
        debut, fin = int(intervalle.group("debut")), int(intervalle.group("fin"))
        if 0 < debut < fin <= debut + 40:
            cles.extend(str(n) for n in range(debut, fin + 1))
    if cles:
        return cles
    unique = normaliser_article(nettoye)
    autres = re.findall(r"\b(\d{1,3})\b", nettoye)
    cles = [unique] if unique else []
    cles += [n for n in autres if n not in cles]
    return [c for c in cles if c]


def acte_du_celex(celex: str) -> tuple[int, int] | None:
    """Année et numéro de l'acte, lus dans son identifiant."""
    for motif in (CELEX_STRUCTURE, CELEX_CONSOLIDE):
        trouve = motif.match(celex)
        if trouve:
            return int(trouve.group("annee")), int(trouve.group("numero"))
    return None


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #


def _en_texte(fragment: str) -> str:
    """Retire le balisage et normalise les blancs, sans toucher aux mots."""
    sans_balise = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(sans_balise)).strip()


#: Le titre d'article dans le rendu XHTML du JO, porteur des identifiants ELI.
TITRE_ARTICLE_ELI = re.compile(
    r'<p[^>]*class="[^"]*oj-ti-art[^"]*"[^>]*>(?P<titre>.*?)</p>', re.S | re.I
)


def extraire_articles_formex(document: str) -> dict[str, str]:
    """Découpe un acte servi en Formex, par son balisage `<ARTICLE>`/`<TI.ART>`."""
    articles: dict[str, str] = {}
    for bloc in re.findall(r"<ARTICLE\b.*?</ARTICLE>", document, re.S):
        titre = re.search(r"<TI\.ART>(.*?)</TI\.ART>", bloc, re.S)
        if titre is None:
            continue
        cle = normaliser_article(_en_texte(titre.group(1)))
        if cle:
            articles[cle] = _en_texte(bloc)
    return articles


def extraire_articles_eli(document: str) -> dict[str, str]:
    """Découpe un acte servi en XHTML du JO, par ses titres d'article.

    Le rendu XHTML imbrique les divisions ; découper sur les balises fermantes
    serait fragile. On découpe donc **entre deux titres d'article**, ce qui suit
    exactement la façon dont le Journal officiel se lit.
    """
    marques = list(TITRE_ARTICLE_ELI.finditer(document))
    articles: dict[str, str] = {}
    for rang, marque in enumerate(marques):
        cle = normaliser_article(_en_texte(marque.group("titre")))
        if not cle:
            continue
        fin = marques[rang + 1].start() if rang + 1 < len(marques) else len(document)
        articles[cle] = _en_texte(document[marque.start() : fin])
    return articles


def extraire_articles(document: str) -> dict[str, str]:
    """Découpe un acte du JO en articles, quel que soit le format servi.

    CELLAR sert selon l'acte du Formex balisé (`<ARTICLE>`) ou le rendu XHTML du
    JO (subdivisions ELI). Les deux sont authentiques ; seul le découpage change.
    Citer une disposition précise est ce qui permet de vérifier une règle au
    niveau où elle prétend s'ancrer, plutôt qu'à l'échelle d'un acte entier.
    """
    return extraire_articles_formex(document) or extraire_articles_eli(document)


#: « Article premier » est la forme du JO pour l'article 1er.
_PREMIER = re.compile(r"\bpremier\b|\b1\s*er\b|\b1er\b", re.IGNORECASE)


def normaliser_article(libelle: str) -> str:
    """Ramène « Article 2 », « Art. 2 », « Article premier » à une clé unique.

    Sans cette normalisation, une règle citant « Article 1er » ne retrouverait
    jamais l'« Article premier » du Journal officiel.
    """
    texte = _en_texte(libelle).lower().replace("’", "'")
    texte = re.sub(r"^(articles?|art\.?)\s*", "", texte).strip()
    if _PREMIER.search(texte) and not re.search(r"\d{2,}", texte):
        return "1"
    trouve = re.search(r"\d+\s*(?:bis|ter|quater)?", texte)
    return re.sub(r"\s+", "", trouve.group(0)) if trouve else ""


def extraire_paragraphe(article: str, paragraphe: str) -> str:
    """Fragment d'un article désigné par « point 17 », « paragraphe 3 », « 2 ».

    Rend une chaîne vide plutôt qu'un fragment approximatif : mieux vaut ne rien
    citer que citer le mauvais point.
    """
    numero = re.search(r"\d+", paragraphe or "")
    if numero is None:
        return ""
    n = numero.group(0)
    for motif in (rf"\b{n}\)\s", rf"\b{n}\.\s"):
        trouve = re.search(motif, article)
        if trouve:
            suite = article[trouve.start() :]
            fin = re.search(rf"\b{int(n) + 1}\)\s", suite)
            return (suite[: fin.start()] if fin else suite)[:4000].strip()
    return ""


# --------------------------------------------------------------------------- #
# Récupération
# --------------------------------------------------------------------------- #


def _document_de_la_charge(charge: bytes) -> str | None:
    """Rend le document, que CELLAR l'ait servi en archive ou en clair.

    Rend `None` plutôt que de lever : une charge illisible est un format qu'on
    ne sait pas exploiter, pas une erreur de récupération.
    """
    if charge[:2] == b"PK":
        try:
            return _texte_du_zip(charge)
        except (zipfile.BadZipFile, RecuperationImpossible):
            return None
    if charge[:5] == b"%PDF-":
        return None
    document = charge.decode("utf-8", errors="replace")
    return document if len(document) > 2000 else None


def _texte_du_zip(charge: bytes) -> str:
    """Le JO est servi en archive : on retient le document, pas ses métadonnées."""
    with tempfile.TemporaryDirectory() as dossier:
        with zipfile.ZipFile(io.BytesIO(charge)) as archive:
            archive.extractall(dossier)
        candidats = [
            chemin
            for chemin in sorted(glob.glob(f"{dossier}/*"))
            if not chemin.endswith(".doc.xml")
        ]
        if not candidats:
            raise RecuperationImpossible("archive sans document exploitable")
        return Path(max(candidats, key=lambda c: Path(c).stat().st_size)).read_text(
            encoding="utf-8", errors="replace"
        )


def _est_dans_la_langue(texte: str, langue: str) -> bool:
    """Valide la langue sur le contenu, jamais sur l'index de manifestation."""
    debut = texte[:60000].lower()
    return sum(1 for marque in LANGUES[langue] if marque in debut) >= 2


def _appeler(recuperateur: Recuperateur, url: str, entetes: dict[str, str]) -> Reponse:
    """Appelle le réseau en ne laissant sortir qu'un seul type d'erreur.

    Un audit qui parcourt cinquante-huit règles ne doit pas s'interrompre parce
    qu'une source répond 404 : l'échec d'une récupération est un résultat, pas
    une panne. Toute erreur de transport devient donc `RecuperationImpossible`.
    """
    try:
        return recuperateur(url, entetes)
    except RecuperationImpossible:
        raise
    except Exception as exc:
        raise RecuperationImpossible(f"{url} : {type(exc).__name__} — {exc}") from exc


#: L'identifiant CELLAR, tel qu'il apparaît dans l'URL de la ressource résolue.
UUID_CELLAR = re.compile(
    r"cellar/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
)


def _uuid_cellar(celex: str, recuperateur: Recuperateur) -> str:
    """Résout un CELEX vers son identifiant CELLAR, par la redirection officielle.

    L'identifiant se lit dans l'**URL finale**, pas dans le corps : le graphe RDF
    rendu cite des dizaines de documents liés, et le premier d'entre eux n'est
    pas l'acte demandé.
    """
    reponse = _appeler(
        recuperateur, f"{RACINE_CELLAR}/celex/{celex}", {"Accept": "application/rdf+xml"}
    )
    if reponse.status != 200:
        raise RecuperationImpossible(f"CELEX « {celex} » : HTTP {reponse.status}")
    trouve = UUID_CELLAR.search(reponse.url)
    if trouve is None:
        raise RecuperationImpossible(
            f"CELEX « {celex} » : la résolution n'a pas rendu d'identifiant CELLAR"
        )
    return trouve.group(1)


def recuperer_texte(
    celex: str,
    langue: str = "FRA",
    recuperateur: Recuperateur = recuperateur_http,
    cache: Path | None = CACHE_PRIMAIRE,
) -> TextePrimaire:
    """Récupère un acte de l'Union depuis CELLAR, dans la langue demandée.

    La manifestation qui porte une langue donnée n'a pas d'index fixe : il
    dépend du nombre de langues de l'acte. On sonde donc, et **on valide la
    langue sur le texte obtenu** — un index n'est pas une preuve.
    """
    if cache is not None:
        en_cache = Path(cache) / f"{celex}.{langue}.json"
        if en_cache.exists():
            return TextePrimaire(**lire_json(en_cache))

    uuid = _uuid_cellar(celex, recuperateur)
    dernier_motif = "aucune manifestation sondée"

    for indice in INDICES_MANIFESTATION:
        for format_ in FORMATS_MANIFESTATION:
            url = f"{RACINE_CELLAR}/cellar/{uuid}.{indice}.{format_}/DOC_1"
            try:
                reponse = recuperateur(url, {"Accept": "*/*"})
            except Exception as exc:
                # 404 et 406 sont la réponse normale d'un couple index/format qui
                # n'existe pas pour cet acte : on continue de sonder.
                dernier_motif = f"{type(exc).__name__} sur {indice}.{format_}"
                continue
            if reponse.status != 200 or not reponse.content:
                continue
            charge = reponse.content
            document = _document_de_la_charge(charge)
            if document is None or not _est_dans_la_langue(document, langue):
                continue

            articles = extraire_articles(document)
            if not articles:
                dernier_motif = f"{indice}.{format_} : aucun article découpable"
                continue
            texte = _en_texte(document)
            journal = re.search(r"\b(L|C)\s?\d{2,4}\b", texte[:400])
            resultat = TextePrimaire(
                celex=celex,
                language=langue,
                retrieved_from=url,
                text=texte,
                sha256=hash_texte(texte),
                byte_size=len(charge),
                official_journal=journal.group(0) if journal else "",
                articles=articles,
            )
            if not resultat.is_authentic:
                dernier_motif = "réponse sans article : page d'erreur ou d'accueil"
                continue
            if cache is not None:
                ecrire_json(Path(cache) / f"{celex}.{langue}.json", resultat.__dict__)
            return resultat

    raise RecuperationImpossible(
        f"CELEX « {celex} » : aucune manifestation en {langue} ({dernier_motif})"
    )


def recuperer_page(
    url: str, recuperateur: Recuperateur = recuperateur_http, cache: Path | None = CACHE_PRIMAIRE
) -> TextePrimaire:
    """Récupère une page institutionnelle (doctrine AMF), sans balisage d'article.

    Une doctrine n'est pas un acte : elle n'a ni articles ni Journal officiel.
    Elle sert de source pour ce qui n'a pas d'équivalent au JO, jamais de preuve
    pour une disposition législative.
    """
    cle = hash_texte(url)[:16]
    if cache is not None:
        en_cache = Path(cache) / f"page-{cle}.json"
        if en_cache.exists():
            return TextePrimaire(**lire_json(en_cache))

    reponse = _appeler(recuperateur, url, {"Accept": "text/html"})
    if reponse.status != 200:
        raise RecuperationImpossible(f"{url} : HTTP {reponse.status}")
    charge = reponse.content
    brut = charge.decode("utf-8", errors="replace")
    sans_script = re.sub(r"<script.*?</script>|<style.*?</style>", " ", brut, flags=re.S | re.I)
    texte = _en_texte(sans_script)
    if len(texte) < 2000:
        raise RecuperationImpossible(f"{url} : réponse trop courte pour être la doctrine")

    resultat = TextePrimaire(
        celex="",
        language="FRA",
        retrieved_from=url,
        text=texte,
        sha256=hash_texte(texte),
        byte_size=len(charge),
    )
    if cache is not None:
        ecrire_json(Path(cache) / f"page-{cle}.json", resultat.__dict__)
    return resultat
