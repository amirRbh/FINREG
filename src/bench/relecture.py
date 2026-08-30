"""Relire ce que le dernier audit a établi, quand le texte primaire est hors d'atteinte.

L'audit de complétude va chercher le texte officiel : sans réseau vers CELLAR,
il ne constate rien. Or ses constats sont déjà **publiés** — le dossier de
complétude porte les structures repérées, les dispositions limitantes recopiées
et les renvois ; la matrice de gold-readiness porte les prérequis ; la matrice
d'exploitabilité porte le blocage principal retenu.

Ce module les relit et reconstruit les `ConstatCompletude` correspondants, pour
que la préparation d'un arbitrage n'ait pas à refaire une passe réseau qu'elle
ne pourrait pas faire.

**Une relecture n'est pas un audit.** Elle ne peut rien établir de neuf : elle
redonne ce qui a été écrit, et le dit — chaque artefact produit à partir d'elle
porte l'empreinte des fichiers relus, pour qu'un pack construit sur un audit
périmé se voie. Le contrôle de concordance (`divergences`) compare le blocage
reconstruit à celui que l'audit avait publié : s'ils diffèrent, la relecture est
fausse et rien ne doit s'écrire dessus.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.bench.completude import (
    CRITERES_VALIDATION,
    MOTIF_TEXTE_INDISPONIBLE,
    ConstatCompletude,
    Structure,
    affirmations_negatives_resolues,
)
from src.bench.readiness import ConstatReadiness, evaluer
from src.bench.regles import Rule
from src.bench.rulebook import ExceptionsStatus
from src.bench.verification import ENCODAGE_CSV, SEPARATEUR_CSV, SEPARATEUR_LISTE
from src.io_utils import hash_fichier, hash_texte

DOSSIER_COMPLETUDE = Path("data/verification/dossier-completude.csv")
DOSSIER_AUDIT = Path("data/verification/dossier-audit.csv")
MATRICE_GOLD = Path("reports/RULEBOOK_GOLD_READINESS.csv")
MATRICE_FAMILY = Path("reports/RULEBOOK_FAMILY_READINESS.csv")

#: Séparateur des blocs du champ `commentaire` du dossier de complétude, tel que
#: `rapport_completude._commentaire` les assemble.
SEPARATEUR_BLOCS = " || "
#: Séparateur des constats à l'intérieur du bloc CONSTATS (`ConstatCompletude.motif`).
SEPARATEUR_MOTIFS = " ; "
#: Préfixe du constat qui énumère les renvois résolus dans l'acte.
PREFIXE_RENVOIS = "renvois vérifiés dans l'acte : articles "
#: Préfixe du commentaire d'audit qui porte l'extrait officiel.
PREFIXE_TEXTE_OFFICIEL = "TEXTE OFFICIEL — "


@dataclass(frozen=True)
class Relecture:
    """Ce que la relecture rend, et de quoi elle le tient."""

    constats: dict[str, ConstatCompletude]
    etats: dict[str, ConstatReadiness]
    extraits: dict[str, str]
    #: Empreinte des artefacts relus : un pack construit dessus peut dire sur
    #: quel état du Rulebook il porte, et cesser d'être valable en silence.
    empreinte: str
    artefacts: tuple[str, ...]


def _lire_csv(chemin: Path, cle: str) -> dict[str, dict[str, str]]:
    with Path(chemin).open("r", encoding=ENCODAGE_CSV, newline="") as flux:
        return {
            ligne[cle]: ligne
            for ligne in csv.DictReader(flux, delimiter=SEPARATEUR_CSV)
            if ligne.get(cle)
        }


def _blocs(commentaire: str) -> dict[str, str]:
    """Décompose `STRUCTURES — … || CRITÈRES MANQUANTS — … || CONSTATS — …`."""
    blocs: dict[str, str] = {}
    for bloc in commentaire.split(SEPARATEUR_BLOCS):
        if " — " in bloc:
            cle, valeur = bloc.split(" — ", 1)
            blocs[cle.strip()] = valeur.strip()
    return blocs


def _structures(valeur: str) -> tuple[Structure, ...]:
    if not valeur or valeur == "aucune":
        return ()
    trouvees = []
    for nom in valeur.split(", "):
        try:
            trouvees.append(Structure(nom))
        except ValueError:  # vocabulaire élargi depuis l'écriture : on ne devine pas
            continue
    return tuple(trouvees)


def _renvois(motifs: list[str]) -> tuple[str, ...]:
    for motif in motifs:
        if motif.startswith(PREFIXE_RENVOIS):
            return tuple(motif[len(PREFIXE_RENVOIS) :].split(", "))
    return ()


def constat_relu(regle: Rule, complet: dict[str, str], gold: dict[str, str]) -> ConstatCompletude:
    """Reconstruit le constat de complétude d'une règle depuis les artefacts publiés."""
    blocs = _blocs(complet.get("commentaire", ""))
    motifs = [m for m in blocs.get("CONSTATS", "").split(SEPARATEUR_MOTIFS) if m]
    manquants = [c for c in blocs.get("CRITÈRES MANQUANTS", "").split(", ") if c]
    exceptions_status = ExceptionsStatus(gold["exceptions_status"])
    extraites = tuple(
        e.strip() for e in complet.get("exceptions_constatees", "").split(SEPARATEUR_LISTE) if e.strip()
    )

    # Texte hors d'atteinte : l'audit n'a coché aucun critère, et c'est ce vide
    # — non pas des critères tous faux — qui fait ressortir la source comme
    # blocage. Le confondre avec « article introuvable » déplacerait l'effort.
    if MOTIF_TEXTE_INDISPONIBLE in motifs:
        return ConstatCompletude(
            rule_id=regle.id,
            domain=regle.domain.value,
            priority=regle.priority.value,
            exceptions_status=exceptions_status,
            statut_propose=regle.status,
            motifs=tuple(motifs),
            temporal_status=gold["temporal_status"],
        )

    criteres = {nom: nom not in manquants for nom in CRITERES_VALIDATION}
    criteres["source_primaire_verifiee"] = gold["source_verified"] == "oui"
    criteres["article_verifie"] = gold["article_verified"] == "oui"
    criteres["renvois_verifies"] = gold["cross_reference_checked"] == "oui"
    criteres_gold = dict(criteres)
    criteres_gold["affirmations_negatives_resolues"] = affirmations_negatives_resolues(regle)

    return ConstatCompletude(
        rule_id=regle.id,
        domain=regle.domain.value,
        priority=regle.priority.value,
        structures=_structures(blocs.get("STRUCTURES", "")),
        exceptions_extraites=extraites,
        renvois=_renvois(motifs),
        exceptions_status=exceptions_status,
        gold_ready=gold["gold_ready"] == "oui",
        gold_ready_reason=gold.get("reason", ""),
        criteres=criteres,
        criteres_gold=criteres_gold,
        statut_propose=regle.status,
        motifs=tuple(motifs),
        temporal_status=gold["temporal_status"],
        cross_reference_checked=criteres["renvois_verifies"],
    )


