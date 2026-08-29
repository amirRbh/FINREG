"""Faux fournisseur local : aucun réseau, réponses déterministes.

Sert au développement du runner et à toute la suite de tests. Il sait produire
les cas pathologiques que le scoring doit attraper (référence inventée,
erreur disqualifiante, abstention) afin qu'ils soient testables sans appeler
un vrai modèle.
"""

from __future__ import annotations

from src.io_utils import hash_texte
from src.providers.base import ErreurFournisseur, Fournisseur, Requete, enregistrer_adaptateur

#: Réponses imposées, par sous-chaîne présente dans la question. Les tests s'en servent
#: pour fabriquer un cas précis sans dépendre de la génération pseudo-aléatoire.
SCENARIOS: dict[str, str] = {}


class FauxFournisseur(Fournisseur):
    """Répond de façon déterministe et compte ses appels."""

    def __init__(self, config) -> None:
        super().__init__(config)
        self.appels: list[Requete] = []
        self.scenarios: dict[str, str] = dict(SCENARIOS)
        #: Sous-chaînes de question qui doivent déclencher une erreur d'appel.
        self.questions_en_echec: set[str] = set()

    @property
    def nb_appels(self) -> int:
        return len(self.appels)

    async def completer(self, requete: Requete, timeout_s: float) -> str:
        self.appels.append(requete)

        for fragment in self.questions_en_echec:
            if fragment in requete.question:
                raise ErreurFournisseur(f"échec simulé pour « {fragment} »")

        for fragment, reponse in self.scenarios.items():
            if fragment in requete.question:
                return reponse

        return self._reponse_par_defaut(requete)

    def _reponse_par_defaut(self, requete: Requete) -> str:
        empreinte = hash_texte(self.modele + requete.question)[:8]
        return (
            f"Réponse du modèle {self.modele} ({empreinte}). "
            "Cette question relève du texte cité en source, dont l'article applicable "
            "encadre l'obligation décrite. Il convient de vérifier la version en vigueur "
            "à la date d'application avant de conclure."
        )


enregistrer_adaptateur("fake", FauxFournisseur)


class FauxJuge(Fournisseur):
    """Juge factice : rend un JSON valide, déterministe, dérivé de la réponse notée.

    Il permet de faire tourner la chaîne complète en local sans appeler de modèle.
    Ses notes n'ont aucune valeur d'évaluation : elles servent à vérifier la
    mécanique, pas à classer des modèles.
    """

    def __init__(self, config) -> None:
        super().__init__(config)
        self.appels: list[Requete] = []
        #: Sortie imposée, si les tests veulent un cas précis.
        self.sortie_imposee: str | None = None

    @property
    def nb_appels(self) -> int:
        return len(self.appels)

    async def completer(self, requete: Requete, timeout_s: float) -> str:
        import json

        self.appels.append(requete)
        if self.sortie_imposee is not None:
            return self.sortie_imposee

        # Notes stables pour un même contenu : le run reste reproductible.
        graine = hash_texte(requete.question)
        notes = {
            axe: int(graine[index], 16) % 3
            for index, axe in enumerate(
                ("exactitude", "sourcing", "calibration", "exploitabilite")
            )
        }
        return json.dumps(
            {"notes": notes, "justification": "Notation factice, sans valeur d'évaluation."},
            ensure_ascii=False,
        )


enregistrer_adaptateur("fake-juge", FauxJuge)
