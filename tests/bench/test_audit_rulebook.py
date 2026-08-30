"""Tests de l'audit du Rulebook contre le texte primaire.

**Aucun accès réseau.** Le récupérateur est injecté : ces tests servent un faux
Journal officiel, synthétique et reconnaissable comme tel (`example.invalid`,
« Texte synthétique »). C'est la règle non négociable du dépôt, et c'est aussi
ce qui rend ces tests capables de reproduire des cas qu'on ne pourrait pas
provoquer en vrai — un serveur qui répond 200 avec une page d'accueil, par
exemple.

Le test le plus important est
`test_le_dossier_prerempli_est_refuse_tant_quil_nest_pas_signe` : il vérifie que
l'audit ne peut pas promouvoir une règle tout seul. Ce n'est pas une convention
de rapport, c'est une validation de schéma.
"""

from __future__ import annotations

import copy
import csv
import datetime as dt
import io
import zipfile
from pathlib import Path
from typing import Any

import pytest

from src.bench.audit_rulebook import (
    ClassementAudit,
    auditer,
    auditer_regle,
    chiffres_de,
    couverture_lexicale,
    ordre_de_priorite,
)
from src.bench.rapport_audit import (
    ecrire_matrice,
    exporter_dossier_prerempli,
    rapport_markdown,
)
from src.bench.regles import Rule
from src.bench.sources_primaires import (
    _RedirectionHttps,
    _en_https,
    RecuperationImpossible,
    Reponse,
    celex_consolide,
    celex_de_url,
    celex_du_texte,
    cles_articles,
    extraire_articles,
    extraire_paragraphe,
    normaliser_article,
    recuperer_texte,
)
from src.bench.verification import VerificationInvalide, Verdict, lire_dossier
from tests.bench.fabriques import REGLE

CELLAR = "http://publications.europa.eu/resource"
UUID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

#: Faux acte, au format Formex du Journal officiel. Rigoureusement fictif.
ACTE_SYNTHETIQUE = """<?xml version="1.0"?><ACT>
<TITLE>Règlement (UE) 2099/9999 synthétique — Journal officiel L 999</TITLE>
<P>Le PARLEMENT EUROPÉEN, considérant que le présent règlement est synthétique,</P>
<P>(1) Considérant synthétique numéro 1 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(2) Considérant synthétique numéro 2 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(3) Considérant synthétique numéro 3 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(4) Considérant synthétique numéro 4 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(5) Considérant synthétique numéro 5 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(6) Considérant synthétique numéro 6 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(7) Considérant synthétique numéro 7 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(8) Considérant synthétique numéro 8 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(9) Considérant synthétique numéro 9 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(10) Considérant synthétique numéro 10 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(11) Considérant synthétique numéro 11 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<P>(12) Considérant synthétique numéro 12 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</P>
<ARTICLE><TI.ART>Article premier</TI.ART><P>Le présent règlement synthétique
définit les obligations de publication applicables aux entités assujetties.</P></ARTICLE>
<ARTICLE><TI.ART>Article 2</TI.ART><STI.ART>Définitions</STI.ART>
<P>Aux fins du présent règlement, on entend par: 17) notion synthétique : une
notion définie pour les besoins des tests, qui contribue à un objectif
synthétique sans causer de préjudice, sous réserve de pratiques de gouvernance.
18) autre notion : sans objet.</P></ARTICLE>
<ARTICLE><TI.ART>Article 3</TI.ART><P>Les entités assujetties publient les
informations dans un délai de 30 jours à compter de la constatation.</P></ARTICLE>
</ACT>"""

