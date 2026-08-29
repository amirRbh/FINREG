"""Pipeline de jugement : déterministe → juge LLM → escalade → revue humaine.

Le juge est un composant faillible. Il est donc encadré de deux façons : il ne
sait pas quel modèle il note, et son verdict part en revue humaine dès qu'il
touche à ce qui se juge mal (citations, prémisses, abstentions) ou dès qu'il
contredit ce que le déterministe a établi.
"""

from __future__ import annotations

import hashlib
import json
import re
from enum import Enum

from pydantic import Field, ValidationError

from src.bench.items import Item
from src.bench.jugement import (
    DeterministicFindings,
    Judgment,
    JudgmentOrigin,
    ObservedBehavior,
    Verdict,
    analyser,
)
from src.bench.modeles import ModeleStrict
from src.bench.reponses import ModelResponse
from src.bench.vocabulaires import ExpectedBehavior, QuestionType
from src.scoring.references import Registre


class EscalationReason(str, Enum):
    """Motifs d'escalade vers la revue humaine (spécification §16)."""

    DETERMINISTIC_JUDGE_DISAGREEMENT = "deterministic_judge_disagreement"
    CRITICAL_ERROR = "critical_error"
    CONTAINS_CITATION = "contains_citation"
    FALSE_PREMISE_ITEM = "false_premise_item"
    ABSTENTION_ITEM = "abstention_item"
    RANDOM_AUDIT = "random_audit"


class JudgePacket(ModeleStrict):
    """Exactement ce que le juge reçoit. Rien de plus.

    Le nom du modèle n'y figure pas : un juge qui sait qu'il note « le gros
    modèle du fournisseur X » ne note plus la réponse.
    """

    question: str
    gold_answer: str
    key_points: list[str]
    disqualifying_errors: list[str]
    expected_behavior: str
    model_answer: str

    def to_prompt(self) -> str:
        erreurs = [f"- {e}" for e in self.disqualifying_errors] or ["- (aucune)"]
        blocs = [
            "QUESTION", self.question, "",
            "RÉPONSE DE RÉFÉRENCE", self.gold_answer, "",
            "POINTS CLÉS ATTENDUS", *(f"- {p}" for p in self.key_points), "",
            "ERREURS DISQUALIFIANTES", *erreurs, "",
            "COMPORTEMENT ATTENDU", self.expected_behavior, "",
            "RÉPONSE À NOTER", self.model_answer or "(réponse vide)",
        ]
        return "\n".join(blocs)


def construire_paquet(item: Item, reponse: ModelResponse) -> JudgePacket:
    return JudgePacket(
        question=item.question,
        gold_answer=item.gold_answer,
        key_points=list(item.key_points),
        disqualifying_errors=list(item.disqualifying_errors),
        expected_behavior=item.expected_behavior.value,
        model_answer=reponse.text,
    )


class JudgeOutput(ModeleStrict):
    """Sortie JSON stricte du juge. Une sortie non conforme est une erreur."""

    verdict: Verdict
    rationale: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class SortieJugeInvalide(RuntimeError):
    """Le juge n'a pas rendu le JSON attendu. On ne devine pas un verdict."""


_BLOC = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


def analyser_sortie_juge(texte: str) -> JudgeOutput:
    candidat = texte.strip()
    bloc = _BLOC.match(candidat)
    if bloc:
        candidat = bloc.group(1).strip()
    if not candidat.startswith("{"):
        debut, fin = candidat.find("{"), candidat.rfind("}")
        if debut == -1 or fin <= debut:
            raise SortieJugeInvalide("aucun objet JSON dans la sortie du juge")
        candidat = candidat[debut : fin + 1]
    try:
        donnees = json.loads(candidat)
    except json.JSONDecodeError as exc:
        raise SortieJugeInvalide(f"JSON illisible : {exc}") from exc
    try:
        return JudgeOutput.model_validate(donnees)
    except ValidationError as exc:
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])} : {e['msg']}" for e in exc.errors()
        )
        raise SortieJugeInvalide(f"sortie non conforme : {detail}") from exc


