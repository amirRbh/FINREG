"""Circuit de vérification du Rulebook.

Ce que ces tests protègent : le verrou de vérification ne doit pas pouvoir être
contourné par le circuit censé le servir. Une règle ne progresse que si un
humain nommé a consulté un texte primaire à une date donnée — ni parce qu'un
CSV le prétend, ni parce qu'une régénération est passée par là.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.bench.qc_rulebook import charger_rulebook, controler
from src.bench.regles import Rule
from src.bench.rulebook import ExceptionsStatus, RuleStatus, VerificationMethod
from src.bench.verification import (
    COLONNES,
    VERDICTS_PROMOTEURS,
    Verdict,
    Verification,
    VerificationInvalide,
    appliquer,
    charger_registre,
    ecrire_registre,
    exporter_dossier,
    fusionner_registre,
    lire_dossier,
)
from src.io_utils import lire_json
from tests.bench.fabriques import REGLE

VERIFICATEUR = "Relecteur de test"
DATE = "2026-08-29"


def brouillon(**modifications) -> Rule:
    """Une règle synthétique au point de départ : non vérifiée, non exploitable."""
    base = dict(REGLE)
    base["source"] = dict(REGLE["source"], verified_by="", verification_date=None)
    base["status"] = "draft"
    base["verification_method"] = "model_knowledge_unverified"
    base.update(modifications)
    return Rule.model_validate(base)


def constat(**modifications) -> dict:
    base = {
        "rule_id": REGLE["id"],
        "verdict": "confirme",
        "verification_method": "primary_text_review",
        "verified_by": VERIFICATEUR,
        "verification_date": DATE,
        "target_status": "source_checked",
    }
    base.update(modifications)
    return base


def refuse(donnees: dict, fragment: str) -> None:
    with pytest.raises(ValidationError) as exc:
        Verification.model_validate(donnees)
    assert fragment in str(exc.value), str(exc.value)


# -- le verrou, vu depuis le constat ------------------------------------------------ #


def test_une_promotion_exige_un_texte_primaire():
    """Le cœur du sujet : une source secondaire ne promeut rien."""
    refuse(constat(verification_method="secondary_source_only"), "texte primaire")
    refuse(constat(verification_method="model_knowledge_unverified"), "texte primaire")


def test_une_promotion_exige_un_verificateur_nomme_et_date():
    refuse(constat(verified_by=""), "vérificateur nommé et une date")
    refuse(constat(verification_date=None), "vérificateur nommé et une date")


def test_une_verification_aboutie_doit_viser_un_statut():
    refuse(constat(target_status="draft"), "sans statut visé")


def test_une_refutation_ne_promeut_rien():
    refuse(
        constat(verdict="refute", target_status="validated", comment="le texte dit autre chose"),
        "aucune promotion n'est possible",
    )
    refuse(
        constat(verdict="non_verifiable", target_status="source_checked"),
        "aucune promotion n'est possible",
    )


def test_une_confirmation_ne_corrige_pas_lenonce():
    """Confirmer et corriger sont deux constats différents, pas un dégradé."""
    refuse(constat(statement="autre chose"), "c'est une correction")


def test_une_correction_dit_ce_que_le_texte_dit():
    refuse(constat(verdict="corrige", target_status="validated"), "sans énoncé corrigé")


def test_une_refutation_dit_ce_qui_cloche():
    refuse(constat(verdict="refute", target_status="draft"), "sans commentaire")


def test_les_exceptions_restent_distinctes_du_silence():
    refuse(constat(exceptions=["une exception"]), "sans exceptions_statut")
    refuse(constat(exceptions_status="listed"), "sans exception constatée")


# -- application aux règles ---------------------------------------------------------- #


def test_une_confirmation_promeut_et_date_la_source():
    regle = brouillon()
    [resultat] = appliquer([regle], [Verification.model_validate(constat())])

    assert resultat.status is RuleStatus.SOURCE_CHECKED
    assert resultat.verification_method is VerificationMethod.PRIMARY_TEXT_REVIEW
    assert resultat.source.verified_by == VERIFICATEUR
    assert resultat.source.is_verified
    assert not resultat.needs_verification


def test_une_correction_reversionne_au_lieu_decraser():
    """Un énoncé corrigé remplace du droit : l'historique doit rester lisible."""
    regle = brouillon()
    correction = Verification.model_validate(
        constat(
            verdict="corrige",
            target_status="validated",
            statement="Ce que le texte dit réellement.",
            exceptions_status="none_identified",
        )
    )
    [resultat] = appliquer([regle], [correction])

    assert resultat.version == regle.version + 1
    assert resultat.supersedes == f"{regle.id}-v{regle.version}"
    assert resultat.statement == "Ce que le texte dit réellement."
    assert resultat.is_usable


