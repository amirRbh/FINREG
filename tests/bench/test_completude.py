"""Tests de l'audit de complétude et de gold-readiness.

Deux invariants portent cette phase, et les tests les tiennent tous les deux :

1. **Ne rien trouver n'est pas trouver qu'il n'y a rien.** Un article sans
   dérogation apparente ne donne jamais `none_identified` : il donne
   `requires_human_review`. Une recherche de motifs ne conclut pas à l'absence.
2. **Validée ne veut pas dire utilisable.** Une règle peut être juridiquement
   irréprochable et trop abstraite pour porter une réponse de référence. C'est
   `gold_ready` qui le dit, et c'est ce qui empêche un faux sentiment de
   complétude.

Aucun accès réseau : les textes sont synthétiques et fournis en dur.
"""

from __future__ import annotations

import copy
import csv
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from src.bench.completude import (
    Structure,
    analyser,
    evaluer_gold_readiness,
    evaluer_temporalite,
    extraire_exceptions,
    renvois_de,
    structures_presentes,
)
from src.bench.rapport_completude import (
    COLONNES_GOLD,
    ecrire_matrice_gold,
    exporter_dossier_completude,
    rapport_markdown,
)
from src.bench.regles import Rule
from src.bench.rulebook import ExceptionsStatus, RuleStatus
from src.bench.verification import VerificationInvalide, lire_dossier
from tests.bench.fabriques import REGLE

#: Un article qui déroge sans jamais employer le mot « exception ».
ARTICLE_AVEC_DEROGATION = (
    "Article 12 Obligations de publication. 1. Les entités assujetties publient "
    "annuellement un rapport détaillant leur dispositif, dans un délai de 30 jours "
    "à compter de la clôture. 2. Par dérogation au paragraphe 1, les entités dont "
    "le total de bilan est inférieur à 20 000 000 EUR publient ce rapport tous les "
    "deux ans. 3. Le paragraphe 1 ne s'applique pas aux entités visées à "
    "l'article 4, qui relèvent d'un régime particulier. 4. Les clients "
    "professionnels ne sont pas tenus de recevoir ce rapport."
)

#: Le même sujet, mais sans aucune structure limitante.
ARTICLE_SANS_DEROGATION = (
    "Article 3 Champ d'application. Les entités assujetties conservent les "
    "documents mentionnés au présent règlement et les tiennent à la disposition de "
    "l'autorité compétente. Elles désignent un responsable de cette conservation."
)


def regle(**modifications: Any) -> Rule:
    """Règle synthétique en `source_checked`, prête à être examinée."""
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "status": "source_checked",
            "verification_method": "primary_text_fetched",
            "gold_ready": False,
            "gold_ready_reason": "",
            "statement": (
                "Les entités assujetties publient annuellement un rapport détaillant "
                "leur dispositif, dans un délai de 30 jours à compter de la clôture."
            ),
        }
    )
    brut.update(modifications)
    return Rule.model_validate(brut)


# --------------------------------------------------------------------------- #
# Structure juridique
# --------------------------------------------------------------------------- #


def test_on_cherche_la_structure_pas_le_mot_exception() -> None:
    """« Par dérogation », « ne s'applique pas », « ne sont pas tenus » : aucun n'est « exception »."""
    trouvees = set(structures_presentes(ARTICLE_AVEC_DEROGATION))
    assert Structure.DEROGATION in trouvees
    assert Structure.EXCLUSION in trouvees
    assert Structure.EXEMPTION in trouvees
    assert Structure.SEUIL in trouvees
    assert Structure.DELAI in trouvees
    assert Structure.REGIME_PARTICULIER in trouvees
    assert "exception" not in ARTICLE_AVEC_DEROGATION.lower()


def test_les_exceptions_sont_recopiees_pas_reformulees() -> None:
    """Une exception reformulée est une exception interprétée."""
    extraits = extraire_exceptions(ARTICLE_AVEC_DEROGATION)
    assert extraits
    for extrait in extraits:
        assert extrait in ARTICLE_AVEC_DEROGATION


def test_les_renvois_sont_releves() -> None:
    assert "4" in renvois_de(ARTICLE_AVEC_DEROGATION)


def test_une_presomption_est_un_allegement() -> None:
    """Le texte ne s'annonce pas comme une exception, et en est une."""
    presomption = (
        "L'entreprise d'investissement est autorisée à présumer que le client "
        "professionnel possède l'expérience requise."
    )
    assert Structure.EXEMPTION in structures_presentes(presomption)


