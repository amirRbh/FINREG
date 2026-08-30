"""Contrôle qualité du Question Family Map (phase 7 §16).

Comme le QC du Rulebook, ce module rend une liste de constats plutôt qu'un
booléen : une carte se corrige à partir d'un rapport, pas d'un échec global.

Les onze contrôles de la spécification §16 sont ici, plus ceux que la structure
rend possibles : cohérence d'un identifiant avec sa règle, réciprocité d'un
couple de jumeaux, motivation d'un blocage. Le contrôle central est le second —
**aucune règle `draft` ne produit de famille finalisable** : c'est le verrou du
Rulebook, transporté à la carte.
"""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter, defaultdict
from pathlib import Path

from src.bench.carte_familles import (
    RENDEMENT_PAR_SCORE,
    faisabilite_distribution,
    lacunes,
    redondances,
)
from src.bench.familles import (
    CODES_FAMILLES,
    CandidateFamily,
    CandidateFamilyStatus,
    FamilyKind,
    ORDRE_FAMILLES,
    SCORE_RETENU,
)
from src.bench.qc_rulebook import Constat, NIVEAUX
from src.bench.regles import Rule
from src.bench.rulebook import Priority, RuleStatus
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV
from src.io_utils import ecrire_json, hash_json, lire_json
from src.bench.vocabulaires import (
    Answerability,
    Domain,
    ExpectedBehavior,
    QuestionType,
    ReasoningTrap,
    REPONDABILITE_PAR_COMPORTEMENT,
)

RACINE_FAMILLES = Path("data/families")
RAPPORT_FAMILLES = Path("reports/FAMILY_MAP_QC.md")
MATRICE_FAMILLES = Path("reports/FAMILY_COVERAGE_MATRIX.csv")

#: Pas d'horodatage dans les artefacts : la carte doit être reproductible.
DATE_GENERATION = dt.date(2026, 8, 29)

VERSION_CARTE = "v0.1.0"

#: Colonnes de la matrice de couverture, dans l'ordre de lecture d'un humain :
#: d'abord où l'on est, puis ce qu'on mesure, puis ce que cela vaut.
COLONNES_MATRICE = (
    "domain",
    "rule_id",
    "rule_type",
    "rule_status",
    "rule_priority",
    "family_code",
    "family_kind",
    "family_id",
    "family_score",
    "retained",
    "question_type",
    "reasoning_trap",
    "predicted_difficulty",
    "priority",
    "candidate_family_status",
    "twin_group_id",
    "twin_type",
    "concept_tested",
    "redundancy_group_id",
    "family_rationale",
)


def chemin_domaine(domaine: Domain, racine: Path = RACINE_FAMILLES) -> Path:
    """Un fichier de familles par domaine, comme le Rulebook range ses règles."""
    return Path(racine) / f"{domaine.value.lower()}-families.json"


def charger_par_fichier(
    racine: Path = RACINE_FAMILLES,
) -> dict[Path, list[CandidateFamily]]:
    """Charge la carte en gardant l'origine de chaque famille, manifeste exclu."""
    par_fichier: dict[Path, list[CandidateFamily]] = {}
    for chemin in sorted(Path(racine).glob("*.json")):
        if "manifest" in chemin.name:
            continue
        par_fichier[chemin] = [
            CandidateFamily.model_validate(brut) for brut in lire_json(chemin)
        ]
    return par_fichier


def charger_familles(racine: Path = RACINE_FAMILLES) -> list[CandidateFamily]:
    """Charge toutes les familles candidates de la carte."""
    return [f for familles in charger_par_fichier(racine).values() for f in familles]


def ecrire_carte(
    familles: list[CandidateFamily], racine: Path = RACINE_FAMILLES
) -> dict[str, int]:
    """Écrit la carte, un fichier par domaine, et rend le compte par fichier.

    Un domaine sans famille reçoit tout de même son fichier, vide : l'absence
    doit se lire dans la carte, pas dans un fichier manquant.
    """
    comptes: dict[str, int] = {}
    for domaine in Domain:
        chemin = chemin_domaine(domaine, racine)
        concernees = sorted(
            (f for f in familles if f.domain is domaine), key=lambda f: f.id
        )
        ecrire_json(chemin, [f.model_dump(mode="json") for f in concernees])
        comptes[chemin.stem] = len(concernees)
    return comptes


