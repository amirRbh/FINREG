"""Dossier de lot : ce qu'il demande, et ce qu'il se refuse à dire.

Ce que ces tests protègent :

1. **La feuille de décision sort vide.** Une valeur par défaut serait une
   décision que personne n'a rendue.
2. **Deux décisions par règle, jamais une.** Confirmer un énoncé ne dit rien
   des dérogations qui le limitent ailleurs ; le dossier pose les deux
   questions et le dit.
3. **Le dossier n'affirme rien du texte.** Il énumère ce qu'il faut y vérifier,
   et rappelle que les statuts ne bougent pas.
4. **Le vocabulaire de la revue se traduit dans le circuit existant** — sans
   quoi chaque relecteur inventerait son encodage, et deux vérités
   coexisteraient.

Aucun accès réseau.
"""

from __future__ import annotations

import copy
import csv
import datetime as dt
from pathlib import Path
from typing import Any

from src.bench.adjudication import construire
from src.bench.completude import analyser
from src.bench.plan_action import construire_lignes
from src.bench.rapport_lot import CORRESPONDANCE_DECISIONS, dossier_de_lot
from src.bench.readiness import evaluer
from src.bench.regles import Rule
from src.bench.relecture import AccesSource
from src.bench.verification import (
    COLONNES_A_REMPLIR,
    ENCODAGE_CSV,
    SEPARATEUR_CSV,
    Verdict,
    exporter_dossier,
    lire_dossier,
)
from tests.bench.fabriques import REGLE

JOUR = dt.date(2026, 8, 30)


def regle(**modifications: Any) -> Rule:
    """Une règle dont le texte primaire n'a jamais été lu."""
    brut = copy.deepcopy(REGLE)
    brut.update(
        {
            "id": modifications.pop("id", "RULE-SYNTH-001"),
            "status": "draft",
            "verification_method": "model_knowledge_unverified",
            "priority": "CRITICAL",
            "exceptions_status": "unknown",
            "common_confusions": ["confondre le délai avec celui d'un autre régime"],
            "gold_ready": False,
            "gold_ready_reason": "",
        }
    )
    brut["source"] = dict(REGLE["source"], verified_by="", verification_date=None)
    brut.update(modifications)
    return Rule.model_validate(brut)


def _lot(sujets: list[Rule]):
    constats, dossiers = {}, []
    for sujet in sujets:
        constat = analyser(sujet, "", "", article_verifie=False, concordance=0.0)
        constats[sujet.id] = constat
        dossiers.append(construire(sujet, constat, evaluer(sujet, constat), "", {sujet.id: sujet}))
    lignes = construire_lignes(dossiers, {d.rule_id: AccesSource.REFUS_DE_LA_SOURCE for d in dossiers})
    return lignes, constats


def rendre(sujets: list[Rule]) -> str:
    lignes, constats = _lot(sujets)
    return dossier_de_lot(
        "LOT-TEST",
        "Texte synthétique de test (aucune valeur juridique)",
        "la source répond HTTP 403 depuis cet environnement",
        lignes,
        {s.id: s for s in sujets},
        constats,
        "data/verification/dossier-lot-test.csv",
        JOUR,
    )


def test_la_feuille_de_decision_sort_vide(tmp_path: Path) -> None:
    """Une colonne pré-remplie serait une décision que personne n'a rendue."""
    chemin = tmp_path / "dossier.csv"
    exporter_dossier([regle(), regle(id="RULE-SYNTH-002")], chemin)
    with chemin.open(encoding=ENCODAGE_CSV, newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=SEPARATEUR_CSV))
    assert len(lignes) == 2
    for ligne in lignes:
        for colonne in COLONNES_A_REMPLIR:
            assert ligne[colonne] == "", colonne
    assert lire_dossier(chemin) == [], "une ligne vide n'est pas une décision"


def test_le_dossier_pose_deux_questions_par_regle() -> None:
    """Confirmer l'énoncé ne dit rien des dérogations qui le limitent ailleurs."""
    rendu = rendre([regle()])
    fiche = rendu.split("### `RULE-SYNTH-001`")[1]
    questions = fiche.split("**Questions exactes à trancher**")[1].split("**Exceptions")[0]
    assert "1." in questions and "2." in questions
    assert "soutient-il l'énoncé" in questions
    assert "dérogation" in questions


def test_le_dossier_naffirme_rien_du_texte() -> None:
    rendu = rendre([regle()])
    assert "Aucun de ces textes n'a été consulté" in rendu
    assert "Aucun statut ne bouge" in rendu
    assert "aucune décision n'est pré-remplie" in rendu


def test_le_dossier_dit_ce_qui_manque_pour_chaque_regle() -> None:
    """« Revue requise » ne se traite pas : la décision manquante se nomme."""
    rendu = rendre([regle()])
    manquant = rendu.split("**Décision actuellement manquante**")[1]
    assert "`model_knowledge_unverified`" in manquant
    assert "`unknown`" in manquant
    assert "aucune ne se déduit de l'autre" in manquant


def test_le_vocabulaire_de_revue_se_traduit_dans_le_circuit_existant() -> None:
    """Chaque décision demandée doit s'encoder avec un verdict qui existe."""
    attendus = {"NONE_IDENTIFIED", "IDENTIFIED_AND_INCORPORATED", "REQUIRES_CORRECTION", "REJECTED"}
    nommees = {decision for decision, _, _ in CORRESPONDANCE_DECISIONS}
    assert attendus <= nommees

    verdicts = {v.value for v in Verdict}
    for _, _, encodage in CORRESPONDANCE_DECISIONS:
        cite = {v for v in verdicts if f"verdict={v}" in encodage}
        assert cite, encodage
        assert cite <= verdicts


def test_le_dossier_rappelle_le_verrou_du_perimetre() -> None:
    """Sans ce rappel, « je n'ai pas trouvé » finirait en « il n'y en a pas »."""
    rendu = rendre([regle()])
    assert "perimetre_exceptions" in rendu
    assert "ne fait jamais passer" in rendu
    assert "`unknown` à `none_identified`" in rendu