# --------------------------------------------------------------------------- #
# Le point dur : ne rien trouver n'est pas trouver qu'il n'y a rien
# --------------------------------------------------------------------------- #


def test_aucune_derogation_trouvee_ne_donne_jamais_none_identified() -> None:
    constat = analyser(regle(), ARTICLE_SANS_DEROGATION, ARTICLE_SANS_DEROGATION)
    assert constat.exceptions_status is ExceptionsStatus.REQUIRES_HUMAN_REVIEW
    assert constat.exceptions_status is not ExceptionsStatus.NONE_IDENTIFIED
    assert any("ne prouve pas" in m for m in constat.motifs)


def test_none_identified_nest_jamais_attribue_par_lanalyse() -> None:
    """Sur aucun texte : conclure à l'absence demande un juriste."""
    for texte in (ARTICLE_AVEC_DEROGATION, ARTICLE_SANS_DEROGATION, "Article 1 Objet."):
        constat = analyser(regle(), texte, texte)
        assert constat.exceptions_status is not ExceptionsStatus.NONE_IDENTIFIED


def test_sans_texte_lanalyse_ne_conclut_rien() -> None:
    """Une source hors d'atteinte laisse les exceptions inconnues, pas absentes."""
    constat = analyser(regle(), "", "")
    assert constat.exceptions_status is ExceptionsStatus.UNKNOWN
    assert not constat.criteres


def test_des_derogations_trouvees_et_recopiees_sont_incorporees() -> None:
    constat = analyser(regle(), ARTICLE_AVEC_DEROGATION, ARTICLE_AVEC_DEROGATION)
    assert constat.exceptions_status is ExceptionsStatus.IDENTIFIED_AND_INCORPORATED
    assert constat.exceptions_extraites


# --------------------------------------------------------------------------- #
# Gold-readiness
# --------------------------------------------------------------------------- #


def test_un_enonce_qui_decrit_le_texte_nest_pas_gold_ready() -> None:
    """L'archétype : exact, et impossible à transformer en réponse de référence."""
    abstraite = regle(
        statement=(
            "Le règlement précise les modalités de l'évaluation, notamment "
            "l'étendue des diligences à accomplir."
        )
    )
    pret, motif = evaluer_gold_readiness(abstraite)
    assert not pret
    assert "décrit le texte au lieu de le dire" in motif


def test_un_enonce_porteur_dun_fait_est_gold_ready() -> None:
    pret, motif = evaluer_gold_readiness(regle())
    assert pret
    assert motif.strip()


def test_un_enonce_sans_rien_de_verifiable_nest_pas_gold_ready() -> None:
    vague = regle(
        statement=(
            "Ce texte européen s'inscrit dans une démarche générale d'harmonisation "
            "entre les différents régimes applicables au secteur financier européen."
        )
    )
    pret, motif = evaluer_gold_readiness(vague)
    assert not pret
    assert "rien de vérifiable" in motif


def test_gold_ready_se_motive_toujours() -> None:
    """Une case cochée sans motif ne se conteste pas."""
    with pytest.raises(ValidationError, match="motiver son gold_ready"):
        Rule.model_validate(
            {
                **copy.deepcopy(REGLE),
                "status": "validated",
                "verification_method": "primary_text_review",
                "gold_ready": True,
                "gold_ready_reason": "",
            }
        )


def test_validee_et_inutilisable_est_un_etat_legitime() -> None:
    """Le cœur de la phase : les deux axes sont indépendants."""
    validee = Rule.model_validate(
        {
            **copy.deepcopy(REGLE),
            "status": "validated",
            "verification_method": "primary_text_review",
            "gold_ready": False,
            "gold_ready_reason": "énoncé trop abstrait pour porter une réponse",
        }
    )
    assert validee.status is RuleStatus.VALIDATED
    assert not validee.is_usable


# --------------------------------------------------------------------------- #
# Temporalité et critères
# --------------------------------------------------------------------------- #


def test_une_reforme_proposee_nest_jamais_etablie() -> None:
    statut, etabli = evaluer_temporalite(regle(regulatory_status="proposed"))
    assert statut == "PROPOSED"
    assert not etabli


def test_une_abrogation_sans_date_de_fin_nest_pas_etablie() -> None:
    abrogee = regle(regulatory_status="repealed", valid_until="2024-01-01")
    statut, etabli = evaluer_temporalite(abrogee)
    assert statut == "REPEALED"
    assert etabli


