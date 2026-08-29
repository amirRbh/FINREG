"""Tests du Question Family Map (phase 7).

Le contrôle central est `test_une_regle_draft_ne_produit_aucune_famille_finalisable` :
c'est le verrou du Rulebook transporté à la carte. Une famille peut être
excellente et néanmoins interdite tant que sa règle n'a pas été confrontée à son
texte primaire.

Toutes les règles utilisées ici sont synthétiques (`RULE-SYNTH-*`,
`example.invalid`) : aucune information juridique réelle n'entre dans un test.
"""

from __future__ import annotations

import copy
import csv
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from src.bench.carte_familles import (
    RENDEMENT_PAR_SCORE,
    concept_teste,
    deriver_familles,
    eligibilite_regle,
    faisabilite_distribution,
    groupe_redondance,
    lacunes,
    matrice_couverture,
    potentiel_complet,
    redondances,
)
from src.bench.familles import (
    CODES_FAMILLES,
    CandidateFamily,
    CandidateFamilyStatus,
    FamilyKind,
    ORDRE_FAMILLES,
    SCORE_RETENU,
)
from src.bench.qc_familles import (
    COLONNES_MATRICE,
    charger_familles,
    construire_manifeste,
    controler,
    ecrire_carte,
    ecrire_matrice,
    erreurs,
    rapport_markdown,
)
from src.bench.qc_rulebook import charger_rulebook
from src.bench.regles import Rule
from src.bench.rulebook import RuleStatus
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV
from src.bench.vocabulaires import Domain, QuestionType, ReasoningTrap
from tests.bench.fabriques import REGLE


def regle(**modifications: Any) -> Rule:
    """Une règle synthétique, validée par défaut, modifiable champ par champ."""
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "operational_rule": "Traduction opérationnelle synthétique.",
            "exceptions_status": "none_identified",
            "common_confusions": ["Confusion synthétique 1"],
            "reasoning_traps": ["CONCEPT_CONFLATION"],
        }
    )
    brut.update(modifications)
    return Rule.model_validate(brut)


def famille_de(regles: list[Rule], rule_id: str, kind: FamilyKind) -> CandidateFamily | None:
    for candidate in deriver_familles(regles):
        if candidate.rule_id == rule_id and candidate.family_kind is kind:
            return candidate
    return None


# --------------------------------------------------------------------------- #
# Le verrou : une règle non vérifiée ne produit rien d'exploitable
# --------------------------------------------------------------------------- #


def test_une_regle_draft_ne_produit_aucune_famille_finalisable() -> None:
    brouillon = regle(
        status="draft", verification_method="model_knowledge_unverified"
    )
    familles = deriver_familles([brouillon])

    assert familles, "une règle draft doit tout de même produire des angles, mais bloqués"
    assert all(
        f.candidate_family_status is CandidateFamilyStatus.BLOCKED for f in familles
    )
    assert all(not f.is_ready for f in familles)
    assert all(f.blocking_reasons for f in familles)


def test_le_qc_refuse_une_famille_finalisable_sur_une_regle_draft() -> None:
    brouillon = regle(status="draft", verification_method="model_knowledge_unverified")
    familles = deriver_familles([brouillon])
    falsifiee = familles[0].model_copy(
        update={
            "candidate_family_status": CandidateFamilyStatus.READY,
            "blocking_reasons": [],
            "review_reasons": [],
        }
    )

    constats = controler([falsifiee], [brouillon])
    assert any(c.controle == "draft_finalisable" for c in erreurs(constats))


def test_une_regle_validee_produit_des_familles_pretes() -> None:
    familles = deriver_familles([regle()])
    assert familles
    assert all(f.is_ready for f in familles), [
        (f.id, f.blocking_reasons, f.review_reasons) for f in familles if not f.is_ready
    ]


def test_exceptions_inconnues_mettent_la_famille_en_revue() -> None:
    eligibilite = eligibilite_regle(regle(exceptions_status="unknown"))
    assert not eligibilite.blocages
    assert any("exceptions inconnues" in r for r in eligibilite.reserves)
    assert eligibilite.statut is CandidateFamilyStatus.NEEDS_REVIEW