def audit_aleatoire(item_id: str, model_id: str, run_index: int, taux: float) -> bool:
    """Sélection d'audit reproductible.

    Tirée d'un hash plutôt que d'un générateur aléatoire : deux exécutions du
    même run auditent exactement les mêmes réponses, sinon le run n'est pas
    reproductible.
    """
    if taux <= 0:
        return False
    if taux >= 1:
        return True
    graine = f"{item_id}|{model_id}|{run_index}".encode("utf-8")
    tirage = int(hashlib.sha256(graine).hexdigest()[:8], 16) / 0xFFFFFFFF
    return tirage < taux


def verdict_deterministe(item: Item, findings: DeterministicFindings) -> Verdict | None:
    """Ce que le déterministe tranche seul, ou None s'il ne tranche pas.

    Il ne tranche que dans un sens : vers l'erreur. Une erreur disqualifiante ou
    un comportement non conforme suffit à conclure ; rien de mécanique ne permet
    de conclure qu'une réponse est juste sur le fond.
    """
    if findings.observed_behavior is ObservedBehavior.NO_RESPONSE:
        return Verdict.NOT_EVALUABLE
    if findings.has_critical_error:
        return Verdict.INCORRECT
    if not findings.behavior_conform:
        return Verdict.INCORRECT
    return None


def motifs_escalade(
    item: Item,
    findings: DeterministicFindings,
    verdict_juge: Verdict,
    model_id: str,
    run_index: int,
    taux_audit: float,
) -> list[EscalationReason]:
    """Les six motifs de la spécification §16."""
    motifs: list[EscalationReason] = []

    tranche = verdict_deterministe(item, findings)
    if tranche is not None and tranche is not verdict_juge:
        motifs.append(EscalationReason.DETERMINISTIC_JUDGE_DISAGREEMENT)
    if findings.has_critical_error:
        motifs.append(EscalationReason.CRITICAL_ERROR)
    if findings.contains_citation:
        motifs.append(EscalationReason.CONTAINS_CITATION)
    if item.question_type is QuestionType.FALSE_PREMISE:
        motifs.append(EscalationReason.FALSE_PREMISE_ITEM)
    if item.expected_behavior in (
        ExpectedBehavior.ABSTAIN,
        ExpectedBehavior.REQUEST_MISSING_INFORMATION,
    ):
        motifs.append(EscalationReason.ABSTENTION_ITEM)
    if audit_aleatoire(item.id, model_id, run_index, taux_audit):
        motifs.append(EscalationReason.RANDOM_AUDIT)

    return motifs


class JudgeProtocol:
    """Un juge : reçoit un paquet anonyme, rend un JSON strict."""

    def juger(self, paquet: JudgePacket) -> str:  # pragma: no cover - interface
        raise NotImplementedError


def juger_reponse(
    item: Item,
    reponse: ModelResponse,
    registre: Registre,
    juge: JudgeProtocol,
    taux_audit: float = 0.05,
) -> Judgment:
    """Chaîne complète pour une réponse : déterministe, juge, escalade."""
    findings = analyser(item, reponse.text, registre)

    if not reponse.is_usable:
        # Une réponse en erreur n'est pas une mauvaise réponse : elle est absente.
        return Judgment(
            item_id=item.id,
            model_id=reponse.model_id,
            run_index=reponse.run_index,
            findings=findings,
            verdict=Verdict.NOT_EVALUABLE,
            rationale="Réponse absente : appel en erreur.",
            origin=JudgmentOrigin.DETERMINISTIC,
        )

    tranche = verdict_deterministe(item, findings)
    if tranche is Verdict.NOT_EVALUABLE:
        return Judgment(
            item_id=item.id,
            model_id=reponse.model_id,
            run_index=reponse.run_index,
            findings=findings,
            verdict=Verdict.NOT_EVALUABLE,
            rationale="Réponse vide.",
            origin=JudgmentOrigin.DETERMINISTIC,
        )

    sortie = analyser_sortie_juge(juge.juger(construire_paquet(item, reponse)))
    motifs = motifs_escalade(
        item, findings, sortie.verdict, reponse.model_id, reponse.run_index, taux_audit
    )

    return Judgment(
        item_id=item.id,
        model_id=reponse.model_id,
        run_index=reponse.run_index,
        findings=findings,
        verdict=sortie.verdict,
        rationale=sortie.rationale,
        confidence=sortie.confidence,
        origin=JudgmentOrigin.JUDGE,
        escalated=bool(motifs),
        escalation_reasons=[m.value for m in motifs],
    )
