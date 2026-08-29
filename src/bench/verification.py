"""Circuit de vérification du Rulebook (spécification §15).

Une règle ne dépasse `draft` que si un humain a consulté le texte primaire. Le
verrou est tenu par le schéma (`regles.Rule`) ; il manquait le circuit qui rend
cette consultation exploitable autrement qu'en éditant cinq fichiers JSON à la
main. Ce module le fournit, en quatre temps :

1. `exporter_dossier` sort un **dossier de vérification** en CSV : une ligne par
   règle, ce qu'il faut aller lire, et les colonnes à remplir ;
2. `lire_dossier` relit le CSV rempli et valide **tout** avant d'appliquer quoi
   que ce soit — un fichier partiellement fautif ne s'applique pas à moitié ;
3. `appliquer` reporte les constats sur les règles, sous le verrou du schéma :
   aucune promotion n'est possible sans méthode suffisante, vérificateur nommé
   et date ;
4. le **registre de vérification** conserve ces constats hors de `data/rules/`,
   pour qu'une régénération du Rulebook ne les efface pas.

Le point 4 n'est pas un détail de rangement : `scripts/generer_rulebook.py`
réécrit `data/rules/*.json` à partir des déclarations, avec `verified_by` vide.
Sans registre séparé, la première régénération effacerait le travail de
vérification sans que rien ne le signale.

Convention de langue : le CSV est un artefact humain, ses colonnes sont en
français comme celles de la file de revue ; le registre est un artefact de
données de la V0.2, ses clés reprennent les noms anglais du schéma `Rule`.
"""

from __future__ import annotations

import csv
import datetime as dt
from enum import Enum
from pathlib import Path

from pydantic import Field, model_validator

from src.bench.modeles import ModeleStrict
from src.bench.regles import Rule
from src.bench.rulebook import (
    METHODES_SUFFISANTES,
    ExceptionsStatus,
    RuleStatus,
    VerificationMethod,
)
from src.io_utils import ecrire_json, lire_json

#: Le registre vit hors de `data/rules/`, que le chargeur du Rulebook parcourt.
REGISTRE_VERIFICATION = Path("data/verification/rulebook-ledger.json")

VERSION_REGISTRE = "v1"

ENCODAGE_CSV = "utf-8-sig"
SEPARATEUR_CSV = ";"
SEPARATEUR_LISTE = " | "


class Verdict(str, Enum):
    """Ce que la consultation du texte primaire a établi.

    Quatre issues, et une seule qui promeut : on ne monte pas une règle en
    grade parce que sa vérification s'est mal passée.
    """

    #: Le texte dit bien ce que l'énoncé dit. La règle peut progresser.
    CONFIRME = "confirme"
    #: Le texte dit autre chose ; l'énoncé corrigé est fourni. La règle est reversionnée.
    CORRIGE = "corrige"
    #: Le texte contredit la règle, ou la disposition citée n'existe pas. Reste `draft`.
    REFUTE = "refute"
    #: Consultée sans trancher (texte introuvable, version incertaine). Reste `draft`.
    NON_VERIFIABLE = "non_verifiable"


#: Verdicts qui autorisent un statut au-delà de `draft`.
VERDICTS_PROMOTEURS: frozenset[Verdict] = frozenset({Verdict.CONFIRME, Verdict.CORRIGE})


class VerificationInvalide(ValueError):
    """Un dossier de vérification n'est pas exploitable. Rien n'est appliqué."""

    def __init__(self, erreurs: list[str]) -> None:
        self.erreurs = erreurs
        super().__init__(
            f"{len(erreurs)} anomalie(s), aucune vérification appliquée :\n"
            + "\n".join(f"  - {e}" for e in erreurs)
        )


