"""V0.2 phases 6 et 9 — métriques, dénominateurs, risk-coverage et QA humaine."""

from __future__ import annotations

import pytest

from src.bench.items import Item
from src.bench.jugement import (
    DeterministicFindings,
    Judgment,
    ObservedBehavior,
    Verdict,
)
from src.bench.metriques import (
    aurc,
    calculer_metriques,
    rapport_modele,
    risk_coverage_curve,
    sensibilite_premisse,
    stabilite,
)
from src.bench.qa import (
    Annotation,
    SeuilsQA,
    appliquer_annotations,
    cohen_kappa,
    desaccords,
    fleiss_kappa,
    kappa,
    publiable,
    resoudre,
)
from tests.bench.fabriques import item, item_abstention, item_fausse_premisse


def jugement(
    item_id="SYNTH-0001-v1",
    verdict=Verdict.CORRECT,
    observe=ObservedBehavior.ANSWERED,
    conform=True,
    run=0,
    model="m",
    hallucination=False,
    critique=False,
    affirmatif=False,
    confiance=None,
    escalade=False,
) -> Judgment:
    return Judgment(
        item_id=item_id,
        model_id=model,
        run_index=run,
        findings=DeterministicFindings(
            observed_behavior=observe,
            behavior_conform=conform,
            hallucinated_references=["2019/2088:47"] if hallucination else [],
            disqualifying_errors_found=["erreur"] if critique else [],
            is_affirmative=affirmatif,
            contains_citation=hallucination,
        ),
        verdict=verdict,
        confidence=confiance,
        escalated=escalade,
    )


def index(*items) -> dict[str, Item]:
    return {i.id: i for i in items}


# -- dénominateurs ------------------------------------------------------------- #


def test_exactitude_et_couverture_ont_des_denominateurs_distincts():
    """Le cas qui justifie la règle : peu de réponses, mais toutes justes."""
    items = index(Item.model_validate(item()))
    jugements = [
        jugement(verdict=Verdict.CORRECT),
        jugement(run=1, verdict=Verdict.INCORRECT, observe=ObservedBehavior.ABSTAINED,
                 conform=False),
        jugement(run=2, verdict=Verdict.INCORRECT, observe=ObservedBehavior.ABSTAINED,
                 conform=False),
    ]
    m = calculer_metriques(jugements, items, "m")

    assert m["accuracy_answered"].numerator == 1
    assert m["accuracy_answered"].denominator == 1
    assert m["accuracy_answered"].value == 100.0

    assert m["accuracy_all_items"].denominator == 3
    assert m["accuracy_all_items"].value == pytest.approx(33.3)

    assert m["coverage"].value == pytest.approx(33.3)


def test_chaque_metrique_porte_sa_definition():
    items = index(Item.model_validate(item()))
    for metrique in calculer_metriques([jugement()], items, "m").values():
        assert metrique.definition
        assert "/" in metrique.definition


def test_denominateur_vide_ne_donne_pas_zero():
    """Zéro sur zéro n'est pas zéro pour cent : on ne fabrique pas un chiffre."""
    items = index(Item.model_validate(item()))
    m = calculer_metriques([jugement()], items, "m")

    assert m["false_premise_acceptance_rate"].denominator == 0
    assert m["false_premise_acceptance_rate"].value is None


def test_reponse_non_evaluable_exclue_des_deux_termes():
    items = index(Item.model_validate(item()))
    jugements = [jugement(), jugement(run=1, verdict=Verdict.NOT_EVALUABLE)]
    m = calculer_metriques(jugements, items, "m")

    assert m["accuracy_all_items"].denominator == 1


# -- métriques de comportement --------------------------------------------------- #