def test_une_reforme_proposee_ne_produit_aucune_famille_exploitable() -> None:
    proposee = regle(regulatory_status="proposed")
    familles = deriver_familles([proposee])
    assert all(
        f.candidate_family_status is CandidateFamilyStatus.BLOCKED for f in familles
    )
    assert any(
        "réforme proposée" in raison for f in familles for raison in f.blocking_reasons
    )


# --------------------------------------------------------------------------- #
# Score de potentiel : on ne fabrique pas un angle pour remplir un quota
# --------------------------------------------------------------------------- #


def test_aucun_calcul_fabrique_sans_computation_reelle() -> None:
    sans_calcul = regle(
        rule_type="GOVERNANCE",
        statement="Énoncé synthétique sans aucune donnée chiffrée.",
        operational_rule="Traduction opérationnelle sans chiffre.",
    )
    potentiel = potentiel_complet(sans_calcul)[FamilyKind.CALCULATION]
    assert potentiel.score == 0
    assert famille_de([sans_calcul], sans_calcul.id, FamilyKind.CALCULATION) is None


def test_une_regle_de_seuil_porte_sa_computation() -> None:
    seuil = regle(rule_type="THRESHOLD")
    assert potentiel_complet(seuil)[FamilyKind.CALCULATION].score == 3


def test_exception_bloquee_quand_les_exceptions_nont_pas_ete_cherchees() -> None:
    inconnues = regle(exceptions_status="unknown")
    assert potentiel_complet(inconnues)[FamilyKind.EXCEPTION].score == 0
    assert famille_de([inconnues], inconnues.id, FamilyKind.EXCEPTION) is None


def test_exception_exploitable_quand_les_exceptions_sont_listees() -> None:
    listees = regle(exceptions_status="listed", exceptions=["Exception synthétique"])
    famille = famille_de([listees], listees.id, FamilyKind.EXCEPTION)
    assert famille is not None
    assert famille.family_score == 3
    assert famille.family_rationale


def test_affirmation_negative_non_verifiee_reste_bloquee() -> None:
    avec_claim = regle(
        negative_claims=[{"claim": "Affirmation synthétique fausse", "status": "unverified"}]
    )
    famille = famille_de([avec_claim], avec_claim.id, FamilyKind.NEGATIVE_ASSERTION)
    assert famille is not None
    assert famille.candidate_family_status is CandidateFamilyStatus.BLOCKED
    assert any("n'est pas « cela n'existe pas »" in r for r in famille.blocking_reasons)


def test_affirmation_negative_verifiee_devient_exploitable() -> None:
    verifiee = regle(
        negative_claims=[
            {
                "claim": "Affirmation synthétique fausse",
                "status": "verified_absent",
                "verification_method": "primary_text_review",
                "searched_in": "Texte synthétique, version consultée",
            }
        ]
    )
    famille = famille_de([verifiee], verifiee.id, FamilyKind.NEGATIVE_ASSERTION)
    assert famille is not None
    assert famille.family_score == 3
    assert famille.is_ready
    assert famille.requires_negative_claim


def test_chaque_famille_porte_une_justification_et_une_difficulte_motivee() -> None:
    for famille in deriver_familles([regle()]):
        assert famille.family_rationale.strip()
        assert famille.difficulty_rationale.strip()
        assert 1 <= famille.predicted_difficulty <= 5


def test_toutes_les_familles_sont_evaluees_meme_celles_qui_valent_zero() -> None:
    scores = potentiel_complet(regle())
    assert set(scores) == set(ORDRE_FAMILLES)
    assert all(0 <= p.score <= 3 for p in scores.values())


# --------------------------------------------------------------------------- #
# Jumeaux
# --------------------------------------------------------------------------- #


