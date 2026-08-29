"""Schémas pydantic du harnais FinReg Bench.

Les noms de champs sont en français : ils font partie du contrat de données du
corpus et ne doivent pas être renommés (cf. CLAUDE.md §4).
"""

from __future__ import annotations

import datetime as dt
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# --------------------------------------------------------------------------- #
# Vocabulaires fermés
# --------------------------------------------------------------------------- #


class Corpus(str, Enum):
    PUBLIC = "public"
    PRIVE = "private"


class TypeItem(str, Enum):
    FAIT = "fait"
    QUALIFICATION = "qualification"
    CALCUL = "calcul"
    PIEGE = "piege"
    ABSTENTION = "abstention"


class Axe(str, Enum):
    EXACTITUDE = "exactitude"
    SOURCING = "sourcing"
    CALIBRATION = "calibration"
    EXPLOITABILITE = "exploitabilite"


AXES: tuple[Axe, ...] = tuple(Axe)

#: Note d'un axe : entier de 0 à 2 (cf. CLAUDE.md §6).
NoteAxe = Annotated[int, Field(ge=0, le=2)]

#: Note maximale cumulée sur les quatre axes.
NOTE_MAX = 2 * len(AXES)


class Flag(str, Enum):
    """Signalements attachés à une réponse, repris tels quels par le site public."""

    HALLUCINATION_SOURCE = "hallucination_source"
    SOURCING_INCOMPLET = "sourcing_incomplet"
    SURCONFIANCE = "surconfiance"
    ABSTENTION = "abstention"
    ERREUR_DISQUALIFIANTE = "erreur_disqualifiante"


class ModeleStrict(BaseModel):
    """Base commune : pas de champ inconnu, chaînes détourées."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# --------------------------------------------------------------------------- #
# Item de corpus
# --------------------------------------------------------------------------- #


class Source(ModeleStrict):
    """Référence réglementaire adossée à un item, avec sa trace de vérification."""

    texte: str
    article: str
    url: str
    date_version: dt.date
    verifie_par: str = ""
    date_verification: dt.date | None = None


class Item(ModeleStrict):
    id: str = Field(min_length=1)
    corpus: Corpus
    domaine: str = Field(min_length=1)
    type: TypeItem
    difficulte: int = Field(ge=1, le=5)
    question: str = Field(min_length=1)
    reponse_reference: str = Field(min_length=1)
    points_cles: list[str] = Field(min_length=1)
    erreurs_disqualifiantes: list[str] = Field(default_factory=list)
    source: Source
    date_validite: dt.date
    sensible_au_temps: bool

    @model_validator(mode="after")
    def _verifier_tracabilite_du_public(self) -> Item:
        """Un item public non vérifié par un humain nommé est refusé (CLAUDE.md §4)."""
        if self.corpus is Corpus.PUBLIC:
            if not self.source.verifie_par:
                raise ValueError(
                    "item public : source.verifie_par est obligatoire et ne peut pas être vide"
                )
            if self.source.date_verification is None:
                raise ValueError(
                    "item public : source.date_verification est obligatoire"
                )
        return self

    @model_validator(mode="after")
    def _verifier_listes_non_vides(self) -> Item:
        if any(not p.strip() for p in self.points_cles):
            raise ValueError("points_cles : aucun point clé ne peut être vide")
        if any(not e.strip() for e in self.erreurs_disqualifiantes):
            raise ValueError(
                "erreurs_disqualifiantes : aucune entrée ne peut être vide"
            )
        return self

    @property
    def est_prive(self) -> bool:
        return self.corpus is Corpus.PRIVE


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #


class ConfigFournisseur(ModeleStrict):
    """Déclaration d'un fournisseur de modèle.

    ``zero_retention`` vaut False par défaut : un fournisseur qui ne garantit
    pas explicitement la non-rétention est refusé pour le corpus privé
    (CLAUDE.md §3). Le champ est un booléen strict, il n'accepte pas ``null``.
    """

    id: str = Field(min_length=1)
    nom: str = Field(min_length=1)
    editeur: str = Field(min_length=1)
    adaptateur: str = Field(min_length=1)
    modele: str = Field(min_length=1)
    zero_retention: bool = False
    actif: bool = True

    @field_validator("zero_retention", mode="before")
    @classmethod
    def _zero_retention_strict(cls, valeur: object) -> bool:
        """Seul un vrai booléen `true` vaut garantie de non-rétention.

        Absent, `null`, `"true"`, `1` : tout ce qui n'est pas un booléen est
        ramené à False. On refuse par défaut plutôt que de déduire une garantie
        d'une valeur approximative (CLAUDE.md §3).
        """
        return valeur is True


class ConfigExecution(ModeleStrict):
    nb_runs: int = Field(default=3, ge=1)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    concurrence: int = Field(default=4, ge=1)
    requetes_par_minute: int = Field(default=60, ge=1)
    timeout_s: float = Field(default=60.0, gt=0)


class ConfigJuge(ModeleStrict):
    """Le juge reçoit le texte des items : il est soumis au même garde-fou."""

    adaptateur: str = "fake"
    modele: str = "juge-factice"
    zero_retention: bool = False
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    #: Écart de note au-delà duquel un item part en revue humaine (CLAUDE.md §6).
    seuil_ecart_revue: int = Field(default=1, ge=0)

    @field_validator("zero_retention", mode="before")
    @classmethod
    def _zero_retention_strict(cls, valeur: object) -> bool:
        return valeur is True


class Config(ModeleStrict):
    """Configuration complète d'une exécution ; gelée telle quelle dans le run."""

    corpus: Corpus
    racine_corpus: str = "corpus"
    chemin_prompt_systeme: str = "prompts/system.txt"
    chemin_prompt_juge: str = "prompts/judge.txt"
    chemin_registre: str = "registry/references.json"
    racine_cache: str = ".cache"
    racine_runs: str = "runs"
    execution: ConfigExecution = Field(default_factory=ConfigExecution)
    juge: ConfigJuge = Field(default_factory=ConfigJuge)
    fournisseurs: list[ConfigFournisseur] = Field(min_length=1)
    #: Domaines acceptés par le site public ; l'export refuse tout autre domaine.
    domaines_publics: list[str] = Field(
        default_factory=lambda: ["SFDR", "MIFID", "AMF", "DORA", "LCBFT"]
    )

    @model_validator(mode="after")
    def _ids_fournisseurs_uniques(self) -> Config:
        vus = [f.id for f in self.fournisseurs]
        doublons = sorted({i for i in vus if vus.count(i) > 1})
        if doublons:
            raise ValueError(f"identifiants de fournisseur en double : {doublons}")
        return self

    @property
    def fournisseurs_actifs(self) -> list[ConfigFournisseur]:
        return [f for f in self.fournisseurs if f.actif]