def test_une_refutation_laisse_la_regle_inexploitable():
    regle = brouillon()
    [resultat] = appliquer(
        [regle],
        [
            Verification.model_validate(
                constat(verdict="refute", target_status="draft", comment="le texte dit l'inverse")
            )
        ],
    )

    assert resultat.status is RuleStatus.DRAFT
    assert not resultat.is_usable
    assert not resultat.source.is_verified
    assert "refute" in resultat.notes


def test_une_regle_validee_ne_peut_pas_ignorer_ses_exceptions():
    """Une règle validée sans ses exceptions se teste comme un absolu qu'elle n'est pas."""
    regle = brouillon(exceptions_status="unknown")
    correction = Verification.model_validate(
        constat(verdict="corrige", target_status="validated", statement="Énoncé rectifié.")
    )
    with pytest.raises(VerificationInvalide, match="exceptions restent"):
        appliquer([regle], [correction])


def test_une_regle_inconnue_arrete_le_lot_entier():
    regle = brouillon()
    with pytest.raises(VerificationInvalide, match="aucune règle de ce nom"):
        appliquer([regle], [Verification.model_validate(constat(rule_id="RULE-ABSENTE"))])


def test_deux_constats_sur_la_meme_regle_sont_refuses():
    regle = brouillon()
    deux = [
        Verification.model_validate(constat()),
        Verification.model_validate(constat(target_status="legal_review")),
    ]
    with pytest.raises(VerificationInvalide, match="deux vérifications"):
        appliquer([regle], deux)


def test_les_regles_non_verifiees_ne_bougent_pas():
    regles = [brouillon(), brouillon(id="RULE-SYNTH-002")]
    resultat = appliquer(regles, [Verification.model_validate(constat())])
    assert resultat[1] == regles[1]


# -- dossier CSV ---------------------------------------------------------------------- #


def remplir(chemin: Path, constats: dict[str, dict[str, str]]) -> None:
    lignes = list(csv.DictReader(chemin.open(encoding="utf-8-sig"), delimiter=";"))
    for ligne in lignes:
        ligne.update(constats.get(ligne["rule_id"], {}))
    with chemin.open("w", encoding="utf-8-sig", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=COLONNES, delimiter=";")
        redacteur.writeheader()
        redacteur.writerows(lignes)


def test_le_dossier_exporte_ce_quil_faut_lire(tmp_path):
    regles = [brouillon(), brouillon(id="RULE-SYNTH-002", priority="CRITICAL")]
    chemin = exporter_dossier(regles, tmp_path / "verification.csv")

    lignes = list(csv.DictReader(chemin.open(encoding="utf-8-sig"), delimiter=";"))
    assert [l["rule_id"] for l in lignes] == ["RULE-SYNTH-002", REGLE["id"]], "priorité d'abord"
    assert lignes[0]["url"] == REGLE["source"]["url"]
    assert lignes[0]["enonce_actuel"] == REGLE["statement"]
    assert all(l["verdict"] == "" for l in lignes), "les constats se remplissent à la main"


