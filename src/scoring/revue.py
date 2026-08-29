"""File de revue humaine.

Tout item dont le score du juge s'écarte de plus d'un point entre deux runs part
en revue humaine, exportée en CSV (CLAUDE.md §6). Le CSV se corrige à la main
puis se réinjecte : la note humaine prime sur celle du juge et reste tracée.

Le CSV est écrit en UTF-8 avec BOM et séparateur « ; » pour s'ouvrir directement
dans un tableur francophone sans manipulation.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from src.schema import AXES, Axe, Item, Score

ENCODAGE_CSV = "utf-8-sig"
SEPARATEUR_CSV = ";"

COLONNES = [
    "item_id",
    "fournisseur_id",
    "axe",
    "notes_par_run",
    "ecart",
    "note_humaine",
    "justification_humaine",
    "domaine",
    "type",
    "question",
    "reponse_reference",
]


@dataclass(frozen=True)
class EntreeRevue:
    """Un désaccord du juge avec lui-même, sur un axe donné, entre deux runs."""

    item_id: str
    fournisseur_id: str
    axe: Axe
    notes_par_run: dict[int, int]
    domaine: str = ""
    type_item: str = ""
    question: str = ""
    reponse_reference: str = ""

    @property
    def ecart(self) -> int:
        valeurs = list(self.notes_par_run.values())
        return max(valeurs) - min(valeurs) if valeurs else 0

    def cle(self) -> tuple[str, str, str]:
        return (self.item_id, self.fournisseur_id, self.axe.value)


def detecter_divergences(
    scores: list[Score], seuil: int = 1, items: dict[str, Item] | None = None
) -> list[EntreeRevue]:
    """Rend les entrées dont l'écart entre deux runs dépasse strictement `seuil`."""
    items = items or {}
    par_axe: dict[tuple[str, str, Axe], dict[int, int]] = defaultdict(dict)

    for score in scores:
        notes = score.notes.as_dict()
        for axe in AXES:
            par_axe[(score.item_id, score.fournisseur_id, axe)][score.index_run] = notes[axe.value]

    entrees: list[EntreeRevue] = []
    for (item_id, fournisseur_id, axe), notes_par_run in par_axe.items():
        if len(notes_par_run) < 2:
            continue
        if max(notes_par_run.values()) - min(notes_par_run.values()) <= seuil:
            continue
        item = items.get(item_id)
        entrees.append(
            EntreeRevue(
                item_id=item_id,
                fournisseur_id=fournisseur_id,
                axe=axe,
                notes_par_run=dict(sorted(notes_par_run.items())),
                domaine=item.domaine if item else "",
                type_item=item.type.value if item else "",
                question=item.question if item else "",
                reponse_reference=item.reponse_reference if item else "",
            )
        )

    return sorted(entrees, key=lambda e: e.cle())


def exporter_csv(entrees: list[EntreeRevue], chemin: Path) -> Path:
    """Écrit la file de revue. Les colonnes de correction sont laissées vides."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=COLONNES, delimiter=SEPARATEUR_CSV)
        redacteur.writeheader()
        for entree in entrees:
            redacteur.writerow(
                {
                    "item_id": entree.item_id,
                    "fournisseur_id": entree.fournisseur_id,
                    "axe": entree.axe.value,
                    "notes_par_run": " / ".join(
                        f"run {index} : {note}" for index, note in entree.notes_par_run.items()
                    ),
                    "ecart": entree.ecart,
                    "note_humaine": "",
                    "justification_humaine": "",
                    "domaine": entree.domaine,
                    "type": entree.type_item,
                    "question": entree.question,
                    "reponse_reference": entree.reponse_reference,
                }
            )

    return chemin


class CorrectionInvalide(ValueError):
    """Une ligne de CSV corrigée n'est pas exploitable. Rien n'est appliqué."""


@dataclass(frozen=True)
class CorrectionHumaine:
    item_id: str
    fournisseur_id: str
    axe: Axe
    note: int
    justification: str = ""


def lire_corrections(chemin: Path) -> list[CorrectionHumaine]:
    """Relit le CSV corrigé. Les lignes sans note humaine sont ignorées.

    Toute la lecture est validée avant de rendre quoi que ce soit : un fichier
    partiellement fautif ne s'applique pas à moitié.
    """
    corrections: list[CorrectionHumaine] = []
    erreurs: list[str] = []

    with Path(chemin).open("r", encoding=ENCODAGE_CSV, newline="") as flux:
        lecteur = csv.DictReader(flux, delimiter=SEPARATEUR_CSV)
        manquantes = {"item_id", "fournisseur_id", "axe", "note_humaine"} - set(
            lecteur.fieldnames or []
        )
        if manquantes:
            raise CorrectionInvalide(
                f"colonnes manquantes dans {chemin} : {sorted(manquantes)}"
            )

        for numero, ligne in enumerate(lecteur, start=2):
            brute = (ligne.get("note_humaine") or "").strip()
            if not brute:
                continue

            try:
                note = int(brute)
            except ValueError:
                erreurs.append(f"ligne {numero} : note_humaine « {brute} » n'est pas un entier")
                continue
            if not 0 <= note <= 2:
                erreurs.append(f"ligne {numero} : note_humaine « {note} » hors de l'intervalle 0–2")
                continue

            axe_brut = (ligne.get("axe") or "").strip()
            try:
                axe = Axe(axe_brut)
            except ValueError:
                erreurs.append(f"ligne {numero} : axe inconnu « {axe_brut} »")
                continue

            corrections.append(
                CorrectionHumaine(
                    item_id=(ligne.get("item_id") or "").strip(),
                    fournisseur_id=(ligne.get("fournisseur_id") or "").strip(),
                    axe=axe,
                    note=note,
                    justification=(ligne.get("justification_humaine") or "").strip(),
                )
            )

    if erreurs:
        raise CorrectionInvalide(
            f"{len(erreurs)} ligne(s) invalide(s), aucune correction appliquée :\n"
            + "\n".join(f"  - {e}" for e in erreurs)
        )

    return corrections


def appliquer_corrections(
    scores: list[Score], corrections: list[CorrectionHumaine]
) -> list[Score]:
    """Réinjecte les notes humaines. La correction prime et remplace tous les runs.

    Une divergence entre runs est justement ce que la revue tranche : la note
    humaine s'applique donc à tous les runs de ce couple (item, fournisseur).
    """
    index = {(c.item_id, c.fournisseur_id, c.axe): c for c in corrections}
    corriges: list[Score] = []

    for score in scores:
        notes = score.notes.as_dict()
        appliquees: list[CorrectionHumaine] = []

        for axe in AXES:
            correction = index.get((score.item_id, score.fournisseur_id, axe))
            if correction is not None:
                notes[axe.value] = correction.note
                appliquees.append(correction)

        if not appliquees:
            corriges.append(score)
            continue

        justifications = " ".join(c.justification for c in appliquees if c.justification)
        corriges.append(
            score.model_copy(
                update={
                    "notes": type(score.notes)(**notes),
                    "origine": "humain",
                    "justification": (
                        justifications
                        or f"Revue humaine : {', '.join(c.axe.value for c in appliquees)}."
                    ),
                }
            )
        )

    return corriges
