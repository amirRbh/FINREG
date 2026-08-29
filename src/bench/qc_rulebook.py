"""Contrôle qualité du Rulebook (spécification §17).

Rend une liste de constats plutôt qu'un booléen : un Rulebook se corrige à partir
d'un rapport, pas d'un échec global.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.bench.regles import Rule
from src.bench.rulebook import (
    METHODES_SUFFISANTES,
    NegativeClaimStatus,
    RuleStatus,
)

RACINE_RULEBOOK = Path("data/rules")

#: Domaines dont une URL trahit une source fabriquée.
DOMAINES_SOURCES_ATTENDUS = (
    "eur-lex.europa.eu",
    "legifrance.gouv.fr",
    "amf-france.org",
    "acpr.banque-france.fr",
    "economie.gouv.fr",
    "esma.europa.eu",
)

NIVEAUX = ("ERREUR", "AVERTISSEMENT", "INFO")


@dataclass(frozen=True)
class Constat:
    niveau: str
    regle_id: str
    controle: str
    message: str

    def __str__(self) -> str:
        return f"[{self.niveau}] {self.regle_id} — {self.controle} : {self.message}"


def charger_rulebook(racine: Path = RACINE_RULEBOOK) -> list[Rule]:
    """Charge toutes les règles du Rulebook, manifeste exclu."""
    regles: list[Rule] = []
    for chemin in sorted(Path(racine).glob("*.json")):
        if "manifest" in chemin.name:
            continue
        for brut in json.loads(chemin.read_text(encoding="utf-8")):
            regles.append(Rule.model_validate(brut))
    return regles


def controler(regles: list[Rule]) -> list[Constat]:
    """Tous les contrôles de la spécification §17, rapportés ensemble."""
    constats: list[Constat] = []
    ids = [r.id for r in regles]
    connus = set(ids)

    for regle in regles:
        rid = regle.id

        if ids.count(rid) > 1:
            constats.append(Constat("ERREUR", rid, "id_unique", "identifiant en double"))

        if not regle.statement.strip():
            constats.append(Constat("ERREUR", rid, "statement", "énoncé vide"))

        if not regle.source.url.strip():
            constats.append(Constat("ERREUR", rid, "source_url", "URL absente"))
        elif not any(d in regle.source.url for d in DOMAINES_SOURCES_ATTENDUS):
            constats.append(
                Constat(
                    "ERREUR", rid, "source_fictive",
                    f"URL hors des domaines officiels attendus : {regle.source.url}",
                )
            )

        if not regle.source.article.strip():
            constats.append(Constat("ERREUR", rid, "source_article", "article absent"))

        if not regle.regulatory_regime.strip():
            constats.append(Constat("ERREUR", rid, "regulatory_regime", "régime absent"))

        if regle.source.version_date is None:
            constats.append(Constat("ERREUR", rid, "version_date", "date de version absente"))

        if regle.status is RuleStatus.VALIDATED and regle.source.verification_date is None:
            constats.append(
                Constat("ERREUR", rid, "validated_sans_verification",
                        "statut validated sans date de vérification")
            )

        for cible in regle.related_rules:
            if cible not in connus:
                constats.append(
                    Constat("ERREUR", rid, "related_rules", f"règle liée inconnue « {cible} »")
                )

        for revendication in regle.negative_claims:
            if (
                revendication.status is NegativeClaimStatus.VERIFIED_ABSENT
                and revendication.verification_method not in METHODES_SUFFISANTES
            ):
                constats.append(
                    Constat("ERREUR", rid, "negative_claim",
                            "absence déclarée vérifiée sans consultation du texte primaire")
                )

        # Avertissements : ce qui n'invalide pas mais limite l'exploitation.
        if regle.needs_verification:
            constats.append(
                Constat("AVERTISSEMENT", rid, "verification",
                        f"source non consultée ({regle.verification_method.value})")
            )
        if regle.exceptions_status.value == "unknown":
            constats.append(
                Constat("AVERTISSEMENT", rid, "exceptions",
                        "exceptions inconnues : la règle peut produire une question simplifiée")
            )
        if not regle.operational_rule.strip():
            constats.append(
                Constat("AVERTISSEMENT", rid, "operational_rule", "interprétation opérationnelle absente")
            )
        if not regle.common_confusions:
            constats.append(
                Constat("AVERTISSEMENT", rid, "common_confusions", "aucune confusion typique identifiée")
            )
        if not regle.candidate_question_families:
            constats.append(
                Constat("AVERTISSEMENT", rid, "candidate_question_families", "aucune famille suggérée")
            )
        if not regle.reasoning_traps:
            constats.append(
                Constat("AVERTISSEMENT", rid, "reasoning_traps", "aucun piège identifié")
            )

    constats.extend(_doublons_conceptuels(regles))
    return sorted(constats, key=lambda c: (NIVEAUX.index(c.niveau), c.regle_id, c.controle))


def _normaliser_titre(titre: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", titre.lower()).strip()


def _doublons_conceptuels(regles: list[Rule]) -> list[Constat]:
    """Deux règles du même domaine visant le même article et le même type."""
    constats: list[Constat] = []
    vus: dict[tuple[str, str, str], str] = {}
    for regle in regles:
        cle = (regle.domain.value, regle.source.article.strip().lower(), regle.rule_type.value)
        if cle in vus:
            constats.append(
                Constat(
                    "AVERTISSEMENT", regle.id, "doublon_conceptuel",
                    f"même domaine, même article et même type que « {vus[cle]} »",
                )
            )
        else:
            vus[cle] = regle.id
    return constats


def erreurs(constats: list[Constat]) -> list[Constat]:
    return [c for c in constats if c.niveau == "ERREUR"]


def rapport_markdown(regles: list[Rule], constats: list[Constat]) -> str:
    """Rapport RULEBOOK_QC.md : ce qui bloque, ce qui limite, et ce qui reste à faire."""
    par_niveau = {n: [c for c in constats if c.niveau == n] for n in NIVEAUX}

    lignes = [
        "# Rulebook — contrôle qualité",
        "",
        "Rapport généré par `src/bench/qc_rulebook.py`. Il liste ce qui bloque",
        "l'exploitation du Rulebook et ce qui la limite.",
        "",
        "## Synthèse",
        "",
        f"- règles : **{len(regles)}**",
        f"- erreurs bloquantes : **{len(par_niveau['ERREUR'])}**",
        f"- avertissements : **{len(par_niveau['AVERTISSEMENT'])}**",
        "",
        "## État de vérification",
        "",
        f"- règles dont la source n'a pas été consultée : "
        f"**{sum(1 for r in regles if r.needs_verification)} / {len(regles)}**",
        f"- règles utilisables pour ancrer un gold : "
        f"**{sum(1 for r in regles if r.is_usable)} / {len(regles)}**",
        "",
        "> Les sources primaires (EUR-Lex, Légifrance, AMF, ACPR, TRACFIN, ESMA) sont",
        "> inaccessibles depuis l'environnement de génération. Aucune règle ne peut donc",
        "> dépasser le statut `draft`, et **aucune n'est utilisable pour ancrer un gold**.",
        "> C'est une propriété tenue par le schéma, pas une convention.",
        "",
    ]

    for niveau in NIVEAUX:
        trouves = par_niveau[niveau]
        if not trouves:
            continue
        lignes += [f"## {niveau.capitalize()}s ({len(trouves)})", ""]
        groupes: dict[str, list[Constat]] = {}
        for constat in trouves:
            groupes.setdefault(constat.controle, []).append(constat)
        for controle, elements in sorted(groupes.items()):
            lignes.append(f"### `{controle}` — {len(elements)}")
            lignes.append("")
            for constat in elements[:20]:
                lignes.append(f"- `{constat.regle_id}` : {constat.message}")
            if len(elements) > 20:
                lignes.append(f"- … et {len(elements) - 20} autre(s)")
            lignes.append("")

    return "\n".join(lignes) + "\n"
