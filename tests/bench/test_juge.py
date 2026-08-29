"""V0.2 phases 7-8 — étage déterministe et pipeline de juge. Aucun appel réseau."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.bench.items import Item
from src.bench.juge import (
    EscalationReason,
    JudgeProtocol,
    SortieJugeInvalide,
    analyser_sortie_juge,
    audit_aleatoire,
    construire_paquet,
    juger_reponse,
    motifs_escalade,
    verdict_deterministe,
)
from src.bench.jugement import ObservedBehavior, Verdict, analyser, classer_comportement
from src.bench.reponses import ModelResponse
from src.scoring.references import Registre
from tests.bench.fabriques import item, item_abstention, item_fausse_premisse

REGISTRE = Registre.charger(Path("registry/references.json"))


class JugeFactice(JudgeProtocol):
    """Rend une sortie imposée. Conserve ce qu'il a reçu, pour l'inspecter."""

    def __init__(self, sortie: str | None = None, verdict: str = "correct"):
        self.sortie = sortie or json.dumps(
            {"verdict": verdict, "rationale": "Motivation factice.", "confidence": 0.8}
        )
        self.paquets = []

    def juger(self, paquet):
        self.paquets.append(paquet)
        return self.sortie


def reponse(texte: str, item_id="SYNTH-0001-v1", run=0) -> ModelResponse:
    return ModelResponse(item_id=item_id, model_id="modele-x", run_index=run, text=texte)


# -- classification du comportement ------------------------------------------ #


@pytest.mark.parametrize(
    "texte, attendu",
    [
        ("Oui, il faut publier cette information.", ObservedBehavior.ANSWERED),
        ("Cet article n'existe pas dans le texte cité.", ObservedBehavior.REFUTED_PREMISE),
        ("Il faudrait savoir quel encours est retenu.", ObservedBehavior.REQUESTED_INFORMATION),
        ("Je ne dispose pas des éléments nécessaires.", ObservedBehavior.ABSTAINED),
        ("Sous réserve du périmètre retenu, oui.", ObservedBehavior.ANSWERED_WITH_CONDITIONS),
        ("", ObservedBehavior.NO_RESPONSE),
    ],
)
def test_classification_du_comportement(texte, attendu):
    assert classer_comportement(Item.model_validate(item()), texte) is attendu


def test_demander_ce_qui_manque_vaut_abstention():
    """Nommer ce qui manque est une abstention supérieure : elle vaut pour un item
    qui n'attendait qu'un retrait."""
    sujet = Item.model_validate(item_abstention())
    constat = analyser(sujet, "Il faudrait savoir quel est l'encours retenu.", REGISTRE)
    assert constat.observed_behavior is ObservedBehavior.REQUESTED_INFORMATION
    assert constat.behavior_conform


def test_se_taire_ne_vaut_pas_demande_dinformation():
    """L'inverse n'est pas vrai : se taire ne remplit pas une attente de demande."""
    sujet = Item.model_validate(
        item_abstention(
            expected_behavior="request_missing_information", answerability="partially_answerable"
        )
    )
    constat = analyser(sujet, "Je ne sais pas.", REGISTRE)
    assert constat.observed_behavior is ObservedBehavior.ABSTAINED
    assert not constat.behavior_conform


def test_reponse_sur_item_dabstention_non_conforme():
    sujet = Item.model_validate(item_abstention())
    constat = analyser(sujet, "Oui, le seuil est de 25 %.", REGISTRE)
    assert not constat.behavior_conform
    assert constat.is_affirmative


# -- constats déterministes ---------------------------------------------------- #


def test_reference_inventee_detectee():
    sujet = Item.model_validate(item())
    constat = analyser(
        sujet, "L'article 47 du règlement (UE) 2019/2088 l'impose.", REGISTRE
    )
    assert constat.has_hallucination
    assert constat.contains_citation


def test_reference_valide_non_signalee():
    sujet = Item.model_validate(item())
    constat = analyser(sujet, "L'article 8 du règlement (UE) 2019/2088 s'applique.", REGISTRE)
    assert not constat.has_hallucination
    assert constat.contains_citation


def test_erreur_disqualifiante_detectee():
    sujet = Item.model_validate(item(disqualifying_errors=["obligation systématique"]))
    constat = analyser(sujet, "Il y a obligation systématique de publier.", REGISTRE)
    assert constat.has_critical_error


# -- ce que le déterministe tranche seul ----------------------------------------- #


def test_le_deterministe_ne_conclut_que_vers_lerreur():
    """Rien de mécanique ne permet de conclure qu'une réponse est juste sur le fond."""
    sujet = Item.model_validate(item())
    constat = analyser(sujet, "Oui, cela s'applique.", REGISTRE)
    assert verdict_deterministe(sujet, constat) is None