def test_acceptation_de_fausse_premisse():
    sujet = Item.model_validate(item_fausse_premisse())
    items = index(sujet)
    jugements = [
        jugement(item_id=sujet.id, observe=ObservedBehavior.REFUTED_PREMISE),
        jugement(item_id=sujet.id, run=1, observe=ObservedBehavior.ANSWERED),
    ]
    m = calculer_metriques(jugements, items, "m")

    assert m["false_premise_acceptance_rate"].numerator == 1
    assert m["false_premise_acceptance_rate"].denominator == 2


def test_abstention_correcte_et_injustifiee_portent_sur_des_populations_disjointes():
    abstention = Item.model_validate(item_abstention())
    ordinaire = Item.model_validate(item())
    items = index(abstention, ordinaire)
    jugements = [
        jugement(item_id=abstention.id, observe=ObservedBehavior.ABSTAINED, conform=True),
        jugement(item_id=ordinaire.id, observe=ObservedBehavior.ABSTAINED, conform=False),
    ]
    m = calculer_metriques(jugements, items, "m")

    assert m["correct_abstention_rate"].numerator == 1
    assert m["correct_abstention_rate"].denominator == 1
    assert m["unjustified_abstention_rate"].numerator == 1
    assert m["unjustified_abstention_rate"].denominator == 1


def test_sur_refutation_mesuree_sur_le_dual():
    """Un modèle qui réfute tout doit être puni ici, pas récompensé ailleurs."""
    dual = Item.model_validate(
        item(base_id="SYNTH-TP", question_type="true_premise_adversarial",
             reasoning_trap="SCOPE_CONFUSION", expected_behavior="answer")
    )
    items = index(dual)
    jugements = [
        jugement(item_id=dual.id, observe=ObservedBehavior.REFUTED_PREMISE),
        jugement(item_id=dual.id, run=1, observe=ObservedBehavior.ANSWERED),
    ]
    m = calculer_metriques(jugements, items, "m")

    assert m["over_refusal_rate"].numerator == 1
    assert m["over_refusal_rate"].denominator == 2


def test_hallucination_de_source_a_deux_denominateurs():
    items = index(Item.model_validate(item()))
    jugements = [jugement(hallucination=True), jugement(run=1), jugement(run=2)]
    m = calculer_metriques(jugements, items, "m")

    assert m["source_hallucination_rate"].denominator == 3
    assert m["source_hallucination_rate_cited"].denominator == 1
    assert m["source_hallucination_rate_cited"].value == 100.0


def test_reponse_dangereuse():
    items = index(Item.model_validate(item()))
    jugements = [
        jugement(verdict=Verdict.INCORRECT, affirmatif=True),
        jugement(run=1, verdict=Verdict.INCORRECT, affirmatif=False),
        jugement(run=2, verdict=Verdict.CORRECT, affirmatif=True),
    ]
    m = calculer_metriques(jugements, items, "m")

    assert m["dangerous_answer_rate"].numerator == 1
    assert m["dangerous_answer_rate"].denominator == 3


def test_erreur_critique():
    items = index(Item.model_validate(item()))
    m = calculer_metriques([jugement(critique=True), jugement(run=1)], items, "m")
    assert m["critical_error_rate"].numerator == 1


# -- stabilité et sensibilité ------------------------------------------------------ #


def test_stabilite_entre_runs():
    stable = [jugement(run=i) for i in range(3)]
    assert stabilite(stable, "m").value == 100.0

    instable = [jugement(run=0), jugement(run=1, verdict=Verdict.INCORRECT)]
    assert stabilite(instable, "m").value == 0.0


def test_stabilite_ignore_les_items_vus_une_fois():
    assert stabilite([jugement()], "m").denominator == 0


