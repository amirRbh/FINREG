"""Registre : charge la hiérarchie et vérifie son intégrité.

Les chargeurs public et privé sont **séparés**. Il n'existe pas de fonction qui
charge les deux d'un coup : lire le privé demande un appel explicite, distinct,
qui ne peut pas se produire par distraction dans un chemin de publication.

Comme en V0.1, la validation rapporte toutes les erreurs d'un coup.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from pydantic import ValidationError

from src.bench.items import Item
from src.bench.regles import Concept, QuestionFamily, Rule, TwinGroup
from src.bench.vocabulaires import Corpus, ValidationStatus

DOSSIERS: dict[Corpus, str] = {Corpus.PUBLIC: "public", Corpus.PRIVE: "private"}


@dataclass(frozen=True)
class Erreur:
    """Une anomalie localisée, corrigeable directement."""

    scope: str
    ref: str
    message: str

    def __str__(self) -> str:
        return f"[{self.scope}] {self.ref} : {self.message}"


class RegistreInvalide(Exception):
    def __init__(self, erreurs: list[Erreur]) -> None:
        self.erreurs = erreurs
        detail = "\n".join(f"  - {e}" for e in erreurs)
        super().__init__(f"{len(erreurs)} anomalie(s) de registre :\n{detail}")


def _messages(exc: ValidationError) -> list[str]:
    return [
        f"{'.'.join(str(p) for p in e['loc']) or '(objet)'} : {e['msg']}"
        for e in exc.errors()
    ]


def _lire_objets(chemin: Path) -> tuple[list[dict], list[Erreur]]:
    try:
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [Erreur("fichier", chemin.name, f"JSON illisible : {exc}")]
    if isinstance(contenu, dict):
        return [contenu], []
    if isinstance(contenu, list) and all(isinstance(o, dict) for o in contenu):
        return contenu, []
    return [], [Erreur("fichier", chemin.name, "attendu : un objet ou une liste d'objets")]


#: Python 3.11 : pas de syntaxe générique PEP 695.
T = TypeVar("T")


def _charger(
    chemins: list[Path], modele: type[T], scope: str
) -> tuple[list[T], list[Erreur]]:
    objets: list[T] = []
    erreurs: list[Erreur] = []
    for chemin in chemins:
        bruts, erreurs_fichier = _lire_objets(chemin)
        erreurs.extend(erreurs_fichier)
        for index, brut in enumerate(bruts):
            ref = str(brut.get("base_id") or brut.get("id") or f"#{index}")
            try:
                objets.append(modele.model_validate(brut))
            except ValidationError as exc:
                erreurs.extend(Erreur(scope, ref, m) for m in _messages(exc))
    return objets, erreurs


@dataclass
class Registre:
    """La hiérarchie complète, en mémoire, et les contrôles qui la lient."""

    rules: list[Rule] = field(default_factory=list)
    concepts: list[Concept] = field(default_factory=list)
    families: list[QuestionFamily] = field(default_factory=list)
    twin_groups: list[TwinGroup] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)

    # -- index ------------------------------------------------------------- #

    @property
    def rules_by_id(self) -> dict[str, Rule]:
        return {r.id: r for r in self.rules}

    @property
    def concepts_by_id(self) -> dict[str, Concept]:
        return {c.id: c for c in self.concepts}

    @property
    def families_by_id(self) -> dict[str, QuestionFamily]:
        return {f.id: f for f in self.families}

    @property
    def twin_groups_by_id(self) -> dict[str, TwinGroup]:
        return {g.id: g for g in self.twin_groups}

    @property
    def items_by_id(self) -> dict[str, Item]:
        return {i.id: i for i in self.items}

    def private_ids(self) -> list[str]:
        return sorted(i.id for i in self.items if i.is_private)

    def latest_versions(self) -> dict[str, Item]:
        """Dernière version de chaque gold. Les précédentes restent dans `items`."""
        derniers: dict[str, Item] = {}
        for item in self.items:
            connu = derniers.get(item.base_id)
            if connu is None or item.version > connu.version:
                derniers[item.base_id] = item
        return derniers

    # -- intégrité ---------------------------------------------------------- #

    def check_integrity(self) -> list[Erreur]:
        """Tous les contrôles inter-objets, rapportés ensemble."""
        erreurs: list[Erreur] = []
        erreurs += self._doublons()
        erreurs += self._rattachements()
        erreurs += self._versions()
        erreurs += self._jumeaux()
        return sorted(erreurs, key=lambda e: (e.scope, e.ref, e.message))

    def _doublons(self) -> list[Erreur]:
        erreurs: list[Erreur] = []
        for scope, valeurs in (
            ("rule", [r.id for r in self.rules]),
            ("concept", [c.id for c in self.concepts]),
            ("family", [f.id for f in self.families]),
            ("twin_group", [g.id for g in self.twin_groups]),
            ("item", [i.id for i in self.items]),
        ):
            vus: set[str] = set()
            for valeur in valeurs:
                if valeur in vus:
                    erreurs.append(Erreur(scope, valeur, "identifiant en double"))
                vus.add(valeur)
        return erreurs

    def _rattachements(self) -> list[Erreur]:
        erreurs: list[Erreur] = []
        regles = self.rules_by_id
        concepts = self.concepts_by_id
        familles = self.families_by_id

        for concept in self.concepts:
            for rule_id in concept.rule_ids:
                if rule_id not in regles:
                    erreurs.append(Erreur("concept", concept.id, f"règle inconnue « {rule_id} »"))

        for famille in self.families:
            if famille.concept_id not in concepts:
                erreurs.append(
                    Erreur("family", famille.id, f"concept inconnu « {famille.concept_id} »")
                )

        for item in self.items:
            if item.family_id not in familles:
                erreurs.append(Erreur("item", item.id, f"famille inconnue « {item.family_id} »"))
            for rule_id in item.rule_ids:
                regle = regles.get(rule_id)
                if regle is None:
                    erreurs.append(Erreur("item", item.id, f"règle inconnue « {rule_id} »"))
                elif item.is_gold and not regle.is_usable:
                    # Un gold adossé à une règle non validée n'est pas opposable.
                    erreurs.append(
                        Erreur(
                            "item",
                            item.id,
                            f"règle « {rule_id} » au statut « {regle.status.value} » : "
                            "un gold ne s'adosse qu'à des règles validées",
                        )
                    )
        return erreurs

    def _versions(self) -> list[Erreur]:
        erreurs: list[Erreur] = []
        connus = self.items_by_id
        par_base: dict[str, list[Item]] = {}
        for item in self.items:
            par_base.setdefault(item.base_id, []).append(item)

        for item in self.items:
            if item.supersedes and item.supersedes not in connus:
                erreurs.append(
                    Erreur(
                        "item",
                        item.id,
                        f"supersedes « {item.supersedes} » introuvable : "
                        "l'historique du gold doit rester disponible",
                    )
                )

        for base_id, versions in par_base.items():
            numeros = sorted(v.version for v in versions)
            attendu = list(range(1, len(numeros) + 1))
            if numeros != attendu:
                erreurs.append(
                    Erreur(
                        "item",
                        base_id,
                        f"suite de versions {numeros} discontinue, attendu {attendu} : "
                        "une version supprimée est un historique perdu",
                    )
                )
        return erreurs

    def _jumeaux(self) -> list[Erreur]:
        erreurs: list[Erreur] = []
        groupes = self.twin_groups_by_id
        membres: dict[str, list[Item]] = {}
        for item in self.items:
            if item.twin_group_id:
                membres.setdefault(item.twin_group_id, []).append(item)

        for group_id, items in membres.items():
            groupe = groupes.get(group_id)
            if groupe is None:
                for item in items:
                    erreurs.append(
                        Erreur("item", item.id, f"twin group inconnu « {group_id} »")
                    )
                continue

            for item in items:
                if item.family_id != groupe.family_id:
                    erreurs.append(
                        Erreur(
                            "twin_group",
                            group_id,
                            f"l'item {item.id} appartient à la famille "
                            f"« {item.family_id} », le groupe à « {groupe.family_id} » : "
                            "des jumeaux doivent être comparables",
                        )
                    )

            if len(items) < 2:
                erreurs.append(
                    Erreur("twin_group", group_id, "un groupe de jumeaux exige au moins 2 items")
                )
            elif not TwinGroup.roles_distincts([i.twin_role for i in items if i.twin_role]):
                erreurs.append(
                    Erreur(
                        "twin_group",
                        group_id,
                        "tous les items jouent le même rôle : le groupe ne mesure "
                        "aucune sensibilité à la prémisse",
                    )
                )

            corpus = {i.corpus for i in items}
            if len(corpus) > 1:
                erreurs.append(
                    Erreur(
                        "twin_group",
                        group_id,
                        "groupe à cheval sur le public et le privé : publier un "
                        "jumeau révélerait la structure de son jumeau privé",
                    )
                )
        return erreurs

    def validate(self) -> Registre:
        """Lève `RegistreInvalide` s'il reste la moindre anomalie."""
        erreurs = self.check_integrity()
        if erreurs:
            raise RegistreInvalide(erreurs)
        return self


