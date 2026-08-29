"""Étape 1 — validation du corpus."""

from __future__ import annotations

import pytest

from src.loader import CorpusInvalide, charger_corpus, resume_corpus, version_corpus
from src.schema import Corpus
from tests.fabriques import ecrire_corpus, item


def test_item_public_valide_est_charge(tmp_path):
    racine = ecrire_corpus(tmp_path, public=[item()])
    items = charger_corpus(racine, Corpus.PUBLIC)
    assert [i.id for i in items] == ["SFDR-0001"]
    assert items[0].source.verifie_par == "A. Rouibah"


@pytest.mark.parametrize("verifie_par", ["", "   "])
def test_item_public_sans_verificateur_est_refuse(tmp_path, verifie_par):
    """La règle centrale : pas de vérificateur nommé, pas d'item public."""
    fautif = item()
    fautif["source"]["verifie_par"] = verifie_par
    racine = ecrire_corpus(tmp_path, public=[fautif])

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    assert any("verifie_par" in e.message for e in exc.value.erreurs)


def test_item_public_sans_date_de_verification_est_refuse(tmp_path):
    fautif = item()
    fautif["source"]["date_verification"] = None
    racine = ecrire_corpus(tmp_path, public=[fautif])

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    assert any("date_verification" in e.message for e in exc.value.erreurs)


def test_item_prive_sans_verificateur_est_accepte(tmp_path):
    """Le corpus privé n'est pas publié : la contrainte de traçabilité ne s'y applique pas."""
    racine = ecrire_corpus(tmp_path, prive=[item("private")])
    items = charger_corpus(racine, Corpus.PRIVE)
    assert [i.id for i in items] == ["PRIV-0001"]
    assert items[0].source.verifie_par == ""


def test_identifiants_en_double_refuses(tmp_path):
    racine = ecrire_corpus(tmp_path, public=[item(), item()])

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    assert any("double" in e.message for e in exc.value.erreurs)


def test_identifiants_en_double_entre_corpus_refuses(tmp_path):
    """Les ids sont uniques tous corpus confondus, sinon le cache mélangerait les réponses."""
    racine = ecrire_corpus(
        tmp_path,
        public=[item()],
        prive=[item("private", id="SFDR-0001")],
    )

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, [Corpus.PUBLIC, Corpus.PRIVE])

    assert any("double" in e.message for e in exc.value.erreurs)


def test_item_prive_depose_dans_public_est_refuse(tmp_path):
    """Un glissement de corpus doit être bloqué au chargement, pas au moment de l'appel."""
    racine = ecrire_corpus(tmp_path, public=[item("private", id="EGARE-1")])

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    assert any("dossier" in e.message for e in exc.value.erreurs)


def test_toutes_les_erreurs_sont_rapportees_ensemble(tmp_path):
    """Un corpus se corrige en une passe : on ne s'arrête pas à la première erreur."""
    sans_verificateur = item(id="A-1")
    sans_verificateur["source"]["verifie_par"] = ""
    type_inconnu = item(id="A-2", type="devinette")
    difficulte_hors_bornes = item(id="A-3", difficulte=9)

    racine = ecrire_corpus(
        tmp_path, public=[sans_verificateur, type_inconnu, difficulte_hors_bornes]
    )

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    positions = {e.position for e in exc.value.erreurs}
    assert {"A-1", "A-2", "A-3"} <= positions


def test_champ_inconnu_refuse(tmp_path):
    racine = ecrire_corpus(tmp_path, public=[item(commentaire="note interne")])

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    assert any("commentaire" in e.message for e in exc.value.erreurs)


def test_points_cles_vides_refuses(tmp_path):
    racine = ecrire_corpus(tmp_path, public=[item(points_cles=[])])

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    assert any("points_cles" in e.message for e in exc.value.erreurs)


def test_json_illisible_est_rapporte_sans_planter(tmp_path):
    racine = ecrire_corpus(tmp_path, public=[item()])
    (racine / "public" / "casse.json").write_text("{ pas du json", encoding="utf-8")

    with pytest.raises(CorpusInvalide) as exc:
        charger_corpus(racine, Corpus.PUBLIC)

    assert any("JSON illisible" in e.message for e in exc.value.erreurs)


def test_version_du_corpus_stable_et_sensible(tmp_path):
    """Le hash identifie le jeu de questions : stable à l'identique, différent sinon."""
    racine = ecrire_corpus(tmp_path, public=[item()])
    items = charger_corpus(racine, Corpus.PUBLIC)

    assert version_corpus(items) == version_corpus(charger_corpus(racine, Corpus.PUBLIC))

    autre = ecrire_corpus(tmp_path / "autre", public=[item(question="Autre question ?")])
    assert version_corpus(items) != version_corpus(charger_corpus(autre, Corpus.PUBLIC))


def test_resume_corpus(tmp_path):
    racine = ecrire_corpus(tmp_path, public=[item(), item(id="DORA-1", domaine="DORA")])
    resume = resume_corpus(charger_corpus(racine, Corpus.PUBLIC))

    assert resume["nb_items"] == 2
    assert resume["par_domaine"] == {"DORA": 1, "SFDR": 1}
    assert resume["par_corpus"]["public"] == 2


def test_dossier_absent_donne_un_corpus_vide(tmp_path):
    assert charger_corpus(tmp_path, Corpus.PRIVE) == []