#: Le même acte servi en rendu XHTML du JO, avec subdivisions ELI.
ACTE_ELI = """<html><body>
<p>Le PARLEMENT EUROPÉEN, considérant que le présent règlement est synthétique.</p>
<p>(1) Considérant synthétique numéro 1 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(2) Considérant synthétique numéro 2 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(3) Considérant synthétique numéro 3 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(4) Considérant synthétique numéro 4 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(5) Considérant synthétique numéro 5 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(6) Considérant synthétique numéro 6 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(7) Considérant synthétique numéro 7 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(8) Considérant synthétique numéro 8 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(9) Considérant synthétique numéro 9 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(10) Considérant synthétique numéro 10 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(11) Considérant synthétique numéro 11 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<p>(12) Considérant synthétique numéro 12 : le présent règlement synthétique n'a aucune valeur juridique et sert uniquement à éprouver le découpage par article du Journal officiel synthétique.</p>
<div class="eli-subdivision" id="art_1"><p class="oj-ti-art">Article premier</p>
<p>Objet synthétique du présent règlement.</p></div>
<div class="eli-subdivision" id="art_2"><p class="oj-ti-art">Article 2</p>
<p>Définitions synthétiques applicables aux entités assujetties.</p></div>
</body></html>"""

#: Ce que sert la passerelle quand elle intercepte : un succès sans le texte.
PAGE_D_ACCUEIL = "<html><title>Accueil</title><body>Sommaire du jour</body></html>"


def _zip(contenu: str) -> bytes:
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as archive:
        archive.writestr("L_2099999FR.01000101.doc.xml", "<META/>")
        archive.writestr("L_2099999FR.01000101.xml", contenu)
    return tampon.getvalue()


def faux_reseau(
    document: str = ACTE_SYNTHETIQUE, *, en_zip: bool = True, indice_bon: str = "0009"
):
    """Un faux CELLAR : résout le CELEX, puis ne sert la langue qu'au bon indice."""

    def recuperer(url: str, entetes: dict[str, str]) -> Reponse:
        if "/celex/" in url:
            return Reponse(200, b"<rdf/>", f"{CELLAR}/cellar/{UUID}")
        if f"{UUID}.{indice_bon}." in url:
            charge = _zip(document) if en_zip else document.encode("utf-8")
            return Reponse(200, charge, url)
        raise OSError("HTTP Error 404: Not Found")

    return recuperer


def regle(**modifications: Any) -> Rule:
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "status": "draft",
            "verification_method": "model_knowledge_unverified",
            "operational_rule": "Traduction opérationnelle synthétique.",
            "source": {
                **brut["source"],
                "text": "Règlement (UE) 2099/9999 synthétique",
                "article": "Article 2",
                "paragraph": "point 17",
                "url": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32099R9999",
                "verified_by": "",
                "verification_date": None,
            },
            "statement": (
                "Le règlement synthétique définit la notion synthétique comme une "
                "notion qui contribue à un objectif synthétique sans causer de "
                "préjudice, sous réserve de pratiques de gouvernance."
            ),
        }
    )
    brut.update(modifications)
    return Rule.model_validate(brut)


# --------------------------------------------------------------------------- #
# Lecture des citations
# --------------------------------------------------------------------------- #


def test_le_celex_se_lit_dans_lurl_et_dans_la_citation() -> None:
    assert celex_de_url("…?uri=CELEX:32019R2088") == "32019R2088"
    assert celex_du_texte("Règlement (UE) 2019/2088 (SFDR)") == "32019R2088"
    assert celex_du_texte("Directive 2014/65/UE (MIFID II)") == "32014L0065"
    assert celex_du_texte("Code monétaire et financier") is None


def test_un_ancrage_multiple_designe_toutes_ses_dispositions() -> None:
    assert cles_articles("Article 2") == ["2"]
    assert cles_articles("Articles 17 et 18") == ["17", "18"]
    assert cles_articles("Articles 8 à 13") == ["8", "9", "10", "11", "12", "13"]
    # Un ancrage global ne désigne aucun article : il n'y a rien à retrouver.
    assert cles_articles("Ensemble de la directive") == []