# --------------------------------------------------------------------------- #
# Chargeurs
# --------------------------------------------------------------------------- #


def _fichiers(dossier: Path) -> list[Path]:
    return sorted(dossier.glob("*.json")) if dossier.is_dir() else []


def charger_referentiel(racine: Path) -> tuple[Registre, list[Erreur]]:
    """Charge règles, concepts, familles et groupes — sans aucun item."""
    racine = Path(racine)
    erreurs: list[Erreur] = []

    rules, e = _charger(_fichiers(racine / "rules"), Rule, "rule")
    erreurs += e
    concepts, e = _charger(_fichiers(racine / "concepts"), Concept, "concept")
    erreurs += e
    families, e = _charger(_fichiers(racine / "families"), QuestionFamily, "family")
    erreurs += e
    groups, e = _charger(_fichiers(racine / "twin_groups"), TwinGroup, "twin_group")
    erreurs += e

    return Registre(rules=rules, concepts=concepts, families=families, twin_groups=groups), erreurs


def _charger_items(racine_corpus: Path, corpus: Corpus) -> tuple[list[Item], list[Erreur]]:
    items, erreurs = _charger(
        _fichiers(Path(racine_corpus) / DOSSIERS[corpus]), Item, "item"
    )
    conformes = []
    for item in items:
        if item.corpus is not corpus:
            # Un item privé déposé sous public/ est le glissement que rien ne
            # rattraperait ensuite : on le refuse au chargement.
            erreurs.append(
                Erreur(
                    "item",
                    item.id,
                    f"corpus déclaré « {item.corpus.value} » dans le dossier "
                    f"« {corpus.value} »",
                )
            )
        else:
            conformes.append(item)
    return conformes, erreurs