def controler(familles: list[CandidateFamily], regles: list[Rule]) -> list[Constat]:
    """Les contrôles de la spécification §16, rapportés d'un seul coup."""
    constats: list[Constat] = []
    par_id = {r.id: r for r in regles}
    identifiants = [f.id for f in familles]

    for famille in familles:
        fid = famille.id

        # 1. chaque famille référence une règle existante
        regle = par_id.get(famille.rule_id)
        if regle is None:
            constats.append(
                Constat("ERREUR", fid, "regle_inconnue", f"règle « {famille.rule_id} » absente du Rulebook")
            )
        else:
            if famille.domain is not regle.domain:
                constats.append(
                    Constat(
                        "ERREUR", fid, "domaine_incoherent",
                        f"domaine « {famille.domain.value} » alors que la règle est "
                        f"en « {regle.domain.value} »",
                    )
                )
            # 2. aucune règle draft ne produit de famille finalisable
            if (
                regle.status is RuleStatus.DRAFT
                and famille.candidate_family_status is not CandidateFamilyStatus.BLOCKED
            ):
                constats.append(
                    Constat(
                        "ERREUR", fid, "draft_finalisable",
                        f"règle « {regle.id} » en draft mais famille en "
                        f"« {famille.candidate_family_status.value} » : une famille "
                        f"destinée au benchmark ne peut pas s'ancrer sur une règle "
                        f"non vérifiée",
                    )
                )
            if famille.source.model_dump() != regle.source.model_dump():
                constats.append(
                    Constat("AVERTISSEMENT", fid, "source_derivee",
                            "la source de la famille diffère de celle de sa règle")
                )

        # 3. identifiants uniques
        if identifiants.count(fid) > 1:
            constats.append(Constat("ERREUR", fid, "id_unique", "identifiant de famille en double"))
        attendu = f"{famille.rule_id}-{CODES_FAMILLES[famille.family_kind]}"
        if fid != attendu:
            constats.append(
                Constat("ERREUR", fid, "id_derive", f"identifiant attendu « {attendu} »")
            )

        # 5 et 6. pièges des jumeaux
        if (
            famille.question_type is QuestionType.FALSE_PREMISE
            and famille.reasoning_trap is ReasoningTrap.NONE
        ):
            constats.append(
                Constat("ERREUR", fid, "fausse_premisse_sans_piege",
                        "fausse prémisse sans piège nommé : elle ne mesure rien")
            )
        if famille.question_type is QuestionType.TRUE_PREMISE_ADVERSARIAL:
            if famille.reasoning_trap is not ReasoningTrap.NONE:
                constats.append(
                    Constat("ERREUR", fid, "vraie_premisse_piegee",
                            f"prémisse vraie portant le piège « {famille.reasoning_trap.value} »")
                )
            if famille.mimicked_trap is None:
                constats.append(
                    Constat("ERREUR", fid, "vraie_premisse_sans_mimique",
                            "prémisse vraie sans mimicked_trap : rien ne dit à quel "
                            "piège elle ressemble, le jumeau n'est pas comparable")
                )

        # 7. comportement attendu cohérent avec la répondabilité
        admises = REPONDABILITE_PAR_COMPORTEMENT[famille.expected_behavior]
        if famille.answerability not in admises:
            constats.append(
                Constat(
                    "ERREUR", fid, "repondabilite_incoherente",
                    f"answerability « {famille.answerability.value} » incompatible "
                    f"avec expected_behavior « {famille.expected_behavior.value} »",
                )
            )

        # 8. aucune famille sans concept testé
        if not famille.concept_tested.strip():
            constats.append(Constat("ERREUR", fid, "concept_teste", "concept_tested vide"))

        # 10. aucune famille sans source
        for champ in ("text", "article", "url"):
            if not getattr(famille.source, champ).strip():
                constats.append(
                    Constat("ERREUR", fid, "source_absente", f"source.{champ} vide")
                )

        # 11. aucune famille temporelle sans régime réglementaire
        if famille.family_kind is FamilyKind.TEMPORAL:
            if famille.temporal_blueprint is None:
                constats.append(
                    Constat("ERREUR", fid, "temporal_sans_ancrage", "famille temporelle sans temporal_blueprint")
                )
            elif not famille.temporal_blueprint.applicable_regime.strip():
                constats.append(
                    Constat("ERREUR", fid, "temporal_sans_regime",
                            "famille temporelle sans régime applicable")
                )

        # Blocage motivé, réserve motivée
        if (
            famille.candidate_family_status is CandidateFamilyStatus.BLOCKED
            and not famille.blocking_reasons
        ):
            constats.append(
                Constat("ERREUR", fid, "blocage_non_motive", "famille bloquée sans motif")
            )

        # Avertissements : ce qui limite sans interdire.
        if famille.family_score < SCORE_RETENU:
            constats.append(
                Constat("AVERTISSEMENT", fid, "score_faible",
                        f"score {famille.family_score} : famille retenue alors qu'elle "
                        f"est en deçà du seuil {SCORE_RETENU}")
            )
        if not famille.candidate_disqualifying_errors:
            constats.append(
                Constat("AVERTISSEMENT", fid, "erreurs_disqualifiantes",
                        "aucune erreur disqualifiante candidate identifiée")
            )
        if famille.family_kind is FamilyKind.FALSE_PREMISE and not famille.twin_candidate:
            constats.append(
                Constat("AVERTISSEMENT", fid, "fausse_premisse_sans_jumeau",
                        "fausse prémisse sans jumeau : le modèle peut gagner des "
                        "points en réfutant systématiquement")
            )
        if famille.requires_negative_claim:
            constats.append(
                Constat("INFO", fid, "verification_negative",
                        f"piège « {famille.reasoning_trap.value} » : l'item exigera une "
                        f"vérification d'absence avant rédaction")
            )

    constats.extend(_carte_a_jour(familles, regles))
    constats.extend(_coherence_des_jumeaux(familles))
    constats.extend(_doublons(familles, regles))
    return sorted(constats, key=lambda c: (NIVEAUX.index(c.niveau), c.regle_id, c.controle))


