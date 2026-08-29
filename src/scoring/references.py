"""Détection des références inventées.

Tout numéro d'article cité dans une réponse est confronté au registre local
`registry/references.json`. Une référence absente du registre est une
hallucination de source (CLAUDE.md §6).

Le rattachement article → texte est explicite : dans une phrase qui mentionne
un texte, les articles cités s'y rapportent ; sinon ils se rapportent au texte
source de l'item, qui est le sujet de la question.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from src.io_utils import lire_json
from src.scoring.texte import normaliser, phrases

#: Marqueur d'un texte dont les articles ne sont pas contrôlés (liste non exhaustive).
JOKER = "*"

# « (UE) 2019/2088 », « 2014/65/UE », « 600/2014 », « 2022/1288 »
_NUMERO_TEXTE = re.compile(r"\b(\d{2,4}/\d{2,4})(?:/(?:UE|CE))?\b")

# « article 8 », « art. 2(17) », « article 18 bis », « articles 24 et 25 ».
# Le `(?!-\d)` écarte les cotes à tirets (321-100), traitées à part.
_ARTICLE_NUMERIQUE = re.compile(
    r"\b(?:articles?|arts?\.)\s+((?:\d+(?!-\d)(?:\s*\(\d+[a-z]?\))?"
    r"(?:\s*(?:bis|ter|quater))?(?:\s*(?:,|et|à)\s*)?)+)",
    flags=re.IGNORECASE,
)
_MORCEAU_NUMERIQUE = re.compile(
    r"\d+(?!-\d)(?:\s*\(\d+[a-z]?\))?(?:\s*(?:bis|ter|quater))?"
)

#: Toute cote à tirets restante, retirée avant l'extraction des articles simples.
_COTE_A_TIRETS = re.compile(r"\b\d+(?:-\d+)+\b")

# « article L. 511-1 », « art. R.561-5 », « D. 561-3-1 »
_ARTICLE_CODE = re.compile(r"\b(?:articles?\s+)?([LRD])\.?\s?(\d+(?:-\d+)+)\b")

# « article 321-100 du règlement général de l'AMF » : cotes à trois blocs
_ARTICLE_RG = re.compile(r"\b(\d{3}-\d+(?:-\d+)?)\b")


@dataclass(frozen=True)
class Citation:
    """Une référence citée par un modèle, telle que repérée dans sa réponse."""

    genre: str  # "texte" | "article" | "article_code" | "article_rg"
    valeur: str  # forme normalisée, ex. « 2019/2088 » ou « 8 »
    rattachement: str | None  # numéro de texte auquel l'article se rapporte
    brut: str

    def cle(self) -> str:
        if self.genre == "texte":
            return self.valeur
        if self.rattachement:
            return f"{self.rattachement}:{self.valeur}"
        return self.valeur


@dataclass
class Registre:
    """Registre local des références réglementaires réputées valides."""

    version: str = ""
    textes: dict[str, set[str]] = field(default_factory=dict)
    codes: dict[str, set[str]] = field(default_factory=dict)
    articles_rg: set[str] = field(default_factory=set)

    @classmethod
    def charger(cls, chemin: Path) -> Registre:
        donnees = lire_json(Path(chemin))
        registre = cls(version=str(donnees.get("version", "")))

        for texte in donnees.get("textes", []):
            registre.textes[texte["numero"]] = {
                _normaliser_article(a) for a in texte.get("articles", [])
            }
        for code in donnees.get("codes", []):
            registre.codes[code["prefixe"].upper()] = {
                _normaliser_article(a) for a in code.get("articles", [])
            }
        for rg in donnees.get("reglements_generaux", []):
            registre.articles_rg |= {_normaliser_article(a) for a in rg.get("articles", [])}

        return registre

    # -- interrogations ---------------------------------------------------- #

    def texte_connu(self, numero: str) -> bool:
        return numero in self.textes

    def article_connu(self, numero_texte: str | None, article: str) -> bool:
        if numero_texte is None:
            # Article cité sans texte rattachable : on ne peut pas conclure à
            # l'invention, on laisse l'axe sourcing au juge.
            return True
        articles = self.textes.get(numero_texte)
        if articles is None:
            return False
        if JOKER in articles:
            return True
        return article in articles

    def article_code_connu(self, prefixe: str, article: str) -> bool:
        articles = self.codes.get(prefixe.upper())
        if articles is None:
            return False
        if JOKER in articles:
            return True
        return article in articles

    def article_rg_connu(self, article: str) -> bool:
        return not self.articles_rg or article in self.articles_rg


def _normaliser_article(valeur: str) -> str:
    """« Article 2(17) » → « 2(17) » ; « L. 511-1 » → « l.511-1 ».

    Le joker est rendu tel quel : la normalisation le viderait de sa substance.
    """
    if valeur.strip() == JOKER:
        return JOKER
    v = normaliser(valeur).replace(" ", "")
    v = re.sub(r"^articles?", "", v)
    return v.strip(".").strip()


def _numeros_de_texte(fragment: str) -> list[str]:
    return _NUMERO_TEXTE.findall(fragment)


def extraire_citations(reponse: str, texte_source: str | None = None) -> list[Citation]:
    """Repère les références citées dans une réponse.

    `texte_source` est le numéro du texte sur lequel porte l'item : il sert de
    rattachement par défaut pour un article cité sans texte dans sa phrase.
    """
    citations: list[Citation] = []
    vues: set[tuple[str, str, str | None]] = set()

    def ajouter(genre: str, valeur: str, rattachement: str | None, brut: str) -> None:
        cle = (genre, valeur, rattachement)
        if cle not in vues:
            vues.add(cle)
            citations.append(Citation(genre, valeur, rattachement, brut))

    for phrase in phrases(reponse):
        textes_de_la_phrase = _numeros_de_texte(phrase)
        for numero in textes_de_la_phrase:
            ajouter("texte", numero, None, numero)

        # Un article se rattache au texte cité dans sa phrase, sinon à la source de l'item.
        rattachement = textes_de_la_phrase[0] if textes_de_la_phrase else texte_source

        for prefixe, numero in _ARTICLE_CODE.findall(phrase):
            ajouter(
                "article_code",
                _normaliser_article(f"{prefixe}.{numero}"),
                prefixe.upper(),
                f"{prefixe}. {numero}",
            )

        sans_codes = _ARTICLE_CODE.sub(" ", phrase)

        if "amf" in normaliser(phrase):
            for cote in _ARTICLE_RG.findall(sans_codes):
                ajouter("article_rg", _normaliser_article(cote), "RG AMF", cote)

        # Les cotes à tirets sont écartées ici pour qu'un « 321-100 » ne soit pas
        # relu comme un article « 321 » du texte rattaché.
        sans_cotes = _COTE_A_TIRETS.sub(" ", sans_codes)
        for groupe in _ARTICLE_NUMERIQUE.findall(sans_cotes):
            for morceau in _MORCEAU_NUMERIQUE.findall(groupe):
                ajouter("article", _normaliser_article(morceau), rattachement, morceau)

    return citations


def references_inventees(
    citations: list[Citation], registre: Registre
) -> list[Citation]:
    """Sous-ensemble des citations que le registre ne reconnaît pas."""
    inventees: list[Citation] = []
    for citation in citations:
        if citation.genre == "texte":
            connu = registre.texte_connu(citation.valeur)
        elif citation.genre == "article_code":
            connu = registre.article_code_connu(citation.rattachement or "", citation.valeur)
        elif citation.genre == "article_rg":
            connu = registre.article_rg_connu(citation.valeur)
        else:
            connu = registre.article_connu(citation.rattachement, citation.valeur)

        if not connu:
            inventees.append(citation)
    return inventees


def numero_texte_source(article_source: str, texte_source: str) -> str | None:
    """Extrait le numéro du texte de référence d'un item, pour servir de rattachement."""
    for fragment in (texte_source, article_source):
        numeros = _numeros_de_texte(fragment or "")
        if numeros:
            return numeros[0]
    return None