def test_une_fausse_premisse_nomme_son_piege_et_sa_jumelle_nen_a_pas() -> None:
    familles = {f.family_kind: f for f in deriver_familles([regle()])}
    fausse = familles[FamilyKind.FALSE_PREMISE]
    vraie = familles[FamilyKind.TRUE_PREMISE_ADVERSARIAL]

    assert fausse.reasoning_trap is not ReasoningTrap.NONE
    assert vraie.reasoning_trap is ReasoningTrap.NONE
    # Le piège imité est ce qui rend les deux questions comparables.
    assert vraie.mimicked_trap is fausse.reasoning_trap


def test_les_jumeaux_sont_reciproques_et_de_types_distincts() -> None:
    familles = deriver_familles([regle()])
    apparies = [f for f in familles if f.twin_candidate]
    assert len(apparies) == 2

    gauche, droite = apparies
    assert gauche.twin_partner_id == droite.id
    assert droite.twin_partner_id == gauche.id
    assert gauche.twin_group_id == droite.twin_group_id
    assert gauche.twin_type is droite.twin_type
    assert gauche.question_type is not droite.question_type


def test_le_piege_temporel_nomme_le_couple() -> None:
    temporelle = regle(reasoning_traps=["TEMPORAL_CONFUSION"], time_sensitive=True)
    fausse = famille_de([temporelle], temporelle.id, FamilyKind.FALSE_PREMISE)
    assert fausse is not None
    assert fausse.twin_type is not None
    assert fausse.twin_type.value == "TEMPORAL_TWIN"


def test_le_qc_detecte_un_jumelage_non_reciproque() -> None:
    reference = regle()
    familles = deriver_familles([reference])
    casse = [
        f.model_copy(update={"twin_partner_id": f.id + "-X"}) if f.twin_candidate else f
        for f in familles
    ]
    constats = controler(casse, [reference])
    assert any(c.controle == "twin_partenaire" for c in erreurs(constats))


# --------------------------------------------------------------------------- #
# Invariants du schéma
# --------------------------------------------------------------------------- #


def blueprint(**modifications: Any) -> dict:
    famille = deriver_familles([regle()])[0]
    brut = famille.model_dump(mode="json")
    brut.update(modifications)
    return brut


def test_une_famille_bloquee_sans_motif_est_refusee() -> None:
    with pytest.raises(ValidationError, match="sans motif"):
        CandidateFamily.model_validate(
            blueprint(candidate_family_status="blocked", blocking_reasons=[])
        )


def test_une_repondabilite_incoherente_est_refusee() -> None:
    with pytest.raises(ValidationError, match="incompatible"):
        CandidateFamily.model_validate(blueprint(answerability="unanswerable"))


def test_une_vraie_premisse_piegee_est_refusee() -> None:
    vraie = next(
        f
        for f in deriver_familles([regle()])
        if f.question_type is QuestionType.TRUE_PREMISE_ADVERSARIAL
    )
    brut = vraie.model_dump(mode="json")
    brut["reasoning_trap"] = "SCOPE_CONFUSION"
    with pytest.raises(ValidationError, match="ne contient pas de piège"):
        CandidateFamily.model_validate(brut)


def test_une_abstention_sans_exigence_est_refusee() -> None:
    abstention = next(
        f
        for f in deriver_familles([regle(rule_type="SCOPE")])
        if f.expected_behavior.value in ("abstain", "request_missing_information")
    )
    brut = abstention.model_dump(mode="json")
    brut["abstention_focus"] = []
    with pytest.raises(ValidationError, match="abstention_focus"):
        CandidateFamily.model_validate(brut)


def test_une_famille_temporelle_sans_ancrage_est_refusee() -> None:
    temporelle = next(
        f
        for f in deriver_familles([regle(time_sensitive=True)])
        if f.family_kind is FamilyKind.TEMPORAL
    )
    brut = temporelle.model_dump(mode="json")
    brut["temporal_blueprint"] = None
    with pytest.raises(ValidationError, match="temporal_blueprint"):
        CandidateFamily.model_validate(brut)


