"""Pack d'arbitrage P0/P1 : dossiers, regroupements, bordereau.

Ce que ces tests protègent :

1. **Le relecteur n'a rien à deviner.** Chaque dossier nomme la disposition à
   examiner, la question à trancher et le périmètre à attester.
2. **Le texte et l'interprétation ne se mélangent pas.** `TEXTUAL_FACTS` ne
   contient que des constats ; tout jugement est dans `INTERPRETIVE_QUESTION`.
3. **Rien n'est décidé à la place du relecteur.** Le bordereau sort avec ses
   colonnes de décision vides, et le schéma refuse ensuite ce que la décision ne
   justifie pas.

Aucun accès réseau : les actes sont synthétiques.
"""

from __future__ import annotations

import copy
import csv
from pathlib import Path
from typing import Any

import pytest

from src.bench.completude import analyser
from src.bench.dossier_revue import (
    DecisionRevue,
    PropositionMecanique,
    construire_dossier,
    dispositions_de_soutien,
)
from src.bench.rapport_revue import (
    COLONNES_BORDEREAU,
    avancement,
    ecrire_bordereau,
    file_de_revue,
    lire_bordereau,
)
from src.bench.readiness import evaluer
from src.bench.regles import Rule
from src.bench.verification import VerificationInvalide
from tests.bench.fabriques import REGLE

#: Faux acte : l'article 12 porte l'obligation, l'article 16 y déroge en la
#: citant, l'article 20 déroge à l'acte entier, l'article 4 déroge à autre chose.
ACTE = {
    "12": (
        "Article 12 Obligations de publication. Les entités assujetties publient "
        "annuellement un rapport détaillant leur dispositif, dans un délai de "
        "30 jours à compter de la clôture."
    ),
    "16": (
        "Article 16 Proportionnalité. Par dérogation, l'article 12 ne s'applique "
        "pas aux entités dont le total de bilan est inférieur à 20 000 000 EUR."
    ),
    "20": (
        "Article 20 Dispositions générales. Sans préjudice du présent règlement, "
        "les autorités compétentes peuvent accorder un délai supplémentaire."
    ),
    "4": (
        "Article 4 Autre matière. Par dérogation au paragraphe 1, les prestataires "
        "de services de paiement transmettent leurs relevés trimestriellement."
    ),
}

ENONCE = (
    "Les entités assujetties publient annuellement un rapport détaillant leur "
    "dispositif, dans un délai de 30 jours à compter de la clôture."
)


def regle(**modifications: Any) -> Rule:
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "status": "source_checked",
            "verification_method": "primary_text_fetched",
            "statement": ENONCE,
            "gold_ready": False,
            "gold_ready_reason": "",
            "source": {**REGLE["source"], "article": "Article 12"},
            # Les dossiers ne couvrent que P0 et P1 : une règle critique bloquée
            # sur ses exceptions est le cas nominal de cette phase.
            "priority": "CRITICAL",
        }
    )
    brut.update(modifications)
    return Rule.model_validate(brut)


def dossier_de(sujet: Rule, articles: dict[str, str] | None = None, cle: str = "12"):
    contenu = ACTE if articles is None else articles
    texte = contenu.get(cle, "")
    constat = analyser(sujet, texte, " ".join(contenu.values()), article_verifie=bool(texte),
                       concordance=0.9)
    etat = evaluer(sujet, constat)
    return construire_dossier(sujet, constat, etat, contenu, cle)


# --------------------------------------------------------------------------- #
# Dispositions de soutien
# --------------------------------------------------------------------------- #


def test_une_derogation_qui_cite_larticle_est_retenue_en_premier() -> None:
    """Le lien le plus fort que la mécanique puisse établir sans lire le droit."""
    trouvees = dispositions_de_soutien(ACTE, "12")
    assert trouvees[0].article == "Article 16"
    assert trouvees[0].cite_larticle
    assert "article 12" in trouvees[0].relation.lower()


def test_une_derogation_a_lacte_entier_est_retenue() -> None:
    articles = {a: t for a, t in ACTE.items() if a in ("12", "20")}
    trouvees = dispositions_de_soutien(articles, "12")
    assert any(d.article == "Article 20" for d in trouvees)