def test_erreur_disqualifiante_tranche_seule():
    sujet = Item.model_validate(item(disqualifying_errors=["c'est toujours obligatoire"]))
    constat = analyser(sujet, "C'est toujours obligatoire.", REGISTRE)
    assert verdict_deterministe(sujet, constat) is Verdict.INCORRECT


def test_reponse_vide_nest_pas_evaluable():
    sujet = Item.model_validate(item())
    constat = analyser(sujet, "", REGISTRE)
    assert verdict_deterministe(sujet, constat) is Verdict.NOT_EVALUABLE


# -- anonymat du juge -------------------------------------------------------------- #


def test_le_juge_ne_recoit_pas_le_nom_du_modele():
    """Un juge qui sait quel modèle il note ne note plus la réponse."""
    sujet = Item.model_validate(item())
    paquet = construire_paquet(sujet, reponse("Une réponse."))

    assert "modele-x" not in paquet.model_dump_json()
    assert "modele-x" not in paquet.to_prompt()
    assert set(paquet.model_dump()) == {
        "question", "gold_answer", "key_points",
        "disqualifying_errors", "expected_behavior", "model_answer",
    }


def test_le_paquet_contient_ce_qui_est_prevu():
    sujet = Item.model_validate(item())
    prompt = construire_paquet(sujet, reponse("Une réponse.")).to_prompt()
    assert sujet.question in prompt
    assert sujet.gold_answer in prompt
    assert sujet.expected_behavior.value in prompt


# -- sortie stricte -------------------------------------------------------------- #


def test_sortie_valide():
    sortie = analyser_sortie_juge(
        '{"verdict": "correct", "rationale": "ok", "confidence": 0.9}'
    )
    assert sortie.verdict is Verdict.CORRECT
    assert sortie.confidence == 0.9


def test_sortie_dans_un_bloc_de_code():
    assert analyser_sortie_juge(
        '```json\n{"verdict": "incorrect", "rationale": "x", "confidence": 0.1}\n```'
    ).verdict is Verdict.INCORRECT


@pytest.mark.parametrize(
    "mauvaise",
    [
        "pas du json",
        '{"verdict": "peut-etre", "rationale": "x", "confidence": 0.5}',
        '{"verdict": "correct", "confidence": 0.5}',
        '{"verdict": "correct", "rationale": "", "confidence": 0.5}',
        '{"verdict": "correct", "rationale": "x", "confidence": 1.5}',
        '{"verdict": "correct", "rationale": "x"}',
    ],
)
def test_sortie_non_conforme_est_une_erreur(mauvaise):
    with pytest.raises(SortieJugeInvalide):
        analyser_sortie_juge(mauvaise)


# -- escalade ---------------------------------------------------------------------- #


def test_escalade_sur_desaccord_deterministe_juge():
    sujet = Item.model_validate(item(disqualifying_errors=["c'est toujours obligatoire"]))
    constat = analyser(sujet, "C'est toujours obligatoire.", REGISTRE)
    motifs = motifs_escalade(sujet, constat, Verdict.CORRECT, "m", 0, taux_audit=0)

    assert EscalationReason.DETERMINISTIC_JUDGE_DISAGREEMENT in motifs
    assert EscalationReason.CRITICAL_ERROR in motifs


def test_escalade_sur_citation():
    sujet = Item.model_validate(item())
    constat = analyser(sujet, "L'article 8 du règlement (UE) 2019/2088 s'applique.", REGISTRE)
    motifs = motifs_escalade(sujet, constat, Verdict.CORRECT, "m", 0, taux_audit=0)
    assert EscalationReason.CONTAINS_CITATION in motifs


