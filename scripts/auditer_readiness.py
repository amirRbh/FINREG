"""Audit d'exploitabilité : de la règle vérifiée à la règle utilisable.

Sorties :

- `reports/RULEBOOK_READINESS_SUMMARY.md` — les trois seuils, les blocages, la
  recommandation ;
- `reports/RULEBOOK_FAMILY_READINESS.csv` — une ligne par règle.

Le script ne modifie rien : il constate. Les corrections passent par le circuit
de vérification, qui exige une signature.
"""

from __future__ import annotations

from pathlib import Path

from src.bench.audit_rulebook import texte_de_la_regle
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.bench.rapport_readiness import (
    MATRICE_READINESS,
    SYNTHESE_READINESS,
    ecrire_matrice_readiness,
    recommandation,
    synthese,
)
from src.bench.readiness import comparer_au_rejeu, controles_integrite, evaluer
from src.bench.sources_primaires import CACHE_PRIMAIRE, recuperateur_http
from src.bench.verification import REGISTRE_VERIFICATION, charger_registre
from scripts.auditer_completude import analyser_regle

#: Longueur de l'extrait officiel reporté dans la file de revue.
LONGUEUR_EXTRAIT = 900


def _rulebook_initial() -> list:
    """Le Rulebook tel que le script de génération le produit, avant vérification.

    C'est le point de départ du rejeu : des règles en `draft`, non vérifiées,
    telles qu'elles sont déclarées dans `scripts/rulebook_*.py`.
    """
    from scripts.generer_rulebook import DOMAINES, normaliser
    from src.bench.regles import Rule

    return [
        Rule.model_validate(normaliser(brut, fichier, domaine))
        for fichier, (domaine, regles) in DOMAINES.items()
        for brut in regles
    ]


def auditer_readiness(
    racine: Path = RACINE_RULEBOOK,
    synthese_chemin: Path = SYNTHESE_READINESS,
    matrice: Path = MATRICE_READINESS,
    registre: Path = REGISTRE_VERIFICATION,
    recuperateur=recuperateur_http,
    cache: Path | None = CACHE_PRIMAIRE,
) -> dict:
    """Situe chaque règle sur les trois seuils, écrit les trois artefacts."""
    regles = charger_rulebook(racine)
    par_id = {r.id: r for r in regles}

    constats = {}
    extraits = {}
    for regle in regles:
        constats[regle.id] = analyser_regle(regle, recuperateur, cache)
        trouve = texte_de_la_regle(regle, recuperateur, cache)
        # Une doctrine n'a pas d'articles : l'extrait est alors la page elle-même.
        brut = trouve.article or (
            trouve.texte.text if trouve.texte and not trouve.texte.articles else ""
        )
        extraits[regle.id] = brut[:LONGUEUR_EXTRAIT]

    etats = [evaluer(r, constats[r.id]) for r in regles]
    par_etat = {e.rule_id: e for e in etats}
    entrees = charger_registre(registre)
    anomalies = controles_integrite(regles, constats, par_etat, entrees)
    # Le rejeu du registre couvre à lui seul les contrôles de version : lui seul
    # sait si une entrée a réellement fait avancer une règle.
    anomalies += comparer_au_rejeu(regles, _rulebook_initial(), entrees)

    # Sept contrôles d'intégrité : ceux qui ne relèvent aucune anomalie passent.
    controles = {a.controle for a in anomalies}
    tous = {
        "rejeu_divergent",
        "regle_hors_registre",
        "registre_non_rejouable",
        "correction_sans_version",
        "enonce_divergent",
        "gold_ready_sans_source",
        "gold_ready_exceptions_inconnues",
        "gold_ready_affirmation_negative",
        "validee_non_corroboree",
        "gold_ready_divergent",
        "family_ready_sans_gold_ready",
    }
    tests_integrite = (len(tous - controles), len(tous & controles))

    Path(synthese_chemin).parent.mkdir(parents=True, exist_ok=True)
    Path(synthese_chemin).write_text(
        synthese(etats, regles, anomalies, tests_integrite), encoding="utf-8"
    )
    ecrire_matrice_readiness(etats, Path(matrice))

    verdict, motif = recommandation(etats, anomalies)
    return {
        "rules": len(regles),
        "gold_ready": sum(1 for e in etats if e.gold_ready),
        "family_ready": sum(1 for e in etats if e.family_ready),
        "gold_sans_family": sum(1 for e in etats if e.gold_ready and not e.family_ready),
        "anomalies": [str(a) for a in anomalies],
        "integrity_passed": tests_integrite[0],
        "integrity_failed": tests_integrite[1],
        "recommendation": verdict,
        "reason": motif,
    }


if __name__ == "__main__":
    resultat = auditer_readiness()
    print(f"{resultat['rules']} règle(s)")
    print(f"  gold_ready   : {resultat['gold_ready']}")
    print(f"  family_ready : {resultat['family_ready']}")
    print(f"  gold sans family : {resultat['gold_sans_family']}")
    print(f"  intégrité : {resultat['integrity_passed']} passés, {resultat['integrity_failed']} échoués")
    for anomalie in resultat["anomalies"]:
        print(f"    {anomalie}")
    print(f"  RECOMMANDATION : {resultat['recommendation']}")