# --------------------------------------------------------------------------- #
# Réponses et scores
# --------------------------------------------------------------------------- #


class ReponseBrute(ModeleStrict):
    """Réponse d'un modèle à un item, pour un index de run donné."""

    item_id: str
    fournisseur_id: str
    modele: str
    index_run: int = Field(ge=0)
    hash_prompt: str
    texte: str
    depuis_cache: bool = False
    latence_ms: int | None = None
    erreur: str | None = None


class ConstatDeterministe(ModeleStrict):
    """Ce que l'étage déterministe a pu établir sans juge (CLAUDE.md §6)."""

    references_citees: list[str] = Field(default_factory=list)
    references_inventees: list[str] = Field(default_factory=list)
    erreurs_disqualifiantes_detectees: list[str] = Field(default_factory=list)
    abstention_detectee: bool = False
    #: Plafonds imposés aux axes ; None = l'axe reste à la main du juge.
    plafonds: dict[Axe, NoteAxe] = Field(default_factory=dict)
    flags: list[Flag] = Field(default_factory=list)


class NotesAxes(ModeleStrict):
    exactitude: NoteAxe
    sourcing: NoteAxe
    calibration: NoteAxe
    exploitabilite: NoteAxe

    def total(self) -> int:
        return self.exactitude + self.sourcing + self.calibration + self.exploitabilite

    def as_dict(self) -> dict[str, int]:
        return self.model_dump()


class ScoreJuge(ModeleStrict):
    """Sortie JSON stricte du juge LLM. Une sortie non conforme est une erreur."""

    notes: NotesAxes
    justification: str = Field(min_length=1)


class Score(ModeleStrict):
    """Score final d'une réponse, après déterministe, juge et éventuelle revue humaine."""

    item_id: str
    fournisseur_id: str
    index_run: int = Field(ge=0)
    notes: NotesAxes
    flags: list[Flag] = Field(default_factory=list)
    constat: ConstatDeterministe
    justification: str = ""
    origine: Literal["deterministe", "juge", "humain"] = "juge"

    def total(self) -> int:
        return self.notes.total()

    def sur_100(self) -> float:
        return round(100 * self.total() / NOTE_MAX, 1)

    def sur_10(self) -> int:
        """Note 0–10 attendue par le site public."""
        return round(10 * self.total() / NOTE_MAX)