class Verification(ModeleStrict):
    """Le constat d'une consultation de texte primaire, pour une règle.

    Ce qui est écrit ici est opposable : c'est ce qui fera passer une règle de
    `draft` à un statut exploitable. Les invariants portent donc sur ce qui rend
    le constat vérifiable par un tiers — qui, quand, sur quel texte.
    """

    rule_id: str = Field(min_length=1)
    verdict: Verdict
    verification_method: VerificationMethod = VerificationMethod.MODEL_KNOWLEDGE_UNVERIFIED
    verified_by: str = ""
    verification_date: dt.date | None = None
    target_status: RuleStatus = RuleStatus.DRAFT

    #: Énoncé corrigé, au plus près de la lettre du texte consulté.
    statement: str = ""
    article: str = ""
    #: Date de la version effectivement consultée — ce que le placeholder ignore.
    version_date: dt.date | None = None
    exceptions_status: ExceptionsStatus | None = None
    exceptions: list[str] = Field(default_factory=list)
    comment: str = ""

    @model_validator(mode="after")
    def _un_verdict_promoteur_exige_une_consultation(self) -> Verification:
        if self.verdict not in VERDICTS_PROMOTEURS:
            if self.target_status is not RuleStatus.DRAFT:
                raise ValueError(
                    f"verdict « {self.verdict.value} » : aucune promotion n'est "
                    f"possible, statut visé « {self.target_status.value} »"
                )
            return self

        if self.verification_method not in METHODES_SUFFISANTES:
            raise ValueError(
                f"verdict « {self.verdict.value} » exige une vérification sur texte "
                f"primaire ; methode vaut « {self.verification_method.value} »"
            )
        if not self.verified_by.strip() or self.verification_date is None:
            raise ValueError(
                f"verdict « {self.verdict.value} » exige un vérificateur nommé et une date"
            )
        if self.target_status is RuleStatus.DRAFT:
            raise ValueError(
                f"verdict « {self.verdict.value} » sans statut visé : une vérification "
                f"aboutie qui ne promeut rien ne sert à rien"
            )
        return self

    @model_validator(mode="after")
    def _une_correction_dit_ce_que_le_texte_dit(self) -> Verification:
        if self.verdict is Verdict.CORRIGE and not self.statement.strip():
            raise ValueError("verdict « corrige » sans énoncé corrigé")
        if self.verdict is Verdict.CONFIRME and self.statement.strip():
            raise ValueError(
                "verdict « confirme » avec un énoncé corrigé : c'est une correction, "
                "pas une confirmation"
            )
        return self

    @model_validator(mode="after")
    def _une_refutation_dit_ce_qui_cloche(self) -> Verification:
        if self.verdict is Verdict.REFUTE and not self.comment.strip():
            raise ValueError(
                "verdict « refute » sans commentaire : une règle réfutée doit dire "
                "ce que le texte dit à sa place"
            )
        return self

    @model_validator(mode="after")
    def _exceptions_coherentes(self) -> Verification:
        """Même distinction que dans `Rule` : listées, aucune identifiée, inconnues."""
        if self.exceptions and self.exceptions_status is not ExceptionsStatus.LISTED:
            raise ValueError("exceptions constatées sans exceptions_statut « listed »")
        if self.exceptions_status is ExceptionsStatus.LISTED and not self.exceptions:
            raise ValueError("exceptions_statut « listed » sans exception constatée")
        if any(not e.strip() for e in self.exceptions):
            raise ValueError("exceptions : aucune entrée ne peut être vide")
        return self


# -- dossier de vérification (CSV) ------------------------------------------------ #

#: Colonnes de contexte, remplies par l'export : ce qu'il faut lire.
COLONNES_CONTEXTE = [
    "rule_id",
    "domaine",
    "type",
    "priorite",
    "statut_actuel",
    "texte_source",
    "article",
    "url",
    "version_date_declaree",
    "enonce_actuel",
    "exceptions_statut_actuel",
]

#: Colonnes à remplir par le vérificateur.
COLONNES_A_REMPLIR = [
    "verdict",
    "methode",
    "verifie_par",
    "date_verification",
    "statut_vise",
    "enonce_corrige",
    "article_corrige",
    "version_date_constatee",
    "exceptions_statut",
    "exceptions_constatees",
    "commentaire",
]

COLONNES = COLONNES_CONTEXTE + COLONNES_A_REMPLIR