def test_une_derogation_a_autre_chose_nest_pas_retenue() -> None:
    """Un dossier qui listerait tout l'acte ne ferait gagner aucun temps."""
    articles = {a: t for a, t in ACTE.items() if a in ("12", "4")}
    trouvees = dispositions_de_soutien(articles, "12")
    assert all(d.article != "Article 4" for d in trouvees)


def test_les_extraits_sont_recopies_du_texte() -> None:
    for disposition in dispositions_de_soutien(ACTE, "12"):
        origine = ACTE[disposition.article.replace("Article ", "")]
        assert disposition.extrait in origine


def test_un_acte_sans_derogation_ne_propose_rien() -> None:
    assert dispositions_de_soutien({"12": ACTE["12"]}, "12") == []


# --------------------------------------------------------------------------- #
# Séparation du texte et de l'interprétation
# --------------------------------------------------------------------------- #


def test_les_faits_textuels_ne_contiennent_aucun_jugement() -> None:
    dossier = dossier_de(regle())
    interdits = ("doit décider", "probablement", "il semble", "on peut penser")
    for fait in dossier.textual_facts:
        assert not any(marque in fait.lower() for marque in interdits), fait


def test_la_question_interpretative_porte_larbitrage() -> None:
    dossier = dossier_de(regle())
    assert dossier.interpretive_question
    assert "doit décider" in dossier.interpretive_question


def test_la_question_neutre_est_binaire_et_sans_conseil() -> None:
    dossier = dossier_de(regle())
    question = dossier.neutral_legal_question
    assert question.endswith("?")
    assert ", ou " in question
    for marque in ("il faut", "nous recommandons", "vous devriez", "il convient"):
        assert marque not in question.lower()


def test_la_question_nomme_les_dispositions_a_examiner() -> None:
    dossier = dossier_de(regle())
    assert "Article 16" in dossier.neutral_legal_question


# --------------------------------------------------------------------------- #
# Proposition mécanique
# --------------------------------------------------------------------------- #


def test_une_derogation_citant_larticle_donne_exception_likely() -> None:
    assert dossier_de(regle()).mechanical_proposal is PropositionMecanique.EXCEPTION_LIKELY


def test_un_acte_sans_derogation_donne_absence_dans_le_perimetre_examine() -> None:
    """Le vocabulaire dit « dans le périmètre examiné », pas « il n'y en a pas »."""
    dossier = dossier_de(regle(), {"12": ACTE["12"]}, "12")
    assert dossier.mechanical_proposal is (
        PropositionMecanique.NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE
    )
    assert "REVIEWED_SCOPE" in dossier.mechanical_proposal.value


def test_le_perimetre_a_attester_est_toujours_nomme() -> None:
    for articles in (ACTE, {"12": ACTE["12"]}):
        dossier = dossier_de(regle(), articles, "12")
        assert dossier.source_scope
        assert REGLE["source"]["text"] in dossier.source_scope


# --------------------------------------------------------------------------- #
# Regroupement des arbitrages
# --------------------------------------------------------------------------- #


def test_deux_regles_du_meme_acte_et_du_meme_blocage_partagent_un_dossier() -> None:
    """Le relecteur ne doit pas trancher trois fois la même chose."""
    a = dossier_de(regle(id="RULE-SYNTH-A"))
    b = dossier_de(regle(id="RULE-SYNTH-B"))
    assert a.review_cluster_id == b.review_cluster_id


def test_deux_regles_visant_des_dispositions_differentes_ne_sont_pas_groupees() -> None:
    a = dossier_de(regle(id="RULE-SYNTH-A"))
    b = dossier_de(regle(id="RULE-SYNTH-B"), {"12": ACTE["12"]}, "12")
    assert a.review_cluster_id != b.review_cluster_id


def test_le_regroupement_ne_fusionne_jamais_les_regles() -> None:
    a = dossier_de(regle(id="RULE-SYNTH-A"))
    b = dossier_de(regle(id="RULE-SYNTH-B"))
    assert a.rule_id != b.rule_id
    assert a.statement == b.statement  # même contenu, deux dossiers distincts


