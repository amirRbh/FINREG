"""Plan de couverture du benchmark.

Les pondérations par domaine et par type sont des données de configuration, pas
des constantes enfouies dans le scoring : changer la composition du corpus ne
doit jamais demander de toucher au code qui note.
"""

from __future__ import annotations

from collections import Counter

from pydantic import Field, model_validator

from src.bench.modeles import ModeleStrict
from src.bench.vocabulaires import Corpus, Domain, QuestionType

#: Répartition V0 par domaine (spécification §3).
POIDS_DOMAINES_V0: dict[str, float] = {
    Domain.SFDR.value: 0.30,
    Domain.MIFID.value: 0.20,
    Domain.AMF.value: 0.20,
    Domain.DORA.value: 0.15,
    Domain.LCBFT.value: 0.15,
}

#: Répartition V0 par type de question (spécification §4).
POIDS_TYPES_V0: dict[str, float] = {
    QuestionType.FACT.value: 0.20,
    QuestionType.QUALIFICATION.value: 0.25,
    QuestionType.CALCULATION.value: 0.10,
    QuestionType.FALSE_PREMISE.value: 0.15,
    QuestionType.TRUE_PREMISE_ADVERSARIAL.value: 0.15,
    QuestionType.CALIBRATED_ABSTENTION.value: 0.15,
}

#: Cibles de volume par corpus (spécification §2).
CIBLES_V0: dict[str, int] = {Corpus.PUBLIC.value: 150, Corpus.PRIVE.value: 700}

#: Cibles par domaine énoncées explicitement par la spécification §3 pour le
#: public. DORA et LCB-FT valent tous deux 15 % de 150, soit 22,5 : la
#: répartition proportionnelle doit trancher une égalité, la spécification l'a
#: déjà tranchée. Ces nombres priment donc sur le calcul.
CIBLES_DOMAINES_EXPLICITES_V0: dict[str, dict[str, int]] = {
    Corpus.PUBLIC.value: {
        Domain.SFDR.value: 45,
        Domain.MIFID.value: 30,
        Domain.AMF.value: 30,
        Domain.DORA.value: 22,
        Domain.LCBFT.value: 23,
    }
}


class BenchmarkPlan(ModeleStrict):
    """Composition visée du corpus, et tolérance admise autour d'elle."""

    targets: dict[str, int] = Field(default_factory=lambda: dict(CIBLES_V0))
    domain_weights: dict[str, float] = Field(default_factory=lambda: dict(POIDS_DOMAINES_V0))
    type_weights: dict[str, float] = Field(default_factory=lambda: dict(POIDS_TYPES_V0))
    #: Cibles par domaine imposées, par corpus. Priment sur la répartition
    #: proportionnelle quand elles existent.
    domain_targets_override: dict[str, dict[str, int]] = Field(
        default_factory=lambda: {
            corpus: dict(cibles)
            for corpus, cibles in CIBLES_DOMAINES_EXPLICITES_V0.items()
        }
    )
    #: Écart admis, en nombre d'items, entre la cible et le réel.
    tolerance: int = Field(default=2, ge=0)

    @model_validator(mode="after")
    def _les_poids_somment_a_un(self) -> BenchmarkPlan:
        for nom, poids in (("domain_weights", self.domain_weights), ("type_weights", self.type_weights)):
            if not poids:
                raise ValueError(f"{nom} ne peut pas être vide")
            total = sum(poids.values())
            if abs(total - 1.0) > 1e-6:
                raise ValueError(f"{nom} : la somme des poids vaut {total}, attendu 1.0")
            if any(p < 0 for p in poids.values()):
                raise ValueError(f"{nom} : un poids négatif n'a pas de sens")

        for corpus, cibles in self.domain_targets_override.items():
            attendu = self.targets.get(corpus)
            if attendu is not None and sum(cibles.values()) != attendu:
                raise ValueError(
                    f"domain_targets_override[{corpus}] somme à "
                    f"{sum(cibles.values())}, attendu {attendu}"
                )
        return self

    def target_for(self, corpus: Corpus) -> int:
        return self.targets.get(corpus.value, 0)

    def _repartir(self, total: int, poids: dict[str, float]) -> dict[str, int]:
        """Répartit un total entier selon des poids, sans perdre d'unité.

        Méthode des plus forts restes : la somme des cibles vaut exactement le
        total, ce qui n'est pas le cas d'un simple arrondi.
        """
        bruts = {cle: total * p for cle, p in poids.items()}
        planchers = {cle: int(valeur) for cle, valeur in bruts.items()}
        reste = total - sum(planchers.values())
        ordre = sorted(bruts, key=lambda cle: (-(bruts[cle] - planchers[cle]), cle))
        for cle in ordre[:reste]:
            planchers[cle] += 1
        return planchers

    def domain_targets(self, corpus: Corpus) -> dict[str, int]:
        impose = self.domain_targets_override.get(corpus.value)
        if impose:
            return dict(impose)
        return self._repartir(self.target_for(corpus), self.domain_weights)

    def type_targets(self, corpus: Corpus) -> dict[str, int]:
        return self._repartir(self.target_for(corpus), self.type_weights)


class LigneCouverture(ModeleStrict):
    key: str
    target: int
    actual: int

    @property
    def gap(self) -> int:
        return self.actual - self.target


def coverage_report(items: list, plan: BenchmarkPlan, corpus: Corpus) -> dict:
    """Écart entre la composition visée et la composition réelle d'un corpus."""
    concernes = [item for item in items if item.corpus is corpus]
    par_domaine = Counter(item.domain.value for item in concernes)
    par_type = Counter(item.question_type.value for item in concernes)

    def lignes(cibles: dict[str, int], reels: Counter) -> list[LigneCouverture]:
        cles = sorted(set(cibles) | set(reels))
        return [
            LigneCouverture(key=cle, target=cibles.get(cle, 0), actual=reels.get(cle, 0))
            for cle in cles
        ]

    domaines = lignes(plan.domain_targets(corpus), par_domaine)
    types = lignes(plan.type_targets(corpus), par_type)

    return {
        "corpus": corpus.value,
        "target_total": plan.target_for(corpus),
        "actual_total": len(concernes),
        "by_domain": [ligne.model_dump() | {"gap": ligne.gap} for ligne in domaines],
        "by_type": [ligne.model_dump() | {"gap": ligne.gap} for ligne in types],
        "within_tolerance": all(
            abs(ligne.gap) <= plan.tolerance for ligne in domaines + types
        ),
    }