def _carte_a_jour(familles: list[CandidateFamily], regles: list[Rule]) -> list[Constat]:
    """La carte dérive-t-elle encore du Rulebook tel qu'il est aujourd'hui ?

    Un avertissement, pas une erreur : une carte en retard n'est pas fausse, elle
    est datée. Mais le retard doit se voir — une carte qui vieillit en silence
    finirait par bloquer des familles dont la règle a été validée depuis.
    """
    chemin = Path(RACINE_FAMILLES) / "family-manifest.json"
    if not chemin.is_file():
        return []
    declaree = lire_json(chemin).get("rulebook_fingerprint", "")
    actuelle = empreinte_rulebook(regles)
    if declaree and declaree != actuelle:
        return [
            Constat(
                "AVERTISSEMENT", "carte", "carte_en_retard",
                "la carte dérive d'un état antérieur du Rulebook : la régénérer "
                "débloquera les familles dont la règle a été validée depuis "
                "(finreg-bench familles generer)",
            )
        ]
    return []


def _coherence_des_jumeaux(familles: list[CandidateFamily]) -> list[Constat]:
    """Un groupe de jumeaux compte deux membres, réciproques, de rôles distincts."""
    constats: list[Constat] = []
    groupes: dict[str, list[CandidateFamily]] = defaultdict(list)
    for famille in familles:
        if famille.twin_group_id:
            groupes[famille.twin_group_id].append(famille)

    par_id = {f.id: f for f in familles}
    for groupe, membres in sorted(groupes.items()):
        if len(membres) != 2:
            constats.append(
                Constat(
                    "ERREUR", groupe, "twin_group_taille",
                    f"{len(membres)} membre(s) : un groupe de jumeaux en compte deux",
                )
            )
            continue
        gauche, droite = sorted(membres, key=lambda f: f.id)
        if gauche.twin_partner_id != droite.id or droite.twin_partner_id != gauche.id:
            constats.append(
                Constat("ERREUR", groupe, "twin_partenaire", "jumelage non réciproque")
            )
        if gauche.twin_type is not droite.twin_type:
            constats.append(
                Constat("ERREUR", groupe, "twin_type", "les deux jumeaux annoncent un type différent")
            )
        if gauche.question_type is droite.question_type:
            constats.append(
                Constat(
                    "ERREUR", groupe, "twin_roles",
                    f"les deux jumeaux sont du même type « {gauche.question_type.value} » : "
                    f"le groupe ne fait varier aucune prémisse",
                )
            )
        if gauche.rule_id != droite.rule_id:
            constats.append(
                Constat("AVERTISSEMENT", groupe, "twin_regles",
                        "jumeaux ancrés sur deux règles différentes : leur forme devra "
                        "être rapprochée à la rédaction")
            )
    return constats


