"""V0.2 — validation du schéma d'item. Fixtures synthétiques uniquement."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.bench.items import Item
from src.bench.vocabulaires import (
    Answerability,
    ExpectedBehavior,
    QuestionType,
    ReasoningTrap,
    ValidationStatus,
)
from tests.bench.fabriques import (
    CHECKLIST_COMPLETE,
    item,
    item_abstention,
    item_fausse_premisse,
    item_valide,
)


def refuse(donnees: dict, fragment: str) -> None:
    with pytest.raises(ValidationError) as exc:
        Item.model_validate(donnees)
    assert fragment in str(exc.value), str(exc.value)


# -- identité et rattachement ---------------------------------------------- #


def test_identifiant_porte_la_version():
    assert Item.model_validate(item(version=1)).id == "SYNTH-0001-v1"
    assert Item.model_validate(item(version=3, supersedes="SYNTH-0001-v2")).id == "SYNTH-0001-v3"


def test_item_sans_regle_refuse():
    """Une question n'existe jamais sans rattachement à une règle."""
    refuse(item(rule_ids=[]), "rule_ids")


def test_champ_inconnu_refuse():
    refuse(item(commentaire="note"), "commentaire")


# -- cohérence type / comportement / répondabilité --------------------------- #


@pytest.mark.parametrize(
    "question_type, expected_behavior",
    [
        ("false_premise", "answer"),
        ("calibrated_abstention", "answer"),
        ("fact", "refute_premise"),
        ("fact", "abstain"),
        ("qualification", "calculate"),
    ],
)
def test_comportement_incompatible_avec_le_type(question_type, expected_behavior):
    refuse(
        item(question_type=question_type, expected_behavior=expected_behavior),
        "incompatible avec question_type",
    )


def test_abstention_exige_une_question_sans_reponse():
    """S'abstenir sur une question répondable serait une sur-abstention, pas un gold."""
    refuse(
        item_abstention(answerability="answerable"),
        "incompatible avec expected_behavior",
    )


def test_repondre_exige_une_question_repondable():
    refuse(item(answerability="unanswerable"), "incompatible avec expected_behavior")


# -- abstention ------------------------------------------------------------- #


def test_abstention_exige_de_dire_ce_qui_manque():
    donnees = item_abstention()
    donnees.pop("abstention_requirements")
    refuse(donnees, "exige abstention_requirements")


def test_exigences_dabstention_hors_contexte_refusees():
    refuse(
        item(abstention_requirements={"missing_information": ["x"]}),
        "n'a de sens que pour un comportement",
    )


def test_exigences_dabstention_non_vides():
    refuse(item_abstention(abstention_requirements={"missing_information": []}), "missing_information")


def test_abstention_valide_nomme_les_manques():
    sujet = Item.model_validate(item_abstention())
    assert sujet.abstention_requirements is not None
    assert len(sujet.abstention_requirements.missing_information) == 2
    assert sujet.abstention_requirements.conditional_conclusion_expected is True


# -- fausse prémisse et reframe ---------------------------------------------- #


def test_fausse_premisse_exige_un_piege_nomme():
    refuse(
        item(question_type="false_premise", expected_behavior="refute_premise",
             reasoning_trap="NONE"),
        "exige un reasoning_trap",
    )


def test_jumeau_a_vraie_premisse_exige_aussi_un_piege():
    """Le dual doit ressembler à un piège, sinon il ne teste pas la sur-réfutation."""
    refuse(
        item(question_type="true_premise_adversarial", expected_behavior="answer",
             reasoning_trap="NONE"),
        "exige un reasoning_trap",
    )


def test_reframe_reserve_aux_fausses_premisses():
    refuse(item(reframe_required=True), "ne s'applique qu'à une fausse prémisse")


def test_reframe_exige_de_dire_quoi_retablir():
    refuse(item_fausse_premisse(reframe_expectation=""), "reframe_expectation")


# -- vérification négative ---------------------------------------------------- #


@pytest.mark.parametrize("piege", ["FALSE_ARTICLE", "FALSE_THRESHOLD", "NEGATIVE_ASSERTION"])
def test_piege_a_disposition_inexistante_exige_negative_claim(piege):
    refuse(
        item_fausse_premisse(reasoning_trap=piege, negative_claim=False,
                             negative_claim_verification=None),
        "negative_claim doit valoir true",
    )


def test_negative_claim_exige_son_attestation():
    refuse(
        item_fausse_premisse(negative_claim_verification=None),
        "exige negative_claim_verification",
    )


