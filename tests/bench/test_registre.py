"""V0.2 — intégrité du registre : rattachements, versions, jumeaux, validation, plan."""

from __future__ import annotations

import copy

import pytest

from src.bench.items import Item
from src.bench.plan import BenchmarkPlan, coverage_report
from src.bench.regles import Rule
from src.bench.registre import RegistreInvalide, charger_public
from src.bench.validation import (
    TransitionInterdite,
    blocages_pour,
    items_publiables,
    nouvelle_version,
    peut_promouvoir,
    promouvoir,
)
from src.bench.vocabulaires import Corpus, ValidationStatus
from tests.bench.fabriques import (
    CHECKLIST_COMPLETE,
    FAMILLE,
    GROUPE,
    REGLE,
    ecrire_corpus,
    ecrire_referentiel,
    item,
    item_fausse_premisse,
    item_valide,
)


def charge(tmp_path, items, **referentiel):
    ref = ecrire_referentiel(tmp_path / "registry", **referentiel)
    corpus = ecrire_corpus(tmp_path / "corpus", public=items)
    return charger_public(ref, corpus)


def erreurs(tmp_path, items, **referentiel) -> list[str]:
    with pytest.raises(RegistreInvalide) as exc:
        charge(tmp_path, items, **referentiel)
    return [e.message for e in exc.value.erreurs]


# -- rattachements ------------------------------------------------------------- #


def test_registre_coherent_se_charge(tmp_path):
    registre = charge(tmp_path, [item()])
    assert [i.id for i in registre.items] == ["SYNTH-0001-v1"]
    assert registre.rules_by_id["RULE-SYNTH-001"].is_usable


def test_famille_inconnue_refusee(tmp_path):
    assert any("famille inconnue" in m for m in erreurs(tmp_path, [item(family_id="FAM-X")]))


def test_regle_inconnue_refusee(tmp_path):
    assert any("règle inconnue" in m for m in erreurs(tmp_path, [item(rule_ids=["RULE-X"])]))


def test_concept_inconnu_refuse(tmp_path):
    famille = dict(FAMILLE, concept_id="CONCEPT-X")
    assert any("concept inconnu" in m for m in erreurs(tmp_path, [item()], families=[famille]))


def test_gold_adosse_a_une_regle_non_validee_refuse(tmp_path):
    """Un gold opposable ne peut pas reposer sur une règle encore en brouillon."""
    brouillon = dict(copy.deepcopy(REGLE), status="draft")
    messages = erreurs(tmp_path, [item_valide()], rules=[brouillon])
    assert any("ne s'adosse qu'à des règles validées" in m for m in messages)


def test_brouillon_adosse_a_une_regle_brouillon_accepte(tmp_path):
    """Tant que l'item est en draft, le rattachement peut mûrir avec la règle."""
    brouillon = dict(copy.deepcopy(REGLE), status="draft")
    registre = charge(tmp_path, [item()], rules=[brouillon])
    assert len(registre.items) == 1


def test_identifiants_dupliques_refuses(tmp_path):
    assert any("double" in m for m in erreurs(tmp_path, [item(), item()]))


# -- versionnement --------------------------------------------------------------- #


def test_historique_des_versions_conserve(tmp_path):
    v1 = item()
    v2 = item(version=2, supersedes="SYNTH-0001-v1", gold_answer="Réponse révisée.")
    registre = charge(tmp_path, [v1, v2])

    assert len(registre.items) == 2
    assert registre.latest_versions()["SYNTH-0001"].version == 2
    assert "SYNTH-0001-v1" in registre.items_by_id


def test_version_dont_le_predecesseur_manque_refusee(tmp_path):
    """Supprimer une version, c'est perdre l'historique d'un gold."""
    orpheline = item(version=2, supersedes="SYNTH-0001-v1")
    messages = erreurs(tmp_path, [orpheline])
    assert any("introuvable" in m for m in messages)
    assert any("discontinue" in m for m in messages)


