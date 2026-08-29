"""Protocole de QA humaine (spécification §17).

Le juge est faillible, et l'annotation humaine aussi. On mesure donc l'accord
entre annotateurs avant de décider qu'un axe est assez fiable pour être publié.
Un kappa bas ne veut pas dire que les annotateurs sont mauvais : le plus souvent
il dit que la consigne est ambiguë.
"""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict

from pydantic import Field

from src.bench.jugement import Judgment, Verdict
from src.bench.modeles import ModeleStrict


class Annotation(ModeleStrict):
    """Le verdict d'un annotateur humain sur une réponse."""

    item_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    run_index: int = Field(ge=0)
    annotator: str = Field(min_length=1)
    verdict: Verdict
    note: str = ""

    @property
    def cle(self) -> tuple[str, str, int]:
        return (self.item_id, self.model_id, self.run_index)


def _par_unite(annotations: list[Annotation]) -> dict[tuple, dict[str, Verdict]]:
    groupes: dict[tuple, dict[str, Verdict]] = defaultdict(dict)
    for annotation in annotations:
        groupes[annotation.cle][annotation.annotator] = annotation.verdict
    return groupes


def cohen_kappa(annotations: list[Annotation]) -> float | None:
    """Accord entre exactement deux annotateurs, corrigé du hasard.

    None si le jeu ne s'y prête pas (moins de deux annotateurs, aucune unité
    doublement annotée). Renvoie 1.0 quand les deux sont d'accord partout, y
    compris s'ils n'ont utilisé qu'une seule catégorie : l'accord est total, même
    si le kappa classique est alors indéfini.
    """
    annotateurs = sorted({a.annotator for a in annotations})
    if len(annotateurs) != 2:
        return None
    a, b = annotateurs

    paires = [
        (verdicts[a], verdicts[b])
        for verdicts in _par_unite(annotations).values()
        if a in verdicts and b in verdicts
    ]
    if not paires:
        return None

    total = len(paires)
    observe = sum(1 for x, y in paires if x is y) / total

    compte_a = Counter(x for x, _ in paires)
    compte_b = Counter(y for _, y in paires)
    categories = set(compte_a) | set(compte_b)
    hasard = sum((compte_a[c] / total) * (compte_b[c] / total) for c in categories)

    if hasard >= 1.0:
        return 1.0 if observe >= 1.0 else 0.0
    return round((observe - hasard) / (1 - hasard), 4)


def fleiss_kappa(annotations: list[Annotation]) -> float | None:
    """Accord entre trois annotateurs ou plus.

    N'utilise que les unités annotées par tout le monde : mélanger des unités
    vues par deux et par cinq annotateurs fausse la correction du hasard.
    """
    annotateurs = sorted({a.annotator for a in annotations})
    if len(annotateurs) < 3:
        return None

    groupes = _par_unite(annotations)
    complets = [v for v in groupes.values() if len(v) == len(annotateurs)]
    if not complets:
        return None

    n = len(annotateurs)
    N = len(complets)
    categories = sorted({v.value for verdicts in complets for v in verdicts.values()})
    if len(categories) < 2:
        return 1.0  # tout le monde d'accord sur une seule catégorie

    accord_par_unite = []
    totaux = Counter()
    for verdicts in complets:
        compte = Counter(v.value for v in verdicts.values())
        totaux.update(compte)
        accord_par_unite.append(
            (sum(c * c for c in compte.values()) - n) / (n * (n - 1))
        )

    p_moyen = sum(accord_par_unite) / N
    p_hasard = sum((totaux[c] / (N * n)) ** 2 for c in categories)

    if p_hasard >= 1.0:
        return 1.0 if p_moyen >= 1.0 else 0.0
    return round((p_moyen - p_hasard) / (1 - p_hasard), 4)


def kappa(annotations: list[Annotation]) -> float | None:
    """Choisit Cohen ou Fleiss selon le nombre d'annotateurs."""
    nombre = len({a.annotator for a in annotations})
    if nombre == 2:
        return cohen_kappa(annotations)
    if nombre >= 3:
        return fleiss_kappa(annotations)
    return None


class Desaccord(ModeleStrict):
    """Une unité sur laquelle les annotateurs ne se rejoignent pas."""

    item_id: str
    model_id: str
    run_index: int
    verdicts: dict[str, str]

    @property
    def cle(self) -> tuple[str, str, int]:
        return (self.item_id, self.model_id, self.run_index)