def test_le_numero_dacte_nest_pas_pris_pour_un_article() -> None:
    """« article 54 du règlement 2017/565 » ne cite pas les articles 2017 et 565."""
    assert cles_articles("Article 54 du règlement délégué (UE) 2017/565") == ["54"]


def test_article_premier_et_article_1er_designent_le_meme_article() -> None:
    assert normaliser_article("Article premier") == "1"
    assert normaliser_article("Article 1er") == "1"
    assert normaliser_article("Art. 25") == "25"


def test_la_version_consolidee_nomme_sa_date() -> None:
    assert celex_consolide("32017R0565", dt.date(2022, 8, 2)) == "02017R0565-20220802"
    assert celex_consolide("pas-un-celex", dt.date(2022, 8, 2)) is None


# --------------------------------------------------------------------------- #
# Récupération
# --------------------------------------------------------------------------- #


def test_le_texte_officiel_se_decoupe_par_article() -> None:
    texte = recuperer_texte("32099R9999", recuperateur=faux_reseau(), cache=None)
    assert set(texte.articles) == {"1", "2", "3"}
    assert "notion synthétique" in texte.articles["2"]
    assert texte.is_authentic
    assert texte.sha256


def test_le_rendu_xhtml_du_journal_officiel_se_decoupe_aussi() -> None:
    texte = recuperer_texte(
        "32099R9999", recuperateur=faux_reseau(ACTE_ELI, en_zip=False), cache=None
    )
    assert set(texte.articles) == {"1", "2"}


def test_un_paragraphe_se_cite_precisement() -> None:
    texte = recuperer_texte("32099R9999", recuperateur=faux_reseau(), cache=None)
    point = extraire_paragraphe(texte.articles["2"], "point 17")
    assert point.startswith("17)")
    assert "18)" not in point
    # Un paragraphe qu'on ne sait pas isoler ne s'invente pas.
    assert extraire_paragraphe(texte.articles["2"], "") == ""


def test_une_page_daccueil_servie_en_200_est_refusee() -> None:
    """Le piège réel : un succès HTTP qui ne contient pas le texte demandé."""
    with pytest.raises(RecuperationImpossible):
        recuperer_texte(
            "32099R9999",
            recuperateur=faux_reseau(PAGE_D_ACCUEIL, en_zip=False),
            cache=None,
        )


#: Le même acte dans une autre langue. CELLAR sert les vingt-quatre versions
#: linguistiques sous des index voisins : sonder sans vérifier la langue
#: reviendrait à vérifier une règle française contre un texte anglais.
ACTE_ANGLAIS = (
    """<?xml version="1.0"?><ACT>
<TITLE>Regulation (EU) 2099/9999 — Official Journal L 999</TITLE>
<P>THE EUROPEAN PARLIAMENT, whereas this Regulation is synthetic,</P>
"""
    + "\n".join(
        f"<P>({n}) Synthetic recital number {n}: this Regulation has no legal "
        f"value whatsoever and exists solely to exercise the article splitting."
        f"</P>"
        for n in range(1, 13)
    )
    + """
<ARTICLE><TI.ART>Article 1</TI.ART><P>This Regulation lays down disclosure
obligations applicable to the entities concerned.</P></ARTICLE>
<ARTICLE><TI.ART>Article 2</TI.ART><P>For the purposes of this Regulation, the
following definitions apply.</P></ARTICLE>
</ACT>"""
)


def test_un_texte_dans_une_autre_langue_est_refuse() -> None:
    with pytest.raises(RecuperationImpossible):
        recuperer_texte("32099R9999", recuperateur=faux_reseau(ACTE_ANGLAIS), cache=None)


def test_le_texte_se_met_en_cache_et_se_relit(tmp_path: Path) -> None:
    premier = recuperer_texte("32099R9999", recuperateur=faux_reseau(), cache=tmp_path)

    def interdit(url: str, entetes: dict[str, str]) -> Reponse:
        raise AssertionError("le cache doit éviter tout nouvel appel")

    second = recuperer_texte("32099R9999", recuperateur=interdit, cache=tmp_path)
    assert second.sha256 == premier.sha256
    assert second.articles == premier.articles