def test_attestation_sans_negative_claim_refusee():
    donnees = item_fausse_premisse(reasoning_trap="SCOPE_CONFUSION", negative_claim=False)
    refuse(donnees, "sans negative_claim")


def test_fausse_premisse_valide_porte_son_attestation():
    sujet = Item.model_validate(item_fausse_premisse())
    assert sujet.question_type is QuestionType.FALSE_PREMISE
    assert sujet.reasoning_trap is ReasoningTrap.FALSE_ARTICLE
    assert sujet.negative_claim_verification is not None
    assert sujet.negative_claim_verification.searched_in
    assert sujet.reframe_required is True


def test_la_fausse_premisse_reste_sourcee():
    """Même une fausse prémisse porte une source primaire : il faut montrer le vrai texte."""
    sujet = Item.model_validate(item_fausse_premisse())
    assert sujet.source.is_verified


# -- versionnement ------------------------------------------------------------ #


def test_version_superieure_exige_de_nommer_la_precedente():
    refuse(item(version=2), "supersedes")


def test_version_un_ne_supersede_rien():
    refuse(item(version=1, supersedes="SYNTH-0001-v0"), "n'a pas de sens")


def test_un_item_ne_se_supersede_pas_lui_meme():
    refuse(item(version=2, supersedes="SYNTH-0001-v2"), "lui-même")


# -- ancrage temporel --------------------------------------------------------- #


def test_fin_de_validite_anterieure_au_debut_refusee():
    refuse(item(valid_from="2020-01-01", valid_until="2019-01-01"), "antérieur à valid_from")


def test_evaluation_avant_entree_en_vigueur_refusee():
    refuse(item(valid_from="2026-01-01", assessment_date="2020-01-01"), "précède valid_from")


def test_evaluation_apres_abrogation_refusee():
    refuse(
        item(regulatory_status="repealed", valid_until="2024-01-01",
             assessment_date="2026-01-01"),
        "dépasse valid_until",
    )


def test_abrogation_exige_une_date_de_fin():
    refuse(item(regulatory_status="repealed"), "exige une date valid_until")


# -- cycle de vie -------------------------------------------------------------- #


def test_validated_exige_la_grille_complete():
    incomplete = dict(CHECKLIST_COMPLETE, source_verified=False)
    refuse(item(status="validated", checklist=incomplete), "source_verified")


def test_validated_exige_un_relecteur_nomme():
    sans_relecteur = dict(CHECKLIST_COMPLETE, reviewed_by="")
    refuse(item(status="validated", checklist=sans_relecteur), "grille complète")


def test_validated_exige_une_source_verifiee():
    source = dict(item()["source"], verified_by="", verification_date=None)
    refuse(item(status="validated", checklist=CHECKLIST_COMPLETE, source=source),
           "source primaire vérifiée")


def test_published_impossible_en_prive():
    refuse(item_valide(corpus="private", status="published"), "inapplicable au corpus")


def test_locked_impossible_en_public():
    refuse(item_valide(status="locked"), "inapplicable au corpus")


def test_draft_nexige_rien():
    """On doit pouvoir déposer un brouillon non vérifié : c'est le point de départ."""
    source = dict(item()["source"], verified_by="", verification_date=None)
    sujet = Item.model_validate(item(source=source))
    assert sujet.status is ValidationStatus.DRAFT
    assert not sujet.is_gold


# -- jumeaux -------------------------------------------------------------------- #


def test_groupe_sans_role_refuse():
    refuse(item(twin_group_id="TWIN-SYNTH-001"), "vont ensemble")


def test_role_sans_groupe_refuse():
    refuse(item(twin_role="true_premise"), "vont ensemble")


def test_role_incompatible_avec_le_type():
    refuse(
        item(twin_group_id="TWIN-SYNTH-001", twin_role="false_premise"),
        "incompatible avec question_type",
    )


# -- traces sûres ----------------------------------------------------------------- #


def test_la_forme_journalisable_ne_contient_aucun_contenu():
    sujet = Item.model_validate(item(corpus="private", question="SECRET-SYNTH"))
    trace = sujet.redacted()

    assert trace["id"] == "SYNTH-0001-v1"
    assert "SECRET-SYNTH" not in str(trace)
    assert sujet.gold_answer not in str(trace)
    assert set(trace) == {"id", "corpus", "domain", "question_type", "expected_behavior", "status"}


def test_enums_exposes():
    sujet = Item.model_validate(item())
    assert sujet.answerability is Answerability.ANSWERABLE
    assert sujet.expected_behavior is ExpectedBehavior.ANSWER