def desaccords(annotations: list[Annotation]) -> list[Desaccord]:
    """Les unités à arbitrer, dans un ordre stable."""
    trouves: list[Desaccord] = []
    for (item_id, model_id, run_index), verdicts in sorted(_par_unite(annotations).items()):
        if len({v for v in verdicts.values()}) > 1:
            trouves.append(
                Desaccord(
                    item_id=item_id,
                    model_id=model_id,
                    run_index=run_index,
                    verdicts={a: v.value for a, v in sorted(verdicts.items())},
                )
            )
    return trouves


def resoudre(
    annotations: list[Annotation], arbitrages: dict[tuple[str, str, int], Verdict]
) -> dict[tuple[str, str, int], Verdict]:
    """Verdict humain retenu par unité : majorité, ou arbitrage s'il y a désaccord.

    Une unité en désaccord sans arbitrage n'est pas tranchée : elle est absente
    du résultat plutôt que résolue au hasard.
    """
    retenus: dict[tuple[str, str, int], Verdict] = {}

    for cle, verdicts in _par_unite(annotations).items():
        compte = Counter(verdicts.values())
        sommet, occurrences = compte.most_common(1)[0]
        majoritaire = occurrences > len(verdicts) / 2

        if cle in arbitrages:
            retenus[cle] = arbitrages[cle]
        elif majoritaire and len(compte) > 0:
            retenus[cle] = sommet

    return retenus


def appliquer_annotations(
    jugements: list[Judgment], verdicts_humains: dict[tuple[str, str, int], Verdict]
) -> list[Judgment]:
    """Reporte les verdicts humains sur les jugements. L'humain prime sur le juge.

    Les jugements d'origine ne sont pas mutés : on rend des copies, pour que le
    verdict du juge reste consultable à côté de celui qui l'a corrigé.
    """
    corriges: list[Judgment] = []
    for jugement in jugements:
        cle = (jugement.item_id, jugement.model_id, jugement.run_index)
        humain = verdicts_humains.get(cle)
        corriges.append(
            jugement.model_copy(update={"human_verdict": humain}) if humain else jugement
        )
    return corriges


class SeuilsQA(ModeleStrict):
    """Seuils au-delà desquels un axe est jugé assez fiable pour être publié."""

    kappa_minimum: float = Field(default=0.6, ge=0.0, le=1.0)
    #: Part minimale des réponses escaladées effectivement revues par un humain.
    couverture_revue_minimum: float = Field(default=0.9, ge=0.0, le=1.0)
    #: Part des jugements du juge confirmés par l'audit aléatoire.
    accord_audit_minimum: float = Field(default=0.8, ge=0.0, le=1.0)


def publiable(
    jugements: list[Judgment],
    annotations: list[Annotation],
    seuils: SeuilsQA | None = None,
) -> dict:
    """Dit si la campagne est assez fiable pour être publiée, et pourquoi.

    Ne rend jamais un simple booléen sans ses raisons : un refus de publication
    doit pouvoir être discuté chiffre en main.
    """
    seuils = seuils or SeuilsQA()

    valeur_kappa = kappa(annotations)
    escalades = [j for j in jugements if j.escalated]
    revues = {(a.item_id, a.model_id, a.run_index) for a in annotations}
    couverture = (
        len([j for j in escalades if (j.item_id, j.model_id, j.run_index) in revues])
        / len(escalades)
        if escalades
        else 1.0
    )

    audites = [
        j
        for j in jugements
        if "random_audit" in j.escalation_reasons and j.human_verdict is not None
    ]
    accord = (
        sum(1 for j in audites if j.human_verdict is j.verdict) / len(audites)
        if audites
        else 1.0
    )

    blocages: list[str] = []
    if valeur_kappa is None:
        blocages.append(
            "kappa incalculable : la double annotation indépendante n'a pas eu lieu"
        )
    elif valeur_kappa < seuils.kappa_minimum:
        blocages.append(
            f"kappa {valeur_kappa} sous le seuil {seuils.kappa_minimum} : "
            "l'accord entre annotateurs est trop faible pour publier"
        )
    if couverture < seuils.couverture_revue_minimum:
        blocages.append(
            f"couverture de revue {round(couverture, 3)} sous le seuil "
            f"{seuils.couverture_revue_minimum} : des escalades n'ont pas été revues"
        )
    if accord < seuils.accord_audit_minimum:
        blocages.append(
            f"accord d'audit {round(accord, 3)} sous le seuil "
            f"{seuils.accord_audit_minimum} : le juge n'est pas assez fiable"
        )

    return {
        "publishable": not blocages,
        "kappa": valeur_kappa,
        "review_coverage": round(couverture, 4),
        "audit_agreement": round(accord, 4),
        "escalated": len(escalades),
        "blockers": blocages,
    }
