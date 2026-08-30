"""Prépare le pack d'arbitrage P0/P1, et sait le réinjecter une fois rempli.

Préparer et appliquer sont deux commandes distinctes, et c'est volontaire : le
pack sort avec ses colonnes de décision vides, et rien ne les remplit tant qu'un
relecteur ne l'a pas fait. `appliquer_revue` traduit ensuite ses décisions dans
le vocabulaire du registre, sans jamais en inventer une.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from src.bench.audit_rulebook import texte_de_la_regle
from src.bench.dossier_revue import DecisionRevue, DossierRevue, construire_dossier
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.bench.rapport_revue import (
    AVANCEMENT_REVUE,
    BORDEREAU_REVUE,
    CORRESPONDANCE_DECISIONS,
    FILE_REVUE,
    avancement,
    ecrire_bordereau,
    file_de_revue,
    lire_bordereau,
)
from src.bench.readiness import evaluer
from src.bench.regles import Rule
from src.bench.rulebook import RuleStatus
from src.bench.sources_primaires import CACHE_PRIMAIRE, cles_articles, recuperateur_http
from src.bench.verification import SEPARATEUR_LISTE, Verification, VerificationInvalide
from scripts.auditer_completude import analyser_regle

#: Seules les deux premières priorités entrent dans ce pack (spécification §1).
PRIORITES_TRAITEES = ("P0", "P1")


def _compter(regles: list[Rule], etats: list) -> dict[str, int]:
    return {
        "validated": sum(1 for r in regles if r.status is RuleStatus.VALIDATED),
        "gold_ready": sum(1 for e in etats if e.gold_ready),
        "family_ready": sum(1 for e in etats if e.family_ready),
    }


def preparer_revue(
    racine: Path = RACINE_RULEBOOK,
    file_chemin: Path = FILE_REVUE,
    bordereau: Path = BORDEREAU_REVUE,
    avancement_chemin: Path = AVANCEMENT_REVUE,
    recuperateur=recuperateur_http,
    cache: Path | None = CACHE_PRIMAIRE,
) -> dict:
    """Construit les dossiers P0/P1 et écrit le pack de revue."""
    regles = charger_rulebook(racine)
    dossiers: list[DossierRevue] = []
    etats = []

    for regle in regles:
        constat = analyser_regle(regle, recuperateur, cache)
        etat = evaluer(regle, constat)
        etats.append(etat)
        if etat.priorite_revue not in PRIORITES_TRAITEES:
            continue
        trouve = texte_de_la_regle(regle, recuperateur, cache)
        articles = trouve.texte.articles if trouve.texte else {}
        cle = (cles_articles(regle.source.article) or [""])[0]
        dossiers.append(construire_dossier(regle, constat, etat, articles, cle))

    Path(file_chemin).parent.mkdir(parents=True, exist_ok=True)
    Path(file_chemin).write_text(file_de_revue(dossiers), encoding="utf-8")
    ecrire_bordereau(dossiers, Path(bordereau))

    decisions = lire_bordereau(Path(bordereau))
    compte = _compter(regles, etats)
    Path(avancement_chemin).write_text(
        avancement(dossiers, {k: v["reviewer_decision"] for k, v in decisions.items()},
                   compte, compte),
        encoding="utf-8",
    )

    clusters: dict[str, list[str]] = {}
    for dossier in dossiers:
        clusters.setdefault(dossier.review_cluster_id, []).append(dossier.rule_id)

    return {
        "dossiers": len(dossiers),
        "p0": sum(1 for d in dossiers if d.priorite == "P0"),
        "p1": sum(1 for d in dossiers if d.priorite == "P1"),
        "clusters": len(clusters),
        "clusters_partages": sum(1 for r in clusters.values() if len(r) > 1),
        "arbitrages_economises": sum(len(r) - 1 for r in clusters.values() if len(r) > 1),
        "avec_dispositions": sum(1 for d in dossiers if d.dispositions),
        "queue": str(file_chemin),
        "bordereau": str(bordereau),
        "avancement": str(avancement_chemin),
    }


def decisions_en_verifications(
    bordereau: Path = BORDEREAU_REVUE,
) -> list[Verification]:
    """Traduit les décisions du relecteur en constats de vérification.

    Aucune décision n'est inventée : seules les lignes portant un
    `reviewer_decision` sont converties, et le schéma refuse ensuite ce que la
    décision ne justifie pas — une absence sans périmètre, une reformulation
    sans énoncé, une promotion sans signature.
    """
    verifications: list[Verification] = []
    erreurs: list[str] = []

    for rule_id, ligne in lire_bordereau(bordereau).items():
        brut = (ligne.get("reviewer_decision") or "").strip().upper()
        try:
            decision = DecisionRevue(brut)
        except ValueError:
            erreurs.append(
                f"{rule_id} : décision « {brut} » inconnue "
                f"({', '.join(d.value for d in DecisionRevue)})"
            )
            continue

        verdict, exceptions_status = CORRESPONDANCE_DECISIONS[decision]
        donnees: dict = {
            "rule_id": rule_id,
            "verdict": verdict,
            "verification_method": "primary_text_review",
            "verified_by": (ligne.get("reviewer_name") or "").strip(),
            "comment": (ligne.get("review_notes") or "").strip(),
            "source_scope": (ligne.get("source_scope") or "").strip(),
        }
        date = (ligne.get("review_date") or "").strip()
        if date:
            try:
                donnees["verification_date"] = dt.date.fromisoformat(date)
            except ValueError:
                erreurs.append(f"{rule_id} : review_date « {date} » n'est pas une date")
                continue
        if exceptions_status:
            donnees["exceptions_status"] = exceptions_status
        exceptions = [
            e.strip()
            for e in (ligne.get("exceptions_constatees") or "").split("|")
            if e.strip()
        ]
        if exceptions:
            donnees["exceptions"] = exceptions
        if decision is DecisionRevue.RULE_REFORMULATED:
            donnees["statement"] = (ligne.get("enonce_reformule") or "").strip()
        if decision is not DecisionRevue.REQUIRES_FURTHER_REVIEW:
            # La décision lève un blocage ; elle ne décrète pas que la règle est
            # validée. `validated` exige en outre une décision sur gold_ready,
            # que le relecteur n'a pas à porter : c'est le calcul de complétude
            # qui la proposera au tour suivant, sur la règle telle qu'elle est
            # devenue. C'est l'exigence du §14 — une décision humaine ne se
            # transforme jamais d'elle-même en exploitabilité.
            donnees["target_status"] = "source_checked"

        try:
            verifications.append(Verification.model_validate(donnees))
        except Exception as exc:
            erreurs.append(f"{rule_id} : {exc}")

    if erreurs:
        raise VerificationInvalide(erreurs)
    return verifications


if __name__ == "__main__":
    resultat = preparer_revue()
    print(f"{resultat['dossiers']} dossier(s) — P0 {resultat['p0']}, P1 {resultat['p1']}")
    print(f"  arbitrages distincts : {resultat['clusters']}")
    print(
        f"  groupes partagés : {resultat['clusters_partages']} "
        f"({resultat['arbitrages_economises']} arbitrage(s) économisé(s))"
    )
    print(f"  dossiers avec dispositions à examiner : {resultat['avec_dispositions']}")
    print(f"  file : {resultat['queue']}")
    print(f"  bordereau à remplir : {resultat['bordereau']}")