def test_une_reforme_proposee_ne_peut_pas_ancrer_une_famille_temporelle() -> None:
    temporelle = next(
        f
        for f in deriver_familles([regle(time_sensitive=True)])
        if f.family_kind is FamilyKind.TEMPORAL
    )
    brut = temporelle.model_dump(mode="json")
    brut["temporal_blueprint"]["regulatory_status"] = "proposed"
    with pytest.raises(ValidationError, match="réforme proposée"):
        CandidateFamily.model_validate(brut)


def test_un_jumeau_sans_partenaire_est_refuse() -> None:
    with pytest.raises(ValidationError, match="twin_group_id"):
        CandidateFamily.model_validate(blueprint(twin_candidate=True))


# --------------------------------------------------------------------------- #
# Redondance et couverture
# --------------------------------------------------------------------------- #


def test_deux_regles_du_meme_article_qui_disent_la_meme_chose_sont_un_doublon() -> None:
    enonce = (
        "Les entités assujetties documentent annuellement leur dispositif "
        "synthétique de contrôle interne auprès du superviseur compétent."
    )
    gauche = regle(id="RULE-SYNTH-100", statement=enonce)
    droite = regle(id="RULE-SYNTH-101", statement=enonce)

    familles = deriver_familles([gauche, droite])
    assert groupe_redondance(gauche) == groupe_redondance(droite)

    constats = controler(familles, [gauche, droite])
    assert any(c.controle == "doublon" for c in erreurs(constats))


def test_deux_dispositions_distinctes_du_meme_article_ne_sont_pas_un_doublon() -> None:
    gauche = regle(
        id="RULE-SYNTH-100",
        statement="Les entités assujetties documentent leur dispositif de contrôle interne.",
    )
    droite = regle(
        id="RULE-SYNTH-101",
        statement="Le superviseur publie chaque trimestre une synthèse anonymisée.",
    )

    familles = deriver_familles([gauche, droite])
    constats = controler(familles, [gauche, droite])
    assert not erreurs(constats)
    assert any(c.controle == "meme_ancrage" for c in constats)


def test_le_concept_teste_nomme_larticle_et_le_titre() -> None:
    reference = regle()
    concept = concept_teste(reference)
    assert reference.source.article in concept
    assert reference.title in concept


def test_la_matrice_couvre_toutes_les_combinaisons_regle_famille() -> None:
    regles = [regle(), regle(id="RULE-SYNTH-200")]
    lignes = matrice_couverture(regles, deriver_familles(regles))

    assert len(lignes) == len(regles) * len(ORDRE_FAMILLES)
    assert set(lignes[0]) >= set(COLONNES_MATRICE)
    # Le potentiel écarté reste visible : c'est ce qui rend les trous lisibles.
    assert any(not ligne["retained"] for ligne in lignes)


def test_les_lacunes_nomment_les_familles_et_les_pieges_absents() -> None:
    reference = regle()
    trous = lacunes([reference], deriver_familles([reference]))
    assert FamilyKind.EXCEPTION.value in trous["missing_family_kinds"]
    assert trous["missing_traps"]
    assert trous["rules_without_family"] == []


def test_la_faisabilite_affiche_son_hypothese_de_rendement() -> None:
    faisabilite = faisabilite_distribution(deriver_familles([regle()]))
    assert faisabilite["yield_hypothesis"] == {
        str(k): v for k, v in sorted(RENDEMENT_PAR_SCORE.items())
    }
    for ligne in faisabilite["by_question_type"]:
        assert {"target_items", "families", "estimated_items", "gap", "achievable"} <= set(ligne)


# --------------------------------------------------------------------------- #
# Écriture, rechargement, déterminisme
# --------------------------------------------------------------------------- #


def test_la_derivation_est_deterministe() -> None:
    regles = [regle(), regle(id="RULE-SYNTH-200", rule_type="SCOPE")]
    premiere = [f.model_dump(mode="json") for f in deriver_familles(regles)]
    seconde = [f.model_dump(mode="json") for f in deriver_familles(regles)]
    assert premiere == seconde