def test_nouvelle_version_repart_en_brouillon():
    sujet = Item.model_validate(item_valide())
    suivante = nouvelle_version(sujet, gold_answer="Réponse mise à jour.")

    assert suivante.version == 2
    assert suivante.supersedes == "SYNTH-0001-v1"
    assert suivante.status is ValidationStatus.DRAFT
    assert not suivante.checklist.is_complete
    # L'original n'a pas bougé.
    assert sujet.version == 1 and sujet.status is ValidationStatus.VALIDATED


# -- jumeaux ------------------------------------------------------------------------ #


def jumeaux() -> list[dict]:
    return [
        item(base_id="SYNTH-T-A", twin_group_id="TWIN-SYNTH-001", twin_role="true_premise"),
        item_fausse_premisse(
            base_id="SYNTH-T-B", twin_group_id="TWIN-SYNTH-001", twin_role="false_premise"
        ),
    ]


def test_groupe_de_jumeaux_valide(tmp_path):
    registre = charge(tmp_path, jumeaux())
    assert len(registre.items) == 2


def test_groupe_a_role_unique_refuse(tmp_path):
    """Deux items du même rôle ne mesurent aucune sensibilité à la prémisse."""
    identiques = [
        item(base_id="SYNTH-T-A", twin_group_id="TWIN-SYNTH-001", twin_role="true_premise"),
        item(base_id="SYNTH-T-B", twin_group_id="TWIN-SYNTH-001", twin_role="true_premise"),
    ]
    assert any("même rôle" in m for m in erreurs(tmp_path, identiques))


def test_groupe_a_un_seul_item_refuse(tmp_path):
    seul = [item(base_id="SYNTH-T-A", twin_group_id="TWIN-SYNTH-001", twin_role="true_premise")]
    assert any("au moins 2 items" in m for m in erreurs(tmp_path, seul))


def test_groupe_inconnu_refuse(tmp_path):
    inconnus = [
        item(base_id="SYNTH-T-A", twin_group_id="TWIN-X", twin_role="true_premise"),
        item(base_id="SYNTH-T-B", twin_group_id="TWIN-X", twin_role="context_shift"),
    ]
    assert any("twin group inconnu" in m for m in erreurs(tmp_path, inconnus))


def test_jumeaux_de_familles_differentes_refuses(tmp_path):
    autre_famille = dict(FAMILLE, id="FAM-SYNTH-002")
    depareilles = [
        item(base_id="SYNTH-T-A", twin_group_id="TWIN-SYNTH-001", twin_role="true_premise"),
        item(base_id="SYNTH-T-B", family_id="FAM-SYNTH-002",
             twin_group_id="TWIN-SYNTH-001", twin_role="context_shift"),
    ]
    messages = erreurs(tmp_path, depareilles, families=[FAMILLE, autre_famille])
    assert any("comparables" in m for m in messages)


def test_jumeaux_a_cheval_sur_les_deux_corpus_refuses(tmp_path):
    """Publier un jumeau public révélerait la structure de son jumeau privé."""
    ref = ecrire_referentiel(tmp_path / "registry")
    corpus = ecrire_corpus(
        tmp_path / "corpus",
        public=[item(base_id="SYNTH-T-A", twin_group_id="TWIN-SYNTH-001",
                     twin_role="true_premise")],
        prive=[item(base_id="SYNTH-T-B", corpus="private",
                    twin_group_id="TWIN-SYNTH-001", twin_role="context_shift")],
    )
    from src.bench.registre import charger_prive, charger_referentiel, _charger_items

    registre, _ = charger_referentiel(ref)
    publics, _ = _charger_items(corpus, Corpus.PUBLIC)
    prives, _ = _charger_items(corpus, Corpus.PRIVE)
    registre.items = publics + prives

    messages = [e.message for e in registre.check_integrity()]
    assert any("à cheval" in m for m in messages)


# -- validation ---------------------------------------------------------------------- #


