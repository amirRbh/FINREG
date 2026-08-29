"""Étape 4 — scoring déterministe. Aucun modèle appelé."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.schema import Axe, Flag, Item, NotesAxes
from src.scoring.deterministe import (
    appliquer_plafonds,
    detecter_abstention,
    detecter_erreurs_disqualifiantes,
    evaluer,
    notes_plancher,
    tranche_seul,
)
from src.scoring.references import (
    Registre,
    extraire_citations,
    numero_texte_source,
    references_inventees,
)
from tests.fabriques import item

REGISTRE = Registre.charger(Path("registry/references.json"))


def item_sfdr(**modifications) -> Item:
    return Item.model_validate(item(**modifications))


# --------------------------------------------------------------------------- #
# Extraction et confrontation au registre
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "texte, attendu",
    [
        ("L'article 8 du règlement (UE) 2019/2088 s'applique.", ("article", "8")),
        ("L'art. 9 du règlement (UE) 2019/2088.", ("article", "9")),
        ("L'article 2(17) du règlement (UE) 2019/2088.", ("article", "2(17)")),
        ("L'article L. 511-1 du code monétaire et financier.", ("article_code", "l.511-1")),
        ("L'article R.561-5 impose la vigilance.", ("article_code", "r.561-5")),
    ],
)
def test_formes_de_citation_reconnues(texte, attendu):
    citations = extraire_citations(texte, "2019/2088")
    assert (attendu[0], attendu[1]) in [(c.genre, c.valeur) for c in citations]


def test_article_inexistant_du_texte_est_signale():
    """Le registre connaît 2019/2088 mais pas son article 47 : c'est une invention."""
    citations = extraire_citations(
        "L'article 47 du règlement (UE) 2019/2088 impose cette publication.", "2019/2088"
    )
    assert [c.valeur for c in references_inventees(citations, REGISTRE)] == ["47"]


def test_texte_inexistant_est_signale():
    citations = extraire_citations("Le règlement (UE) 9999/1234 le prévoit.", None)
    assert [c.valeur for c in references_inventees(citations, REGISTRE)] == ["9999/1234"]


def test_article_de_code_inexistant_est_signale():
    citations = extraire_citations("L'article L. 999-9 du CMF l'impose.", None)
    assert [c.valeur for c in references_inventees(citations, REGISTRE)] == ["l.999-9"]


def test_articles_valides_ne_sont_pas_signales():
    citations = extraire_citations(
        "Les articles 24 et 25 de la directive 2014/65/UE encadrent le conseil, "
        "et l'article 321-100 du règlement général de l'AMF le complète.",
        None,
    )
    assert references_inventees(citations, REGISTRE) == []


def test_texte_a_articles_joker_nest_jamais_signale():
    """Un texte dont la liste d'articles vaut « * » est reconnu sans contrôle d'article."""
    citations = extraire_citations(
        "L'article 137 du règlement délégué (UE) 2022/1288 le prévoit.", None
    )
    assert references_inventees(citations, REGISTRE) == []


def test_article_sans_texte_rattachable_nest_pas_declare_invente():
    """On ne conclut pas à l'invention faute de rattachement : l'axe revient au juge."""
    citations = extraire_citations("L'article 12 le prévoit.", None)
    assert references_inventees(citations, REGISTRE) == []


def test_numero_texte_source():
    assert numero_texte_source("Article 8", "Règlement (UE) 2019/2088 (SFDR)") == "2019/2088"
    assert numero_texte_source("Article 8", "Doctrine de place") is None


# --------------------------------------------------------------------------- #
# Erreurs disqualifiantes
# --------------------------------------------------------------------------- #


def test_erreur_disqualifiante_detectee_malgre_casse_et_accents():
    sujet = item_sfdr(erreurs_disqualifiantes=["obligation systématique de publier"])
    detectees = detecter_erreurs_disqualifiantes(
        "Il y a OBLIGATION SYSTEMATIQUE  de   publier une part minimale.", sujet
    )
    assert detectees == ["obligation systématique de publier"]


def test_erreur_disqualifiante_absente():
    sujet = item_sfdr(erreurs_disqualifiantes=["obligation systématique de publier"])
    assert detecter_erreurs_disqualifiantes("La publication reste facultative.", sujet) == []


def test_la_correspondance_litterale_est_stricte():
    """Choix assumé : pas de correspondance approximative sur un critère qui met un axe à 0.

    Une formulation qui s'écarte de la lettre n'est pas attrapée ; c'est ce que
    le préfixe `re:` sert à couvrir, explicitement, item par item.
    """
    litteral = item_sfdr(erreurs_disqualifiantes=["publication toujours obligatoire"])
    assert detecter_erreurs_disqualifiantes("La publication est toujours obligatoire.", litteral) == []

    avec_regex = item_sfdr(erreurs_disqualifiantes=["re:publication (est )?toujours obligatoire"])
    assert detecter_erreurs_disqualifiantes("La publication est toujours obligatoire.", avec_regex)


def test_erreur_disqualifiante_en_expression_reguliere():
    sujet = item_sfdr(erreurs_disqualifiantes=["re:seuil de (20|25) %"])
    assert detecter_erreurs_disqualifiantes("Le seuil de 25 % s'applique.", sujet)
    assert not detecter_erreurs_disqualifiantes("Le seuil de 30 % s'applique.", sujet)


def test_motif_regex_invalide_ne_disqualifie_pas():
    """Un motif de corpus cassé ne doit pas faire chuter une réponse correcte."""
    sujet = item_sfdr(erreurs_disqualifiantes=["re:seuil de ((("])
    assert detecter_erreurs_disqualifiantes("Le seuil de 25 % s'applique.", sujet) == []