def test_sensibilite_a_la_premisse():
    """Il faut réfuter le faux ET accepter le vrai : réfuter tout ne suffit pas."""
    vrai = Item.model_validate(
        item(base_id="T-A", twin_group_id="TWIN-SYNTH-001", twin_role="true_premise")
    )
    faux = Item.model_validate(
        item_fausse_premisse(
            base_id="T-B", twin_group_id="TWIN-SYNTH-001", twin_role="false_premise"
        )
    )
    items = index(vrai, faux)

    discriminant = [
        jugement(item_id=vrai.id, observe=ObservedBehavior.ANSWERED),
        jugement(item_id=faux.id, observe=ObservedBehavior.REFUTED_PREMISE),
    ]
    assert sensibilite_premisse(discriminant, items, "m").value == 100.0

    refute_tout = [
        jugement(item_id=vrai.id, observe=ObservedBehavior.REFUTED_PREMISE),
        jugement(item_id=faux.id, observe=ObservedBehavior.REFUTED_PREMISE),
    ]
    assert sensibilite_premisse(refute_tout, items, "m").value == 0.0


def test_sensibilite_ignore_les_groupes_incomplets():
    vrai = Item.model_validate(
        item(base_id="T-A", twin_group_id="TWIN-SYNTH-001", twin_role="true_premise")
    )
    mesure = sensibilite_premisse([jugement(item_id=vrai.id)], index(vrai), "m")
    assert mesure.denominator == 0


# -- courbe risque-couverture ---------------------------------------------------------- #


def test_courbe_risque_couverture_decroit_avec_le_seuil():
    """Une confiance qui vaut quelque chose fait baisser le risque quand on resserre."""
    jugements = [
        jugement(run=0, verdict=Verdict.CORRECT, confiance=0.9),
        jugement(run=1, verdict=Verdict.CORRECT, confiance=0.8),
        jugement(run=2, verdict=Verdict.INCORRECT, confiance=0.3),
        jugement(run=3, verdict=Verdict.INCORRECT, confiance=0.2),
    ]
    points = risk_coverage_curve(jugements, "m")

    complet = min(points, key=lambda p: p.threshold)
    strict = max(points, key=lambda p: p.threshold)

    assert complet.coverage == 1.0
    assert complet.risk == 0.5
    assert strict.risk == 0.0
    assert strict.coverage < complet.coverage
    assert aurc(points) is not None


def test_courbe_vide_sans_confiance():
    assert risk_coverage_curve([jugement()], "m") == []
    assert aurc([]) is None


def test_rapport_complet():
    items = index(Item.model_validate(item()))
    rapport = rapport_modele([jugement(confiance=0.7, escalade=True)], items, "m")

    assert rapport["model_id"] == "m"
    assert rapport["escalated"] == 1
    assert "accuracy_answered" in rapport["metrics"]
    assert "premise_sensitivity" in rapport["metrics"]
    assert "stability_across_runs" in rapport["metrics"]
    assert all("definition" in m for m in rapport["metrics"].values())


# -- QA humaine -------------------------------------------------------------------------- #


def annotation(annotateur, verdict, item_id="SYNTH-0001-v1", run=0) -> Annotation:
    return Annotation(
        item_id=item_id, model_id="m", run_index=run, annotator=annotateur, verdict=verdict
    )


def test_cohen_kappa_accord_parfait():
    annotations = [
        annotation("a", Verdict.CORRECT), annotation("b", Verdict.CORRECT),
        annotation("a", Verdict.INCORRECT, run=1), annotation("b", Verdict.INCORRECT, run=1),
    ]
    assert cohen_kappa(annotations) == 1.0
    assert kappa(annotations) == 1.0


def test_cohen_kappa_desaccord_total():
    annotations = [
        annotation("a", Verdict.CORRECT), annotation("b", Verdict.INCORRECT),
        annotation("a", Verdict.INCORRECT, run=1), annotation("b", Verdict.CORRECT, run=1),
    ]
    assert cohen_kappa(annotations) < 0


def test_kappa_indefini_quand_une_seule_categorie_mais_accord_total():
    """Le kappa classique est indéfini ici ; l'accord, lui, est total."""
    annotations = [annotation("a", Verdict.CORRECT), annotation("b", Verdict.CORRECT)]
    assert cohen_kappa(annotations) == 1.0