def test_le_dossier_se_relit_et_sapplique(tmp_path):
    regles = [brouillon(), brouillon(id="RULE-SYNTH-002")]
    chemin = exporter_dossier(regles, tmp_path / "verification.csv")
    remplir(
        chemin,
        {
            REGLE["id"]: {
                "verdict": "confirme",
                "methode": "primary_text_fetched",
                "verifie_par": VERIFICATEUR,
                "date_verification": DATE,
                "statut_vise": "source_checked",
                "version_date_constatee": "2019-12-09",
            }
        },
    )

    [verification] = lire_dossier(chemin)
    assert verification.rule_id == REGLE["id"]

    resultat = {r.id: r for r in appliquer(regles, [verification])}
    assert resultat[REGLE["id"]].status is RuleStatus.SOURCE_CHECKED
    assert resultat[REGLE["id"]].source.version_date.isoformat() == "2019-12-09"
    assert resultat["RULE-SYNTH-002"].status is RuleStatus.DRAFT


def test_les_lignes_sans_verdict_sont_ignorees(tmp_path):
    chemin = exporter_dossier([brouillon()], tmp_path / "verification.csv")
    assert lire_dossier(chemin) == []


def test_une_ligne_fautive_annule_tout_le_dossier(tmp_path):
    """Comme la file de revue : un fichier partiellement fautif ne s'applique pas à moitié."""
    regles = [brouillon(), brouillon(id="RULE-SYNTH-002")]
    chemin = exporter_dossier(regles, tmp_path / "verification.csv")
    remplir(
        chemin,
        {
            REGLE["id"]: {
                "verdict": "confirme",
                "methode": "primary_text_review",
                "verifie_par": VERIFICATEUR,
                "date_verification": DATE,
                "statut_vise": "source_checked",
            },
            "RULE-SYNTH-002": {
                "verdict": "confirme",
                "methode": "model_knowledge_unverified",
                "verifie_par": VERIFICATEUR,
                "date_verification": DATE,
                "statut_vise": "validated",
            },
        },
    )

    with pytest.raises(VerificationInvalide) as exc:
        lire_dossier(chemin)
    assert "RULE-SYNTH-002" in str(exc.value)
    assert "texte primaire" in str(exc.value)


def test_une_date_illisible_est_signalee_avec_sa_ligne(tmp_path):
    chemin = exporter_dossier([brouillon()], tmp_path / "verification.csv")
    remplir(
        chemin,
        {
            REGLE["id"]: {
                "verdict": "confirme",
                "methode": "primary_text_review",
                "verifie_par": VERIFICATEUR,
                "date_verification": "29/08/2026",
                "statut_vise": "source_checked",
            }
        },
    )
    with pytest.raises(VerificationInvalide, match="AAAA-MM-JJ"):
        lire_dossier(chemin)


def test_un_dossier_sans_les_bonnes_colonnes_est_refuse(tmp_path):
    chemin = tmp_path / "autre.csv"
    chemin.write_text("a;b\n1;2\n", encoding="utf-8-sig")
    with pytest.raises(VerificationInvalide, match="colonnes manquantes"):
        lire_dossier(chemin)


# -- registre ----------------------------------------------------------------------- #


def test_le_registre_se_relit_a_lidentique(tmp_path):
    verifications = [
        Verification.model_validate(constat(rule_id="RULE-B")),
        Verification.model_validate(constat(rule_id="RULE-A")),
    ]
    chemin = ecrire_registre(verifications, tmp_path / "ledger.json")
    relues = charger_registre(chemin)

    assert [v.rule_id for v in relues] == ["RULE-A", "RULE-B"], "trié, donc reproductible"
    assert relues == sorted(verifications, key=lambda v: v.rule_id)


def test_un_registre_absent_vaut_aucune_verification(tmp_path):
    assert charger_registre(tmp_path / "jamais-ecrit.json") == []


def test_la_fusion_garde_le_constat_le_plus_recent(tmp_path):
    chemin = ecrire_registre([Verification.model_validate(constat())], tmp_path / "ledger.json")
    fusionne = fusionner_registre(
        [Verification.model_validate(constat(target_status="validated", exceptions_status="none_identified"))],
        chemin,
    )
    assert len(fusionne) == 1
    assert fusionne[0].target_status is RuleStatus.VALIDATED