# --------------------------------------------------------------------------- #
# Abstention
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "reponse",
    [
        "Je ne sais pas répondre avec certitude.",
        "Je ne dispose pas des éléments nécessaires.",
        "Il n'est pas possible de répondre en l'état.",
    ],
)
def test_abstention_detectee(reponse):
    assert detecter_abstention(reponse)


def test_absence_dabstention():
    assert not detecter_abstention("L'article 8 du règlement (UE) 2019/2088 s'applique.")


# --------------------------------------------------------------------------- #
# Constat complet et plafonds
# --------------------------------------------------------------------------- #


def test_reference_inventee_annule_le_sourcing_et_borne_le_reste():
    constat = evaluer(
        item_sfdr(),
        "L'article 47 du règlement (UE) 2019/2088 impose cette publication.",
        REGISTRE,
    )
    assert Flag.HALLUCINATION_SOURCE in constat.flags
    assert constat.plafonds[Axe.SOURCING] == 0
    assert constat.plafonds[Axe.EXACTITUDE] == 1
    assert constat.plafonds[Axe.CALIBRATION] == 1


def test_erreur_disqualifiante_annule_lexactitude():
    sujet = item_sfdr(erreurs_disqualifiantes=["publication toujours obligatoire"])
    constat = evaluer(
        sujet,
        "La publication toujours obligatoire, cf. article 8 du règlement (UE) 2019/2088.",
        REGISTRE,
    )
    assert Flag.ERREUR_DISQUALIFIANTE in constat.flags
    assert constat.plafonds[Axe.EXACTITUDE] == 0


def test_reponse_sans_aucune_source_est_signalee():
    constat = evaluer(item_sfdr(), "Non, ce n'est pas obligatoire.", REGISTRE)
    assert Flag.SOURCING_INCOMPLET in constat.flags
    assert constat.plafonds[Axe.SOURCING] == 0


def test_texte_cite_sans_article_borne_le_sourcing_a_un():
    constat = evaluer(
        item_sfdr(), "Le règlement (UE) 2019/2088 le prévoit.", REGISTRE
    )
    assert Flag.SOURCING_INCOMPLET in constat.flags
    assert constat.plafonds[Axe.SOURCING] == 1


def test_reponse_correctement_sourcee_nimpose_aucun_plafond():
    constat = evaluer(
        item_sfdr(),
        "Non. L'article 8 du règlement (UE) 2019/2088 vise la promotion de "
        "caractéristiques, sans objectif durable au sens de l'article 2(17).",
        REGISTRE,
    )
    assert constat.plafonds == {}
    assert constat.flags == []


def test_item_dabstention_repondu_quand_meme_est_une_surconfiance():
    sujet = item_sfdr(type="abstention")
    constat = evaluer(
        sujet, "Oui, l'article 8 du règlement (UE) 2019/2088 tranche la question.", REGISTRE
    )
    assert Flag.SURCONFIANCE in constat.flags
    assert constat.plafonds[Axe.CALIBRATION] == 0


def test_item_dabstention_correctement_traite():
    sujet = item_sfdr(type="abstention")
    constat = evaluer(sujet, "Je ne dispose pas des éléments pour trancher.", REGISTRE)
    assert Flag.ABSTENTION in constat.flags
    assert Flag.SURCONFIANCE not in constat.flags
    assert Axe.CALIBRATION not in constat.plafonds


def test_abstention_nest_pas_penalisee_pour_sourcing_absent():
    """S'abstenir sans citer de texte n'est pas un défaut de sourcing."""
    constat = evaluer(item_sfdr(), "Je ne sais pas.", REGISTRE)
    assert Flag.SOURCING_INCOMPLET not in constat.flags


def test_les_plafonds_bornent_les_notes_du_juge():
    constat = evaluer(
        item_sfdr(),
        "L'article 47 du règlement (UE) 2019/2088 impose cette publication.",
        REGISTRE,
    )
    genereuses = NotesAxes(exactitude=2, sourcing=2, calibration=2, exploitabilite=2)
    bornees = appliquer_plafonds(genereuses, constat)

    assert bornees.sourcing == 0
    assert bornees.exactitude == 1
    assert bornees.calibration == 1
    assert bornees.exploitabilite == 2  # axe non plafonné : le juge reste maître


def test_les_plafonds_ne_remontent_jamais_une_note():
    constat = evaluer(item_sfdr(), "Le règlement (UE) 2019/2088 le prévoit.", REGISTRE)
    severes = NotesAxes(exactitude=0, sourcing=0, calibration=0, exploitabilite=0)
    assert appliquer_plafonds(severes, constat).as_dict() == severes.as_dict()


def test_cas_ou_le_deterministe_tranche_seul():
    sujet = item_sfdr(type="abstention", erreurs_disqualifiantes=["c'est obligatoire"])
    constat = evaluer(sujet, "C'est obligatoire selon l'article 47 du règlement (UE) 2019/2088.", REGISTRE)
    constat.plafonds[Axe.EXPLOITABILITE] = 0
    constat.plafonds[Axe.SOURCING] = 0
    constat.plafonds[Axe.EXACTITUDE] = 0
    constat.plafonds[Axe.CALIBRATION] = 0

    assert tranche_seul(constat)
    assert notes_plancher(constat).total() == 0


def test_le_deterministe_ne_tranche_pas_seul_par_defaut():
    constat = evaluer(item_sfdr(), "Non, ce n'est pas obligatoire.", REGISTRE)
    assert not tranche_seul(constat)