def extrait_relu(audit: dict[str, str] | None, regle: Rule) -> str:
    """L'extrait officiel, tel que l'audit l'a reporté en commentaire.

    À défaut, les notes de la règle : le circuit de vérification y recopie le
    texte confirmé. Aucune reconstruction — sans extrait, la fiche le dit.
    """
    for source in ((audit or {}).get("commentaire", ""), regle.notes):
        if PREFIXE_TEXTE_OFFICIEL in source:
            # Le commentaire empile plusieurs blocs : l'extrait s'arrête au
            # suivant, sinon les réserves du vérificateur passeraient pour du
            # texte officiel.
            apres = source.split(PREFIXE_TEXTE_OFFICIEL, 1)[1]
            return apres.split(SEPARATEUR_BLOCS, 1)[0].strip()
    return ""


def divergences(etats: dict[str, ConstatReadiness], family: dict[str, dict[str, str]]) -> list[str]:
    """Le blocage reconstruit est-il celui que l'audit avait publié ?

    C'est le seul contrôle qui rend la relecture opposable : si un blocage
    reconstruit diffère de celui publié, la relecture a inventé quelque chose,
    et rien ne doit s'écrire dessus.
    """
    ecarts: list[str] = []
    for rule_id, etat in etats.items():
        publie = family.get(rule_id)
        if publie is None:
            ecarts.append(f"{rule_id} : absente de la matrice d'exploitabilité publiée")
            continue
        attendu = (publie["family_blocker"], publie["blocker_category"])
        obtenu = (etat.family_blocker, etat.blocker_category)
        if attendu != obtenu:
            ecarts.append(
                f"{rule_id} : blocage relu {obtenu} ≠ blocage publié {attendu}"
            )
    return ecarts


def relire(
    regles: list[Rule],
    dossier_completude: Path = DOSSIER_COMPLETUDE,
    dossier_audit: Path = DOSSIER_AUDIT,
    matrice_gold: Path = MATRICE_GOLD,
    matrice_family: Path = MATRICE_FAMILY,
) -> Relecture:
    """Relit les quatre artefacts et reconstruit constats, états et extraits."""
    complets = _lire_csv(dossier_completude, "rule_id")
    audits = _lire_csv(dossier_audit, "rule_id")
    golds = _lire_csv(matrice_gold, "ID")
    familles = _lire_csv(matrice_family, "ID")

    constats: dict[str, ConstatCompletude] = {}
    etats: dict[str, ConstatReadiness] = {}
    extraits: dict[str, str] = {}
    for regle in regles:
        complet, gold = complets.get(regle.id), golds.get(regle.id)
        if complet is None or gold is None:
            raise ValueError(
                f"{regle.id} : absente des artefacts d'audit publiés — relancer "
                f"« finreg-bench rulebook completude » avant de préparer un arbitrage"
            )
        constats[regle.id] = constat_relu(regle, complet, gold)
        etats[regle.id] = evaluer(regle, constats[regle.id])
        extraits[regle.id] = extrait_relu(audits.get(regle.id), regle)

    ecarts = divergences(etats, familles)
    if ecarts:
        raise ValueError(
            "la relecture ne reproduit pas l'audit publié — aucun arbitrage ne "
            "peut se préparer dessus :\n  " + "\n  ".join(ecarts)
        )

    chemins = (dossier_completude, dossier_audit, matrice_gold, matrice_family)
    empreintes = [hash_fichier(Path(c)) for c in chemins]
    return Relecture(
        constats=constats,
        etats=etats,
        extraits=extraits,
        empreinte=hash_texte("".join(empreintes))[:16],
        artefacts=tuple(str(c) for c in chemins),
    )