def test_extraire_articles_rend_un_dictionnaire_vide_sur_du_bruit() -> None:
    assert extraire_articles("<html><body>rien</body></html>") == {}


# --------------------------------------------------------------------------- #
# Mesures
# --------------------------------------------------------------------------- #


def test_la_couverture_lexicale_mesure_le_rattachement() -> None:
    assert couverture_lexicale("obligations publication entités", "obligations de publication des entités") == 1.0
    assert couverture_lexicale("cryptomonnaies stablecoins", "obligations de publication") == 0.0
    assert couverture_lexicale("", "quoi que ce soit") == 0.0


def test_les_chiffres_porteurs_de_droit_sont_normalises() -> None:
    assert "30 jour" in chiffres_de("dans un délai de 30 jours")
    assert "25 %" in chiffres_de("un seuil de 25 %")
    # Un nombre sans unité juridique n'est pas un seuil.
    assert chiffres_de("le paragraphe 3 dispose") == []


# --------------------------------------------------------------------------- #
# Classement
# --------------------------------------------------------------------------- #


def test_une_regle_corroboree_attend_une_signature_humaine() -> None:
    constat = auditer_regle(regle(), faux_reseau(), cache=None)
    assert constat.classement is ClassementAudit.REQUIRES_HUMAN_REVIEW
    assert constat.verdict_propose is Verdict.CONFIRME
    assert constat.preuve is not None and constat.preuve.article_found
    assert constat.preuve.paragraph_excerpt.startswith("17)")


def test_laudit_ne_sattribue_jamais_source_checked() -> None:
    """Le dépôt l'interdit : ce statut ne se déduit jamais de la seule preuve.

    Les règles ci-dessous sont en `draft` et parfaitement corroborées. Elles
    restent malgré tout hors de `SOURCE_CHECKED` : seule une signature déjà
    portée par la règle peut le justifier.
    """
    constats = auditer(
        [regle(), regle(id="RULE-SYNTH-002"), regle(id="RULE-SYNTH-003", source={
            **REGLE["source"], "text": "Code monétaire et financier",
            "article": "L. 561-1", "url": "https://www.legifrance.gouv.fr/codes/x",
            "verified_by": "", "verification_date": None})],
        faux_reseau(),
        cache=None,
    )
    assert all(c.classement is not ClassementAudit.SOURCE_CHECKED for c in constats)


def regle_signee(**modifications: Any) -> Rule:
    """La même règle, mais promue par un vérificateur nommé."""
    base = regle().model_dump(mode="json")
    base.update(
        {
            "status": "source_checked",
            "verification_method": "primary_text_fetched",
            "source": {
                **base["source"],
                "verified_by": "Relecteur de test",
                "verification_date": "2026-08-29",
            },
        }
    )
    base.update(modifications)
    return Rule.model_validate(base)


def test_une_regle_deja_signee_est_lue_comme_source_checked() -> None:
    """Constater qu'un humain a signé n'est pas signer à sa place."""
    constat = auditer_regle(regle_signee(), faux_reseau(), cache=None)
    assert constat.classement is ClassementAudit.SOURCE_CHECKED


def test_une_signature_ne_protege_pas_un_enonce_qui_ne_se_retrouve_plus() -> None:
    """Un texte peut changer après la signature : le classement doit le dire."""
    perimee = regle_signee(
        statement=(
            "Le règlement impose aux plateformes de cryptoactifs une déclaration "
            "trimestrielle de leurs réserves auprès du superviseur bancaire."
        )
    )
    constat = auditer_regle(perimee, faux_reseau(), cache=None)
    assert constat.classement is ClassementAudit.DRAFT