def _doublons(familles: list[CandidateFamily], regles: list[Rule]) -> list[Constat]:
    """Deux familles qui mesurent la même chose de la même façon (§8, §16).

    Même concept, même famille, même piège : elles ne différeraient que par la
    formulation, et la spécification l'interdit. Deux familles ancrées sur le
    même article mais sur des obligations distinctes ne sont pas des doublons —
    c'est le cas ordinaire d'un article qui porte plusieurs dispositions, et le
    QC du Rulebook le traite déjà ainsi. La proximité des énoncés tranche.
    """
    constats: list[Constat] = []
    for collision in redondances(familles, regles)["collisions"]:
        gauche, droite = collision["family_ids"]
        if collision["redundant"]:
            constats.append(
                Constat(
                    "ERREUR", droite, "doublon",
                    f"mesure la même chose que « {gauche} » : même concept, même "
                    f"famille ({collision['family_kind']}), même piège "
                    f"({collision['reasoning_trap']}), énoncés proches "
                    f"({collision['statement_proximity']:.0%} de mots communs)",
                )
            )
        else:
            constats.append(
                Constat(
                    "AVERTISSEMENT", droite, "meme_ancrage",
                    f"partage l'ancrage et la famille de « {gauche} » mais porte une "
                    f"autre disposition ({collision['statement_proximity']:.0%} de mots "
                    f"communs) : questions à écrire sur des faits distincts",
                )
            )
    return constats


def erreurs(constats: list[Constat]) -> list[Constat]:
    return [c for c in constats if c.niveau == "ERREUR"]


# --------------------------------------------------------------------------- #
# Manifeste et matrice
# --------------------------------------------------------------------------- #


def empreinte_rulebook(regles: list[Rule]) -> str:
    """Empreinte de l'état du Rulebook dont une carte dérive.

    La carte est un artefact **dérivé** : elle retarde légitimement sur le
    Rulebook, le temps qu'on décide de la régénérer. Ce qui ne doit jamais
    arriver, c'est qu'elle retarde sans que personne le sache. L'empreinte rend
    l'écart visible et datable au lieu de le laisser silencieux.
    """
    return hash_json(
        [
            {
                "id": r.id,
                "version": r.version,
                "status": r.status.value,
                "gold_ready": r.gold_ready,
                "exceptions_status": r.exceptions_status.value,
            }
            for r in sorted(regles, key=lambda r: r.id)
        ]
    )


def construire_manifeste(
    familles: list[CandidateFamily], regles: list[Rule], par_fichier: dict[str, int]
) -> dict:
    """Récapitulatif chiffré de la carte, écrit à côté d'elle."""

    def compter(cle) -> dict[str, int]:
        valeurs: Counter[str] = Counter(cle(f) for f in familles)
        return dict(sorted(valeurs.items()))

    exploitables = sorted({f.rule_id for f in familles})
    groupes = {f.twin_group_id for f in familles if f.twin_group_id}

    return {
        "family_map_version": VERSION_CARTE,
        "rulebook_fingerprint": empreinte_rulebook(regles),
        "generation_date": DATE_GENERATION.isoformat(),
        "retention_threshold": SCORE_RETENU,
        "number_of_rules": len(regles),
        "number_of_usable_rules": sum(1 for r in regles if r.is_usable),
        "number_of_rules_with_family": len(exploitables),
        "number_of_families": len(familles),
        "families_per_domain": compter(lambda f: f.domain.value),
        "families_per_kind": compter(lambda f: f.family_kind.value),
        "families_per_question_type": compter(lambda f: f.question_type.value),
        "families_per_status": compter(lambda f: f.candidate_family_status.value),
        "families_per_priority": compter(lambda f: f.priority.value),
        "families_per_difficulty": {
            str(k): v for k, v in sorted(Counter(f.predicted_difficulty for f in familles).items())
        },
        "families_per_trap": compter(lambda f: f.reasoning_trap.value),
        "families_per_file": dict(sorted(par_fichier.items())),
        "number_of_twin_groups": len(groupes),
        "number_of_twin_candidates": sum(1 for f in familles if f.twin_candidate),
        "number_critical": sum(1 for f in familles if f.priority is Priority.CRITICAL),
        "number_ready": sum(1 for f in familles if f.is_ready),
        "number_blocked": sum(
            1 for f in familles if f.candidate_family_status is CandidateFamilyStatus.BLOCKED
        ),
        "number_requiring_negative_claim": sum(1 for f in familles if f.requires_negative_claim),
        "number_of_redundancy_groups": len({f.redundancy_group_id for f in familles}),
        "status_note": _note_de_statut(familles, regles),
    }