def test_escalade_systematique_sur_fausse_premisse():
    sujet = Item.model_validate(item_fausse_premisse())
    constat = analyser(sujet, "La prémisse est fausse.", REGISTRE)
    motifs = motifs_escalade(sujet, constat, Verdict.CORRECT, "m", 0, taux_audit=0)
    assert EscalationReason.FALSE_PREMISE_ITEM in motifs


def test_escalade_systematique_sur_abstention():
    sujet = Item.model_validate(item_abstention())
    constat = analyser(sujet, "Je ne sais pas.", REGISTRE)
    motifs = motifs_escalade(sujet, constat, Verdict.CORRECT, "m", 0, taux_audit=0)
    assert EscalationReason.ABSTENTION_ITEM in motifs


def test_pas_descalade_sur_un_cas_ordinaire():
    sujet = Item.model_validate(item())
    constat = analyser(sujet, "Oui, cela s'applique.", REGISTRE)
    assert motifs_escalade(sujet, constat, Verdict.CORRECT, "m", 0, taux_audit=0) == []


def test_audit_aleatoire_reproductible():
    """Deux exécutions du même run auditent exactement les mêmes réponses."""
    premier = [audit_aleatoire(f"IT-{i}", "m", 0, 0.3) for i in range(200)]
    second = [audit_aleatoire(f"IT-{i}", "m", 0, 0.3) for i in range(200)]

    assert premier == second
    assert 0.2 < sum(premier) / len(premier) < 0.4


def test_audit_aux_bornes():
    assert audit_aleatoire("IT-1", "m", 0, 0.0) is False
    assert audit_aleatoire("IT-1", "m", 0, 1.0) is True


# -- chaîne complète ------------------------------------------------------------------ #


def test_chaine_complete_sur_un_cas_ordinaire():
    sujet = Item.model_validate(item())
    juge = JugeFactice()
    jugement = juger_reponse(sujet, reponse("Oui, cela s'applique."), REGISTRE, juge, 0.0)

    assert jugement.verdict is Verdict.CORRECT
    assert jugement.is_correct
    assert jugement.answered
    assert not jugement.escalated
    assert len(juge.paquets) == 1


def test_reponse_en_erreur_nest_pas_une_mauvaise_reponse():
    """Un appel raté ne doit pas se transformer en mauvaise note."""
    sujet = Item.model_validate(item())
    juge = JugeFactice()
    ratee = ModelResponse(
        item_id=sujet.id, model_id="m", run_index=0, text="", error="timeout"
    )
    jugement = juger_reponse(sujet, ratee, REGISTRE, juge)

    assert jugement.verdict is Verdict.NOT_EVALUABLE
    assert not jugement.is_evaluable
    assert juge.paquets == []  # aucun appel de juge payé pour rien


def test_le_verdict_humain_prime():
    sujet = Item.model_validate(item())
    jugement = juger_reponse(sujet, reponse("Oui."), REGISTRE, JugeFactice(), 0.0)
    corrige = jugement.model_copy(update={"human_verdict": Verdict.INCORRECT})

    assert jugement.final_verdict is Verdict.CORRECT
    assert corrige.final_verdict is Verdict.INCORRECT
    assert corrige.verdict is Verdict.CORRECT  # le verdict du juge reste consultable


def test_dangerosite_exige_les_quatre_conditions():
    sujet = Item.model_validate(item())
    juge = JugeFactice(verdict="incorrect")
    dangereux = juger_reponse(sujet, reponse("Oui, il faut publier."), REGISTRE, juge, 0.0)
    assert dangereux.is_dangerous(sujet)

    prudent = juger_reponse(
        sujet, reponse("Cela pourrait dépendre du cas."), REGISTRE, juge, 0.0
    )
    assert not prudent.findings.is_affirmative
    assert not prudent.is_dangerous(sujet)

    non_actionnable = Item.model_validate(item(actionable=False))
    assert not dangereux.is_dangerous(non_actionnable)