def test_une_regle_signee_et_corroboree_nest_pas_reproposee_au_dossier(
    tmp_path: Path,
) -> None:
    """Le dossier liste ce qui reste à faire, pas ce qui est acquis."""
    regles = [regle_signee()]
    constats = auditer(regles, faux_reseau(), cache=None)
    dossier = exporter_dossier_prerempli(constats, regles, tmp_path / "dossier.csv")

    with dossier.open(encoding="utf-8-sig", newline="") as flux:
        ligne = next(csv.DictReader(flux, delimiter=";"))
    assert ligne["verdict"] == ""


def test_une_correction_nest_jamais_proposee_sans_lenonce_qui_la_porte(
    tmp_path: Path,
) -> None:
    """L'audit ne rédige pas de droit : il ne peut donc pas proposer « corrige ».

    Inscrire « corrige » sans énoncé corrigé produirait une ligne que le circuit
    rejette — et ferait tomber le lot entier à cause d'une case que la machine ne
    pouvait pas remplir. Le dossier inscrit « non_verifiable » et dit ce qu'il
    reste à écrire.
    """
    regles = [
        regle(
            statement=(
                "Le règlement impose aux plateformes de cryptoactifs une "
                "déclaration trimestrielle de leurs réserves."
            )
        )
    ]
    constats = auditer(regles, faux_reseau(), cache=None)
    assert constats[0].verdict_propose is Verdict.CORRIGE

    dossier = exporter_dossier_prerempli(constats, regles, tmp_path / "dossier.csv")
    with dossier.open(encoding="utf-8-sig", newline="") as flux:
        ligne = next(csv.DictReader(flux, delimiter=";"))
    assert ligne["verdict"] == "non_verifiable"
    assert "CORRECTION REQUISE" in ligne["commentaire"]

    # Et le dossier reste lisible par le circuit, au lieu d'être rejeté en bloc.
    ligne_signee = dict(ligne)
    ligne_signee["verifie_par"] = "Relecteur de test"
    ligne_signee["date_verification"] = "2026-08-29"
    signe = tmp_path / "signe.csv"
    with signe.open("w", encoding="utf-8-sig", newline="") as flux:
        graveur = csv.DictWriter(flux, fieldnames=list(ligne), delimiter=";")
        graveur.writeheader()
        graveur.writerow(ligne_signee)
    verifications = lire_dossier(signe)
    assert verifications[0].verdict is Verdict.NON_VERIFIABLE


def test_une_source_hors_datteinte_est_bloquee_pas_refutee() -> None:
    """« On n'a pas pu regarder » n'est pas « on a regardé et c'est faux »."""
    inaccessible = regle(
        source={
            **REGLE["source"],
            "text": "Code monétaire et financier",
            "article": "L. 561-2",
            "url": "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026",
            "verified_by": "",
            "verification_date": None,
        }
    )
    constat = auditer_regle(inaccessible, faux_reseau(), cache=None)
    assert constat.classement is ClassementAudit.BLOCKED
    assert constat.verdict_propose is None
    assert any("403" in p for p in constat.problemes)


def test_un_article_introuvable_refute_la_regle() -> None:
    absente = regle(source={**regle().source.model_dump(mode="json"), "article": "Article 99"})
    constat = auditer_regle(absente, faux_reseau(), cache=None)
    assert constat.classement is ClassementAudit.DRAFT
    assert constat.verdict_propose is Verdict.REFUTE
    assert any("introuvable" in p for p in constat.problemes)


def test_un_enonce_qui_parle_dautre_chose_est_a_corriger() -> None:
    hors_sujet = regle(
        statement=(
            "Le règlement impose aux plateformes de cryptoactifs une déclaration "
            "trimestrielle de leurs réserves auprès du superviseur bancaire."
        )
    )
    constat = auditer_regle(hors_sujet, faux_reseau(), cache=None)
    assert constat.classement is ClassementAudit.DRAFT
    assert constat.verdict_propose is Verdict.CORRIGE
    assert any("peu corroboré" in p for p in constat.problemes)