def _note_de_statut(familles: list[CandidateFamily], regles: list[Rule]) -> str:
    """Ce que la carte autorise aujourd'hui, dit en une phrase, sans euphémisme."""
    prets = sum(1 for f in familles if f.is_ready)
    utilisables = sum(1 for r in regles if r.is_usable)
    if utilisables == 0:
        return (
            "Aucune règle du Rulebook n'est validée : les "
            f"{len(familles)} familles de la carte sont toutes « blocked » et aucune "
            "ne peut engendrer un item du benchmark. La carte décrit ce qui sera "
            "mesurable une fois la vérification faite, pas ce qui l'est aujourd'hui."
        )
    return (
        f"{utilisables} règle(s) validée(s) sur {len(regles)} ; {prets} famille(s) "
        f"prête(s) sur {len(familles)}. Les familles « blocked » le restent tant que "
        f"leur règle n'a pas été confrontée à son texte primaire."
    )


def ecrire_matrice(lignes: list[dict], chemin: Path) -> None:
    """Matrice de couverture en CSV, aux conventions des artefacts humains du dépôt.

    UTF-8 avec BOM et point-virgule : comme la file de revue et le dossier de
    vérification, ce fichier s'ouvre dans un tableur français sans manipulation.
    """
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        graveur = csv.DictWriter(
            flux, fieldnames=list(COLONNES_MATRICE), delimiter=SEPARATEUR_CSV
        )
        graveur.writeheader()
        for ligne in lignes:
            graveur.writerow({colonne: ligne[colonne] for colonne in COLONNES_MATRICE})


# --------------------------------------------------------------------------- #
# Rapport
# --------------------------------------------------------------------------- #