def test_promotion_impossible_sans_grille():
    brouillon = Item.model_validate(item(status="review"))
    blocages = blocages_pour(brouillon, ValidationStatus.VALIDATED)

    assert not peut_promouvoir(brouillon, ValidationStatus.VALIDATED)
    assert any("checklist" in b.champ for b in blocages)

    with pytest.raises(TransitionInterdite):
        promouvoir(brouillon, ValidationStatus.VALIDATED)


def test_promotion_possible_avec_grille_complete():
    pret = Item.model_validate(item(status="review", checklist=CHECKLIST_COMPLETE))
    promu = promouvoir(pret, ValidationStatus.VALIDATED)

    assert promu.status is ValidationStatus.VALIDATED
    assert pret.status is ValidationStatus.REVIEW  # l'original n'est pas muté


def test_on_ne_saute_pas_draft_a_published():
    brouillon = Item.model_validate(item(checklist=CHECKLIST_COMPLETE))
    with pytest.raises(TransitionInterdite, match="non prévue"):
        promouvoir(brouillon, ValidationStatus.PUBLISHED)


def test_un_gold_publie_est_fige():
    publie = Item.model_validate(item_valide(status="published"))
    blocages = blocages_pour(publie, ValidationStatus.REVIEW)
    assert any("figé" in b.message for b in blocages)


def test_locked_inaccessible_en_public():
    valide = Item.model_validate(item_valide())
    assert any("inapplicable" in b.message for b in blocages_pour(valide, ValidationStatus.LOCKED))


def test_seuls_les_items_publies_sont_publiables():
    lot = [
        Item.model_validate(item_valide(status="published")),
        Item.model_validate(item_valide(base_id="SYNTH-0002")),
        Item.model_validate(item(base_id="SYNTH-0003")),
        Item.model_validate(item_valide(base_id="SYNTH-P-001", corpus="private", status="locked")),
    ]
    assert [i.id for i in items_publiables(lot)] == ["SYNTH-0001-v1"]


# -- plan de couverture ---------------------------------------------------------------- #


def test_cibles_conformes_a_la_specification():
    plan = BenchmarkPlan()
    assert plan.domain_targets(Corpus.PUBLIC) == {
        "SFDR": 45, "MIFID": 30, "AMF": 30, "DORA": 22, "LCBFT": 23
    }
    assert sum(plan.domain_targets(Corpus.PRIVE).values()) == 700
    assert sum(plan.type_targets(Corpus.PUBLIC).values()) == 150


def test_les_poids_sont_configurables():
    plan = BenchmarkPlan(
        targets={"public": 10},
        domain_weights={"SFDR": 0.5, "DORA": 0.5},
        type_weights={"fact": 1.0},
        domain_targets_override={},
    )
    assert plan.domain_targets(Corpus.PUBLIC) == {"SFDR": 5, "DORA": 5}


def test_poids_qui_ne_somment_pas_a_un_refuses():
    with pytest.raises(ValueError, match="somme des poids"):
        BenchmarkPlan(domain_weights={"SFDR": 0.5, "DORA": 0.2}, domain_targets_override={})


def test_cibles_explicites_incoherentes_refusees():
    with pytest.raises(ValueError, match="attendu 150"):
        BenchmarkPlan(domain_targets_override={"public": {"SFDR": 1}})


def test_rapport_de_couverture():
    plan = BenchmarkPlan(
        targets={"public": 2},
        domain_weights={"SFDR": 0.5, "DORA": 0.5},
        type_weights={"qualification": 1.0},
        domain_targets_override={},
        tolerance=0,
    )
    items = [Item.model_validate(item()), Item.model_validate(item(base_id="SYNTH-0002"))]
    rapport = coverage_report(items, plan, Corpus.PUBLIC)

    assert rapport["actual_total"] == 2
    par_domaine = {ligne["key"]: ligne for ligne in rapport["by_domain"]}
    assert par_domaine["SFDR"] == {"key": "SFDR", "target": 1, "actual": 2, "gap": 1}
    assert par_domaine["DORA"]["gap"] == -1
    assert rapport["within_tolerance"] is False