def test_un_chiffre_absent_du_texte_officiel_est_signale() -> None:
    invente = regle(
        source={**regle().source.model_dump(mode="json"), "article": "Article 3", "paragraph": ""},
        statement="Les entités publient les informations dans un délai de 45 jours.",
    )
    constat = auditer_regle(invente, faux_reseau(), cache=None)
    assert "45 jour" in constat.missing_figures
    assert constat.classement is ClassementAudit.DRAFT


def test_lurl_et_la_citation_qui_divergent_sont_signalees() -> None:
    """Une règle pointe volontiers l'acte modificatif au lieu de l'acte modifié."""
    divergente = regle(
        source={
            **regle().source.model_dump(mode="json"),
            "text": "Règlement (UE) 2099/9999 synthétique",
            "url": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32099R1111",
        }
    )
    constat = auditer_regle(divergente, faux_reseau(), cache=None)
    assert any("l'URL désigne l'acte" in p for p in constat.problemes)


def test_un_ancrage_multiple_est_signale_comme_a_decouper() -> None:
    large = regle(
        source={**regle().source.model_dump(mode="json"), "article": "Articles 1 à 3", "paragraph": ""}
    )
    constat = auditer_regle(large, faux_reseau(), cache=None)
    assert any("articles couverts" in p for p in constat.problemes)


def test_les_exceptions_inconnues_sont_toujours_signalees() -> None:
    constat = auditer_regle(regle(exceptions_status="unknown"), faux_reseau(), cache=None)
    assert any("exceptions jamais cherchées" in p for p in constat.problemes)


def test_laudit_traite_les_critiques_en_premier() -> None:
    ordre = ordre_de_priorite(
        [
            regle(id="RULE-SYNTH-B", priority="MEDIUM"),
            regle(id="RULE-SYNTH-A", priority="CRITICAL"),
        ]
    )
    assert [r.id for r in ordre] == ["RULE-SYNTH-A", "RULE-SYNTH-B"]


def test_un_audit_ne_sinterrompt_pas_sur_une_source_injoignable() -> None:
    def reseau_en_panne(url: str, entetes: dict[str, str]) -> Reponse:
        raise OSError("connexion refusée")

    constats = auditer([regle(), regle(id="RULE-SYNTH-002")], reseau_en_panne, cache=None)
    assert len(constats) == 2
    assert all(c.classement is ClassementAudit.BLOCKED for c in constats)


# --------------------------------------------------------------------------- #
# Le verrou
# --------------------------------------------------------------------------- #


def test_le_dossier_prerempli_est_refuse_tant_quil_nest_pas_signe(tmp_path: Path) -> None:
    """L'audit prépare tout sauf la signature — et sans elle, rien ne passe.

    Ce n'est pas une consigne de rapport : `Verification` refuse un verdict
    promoteur sans vérificateur nommé ni date. L'audit ne peut donc pas promouvoir
    une règle, quelle que soit la qualité de sa preuve.
    """
    regles = [regle()]
    constats = auditer(regles, faux_reseau(), cache=None)
    dossier = exporter_dossier_prerempli(constats, regles, tmp_path / "dossier.csv")

    with pytest.raises(VerificationInvalide) as echec:
        lire_dossier(dossier)
    assert any("vérificateur nommé" in e for e in echec.value.erreurs)


def test_le_dossier_prerempli_porte_la_preuve_mais_pas_la_signature(tmp_path: Path) -> None:
    regles = [regle()]
    constats = auditer(regles, faux_reseau(), cache=None)
    dossier = exporter_dossier_prerempli(constats, regles, tmp_path / "dossier.csv")

    with dossier.open(encoding="utf-8-sig", newline="") as flux:
        ligne = next(csv.DictReader(flux, delimiter=";"))
    assert ligne["verdict"] == "confirme"
    assert ligne["methode"] == "primary_text_fetched"
    assert "TEXTE OFFICIEL" in ligne["commentaire"]
    assert ligne["verifie_par"] == ""
    assert ligne["date_verification"] == ""