def rapport_markdown(
    familles: list[CandidateFamily], regles: list[Rule], constats: list[Constat]
) -> str:
    """`reports/FAMILY_MAP_QC.md` : ce que la carte contient, ce qu'elle bloque, ce qui manque."""
    par_niveau = {n: [c for c in constats if c.niveau == n] for n in NIVEAUX}
    trous = lacunes(regles, familles)
    doubles = redondances(familles, regles)
    faisabilite = faisabilite_distribution(familles)
    par_domaine = Counter(f.domain.value for f in familles)
    par_kind = Counter(f.family_kind.value for f in familles)
    utilisables = sum(1 for r in regles if r.is_usable)

    lignes = [
        "# Question Family Map — contrôle qualité",
        "",
        "Rapport généré par `src/bench/qc_familles.py` (phase 7). Il dit ce que le",
        "Rulebook permet de mesurer, ce qu'il ne permet pas encore, et pourquoi.",
        "",
        "**Aucune question n'est rédigée à ce stade.** La carte décrit des angles",
        "d'interrogation et leurs conditions ; la rédaction des items est la phase",
        "suivante.",
        "",
        "## Synthèse",
        "",
        f"- règles au Rulebook : **{len(regles)}**",
        f"- règles utilisables pour ancrer un gold (`validated`) : **{utilisables}**",
        f"- règles ayant au moins une famille intéressante : "
        f"**{len({f.rule_id for f in familles})}**",
        f"- familles candidates retenues (score ≥ {SCORE_RETENU}) : **{len(familles)}**",
        f"- familles prêtes (`ready`) : **{sum(1 for f in familles if f.is_ready)}**",
        f"- familles bloquées (`blocked`) : "
        f"**{sum(1 for f in familles if f.candidate_family_status is CandidateFamilyStatus.BLOCKED)}**",
        f"- groupes de jumeaux : **{len({f.twin_group_id for f in familles if f.twin_group_id})}**",
        f"- familles critiques : "
        f"**{sum(1 for f in familles if f.priority is Priority.CRITICAL)}**",
        f"- erreurs bloquantes : **{len(par_niveau['ERREUR'])}**",
        f"- avertissements : **{len(par_niveau['AVERTISSEMENT'])}**",
        "",
        "> " + _note_de_statut(familles, regles).replace("\n", "\n> "),
        "",
        "## Familles par domaine",
        "",
        "| Domaine | Familles | Prêtes | Bloquées | Jumeaux | Critiques |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for domaine in sorted(d.value for d in Domain):
        concernees = [f for f in familles if f.domain.value == domaine]
        lignes.append(
            f"| {domaine} | {len(concernees)} | "
            f"{sum(1 for f in concernees if f.is_ready)} | "
            f"{sum(1 for f in concernees if f.candidate_family_status is CandidateFamilyStatus.BLOCKED)} | "
            f"{sum(1 for f in concernees if f.twin_candidate)} | "
            f"{sum(1 for f in concernees if f.priority is Priority.CRITICAL)} |"
        )

    lignes += [
        "",
        "## Familles par type",
        "",
        "| Code | Famille | Retenues | Score moyen | Difficulté moyenne |",
        "|---|---|---:|---:|---:|",
    ]
    for kind in ORDRE_FAMILLES:
        concernees = [f for f in familles if f.family_kind is kind]
        if concernees:
            score = sum(f.family_score for f in concernees) / len(concernees)
            difficulte = sum(f.predicted_difficulty for f in concernees) / len(concernees)
            lignes.append(
                f"| {CODES_FAMILLES[kind]} | {kind.value} | {len(concernees)} | "
                f"{score:.2f} | {difficulte:.1f} |"
            )
        else:
            lignes.append(f"| {CODES_FAMILLES[kind]} | {kind.value} | 0 | — | — |")

    lignes += [
        "",
        "## Distribution visée (§10)",
        "",
        "Hypothèse de rendement — **une hypothèse de planification, pas une promesse** :",
        f"une famille de score 3 est réputée engendrer {RENDEMENT_PAR_SCORE[3]} items,",
        f"une famille de score 2 en engendrer {RENDEMENT_PAR_SCORE[2]}.",
        "",
        f"Cible : **{faisabilite['target_total']} items publics**.",
        "",
        "| Type | Cible | Familles | Items estimés | Écart | Atteignable |",
        "|---|---:|---:|---:|---:|:--:|",
    ]
    for ligne in faisabilite["by_question_type"]:
        lignes.append(
            f"| {ligne['question_type']} | {ligne['target_items']} | {ligne['families']} | "
            f"{ligne['estimated_items']} | {ligne['gap']:+d} | "
            f"{'oui' if ligne['achievable'] else '**non**'} |"
        )

    lignes += [
        "",
        "| Domaine | Cible | Familles | Items estimés | Écart | Atteignable |",
        "|---|---:|---:|---:|---:|:--:|",
    ]
    for ligne in faisabilite["by_domain"]:
        lignes.append(
            f"| {ligne['domain']} | {ligne['target_items']} | {ligne['families']} | "
            f"{ligne['estimated_items']} | {ligne['gap']:+d} | "
            f"{'oui' if ligne['achievable'] else '**non**'} |"
        )

    lignes += [
        "",
        "## Lacunes de couverture",
        "",
    ]
    if trous["missing_family_kinds"]:
        lignes.append(
            "- **familles absentes de toute la carte** : "
            + ", ".join(f"`{k}`" for k in trous["missing_family_kinds"])
        )
    if trous["missing_traps"]:
        lignes.append(
            "- **pièges jamais mesurés** : " + ", ".join(f"`{t}`" for t in trous["missing_traps"])
        )
    if trous["rules_without_family"]:
        lignes.append(
            f"- **règles sans aucune famille intéressante** "
            f"({len(trous['rules_without_family'])}) : "
            + ", ".join(f"`{r}`" for r in trous["rules_without_family"])
        )
    if trous["false_premises_without_twin"]:
        lignes.append(
            f"- **fausses prémisses sans jumeau** "
            f"({len(trous['false_premises_without_twin'])}) : "
            + ", ".join(f"`{r}`" for r in trous["false_premises_without_twin"][:15])
        )
    lignes.append("")
    lignes += ["### Familles manquantes par domaine", "", "| Domaine | Familles absentes |", "|---|---|"]
    for domaine, manquantes in sorted(trous["missing_family_kinds_by_domain"].items()):
        lignes.append(f"| {domaine} | {', '.join(manquantes) if manquantes else '—'} |")

    lignes += [
        "",
        "### Exploitation des règles",
        "",
        "| Règle | Familles |",
        "|---|---:|",
    ]
    for entree in trous["most_exploited_rules"]:
        lignes.append(f"| `{entree['rule_id']}` | {entree['families']} |")
    if trous["least_exploited_rules"]:
        lignes += [
            "",
            f"Règles sous-exploitées (au plus une famille) : "
            + ", ".join(f"`{e['rule_id']}`" for e in trous["least_exploited_rules"]),
        ]

    lignes += [
        "",
        "## Redondances",
        "",
        f"- groupes de redondance : **{doubles['number_of_groups']}**",
        f"- groupes couvrant plusieurs règles : **{len(doubles['groups'])}**",
        f"- collisions d'ancrage (même concept, même famille, même piège) : "
        f"**{len(doubles['collisions'])}**",
        f"- dont doublons réels (énoncés proches à "
        f"{doubles['proximity_threshold']:.0%} ou plus) : **{doubles['number_redundant']}**",
        "",
    ]
    if doubles["groups"]:
        lignes += ["| Groupe | Règles | Familles |", "|---|---|---:|"]
        for groupe in doubles["groups"][:20]:
            lignes.append(
                f"| `{groupe['redundancy_group_id']}` | "
                f"{', '.join(f'`{r}`' for r in groupe['rules'])} | {groupe['families']} |"
            )
        lignes.append("")
    if doubles["collisions"]:
        lignes.append("### Collisions d'ancrage")
        lignes.append("")
        for collision in doubles["collisions"][:20]:
            verdict = "**doublon**" if collision["redundant"] else "ancrage commun"
            lignes.append(
                f"- `{collision['redundancy_group_id']}` — {collision['family_kind']} / "
                f"{collision['reasoning_trap']} — {verdict} "
                f"({collision['statement_proximity']:.0%} de mots communs) : "
                + ", ".join(f"`{i}`" for i in collision["family_ids"])
            )
        lignes.append("")

    lignes += ["## Constats", ""]
    for niveau in NIVEAUX:
        trouves = par_niveau[niveau]
        if not trouves:
            continue
        lignes += [f"### {niveau.capitalize()}s ({len(trouves)})", ""]
        groupes_constats: dict[str, list[Constat]] = defaultdict(list)
        for constat in trouves:
            groupes_constats[constat.controle].append(constat)
        for controle, elements in sorted(groupes_constats.items()):
            lignes += [f"#### `{controle}` — {len(elements)}", ""]
            for constat in elements[:15]:
                lignes.append(f"- `{constat.regle_id}` : {constat.message}")
            if len(elements) > 15:
                lignes.append(f"- … et {len(elements) - 15} autre(s)")
            lignes.append("")

    lignes += [
        "## Ce que la carte n'est pas",
        "",
        "- Elle ne contient **aucune question rédigée** : la phase 7 s'arrête à ce qui",
        "  est mesurable.",
        "- Elle n'affecte **rien au public ni au privé** : `public_eligible` et",
        "  `private_eligible` restent tous deux vrais, et `holdout_recommendation`",
        "  ne fait que transporter le signal jusqu'à l'arbitrage.",
        "- Elle ne promeut **aucune règle** : une famille `blocked` le reste jusqu'à",
        "  ce que la vérification du Rulebook fasse passer sa règle en `validated`.",
        "",
    ]

    return "\n".join(lignes) + "\n"
