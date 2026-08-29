"""Agrégation des scores et classement.

Toutes les moyennes sont arrondies au dixième, comme les affiche le site public :
l'artefact du run et la page publiée disent exactement le même chiffre.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass, field

from src.schema import AXES, Config, Flag, Item, NOTE_MAX, Score, TypeItem


def _moyenne(valeurs: list[float]) -> float:
    return round(statistics.fmean(valeurs), 1) if valeurs else 0.0


def _pourcentage(numerateur: int, denominateur: int) -> float:
    return round(100 * numerateur / denominateur, 1) if denominateur else 0.0


@dataclass
class AgregatModele:
    fournisseur_id: str
    nom: str
    editeur: str
    score_global: float = 0.0
    taux_hallucination_source: float = 0.0
    taux_abstention_correcte: float = 0.0
    ecart_type: float = 0.0
    scores_domaines: dict[str, float] = field(default_factory=dict)
    scores_axes: dict[str, float] = field(default_factory=dict)
    nb_items: int = 0
    nb_reponses_notees: int = 0
    nb_items_abstention: int = 0

    def as_dict(self) -> dict:
        return {
            "fournisseur_id": self.fournisseur_id,
            "nom": self.nom,
            "editeur": self.editeur,
            "score_global": self.score_global,
            "taux_hallucination_source": self.taux_hallucination_source,
            "taux_abstention_correcte": self.taux_abstention_correcte,
            "ecart_type": self.ecart_type,
            "scores_domaines": self.scores_domaines,
            "scores_axes": self.scores_axes,
            "nb_items": self.nb_items,
            "nb_reponses_notees": self.nb_reponses_notees,
            "nb_items_abstention": self.nb_items_abstention,
        }


def scores_par_couple(scores: list[Score]) -> dict[tuple[str, str], list[Score]]:
    """Regroupe les scores par (item, fournisseur), tous runs confondus."""
    groupes: dict[tuple[str, str], list[Score]] = defaultdict(list)
    for score in scores:
        groupes[(score.item_id, score.fournisseur_id)].append(score)
    return {cle: sorted(v, key=lambda s: s.index_run) for cle, v in groupes.items()}


def score_item_sur_100(scores_du_couple: list[Score]) -> float:
    """Score d'un item pour un modèle : moyenne de ses runs, sur 100."""
    return _moyenne([s.sur_100() for s in scores_du_couple])


def agreger_modele(
    fournisseur_id: str,
    nom: str,
    editeur: str,
    items: dict[str, Item],
    scores: list[Score],
) -> AgregatModele:
    siens = [s for s in scores if s.fournisseur_id == fournisseur_id]
    agregat = AgregatModele(fournisseur_id=fournisseur_id, nom=nom, editeur=editeur)
    if not siens:
        return agregat

    par_couple = scores_par_couple(siens)
    agregat.nb_items = len(par_couple)
    agregat.nb_reponses_notees = len(siens)

    # Score global : moyenne sur les items de la moyenne de leurs runs.
    agregat.score_global = _moyenne(
        [score_item_sur_100(runs) for runs in par_couple.values()]
    )

    # Écart-type : dispersion du score global d'un run à l'autre, c'est-à-dire
    # l'instabilité du modèle, pas la dispersion entre questions.
    par_run: dict[int, list[float]] = defaultdict(list)
    for score in siens:
        par_run[score.index_run].append(score.sur_100())
    scores_de_run = [statistics.fmean(v) for v in par_run.values() if v]
    agregat.ecart_type = (
        round(statistics.pstdev(scores_de_run), 1) if len(scores_de_run) > 1 else 0.0
    )

    agregat.taux_hallucination_source = _pourcentage(
        sum(1 for s in siens if Flag.HALLUCINATION_SOURCE in s.flags), len(siens)
    )

    # Abstention correcte : parmi les items qui appelaient une abstention,
    # ceux où le modèle s'est effectivement abstenu sur tous ses runs.
    ids_abstention = [i for i, item in items.items() if item.type is TypeItem.ABSTENTION]
    agregat.nb_items_abstention = len(ids_abstention)
    reussies = sum(
        1
        for item_id in ids_abstention
        if (runs := par_couple.get((item_id, fournisseur_id)))
        and all(Flag.ABSTENTION in s.flags for s in runs)
    )
    agregat.taux_abstention_correcte = _pourcentage(reussies, len(ids_abstention))

    # Par domaine, sur 100.
    par_domaine: dict[str, list[float]] = defaultdict(list)
    for (item_id, _), runs in par_couple.items():
        item = items.get(item_id)
        if item is not None:
            par_domaine[item.domaine].append(score_item_sur_100(runs))
    agregat.scores_domaines = {d: _moyenne(v) for d, v in sorted(par_domaine.items())}

    # Par axe, sur 2.
    agregat.scores_axes = {
        axe.value: _moyenne([s.notes.as_dict()[axe.value] for s in siens]) for axe in AXES
    }

    return agregat


def agreger(config: Config, items: list[Item], scores: list[Score]) -> list[AgregatModele]:
    """Un agrégat par fournisseur actif, classé par score global décroissant."""
    index_items = {item.id: item for item in items}
    agregats = [
        agreger_modele(f.id, f.nom, f.editeur, index_items, scores)
        for f in config.fournisseurs_actifs
    ]
    # Classement stable : à score égal, l'ordre alphabétique tranche.
    return sorted(agregats, key=lambda a: (-a.score_global, a.fournisseur_id))


def resume(
    config: Config,
    items: list[Item],
    scores: list[Score],
    agregats: list[AgregatModele],
    nb_entrees_revue: int = 0,
) -> dict:
    """Résumé lisible du run, écrit dans resume.json."""
    origines: dict[str, int] = defaultdict(int)
    for score in scores:
        origines[score.origine] += 1

    return {
        "corpus": config.corpus.value,
        "nb_items": len(items),
        "nb_runs": config.execution.nb_runs,
        "nb_scores": len(scores),
        "note_max_par_reponse": NOTE_MAX,
        "origine_des_scores": dict(sorted(origines.items())),
        "nb_entrees_revue_humaine": nb_entrees_revue,
        "classement": [
            {
                "rang": rang,
                "fournisseur_id": a.fournisseur_id,
                "nom": a.nom,
                "editeur": a.editeur,
                "score_global": a.score_global,
                "taux_hallucination_source": a.taux_hallucination_source,
                "ecart_type": a.ecart_type,
            }
            for rang, a in enumerate(agregats, start=1)
        ],
        "modeles": [a.as_dict() for a in agregats],
    }
