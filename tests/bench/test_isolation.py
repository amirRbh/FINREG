"""V0.2 — isolation du corpus privé. Le corpus privé est l'actif : rien ne sort."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.bench.isolation import (
    PrivateLeakError,
    assert_no_private_content,
    assert_no_private_ids,
    assert_no_private_tracked_by_git,
    assert_private_is_gitignored,
    public_only,
    redact_for_log,
)
from src.bench.items import Item
from src.bench.registre import (
    RegistreInvalide,
    charger_prive,
    charger_public,
    collisions_inter_corpus,
    ids_publics_et_prives,
)
from src.bench.vocabulaires import Corpus
from tests.bench.fabriques import ecrire_corpus, ecrire_referentiel, item


# -- chargeurs séparés -------------------------------------------------------- #


def projet(tmp_path, public=None, prive=None) -> tuple[Path, Path]:
    referentiel = ecrire_referentiel(tmp_path / "registry")
    corpus = ecrire_corpus(
        tmp_path / "corpus",
        public=public if public is not None else [item()],
        prive=prive if prive is not None else [item(base_id="SYNTH-P-001", corpus="private")],
    )
    return referentiel, corpus


def test_le_chargeur_public_ne_lit_jamais_le_prive(tmp_path):
    referentiel, corpus = projet(tmp_path)
    registre = charger_public(referentiel, corpus)

    assert [i.id for i in registre.items] == ["SYNTH-0001-v1"]
    assert registre.private_ids() == []


def test_charger_le_prive_exige_un_aveu_explicite(tmp_path):
    referentiel, corpus = projet(tmp_path)

    with pytest.raises(PermissionError, match="je_confirme_usage_local"):
        charger_prive(referentiel, corpus, je_confirme_usage_local=False)


def test_le_chargeur_prive_fonctionne_avec_le_drapeau(tmp_path):
    referentiel, corpus = projet(tmp_path)
    registre = charger_prive(referentiel, corpus, je_confirme_usage_local=True)

    assert registre.private_ids() == ["SYNTH-P-001-v1"]


def test_item_prive_depose_sous_public_est_refuse(tmp_path):
    referentiel, corpus = projet(tmp_path, public=[item(corpus="private")])

    with pytest.raises(RegistreInvalide) as exc:
        charger_public(referentiel, corpus)

    assert any("dans le dossier" in e.message for e in exc.value.erreurs)


def test_identifiants_lisibles_sans_charger_le_contenu(tmp_path):
    _, corpus = projet(tmp_path)
    publics, prives = ids_publics_et_prives(corpus)

    assert publics == {"SYNTH-0001-v1"}
    assert prives == {"SYNTH-P-001-v1"}


def test_collision_didentifiant_entre_corpus_detectee(tmp_path):
    _, corpus = projet(tmp_path, prive=[item(corpus="private")])
    assert collisions_inter_corpus(corpus) == ["SYNTH-0001-v1"]


def test_aucune_collision_dans_le_cas_normal(tmp_path):
    _, corpus = projet(tmp_path)
    assert collisions_inter_corpus(corpus) == []


# -- détection de fuite -------------------------------------------------------- #


def test_identifiant_prive_dans_un_artefact_detecte():
    with pytest.raises(PrivateLeakError, match="corpus privé"):
        assert_no_private_ids({"items": ["SYNTH-P-001-v1"]}, ["SYNTH-P-001-v1"], "export")


def test_identifiant_prive_sans_version_detecte():
    """Un export peut recopier l'identifiant de base sans son suffixe de version."""
    with pytest.raises(PrivateLeakError):
        assert_no_private_ids({"id": "SYNTH-P-001"}, ["SYNTH-P-001-v2"])


def test_identifiant_public_voisin_non_confondu():
    """« SYNTH-P-0010 » n'est pas « SYNTH-P-001 » : pas de faux positif sur un préfixe."""
    assert_no_private_ids({"id": "SYNTH-P-0010-v1"}, ["SYNTH-P-001-v1"])


def test_artefact_propre_passe():
    assert_no_private_ids({"items": ["SYNTH-0001-v1"]}, ["SYNTH-P-001-v1"])


def test_contenu_prive_recopie_sans_identifiant_detecte():
    with pytest.raises(PrivateLeakError):
        assert_no_private_content(
            {"texte": "voici la question privée intégrale"}, ["la question privée intégrale"]
        )


def test_le_message_de_fuite_ne_reproduit_pas_le_contenu():
    with pytest.raises(PrivateLeakError) as exc:
        assert_no_private_content({"t": "SECRET-SYNTH-XYZ"}, ["SECRET-SYNTH-XYZ"])
    assert "SECRET-SYNTH-XYZ" not in str(exc.value)


# -- garde-fous de dépôt --------------------------------------------------------- #


def test_le_corpus_prive_est_gitignore():
    assert_private_is_gitignored(Path("."))


def test_aucun_fichier_prive_suivi_par_git():
    assert assert_no_private_tracked_by_git(Path(".")) == []


def test_gitignore_absent_signale(tmp_path):
    with pytest.raises(PrivateLeakError, match="aucun .gitignore"):
        assert_private_is_gitignored(tmp_path)


def test_gitignore_sans_le_prive_signale(tmp_path):
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    with pytest.raises(PrivateLeakError, match="pourrait"):
        assert_private_is_gitignored(tmp_path)


# -- filtres --------------------------------------------------------------------- #


def test_public_only():
    lot = [
        Item.model_validate(item()),
        Item.model_validate(item(base_id="SYNTH-P-001", corpus="private")),
    ]
    assert [i.id for i in public_only(lot)] == ["SYNTH-0001-v1"]
    assert all(i.corpus is Corpus.PUBLIC for i in public_only(lot))


def test_la_journalisation_dun_lot_prive_ne_contient_aucun_contenu():
    lot = [Item.model_validate(item(corpus="private", question="SECRET-SYNTH"))]
    trace = str(redact_for_log(lot))

    assert "SECRET-SYNTH" not in trace
    assert "SYNTH-0001-v1" in trace