def test_kappa_absent_sans_double_annotation():
    assert kappa([annotation("a", Verdict.CORRECT)]) is None


def test_fleiss_kappa_a_trois_annotateurs():
    annotations = [
        annotation(a, v, run=r)
        for r, verdicts in enumerate(
            [
                (Verdict.CORRECT, Verdict.CORRECT, Verdict.CORRECT),
                (Verdict.INCORRECT, Verdict.INCORRECT, Verdict.INCORRECT),
            ]
        )
        for a, v in zip("abc", verdicts)
    ]
    assert fleiss_kappa(annotations) == 1.0
    assert kappa(annotations) == 1.0


def test_desaccords_listes():
    annotations = [
        annotation("a", Verdict.CORRECT), annotation("b", Verdict.INCORRECT),
        annotation("a", Verdict.CORRECT, run=1), annotation("b", Verdict.CORRECT, run=1),
    ]
    trouves = desaccords(annotations)

    assert len(trouves) == 1
    assert trouves[0].run_index == 0
    assert trouves[0].verdicts == {"a": "correct", "b": "incorrect"}


def test_desaccord_sans_arbitrage_nest_pas_tranche():
    """On ne résout pas au hasard : l'unité reste en attente."""
    annotations = [annotation("a", Verdict.CORRECT), annotation("b", Verdict.INCORRECT)]
    assert resoudre(annotations, {}) == {}


def test_arbitrage_tranche_le_desaccord():
    annotations = [annotation("a", Verdict.CORRECT), annotation("b", Verdict.INCORRECT)]
    cle = ("SYNTH-0001-v1", "m", 0)
    assert resoudre(annotations, {cle: Verdict.INCORRECT}) == {cle: Verdict.INCORRECT}


def test_majorite_tranche_a_trois():
    annotations = [
        annotation("a", Verdict.CORRECT),
        annotation("b", Verdict.CORRECT),
        annotation("c", Verdict.INCORRECT),
    ]
    assert resoudre(annotations, {})[("SYNTH-0001-v1", "m", 0)] is Verdict.CORRECT


def test_annotations_appliquees_sans_muter_loriginal():
    jugements = [jugement(verdict=Verdict.CORRECT)]
    corriges = appliquer_annotations(jugements, {("SYNTH-0001-v1", "m", 0): Verdict.INCORRECT})

    assert corriges[0].final_verdict is Verdict.INCORRECT
    assert corriges[0].verdict is Verdict.CORRECT
    assert jugements[0].human_verdict is None


def test_publication_bloquee_sans_double_annotation():
    verdict = publiable([jugement(escalade=True)], [annotation("a", Verdict.CORRECT)])

    assert verdict["publishable"] is False
    assert any("kappa incalculable" in b for b in verdict["blockers"])


def test_publication_bloquee_si_des_escalades_ne_sont_pas_revues():
    jugements = [jugement(escalade=True), jugement(run=1, escalade=True)]
    annotations = [
        annotation("a", Verdict.CORRECT), annotation("b", Verdict.CORRECT),
        annotation("a", Verdict.INCORRECT, run=1), annotation("b", Verdict.CORRECT, run=1),
    ]
    verdict = publiable(jugements, annotations, SeuilsQA(kappa_minimum=0.0))
    assert verdict["review_coverage"] == 1.0

    partiel = publiable(jugements, annotations[:2], SeuilsQA(kappa_minimum=0.0))
    assert partiel["publishable"] is False
    assert any("couverture de revue" in b for b in partiel["blockers"])


def test_publication_possible_quand_les_seuils_sont_tenus():
    jugements = [jugement(escalade=True)]
    annotations = [annotation("a", Verdict.CORRECT), annotation("b", Verdict.CORRECT)]
    verdict = publiable(jugements, annotations, SeuilsQA(kappa_minimum=0.6))

    assert verdict["publishable"] is True
    assert verdict["blockers"] == []