def test_une_regeneration_neffacerait_pas_la_verification(tmp_path, monkeypatch):
    """Le point qui rend le registre nécessaire : `generer()` réécrit data/rules/."""
    from scripts import generer_rulebook

    verification = Verification.model_validate(
        constat(rule_id="SFDR-R-005", target_status="source_checked")
    )
    monkeypatch.setattr(generer_rulebook, "SORTIE", tmp_path)
    monkeypatch.setattr(generer_rulebook, "charger_registre", lambda: [verification])

    regles, manifeste = generer_rulebook.generer()
    par_id = {r.id: r for r in regles}

    assert par_id["SFDR-R-005"].status is RuleStatus.SOURCE_CHECKED
    assert par_id["SFDR-R-005"].source.verified_by == VERIFICATEUR
    assert manifeste["number_source_checked"] == 1
    assert "1 règle(s) sur" in manifeste["verification_note"]


def test_la_generation_reproduit_le_rulebook_livre(tmp_path, monkeypatch):
    """Les fichiers versionnés doivent être exactement ce que la génération produit."""
    from scripts import generer_rulebook

    monkeypatch.setattr(generer_rulebook, "SORTIE", tmp_path)
    generer_rulebook.generer()

    for produit in sorted(tmp_path.glob("*.json")):
        livre = Path("data/rules") / produit.name
        assert livre.is_file(), produit.name
        assert json.loads(produit.read_text(encoding="utf-8")) == json.loads(
            livre.read_text(encoding="utf-8")
        ), produit.name


def test_le_registre_livre_consigne_chaque_verification_appliquee():
    """Le registre est la mémoire du travail de vérification, hors de `data/rules/`.

    Sans lui, régénérer le Rulebook effacerait le seul travail que le script de
    génération ne sait pas refaire. Chaque constat qui a promu une règle doit
    donc y porter son vérificateur et sa date.
    """
    registre = Path("data/verification/rulebook-ledger.json")
    assert registre.is_file()
    constats = charger_registre(registre)

    statuts = {r.id: r for r in charger_rulebook()}
    for verification in constats:
        assert verification.rule_id in statuts, verification.rule_id
        if verification.verdict in VERDICTS_PROMOTEURS:
            assert verification.verified_by.strip(), verification.rule_id
            assert verification.verification_date is not None, verification.rule_id

    promues = {r.id for r in statuts.values() if r.status is not RuleStatus.DRAFT}
    consignees = {
        v.rule_id for v in constats if v.verdict in VERDICTS_PROMOTEURS
    }
    assert promues == consignees, "toute promotion doit être traçable au registre"


# -- contrôles qualité ajoutés -------------------------------------------------------- #


def controles(regles: list[Rule]) -> dict[str, list[str]]:
    resultat: dict[str, list[str]] = {}
    for c in controler(regles):
        resultat.setdefault(c.controle, []).append(c.regle_id)
    return resultat


def test_une_version_anterieure_a_lacte_est_signalee():
    """Une version consultée ne peut pas précéder l'acte qu'elle porte."""
    source = dict(
        REGLE["source"],
        text="Règlement (UE) 2022/2554 (DORA)",
        url="https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554",
        version_date="2020-01-01",
    )
    assert "version_date_placeholder" in controles([brouillon(source=source)])


def test_une_version_posterieure_a_lacte_ne_lest_pas():
    source = dict(
        REGLE["source"],
        text="Règlement (UE) 2022/2554 (DORA)",
        url="https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554",
        version_date="2023-05-04",
    )
    assert "version_date_placeholder" not in controles([brouillon(source=source)])


def test_une_url_designant_un_autre_acte_est_signalee():
    source = dict(
        REGLE["source"],
        text="Règlement délégué (UE) 2017/565",
        url="https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32021R1253",
        version_date="2022-01-01",
    )
    assert "url_acte_different" in controles([brouillon(source=source)])


def test_un_ancrage_couvrant_plusieurs_articles_est_signale():
    for article in ("Articles 8 à 13", "Ensemble de la directive", "Articles 17 et 18"):
        source = dict(REGLE["source"], article=article)
        assert "ancrage_imprecis" in controles([brouillon(source=source)]), article


def test_un_article_unique_ne_lest_pas():
    source = dict(REGLE["source"], article="Article 8")
    assert "ancrage_imprecis" not in controles([brouillon(source=source)])