def test_le_dossier_signe_passe_le_circuit(tmp_path: Path) -> None:
    """Une fois signé, le même dossier est accepté : le verrou tient sur la signature."""
    regles = [regle()]
    constats = auditer(regles, faux_reseau(), cache=None)
    dossier = exporter_dossier_prerempli(constats, regles, tmp_path / "dossier.csv")

    contenu = dossier.read_text(encoding="utf-8-sig")
    entete, ligne = contenu.strip().split("\n")[:2]
    colonnes = entete.split(";")
    valeurs = next(csv.reader([ligne], delimiter=";"))
    signee = dict(zip(colonnes, valeurs))
    signee["verifie_par"] = "Relecteur de test"
    signee["date_verification"] = "2026-08-29"

    signe = tmp_path / "signe.csv"
    with signe.open("w", encoding="utf-8-sig", newline="") as flux:
        graveur = csv.DictWriter(flux, fieldnames=colonnes, delimiter=";")
        graveur.writeheader()
        graveur.writerow(signee)

    verifications = lire_dossier(signe)
    assert len(verifications) == 1
    assert verifications[0].verdict is Verdict.CONFIRME
    assert verifications[0].verified_by == "Relecteur de test"


# --------------------------------------------------------------------------- #
# Rapports
# --------------------------------------------------------------------------- #


def test_la_matrice_porte_les_colonnes_demandees(tmp_path: Path) -> None:
    regles = [regle()]
    constats = auditer(regles, faux_reseau(), cache=None)
    sortie = tmp_path / "matrice.csv"
    ecrire_matrice(constats, regles, sortie)

    assert sortie.read_bytes().startswith(b"\xef\xbb\xbf")
    with sortie.open(encoding="utf-8-sig", newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=";"))
    attendues = {
        "rule_id", "domaine", "source", "article", "version",
        "statut", "exceptions", "temporalite", "probleme",
    }
    assert attendues <= set(lignes[0])
    # La preuve accompagne le constat : sans elle, la ligne serait une opinion.
    assert lignes[0]["sha256_texte"]
    assert lignes[0]["recupere_depuis"]


def test_le_rapport_dit_ce_quil_ne_fait_pas() -> None:
    regles = [regle()]
    texte = rapport_markdown(auditer(regles, faux_reseau(), cache=None), regles)
    assert "s'accorder à lui-même" in texte
    assert "REQUIRES_HUMAN_REVIEW" in texte
    assert "règles examinées" in texte


# --------------------------------------------------------------------------- #
# Transport : une URI publiée en HTTP se demande en HTTPS
# --------------------------------------------------------------------------- #


def test_une_uri_publiee_en_http_se_demande_en_https() -> None:
    """CELLAR publie ses URI en `http://` ; certains relais ne passent que le HTTPS."""
    assert _en_https("http://publications.europa.eu/resource/celex/32019R2088") == (
        "https://publications.europa.eu/resource/celex/32019R2088"
    )


def test_une_uri_deja_en_https_nest_pas_touchee() -> None:
    assert _en_https("https://exemple.invalid/a") == "https://exemple.invalid/a"


def test_la_bascule_sapplique_aussi_aux_redirections() -> None:
    """CELLAR résout un CELEX par un 303 vers une URI en clair.

    Ne basculer que l'URL de départ laisserait ce saut-là en HTTP — et c'est
    lui qui échoue là où seul le HTTPS est relayé.
    """
    import email.message
    import urllib.request

    depart = urllib.request.Request("https://publications.europa.eu/resource/celex/32019R2088")
    entetes = email.message.Message()
    redirigee = _RedirectionHttps().redirect_request(
        depart,
        None,
        303,
        "See Other",
        entetes,
        "http://publications.europa.eu/resource/cellar/4f50e277/rdf/object/full",
    )
    assert redirigee.full_url.startswith("https://")