# --------------------------------------------------------------------------- #
# Impact sur le benchmark
# --------------------------------------------------------------------------- #


def test_chaque_dossier_dit_ce_que_chaque_issue_changerait() -> None:
    dossier = dossier_de(regle())
    assert dossier.if_exception_exists
    assert dossier.if_no_exception
    assert dossier.if_exception_exists != dossier.if_no_exception


# --------------------------------------------------------------------------- #
# Bordereau et file
# --------------------------------------------------------------------------- #


def test_le_bordereau_sort_avec_les_colonnes_du_relecteur_vides(tmp_path: Path) -> None:
    chemin = ecrire_bordereau([dossier_de(regle())], tmp_path / "b.csv")
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        ligne = next(csv.DictReader(flux, delimiter=";"))
    assert list(ligne) == list(COLONNES_BORDEREAU)
    for colonne in (
        "reviewer_decision", "reviewer_name", "review_date", "review_notes",
        "source_scope", "enonce_reformule", "exceptions_constatees",
    ):
        assert ligne[colonne] == "", colonne
    # Ce que la machine a préparé, en revanche, est là.
    assert ligne["neutral_legal_question"]
    assert ligne["dispositions_a_examiner"]
    assert ligne["source_scope_demande"]


def test_un_bordereau_vierge_ne_porte_aucune_decision(tmp_path: Path) -> None:
    chemin = ecrire_bordereau([dossier_de(regle())], tmp_path / "b.csv")
    assert lire_bordereau(chemin) == {}


def test_la_file_place_les_p0_avant_les_p1_puis_trie_par_domaine() -> None:
    critique = dossier_de(regle(id="RULE-SYNTH-P0", priority="CRITICAL"))
    moindre = dossier_de(regle(id="RULE-SYNTH-P1", priority="CRITICAL", domain="MIFID"))
    texte = file_de_revue([moindre, critique])

    # Même priorité : c'est alors le domaine puis l'identifiant qui ordonnent.
    assert texte.index("Domaine MIFID") < texte.index("Domaine SFDR")
    assert "P0 — REVIEW REQUIRED" in texte
    assert "aucun conseil juridique" in texte


def test_la_file_porte_toutes_les_rubriques_demandees() -> None:
    texte = file_de_revue([dossier_de(regle())])
    for rubrique in (
        "**RULE**", "**CURRENT STATEMENT**", "**PRIMARY SOURCE**",
        "**SUPPORTING PROVISION**", "TEXTUAL_FACTS", "INTERPRETIVE_QUESTION",
        "NEUTRAL_LEGAL_QUESTION", "mechanical_proposal", "if_exception_exists",
        "if_no_exception", "reviewer_decision", "PÉRIMÈTRE À ATTESTER",
    ):
        assert rubrique in texte, rubrique


def test_lavancement_compte_ce_qui_reste() -> None:
    dossiers = [dossier_de(regle(id="RULE-SYNTH-A"))]
    texte = avancement(dossiers, {}, {"validated": 12}, {"validated": 12})
    assert "P0 total     : 1" in texte
    assert "P0 reviewed  : 0" in texte
    assert "P0 remaining : 1" in texte
    assert "jamais `gold_ready` par elle-même" in texte


# --------------------------------------------------------------------------- #
# Réinjection des décisions
# --------------------------------------------------------------------------- #


def _bordereau_rempli(tmp_path: Path, **decision: str) -> Path:
    chemin = ecrire_bordereau([dossier_de(regle())], tmp_path / "b.csv")
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        lecteur = csv.DictReader(flux, delimiter=";")
        colonnes, lignes = lecteur.fieldnames, list(lecteur)
    lignes[0].update(decision)
    with chemin.open("w", encoding="utf-8-sig", newline="") as flux:
        graveur = csv.DictWriter(flux, fieldnames=colonnes, delimiter=";")
        graveur.writeheader()
        graveur.writerows(lignes)
    return chemin


def test_une_absence_sans_perimetre_est_refusee(tmp_path: Path) -> None:
    """Le cœur du §11 : le relecteur doit attester ce qu'il a examiné."""
    from scripts.preparer_revue import decisions_en_verifications

    chemin = _bordereau_rempli(
        tmp_path,
        reviewer_decision="NONE_IDENTIFIED",
        reviewer_name="Relecteur de test",
        review_date="2026-08-30",
    )
    with pytest.raises(VerificationInvalide, match="source_scope"):
        decisions_en_verifications(chemin)