def charger_public(racine_referentiel: Path, racine_corpus: Path) -> Registre:
    """Charge le référentiel et **le seul corpus public**.

    C'est le chargeur qu'utilisent l'export et tout ce qui produit un artefact
    publiable. Il ne touche jamais au dossier privé.
    """
    registre, erreurs = charger_referentiel(racine_referentiel)
    items, erreurs_items = _charger_items(racine_corpus, Corpus.PUBLIC)
    registre.items = items
    erreurs += erreurs_items

    erreurs += registre.check_integrity()
    if erreurs:
        raise RegistreInvalide(sorted(erreurs, key=lambda e: (e.scope, e.ref, e.message)))
    return registre


def charger_prive(
    racine_referentiel: Path, racine_corpus: Path, *, je_confirme_usage_local: bool
) -> Registre:
    """Charge le référentiel et le corpus privé.

    Le drapeau est obligatoire et nommé pour qu'aucun appel ne puisse charger le
    privé sans que ce soit lisible à la relecture du code.
    """
    if je_confirme_usage_local is not True:
        raise PermissionError(
            "chargement du corpus privé refusé : je_confirme_usage_local doit valoir True. "
            "Le corpus privé ne quitte jamais la machine."
        )

    registre, erreurs = charger_referentiel(racine_referentiel)
    items, erreurs_items = _charger_items(racine_corpus, Corpus.PRIVE)
    registre.items = items
    erreurs += erreurs_items

    erreurs += registre.check_integrity()
    if erreurs:
        raise RegistreInvalide(sorted(erreurs, key=lambda e: (e.scope, e.ref, e.message)))
    return registre


def ids_publics_et_prives(racine_corpus: Path) -> tuple[set[str], set[str]]:
    """Identifiants des deux corpus, sans charger le moindre contenu.

    Sert au contrôle d'unicité inter-corpus et aux tests de fuite : on a besoin
    des identifiants privés pour vérifier qu'ils n'apparaissent nulle part, pas
    de leur contenu.
    """
    def ids(corpus: Corpus) -> set[str]:
        trouves: set[str] = set()
        for chemin in _fichiers(Path(racine_corpus) / DOSSIERS[corpus]):
            bruts, _ = _lire_objets(chemin)
            for brut in bruts:
                base = brut.get("base_id")
                if base:
                    trouves.add(f"{base}-v{brut.get('version', 1)}")
        return trouves

    return ids(Corpus.PUBLIC), ids(Corpus.PRIVE)


def collisions_inter_corpus(racine_corpus: Path) -> list[str]:
    """Identifiants présents dans les deux corpus. Doit toujours être vide."""
    publics, prives = ids_publics_et_prives(racine_corpus)
    return sorted(publics & prives)