def exporter_dossier(regles: list[Rule], chemin: Path) -> Path:
    """Écrit le dossier de vérification. Les colonnes de constat restent vides.

    L'ordre est celui de la priorité décroissante puis de l'identifiant : on
    vérifie d'abord les règles dont une erreur de compréhension coûte le plus.
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    rang = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    ordonnees = sorted(regles, key=lambda r: (rang.get(r.priority.value, 9), r.id))

    with chemin.open("w", encoding=ENCODAGE_CSV, newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=COLONNES, delimiter=SEPARATEUR_CSV)
        redacteur.writeheader()
        for regle in ordonnees:
            ligne = {colonne: "" for colonne in COLONNES}
            ligne.update(
                {
                    "rule_id": regle.id,
                    "domaine": regle.domain.value,
                    "type": regle.rule_type.value,
                    "priorite": regle.priority.value,
                    "statut_actuel": regle.status.value,
                    "texte_source": regle.source.text,
                    "article": regle.source.article,
                    "url": regle.source.url,
                    "version_date_declaree": regle.source.version_date.isoformat(),
                    "enonce_actuel": regle.statement,
                    "exceptions_statut_actuel": regle.exceptions_status.value,
                }
            )
            redacteur.writerow(ligne)

    return chemin


def _date(brut: str, colonne: str, numero: int, erreurs: list[str]) -> dt.date | None:
    brut = brut.strip()
    if not brut:
        return None
    try:
        return dt.date.fromisoformat(brut)
    except ValueError:
        erreurs.append(f"ligne {numero} : {colonne} « {brut} » n'est pas une date AAAA-MM-JJ")
        return None


def lire_dossier(chemin: Path) -> list[Verification]:
    """Relit le dossier rempli. Les lignes sans verdict sont ignorées.

    Toute la lecture est validée avant de rendre quoi que ce soit : comme pour la
    file de revue, un fichier partiellement fautif ne s'applique pas à moitié.
    """
    verifications: list[Verification] = []
    erreurs: list[str] = []

    with Path(chemin).open("r", encoding=ENCODAGE_CSV, newline="") as flux:
        lecteur = csv.DictReader(flux, delimiter=SEPARATEUR_CSV)
        manquantes = {"rule_id", "verdict", "methode", "verifie_par", "date_verification"} - set(
            lecteur.fieldnames or []
        )
        if manquantes:
            raise VerificationInvalide(
                [f"colonnes manquantes dans {chemin} : {sorted(manquantes)}"]
            )

        for numero, ligne in enumerate(lecteur, start=2):
            brut = (ligne.get("verdict") or "").strip()
            if not brut:
                continue

            donnees = {
                "rule_id": (ligne.get("rule_id") or "").strip(),
                "verdict": brut,
                "verified_by": (ligne.get("verifie_par") or "").strip(),
                "statement": (ligne.get("enonce_corrige") or "").strip(),
                "article": (ligne.get("article_corrige") or "").strip(),
                "comment": (ligne.get("commentaire") or "").strip(),
                "verification_date": _date(
                    ligne.get("date_verification") or "", "date_verification", numero, erreurs
                ),
                "version_date": _date(
                    ligne.get("version_date_constatee") or "",
                    "version_date_constatee",
                    numero,
                    erreurs,
                ),
                "exceptions": [
                    e.strip()
                    for e in (ligne.get("exceptions_constatees") or "").split("|")
                    if e.strip()
                ],
            }

            methode = (ligne.get("methode") or "").strip()
            if methode:
                donnees["verification_method"] = methode
            statut = (ligne.get("statut_vise") or "").strip()
            if statut:
                donnees["target_status"] = statut
            exceptions_statut = (ligne.get("exceptions_statut") or "").strip()
            if exceptions_statut:
                donnees["exceptions_status"] = exceptions_statut

            try:
                verifications.append(Verification.model_validate(donnees))
            except ValueError as exc:
                premiere = str(exc).splitlines()
                detail = next(
                    (l.strip() for l in premiere if "Value error," in l), premiere[0]
                ).replace("Value error, ", "")
                erreurs.append(f"ligne {numero} ({donnees['rule_id'] or 'sans rule_id'}) : {detail}")

    if erreurs:
        raise VerificationInvalide(erreurs)

    return verifications


# -- application aux règles -------------------------------------------------------- #


def appliquer(regles: list[Rule], verifications: list[Verification]) -> list[Rule]:
    """Reporte les constats sur les règles. Tout est validé avant d'appliquer.

    Une règle corrigée est **reversionnée**, jamais écrasée : `version` avance et
    `supersedes` nomme ce qui est remplacé, comme pour un gold.
    """
    index = {r.id: r for r in regles}
    erreurs: list[str] = []
    vus: set[str] = set()

    for verification in verifications:
        rid = verification.rule_id
        if rid not in index:
            erreurs.append(f"{rid} : aucune règle de ce nom dans le Rulebook")
            continue
        if rid in vus:
            erreurs.append(f"{rid} : deux vérifications pour la même règle")
            continue
        vus.add(rid)

        regle = index[rid]
        if verification.target_status is RuleStatus.VALIDATED:
            statut = verification.exceptions_status or regle.exceptions_status
            if statut is ExceptionsStatus.UNKNOWN:
                erreurs.append(
                    f"{rid} : statut « validated » alors que les exceptions restent "
                    f"inconnues — une règle validée sans ses exceptions se teste "
                    f"comme un absolu qu'elle n'est pas"
                )

    if erreurs:
        raise VerificationInvalide(erreurs)

    par_regle = {v.rule_id: v for v in verifications}
    appliquees: list[Rule] = []

    for regle in regles:
        verification = par_regle.get(regle.id)
        if verification is None:
            appliquees.append(regle)
            continue
        try:
            appliquees.append(_appliquer_une(regle, verification))
        except ValueError as exc:
            erreurs.append(f"{regle.id} : {exc}")

    if erreurs:
        raise VerificationInvalide(erreurs)

    return appliquees


def _appliquer_une(regle: Rule, verification: Verification) -> Rule:
    """Construit la règle vérifiée, en repassant par la validation du schéma.

    `model_copy` contournerait les validateurs : c'est justement eux qui tiennent
    le verrou de vérification, on repasse donc par `model_validate`.
    """
    donnees = regle.model_dump(mode="json")
    source = dict(donnees["source"])

    if verification.verdict in VERDICTS_PROMOTEURS:
        source["verified_by"] = verification.verified_by
        source["verification_date"] = verification.verification_date.isoformat()
        donnees["status"] = verification.target_status.value
    donnees["verification_method"] = verification.verification_method.value

    if verification.article:
        source["article"] = verification.article
    if verification.version_date is not None:
        source["version_date"] = verification.version_date.isoformat()
    donnees["source"] = source

    if verification.exceptions_status is not None:
        donnees["exceptions_status"] = verification.exceptions_status.value
        donnees["exceptions"] = list(verification.exceptions)

    if verification.verdict is Verdict.CORRIGE:
        # Un énoncé corrigé remplace du droit : on reversionne au lieu d'écraser.
        donnees["supersedes"] = f"{regle.id}-v{regle.version}"
        donnees["version"] = regle.version + 1
        donnees["statement"] = verification.statement

    if verification.comment:
        notes = donnees.get("notes", "")
        marque = f"[{verification.verdict.value}] {verification.comment}"
        donnees["notes"] = f"{notes} {marque}".strip()

    return Rule.model_validate(donnees)


# -- registre de vérification ------------------------------------------------------ #


def charger_registre(chemin: Path = REGISTRE_VERIFICATION) -> list[Verification]:
    """Lit le registre. Un registre absent vaut « aucune vérification »."""
    chemin = Path(chemin)
    if not chemin.is_file():
        return []
    contenu = lire_json(chemin)
    return [Verification.model_validate(e) for e in contenu.get("entries", [])]


def ecrire_registre(
    verifications: list[Verification], chemin: Path = REGISTRE_VERIFICATION
) -> Path:
    """Écrit le registre sous forme canonique, trié par identifiant de règle."""
    chemin = Path(chemin)
    ecrire_json(
        chemin,
        {
            "ledger_version": VERSION_REGISTRE,
            "entries": [
                v.model_dump(mode="json")
                for v in sorted(verifications, key=lambda v: v.rule_id)
            ],
        },
    )
    return chemin


def fusionner_registre(
    nouvelles: list[Verification], chemin: Path = REGISTRE_VERIFICATION
) -> list[Verification]:
    """Ajoute des constats au registre ; le plus récent l'emporte sur une même règle."""
    par_regle = {v.rule_id: v for v in charger_registre(chemin)}
    for verification in nouvelles:
        par_regle[verification.rule_id] = verification
    return sorted(par_regle.values(), key=lambda v: v.rule_id)