def test_une_decision_humaine_ne_promeut_jamais_directement_en_validated(
    tmp_path: Path,
) -> None:
    """§14 : la décision lève un blocage, le calcul dit ce que la règle devient."""
    from scripts.preparer_revue import decisions_en_verifications

    chemin = _bordereau_rempli(
        tmp_path,
        reviewer_decision="NONE_IDENTIFIED",
        reviewer_name="Relecteur de test",
        review_date="2026-08-30",
        source_scope="Acte synthétique entier, version 2020-01-01",
    )
    [verification] = decisions_en_verifications(chemin)
    assert verification.target_status.value == "source_checked"
    assert verification.gold_ready is None


def test_une_absence_attestee_est_acceptee(tmp_path: Path) -> None:
    from scripts.preparer_revue import decisions_en_verifications

    chemin = _bordereau_rempli(
        tmp_path,
        reviewer_decision="NONE_IDENTIFIED",
        reviewer_name="Relecteur de test",
        review_date="2026-08-30",
        source_scope="Acte synthétique entier, version 2020-01-01",
        review_notes="Aucune dérogation trouvée hors article 16, déjà écartée.",
    )
    [verification] = decisions_en_verifications(chemin)
    assert verification.exceptions_status.value == "none_identified"
    assert verification.source_scope
    assert verification.verified_by == "Relecteur de test"


def test_une_reformulation_sans_enonce_est_refusee(tmp_path: Path) -> None:
    from scripts.preparer_revue import decisions_en_verifications

    chemin = _bordereau_rempli(
        tmp_path,
        reviewer_decision="RULE_REFORMULATED",
        reviewer_name="Relecteur de test",
        review_date="2026-08-30",
    )
    with pytest.raises(VerificationInvalide, match="sans énoncé corrigé"):
        decisions_en_verifications(chemin)


def test_une_decision_inconnue_arrete_le_lot(tmp_path: Path) -> None:
    from scripts.preparer_revue import decisions_en_verifications

    chemin = _bordereau_rempli(tmp_path, reviewer_decision="PEUT-ETRE")
    with pytest.raises(VerificationInvalide, match="inconnue"):
        decisions_en_verifications(chemin)


def test_une_demande_de_revue_supplementaire_ne_promeut_rien(tmp_path: Path) -> None:
    from scripts.preparer_revue import decisions_en_verifications

    chemin = _bordereau_rempli(
        tmp_path,
        reviewer_decision="REQUIRES_FURTHER_REVIEW",
        reviewer_name="Relecteur de test",
        review_date="2026-08-30",
        review_notes="Il faut consulter la version consolidée.",
    )
    [verification] = decisions_en_verifications(chemin)
    assert verification.verdict.value == "non_verifiable"
    assert verification.target_status.value == "draft"


def test_les_quatre_decisions_sont_couvertes() -> None:
    from src.bench.rapport_revue import CORRESPONDANCE_DECISIONS

    assert set(CORRESPONDANCE_DECISIONS) == set(DecisionRevue)


# --------------------------------------------------------------------------- #
# Le pack livré
# --------------------------------------------------------------------------- #


def test_le_bordereau_livre_ne_porte_aucune_decision() -> None:
    """§15 : la phase s'arrête à la préparation."""
    chemin = Path("data/verification/dossier-revue-p0p1.csv")
    if not chemin.is_file():
        pytest.skip("bordereau non généré")
    assert lire_bordereau(chemin) == {}


def test_le_pack_livre_ne_couvre_que_les_p0_et_p1() -> None:
    chemin = Path("data/verification/dossier-revue-p0p1.csv")
    if not chemin.is_file():
        pytest.skip("bordereau non généré")
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=";"))
    assert {l["priorite"] for l in lignes} <= {"P0", "P1"}
    assert all(l["neutral_legal_question"].endswith("?") for l in lignes)
    assert all(l["source_scope_demande"] for l in lignes)
