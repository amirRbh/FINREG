"""Étape 2 — garde-fou de non-rétention. Ces tests ne doivent jamais être désactivés."""

from __future__ import annotations

import pytest

from src.schema import ConfigFournisseur, Corpus, Item
from src.securite import (
    PrivateCorpusLeakError,
    filtrer_publics,
    verifier_autorisation,
    verifier_lot,
)
from tests.fabriques import item


def fournisseur(**modifications) -> ConfigFournisseur:
    base = {
        "id": "fournisseur-x",
        "nom": "Fournisseur X",
        "editeur": "Éditeur X",
        "adaptateur": "fake",
        "modele": "modele-x",
    }
    base.update(modifications)
    return ConfigFournisseur(**base)


def test_corpus_prive_vers_fournisseur_non_conforme_leve():
    """Le test central exigé par la règle de sécurité."""
    with pytest.raises(PrivateCorpusLeakError) as exc:
        verifier_autorisation(Corpus.PRIVE, fournisseur(zero_retention=False))

    assert "zero_retention" in str(exc.value)
    assert "Aucun appel n'a été émis" in str(exc.value)


def test_zero_retention_absent_vaut_refus():
    """L'absence de déclaration n'est pas une garantie : refus par défaut."""
    with pytest.raises(PrivateCorpusLeakError):
        verifier_autorisation(Corpus.PRIVE, fournisseur())


@pytest.mark.parametrize("valeur", [None, "true", "oui", 1, "1", [], {}])
def test_zero_retention_non_booleen_vaut_refus(valeur):
    """Ni `"true"` ni `1` ne valent une garantie contractuelle de non-rétention."""
    config = fournisseur(zero_retention=valeur)
    assert config.zero_retention is False

    with pytest.raises(PrivateCorpusLeakError):
        verifier_autorisation(Corpus.PRIVE, config)


def test_corpus_prive_vers_fournisseur_conforme_passe():
    verifier_autorisation(Corpus.PRIVE, fournisseur(zero_retention=True))


def test_corpus_public_passe_meme_sans_garantie():
    verifier_autorisation(Corpus.PUBLIC, fournisseur(zero_retention=False))


def test_le_message_ne_divulgue_aucun_contenu_prive():
    """Un message d'erreur finit dans les logs : il ne doit rien contenir de privé."""
    prive = Item.model_validate(item("private", question="SECRET-QUESTION"))

    with pytest.raises(PrivateCorpusLeakError) as exc:
        verifier_lot([prive], fournisseur())

    message = str(exc.value)
    assert "SECRET-QUESTION" not in message
    assert prive.reponse_reference not in message


def test_un_seul_item_prive_bloque_tout_le_lot():
    """Le contrôle est fait sur le lot entier : rien ne part si un item est en cause."""
    lot = [
        Item.model_validate(item(id="PUB-1")),
        Item.model_validate(item("private", id="PRIV-9")),
    ]

    with pytest.raises(PrivateCorpusLeakError):
        verifier_lot(lot, fournisseur())


def test_lot_public_passe():
    verifier_lot([Item.model_validate(item(id="PUB-1"))], fournisseur())


def test_filtrer_publics():
    lot = [
        Item.model_validate(item(id="PUB-1")),
        Item.model_validate(item("private", id="PRIV-1")),
    ]
    assert [i.id for i in filtrer_publics(lot)] == ["PUB-1"]


def test_config_juge_soumise_a_la_meme_regle():
    """Le juge reçoit le texte des items : il ne peut pas y échapper."""
    from src.schema import ConfigJuge

    juge = ConfigJuge(zero_retention="true")
    assert juge.zero_retention is False


def test_zero_retention_vrai_est_bien_lu():
    assert fournisseur(zero_retention=True).zero_retention is True