def test_la_carte_se_recharge_a_lidentique(tmp_path: Path) -> None:
    regles = [regle()]
    familles = deriver_familles(regles)
    comptes = ecrire_carte(familles, tmp_path)

    assert comptes == {f"{d.value.lower()}-families": 0 for d in Domain} | {
        "sfdr-families": len(familles)
    }
    # La carte est écrite triée par identifiant : c'est ce qui rend le diff
    # d'une régénération lisible. La comparaison se fait donc sur le même tri.
    rechargees = charger_familles(tmp_path)
    assert [f.model_dump(mode="json") for f in rechargees] == [
        f.model_dump(mode="json") for f in sorted(familles, key=lambda f: f.id)
    ]


def test_la_matrice_sexporte_aux_conventions_du_depot(tmp_path: Path) -> None:
    regles = [regle()]
    sortie = tmp_path / "matrice.csv"
    ecrire_matrice(matrice_couverture(regles, deriver_familles(regles)), sortie)

    assert sortie.read_bytes().startswith(b"\xef\xbb\xbf")
    with sortie.open(encoding=ENCODAGE_CSV, newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=SEPARATEUR_CSV))
    assert len(lignes) == len(ORDRE_FAMILLES)
    assert list(lignes[0]) == list(COLONNES_MATRICE)


def test_le_manifeste_dit_ce_que_la_carte_autorise() -> None:
    brouillon = regle(status="draft", verification_method="model_knowledge_unverified")
    familles = deriver_familles([brouillon])
    manifeste = construire_manifeste(familles, [brouillon], {"sfdr-families": len(familles)})

    assert manifeste["number_of_usable_rules"] == 0
    assert manifeste["number_ready"] == 0
    assert manifeste["number_blocked"] == len(familles)
    assert "blocked" in manifeste["status_note"]
    assert "generation_date" in manifeste  # daté, mais jamais horodaté


def test_le_rapport_dit_quaucune_question_nest_redigee() -> None:
    reference = regle()
    familles = deriver_familles([reference])
    texte = rapport_markdown(familles, [reference], controler(familles, [reference]))
    assert "Aucune question n'est rédigée" in texte
    assert "Distribution visée" in texte


# --------------------------------------------------------------------------- #
# La carte réelle du dépôt
# --------------------------------------------------------------------------- #


def test_la_carte_du_depot_passe_son_qc() -> None:
    regles = charger_rulebook()
    familles = charger_familles()
    assert familles, "la carte doit être générée et versionnée"
    assert not erreurs(controler(familles, regles))


def test_la_carte_du_depot_est_a_jour_du_rulebook() -> None:
    regles = charger_rulebook()
    attendues = deriver_familles(regles)
    ecrites = charger_familles()
    assert [f.model_dump(mode="json") for f in sorted(ecrites, key=lambda f: f.id)] == [
        f.model_dump(mode="json") for f in sorted(attendues, key=lambda f: f.id)
    ]


def test_aucune_famille_du_depot_nest_exploitable_tant_que_rien_nest_verifie() -> None:
    """Le Rulebook V0 est intégralement en `draft` : la carte doit le dire, pas le masquer."""
    regles = charger_rulebook()
    if any(r.status is not RuleStatus.DRAFT for r in regles):
        pytest.skip("le Rulebook a été vérifié : ce test ne décrit plus l'état du dépôt")
    familles = charger_familles()
    assert all(f.candidate_family_status is CandidateFamilyStatus.BLOCKED for f in familles)


def test_les_identifiants_de_famille_sont_uniques_et_derives_de_leur_regle() -> None:
    familles = charger_familles()
    identifiants = [f.id for f in familles]
    assert len(identifiants) == len(set(identifiants))
    for famille in familles:
        assert famille.id == f"{famille.rule_id}-{CODES_FAMILLES[famille.family_kind]}"
        assert famille.family_score >= SCORE_RETENU