def test_les_huit_criteres_sont_nommes() -> None:
    constat = analyser(
        regle(), ARTICLE_AVEC_DEROGATION, ARTICLE_AVEC_DEROGATION,
        article_verifie=True, concordance=0.9,
    )
    assert len(constat.criteres) == 8
    assert set(constat.criteres) == {
        "source_primaire_verifiee",
        "article_verifie",
        "enonce_fidele",
        "exceptions_recherchees",
        "conditions_capturees",
        "temporalite_etablie",
        "renvois_verifies",
        "sans_ambiguite",
    }


def test_un_seul_critere_manquant_refuse_la_validation() -> None:
    constat = analyser(
        regle(), ARTICLE_AVEC_DEROGATION, ARTICLE_AVEC_DEROGATION,
        article_verifie=True, concordance=0.1,
    )
    assert constat.statut_propose is not RuleStatus.VALIDATED
    assert "enonce_fidele" in constat.criteres_manquants


def test_une_regle_draft_ne_devient_pas_validee_par_cette_passe() -> None:
    """La complétude ne remplace pas la vérification de source."""
    brouillon = regle(
        status="draft",
        verification_method="model_knowledge_unverified",
        source={**REGLE["source"], "verified_by": "", "verification_date": None},
    )
    constat = analyser(
        brouillon, ARTICLE_AVEC_DEROGATION, ARTICLE_AVEC_DEROGATION,
        article_verifie=True, concordance=0.9,
    )
    assert constat.statut_propose is RuleStatus.DRAFT


def test_une_regle_critical_subit_un_controle_renforce() -> None:
    """§9 : exceptions **et** renvois, sinon pas de validation."""
    critique = regle(priority="CRITICAL")
    constat = analyser(
        critique, ARTICLE_SANS_DEROGATION, ARTICLE_SANS_DEROGATION,
        article_verifie=True, concordance=0.9,
    )
    assert constat.statut_propose is not RuleStatus.VALIDATED


def test_un_enonce_non_corrobore_demande_un_arbitrage_humain() -> None:
    constat = analyser(
        regle(), ARTICLE_AVEC_DEROGATION, ARTICLE_AVEC_DEROGATION,
        article_verifie=True, concordance=0.05,
    )
    assert constat.statut_propose is RuleStatus.REQUIRES_HUMAN_REVIEW


# --------------------------------------------------------------------------- #
# Artefacts
# --------------------------------------------------------------------------- #


def _constat_validable():
    sujet = regle(
        gold_ready=False,
        gold_ready_reason="",
        regulatory_status="in_force",
        time_sensitive=False,
    )
    return sujet, analyser(
        sujet, ARTICLE_AVEC_DEROGATION, ARTICLE_AVEC_DEROGATION,
        article_verifie=True, concordance=0.9,
    )


def test_la_matrice_porte_les_colonnes_demandees(tmp_path: Path) -> None:
    sujet, constat = _constat_validable()
    sortie = tmp_path / "gold.csv"
    ecrire_matrice_gold([constat], [sujet], sortie)

    assert sortie.read_bytes().startswith(b"\xef\xbb\xbf")
    with sortie.open(encoding="utf-8-sig", newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=";"))
    assert list(lignes[0]) == list(COLONNES_GOLD)
    assert lignes[0]["ID"] == sujet.id
    assert lignes[0]["reason"]


def test_le_dossier_de_completude_est_refuse_sans_signature(tmp_path: Path) -> None:
    """Même verrou que l'audit de sources : la machine propose, elle ne signe pas."""
    sujet, constat = _constat_validable()
    assert constat.statut_propose is RuleStatus.VALIDATED

    dossier = exporter_dossier_completude([constat], [sujet], tmp_path / "d.csv")
    with pytest.raises(VerificationInvalide) as echec:
        lire_dossier(dossier)
    assert any("vérificateur nommé" in e for e in echec.value.erreurs)


def test_le_dossier_porte_les_exceptions_recopiees(tmp_path: Path) -> None:
    sujet, constat = _constat_validable()
    dossier = exporter_dossier_completude([constat], [sujet], tmp_path / "d.csv")
    with dossier.open(encoding="utf-8-sig", newline="") as flux:
        ligne = next(csv.DictReader(flux, delimiter=";"))
    assert ligne["exceptions_statut"] == "identified_and_incorporated"
    assert ligne["exceptions_constatees"]
    assert ligne["gold_ready"] in ("oui", "non")
    assert ligne["verifie_par"] == ""


def test_le_rapport_distingue_validee_et_utilisable() -> None:
    sujet, constat = _constat_validable()
    texte = rapport_markdown([constat], [sujet])
    assert "faux sentiment de complétude" in texte
    assert "gold_ready" in texte
    assert "n'est jamais attribué par cette passe" in texte