def test_deux_regles_du_meme_article_ne_font_pas_un_doublon():
    """Un même article porte couramment deux obligations distinctes."""
    regles = [
        brouillon(statement="Le texte impose une évaluation de l'adéquation au conseil."),
        brouillon(
            id="RULE-SYNTH-002",
            statement="Le texte impose un avertissement lorsque le service n'est pas approprié.",
        ),
    ]
    resultat = controles(regles)
    assert "doublon_conceptuel" not in resultat
    assert resultat["meme_article"] == ["RULE-SYNTH-002"]


def test_deux_regles_qui_disent_la_meme_chose_font_un_doublon():
    enonce = "Le texte impose une évaluation de l'adéquation avant tout conseil en investissement."
    regles = [
        brouillon(statement=enonce),
        brouillon(id="RULE-SYNTH-002", statement=enonce + " Sans exception."),
    ]
    assert "doublon_conceptuel" in controles(regles)


def test_une_regle_consultee_mais_non_promue_reste_visible():
    """Une règle réfutée sort du dossier de vérification : le QC doit la rattraper."""
    regle = brouillon(verification_method="primary_text_review")
    assert "verification_sans_promotion" in controles([regle])
    assert regle.status is RuleStatus.DRAFT


# -- le Rulebook livré ----------------------------------------------------------------- #


def test_aucune_regle_livree_nest_utilisable_sans_ses_exceptions():
    """`source_checked` n'est pas `validated`, et l'écart tient aux exceptions.

    Une source attestée dit que le texte a été lu ; elle ne dit pas que la règle
    est complète. Tant que ses exceptions n'ont pas été cherchées, une règle se
    testerait comme un absolu qu'elle n'est peut-être pas — et n'ancre donc
    aucun gold.
    """
    regles = charger_rulebook()
    for regle in regles:
        if regle.is_usable:
            assert regle.exceptions_status is not ExceptionsStatus.UNKNOWN, regle.id
    assert any(
        r.status is not RuleStatus.DRAFT for r in regles
    ), "le Rulebook livré porte le travail de vérification déjà appliqué"


def test_aucune_regle_a_verifier_nechappe_au_dossier(tmp_path):
    """Ce qui reste à vérifier doit toujours revenir dans le dossier.

    Une règle non vérifiée qui n'apparaîtrait pas à l'export sortirait
    silencieusement du circuit : personne ne saurait plus qu'elle attend.
    """
    regles = charger_rulebook()
    a_verifier = [r for r in regles if r.needs_verification]
    chemin = exporter_dossier(a_verifier, tmp_path / "v.csv")
    lignes = list(csv.DictReader(chemin.open(encoding="utf-8-sig"), delimiter=";"))
    assert {l["rule_id"] for l in lignes} == {r.id for r in a_verifier}
    assert len(lignes) == len(a_verifier)


def test_les_exceptions_inconnues_bloquent_la_validation_des_regles_livrees():
    """55 règles sur 58 ne pourront pas passer `validated` sans chercher leurs exceptions."""
    regles = [r for r in charger_rulebook() if r.exceptions_status is ExceptionsStatus.UNKNOWN]
    assert regles
    correction = [
        Verification.model_validate(
            constat(rule_id=r.id, verdict="corrige", target_status="validated", statement="X.")
        )
        for r in regles[:1]
    ]
    with pytest.raises(VerificationInvalide, match="exceptions restent"):
        appliquer(charger_rulebook(), correction)


def test_un_constat_orphelin_arrete_la_generation(tmp_path, monkeypatch):
    """Un constat qui ne trouve plus sa règle est du travail de vérification perdu."""
    from scripts import generer_rulebook

    monkeypatch.setattr(generer_rulebook, "SORTIE", tmp_path)
    monkeypatch.setattr(
        generer_rulebook,
        "charger_registre",
        lambda: [Verification.model_validate(constat(rule_id="REGLE-RENOMMEE"))],
    )
    with pytest.raises(VerificationInvalide, match="sans règle correspondante"):
        generer_rulebook.generer()
