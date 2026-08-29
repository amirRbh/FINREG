"""Juge LLM.

Il n'intervient qu'après l'étage déterministe et seulement pour ce que celui-ci
n'a pas tranché. Le barème est dans `prompts/judge.txt`, fichier versionné dont
le hash est tracé dans chaque run. La sortie est du JSON strict : une sortie non
conforme est une erreur, jamais une note par défaut (CLAUDE.md §6).
"""

from __future__ import annotations

import json
import re

from pydantic import ValidationError

from src.providers.base import Fournisseur, Requete
from src.schema import (
    ConstatDeterministe,
    Corpus,
    Item,
    ReponseBrute,
    Score,
    ScoreJuge,
)
from src.scoring.deterministe import appliquer_plafonds, notes_plancher, tranche_seul
from src.securite import verifier_autorisation

_BLOC_CODE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


class SortieJugeInvalide(RuntimeError):
    """Le juge n'a pas rendu le JSON attendu. On ne devine pas une note à sa place."""


def extraire_json(texte: str) -> dict:
    """Isole l'objet JSON de la réponse du juge, ou lève."""
    candidat = texte.strip()

    bloc = _BLOC_CODE.match(candidat)
    if bloc:
        candidat = bloc.group(1).strip()

    if not candidat.startswith("{"):
        # Certains modèles préfixent une phrase : on récupère le premier objet complet.
        debut = candidat.find("{")
        fin = candidat.rfind("}")
        if debut == -1 or fin <= debut:
            raise SortieJugeInvalide("aucun objet JSON trouvé dans la sortie du juge")
        candidat = candidat[debut : fin + 1]

    try:
        donnees = json.loads(candidat)
    except json.JSONDecodeError as exc:
        raise SortieJugeInvalide(f"JSON illisible dans la sortie du juge : {exc}") from exc

    if not isinstance(donnees, dict):
        raise SortieJugeInvalide("la sortie du juge n'est pas un objet JSON")
    return donnees


def analyser_sortie(texte: str) -> ScoreJuge:
    try:
        return ScoreJuge.model_validate(extraire_json(texte))
    except ValidationError as exc:
        messages = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])} : {e['msg']}" for e in exc.errors()
        )
        raise SortieJugeInvalide(f"sortie du juge non conforme au schéma : {messages}") from exc


def construire_message(item: Item, reponse: str, constat: ConstatDeterministe) -> str:
    """Assemble ce que le juge voit. Format stable : il entre dans le hash du run."""
    lignes = [
        f"QUESTION ({item.domaine}, type {item.type.value}, difficulté {item.difficulte})",
        item.question,
        "",
        "RÉPONSE DE RÉFÉRENCE",
        item.reponse_reference,
        "",
        "POINTS CLÉS ATTENDUS",
        *(f"- {point}" for point in item.points_cles),
        "",
        "SOURCE DE RÉFÉRENCE",
        f"{item.source.texte} — {item.source.article}",
        "",
        "RÉPONSE À NOTER",
        reponse if reponse.strip() else "(réponse vide)",
    ]

    if constat.references_inventees or constat.erreurs_disqualifiantes_detectees:
        lignes += ["", "CONSTAT AUTOMATIQUE (déjà pris en compte, ne le note pas deux fois)"]
        if constat.references_inventees:
            lignes.append(
                "- références non reconnues : " + ", ".join(constat.references_inventees)
            )
        if constat.erreurs_disqualifiantes_detectees:
            lignes.append(
                "- erreurs disqualifiantes détectées : "
                + ", ".join(constat.erreurs_disqualifiantes_detectees)
            )

    return "\n".join(lignes)


class Juge:
    """Enveloppe un fournisseur pour l'usage « notation »."""

    def __init__(self, fournisseur: Fournisseur, prompt: str, temperature: float = 0.0) -> None:
        self.fournisseur = fournisseur
        self.prompt = prompt
        self.temperature = temperature

    async def noter(
        self,
        item: Item,
        reponse: ReponseBrute,
        constat: ConstatDeterministe,
        timeout_s: float = 60.0,
    ) -> Score:
        # Le juge reçoit le texte de l'item : il est soumis au même garde-fou.
        verifier_autorisation(item.corpus, self.fournisseur)

        if tranche_seul(constat):
            # Rien ne reste à apprécier : inutile de payer un appel de juge.
            return Score(
                item_id=item.id,
                fournisseur_id=reponse.fournisseur_id,
                index_run=reponse.index_run,
                notes=notes_plancher(constat),
                flags=constat.flags,
                constat=constat,
                justification="Tranché par l'étage déterministe, sans recours au juge.",
                origine="deterministe",
            )

        requete = Requete(
            prompt_systeme=self.prompt,
            question=construire_message(item, reponse.texte, constat),
            temperature=self.temperature,
        )
        sortie = await self.fournisseur.completer(requete, timeout_s)
        rendu = analyser_sortie(sortie)

        return Score(
            item_id=item.id,
            fournisseur_id=reponse.fournisseur_id,
            index_run=reponse.index_run,
            notes=appliquer_plafonds(rendu.notes, constat),
            flags=constat.flags,
            constat=constat,
            justification=rendu.justification,
            origine="juge",
        )


def verifier_juge_autorise(corpus: Corpus, fournisseur: Fournisseur) -> None:
    """Contrôle préalable, avant toute session de notation."""
    verifier_autorisation(corpus, fournisseur)
