"""Audit de complétude du Rulebook : exceptions, conditions, renvois, gold-readiness.

Sorties :

- `reports/RULEBOOK_COMPLETENESS_QC.md` ;
- `reports/RULEBOOK_GOLD_READINESS.csv` ;
- `data/verification/dossier-completude.csv`, pré-rempli **sans signature**.

Le script ne modifie jamais `data/rules/` : il propose, le circuit de
vérification dispose — et seulement après qu'un vérificateur nommé a signé.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from src.bench.audit_rulebook import couverture_lexicale, texte_de_la_regle
from src.bench.completude import ConstatCompletude, analyser
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.bench.rapport_completude import (
    DOSSIER_COMPLETUDE,
    MATRICE_GOLD,
    RAPPORT_COMPLETUDE,
    ecrire_matrice_gold,
    exporter_dossier_completude,
    rapport_markdown,
)
from src.bench.regles import Rule
from src.bench.rulebook import RuleStatus
from src.bench.sources_primaires import CACHE_PRIMAIRE, recuperateur_http


def analyser_regle(
    regle: Rule, recuperateur=recuperateur_http, cache: Path | None = CACHE_PRIMAIRE
) -> ConstatCompletude:
    """Récupère le texte cité et en analyse la structure juridique."""
    trouve = texte_de_la_regle(regle, recuperateur, cache)
    if trouve.texte is None:
        return analyser(regle, "", "")

    # Une doctrine n'a pas d'articles : la référence est alors la page entière.
    article = trouve.article or (
        trouve.texte.text if not trouve.texte.articles else ""
    )
    article_verifie = bool(trouve.trouvees) or not trouve.texte.articles
    return analyser(
        regle,
        article,
        trouve.texte.text,
        article_verifie=article_verifie,
        concordance=couverture_lexicale(regle.statement, article) if article else 0.0,
    )


def auditer_completude(
    racine: Path = RACINE_RULEBOOK,
    rapport: Path = RAPPORT_COMPLETUDE,
    matrice: Path = MATRICE_GOLD,
    dossier: Path = DOSSIER_COMPLETUDE,
    recuperateur=recuperateur_http,
    cache: Path | None = CACHE_PRIMAIRE,
) -> dict:
    """Analyse, écrit les trois artefacts, et rend le compte rendu chiffré."""
    regles = charger_rulebook(racine)
    # Ordre de priorité : les critiques d'abord, comme pour l'audit de sources.
    constats = [analyser_regle(r, recuperateur, cache) for r in regles]

    Path(rapport).parent.mkdir(parents=True, exist_ok=True)
    Path(rapport).write_text(rapport_markdown(constats, regles), encoding="utf-8")
    ecrire_matrice_gold(constats, regles, Path(matrice))
    exporter_dossier_completude(constats, regles, Path(dossier))

    utilisables = [
        c for c in constats if c.statut_propose is RuleStatus.VALIDATED and c.gold_ready
    ]
    return {
        "rules": len(regles),
        "by_status": dict(sorted(Counter(c.statut_propose.value for c in constats).items())),
        "by_exceptions": dict(
            sorted(Counter(c.exceptions_status.value for c in constats).items())
        ),
        "gold_ready": sum(1 for c in constats if c.gold_ready),
        "usable_for_families": len(utilisables),
        "rules_modified": sum(1 for c in constats if c.exceptions_extraites),
        "report": str(rapport),
        "matrix": str(matrice),
        "dossier": str(dossier),
    }


if __name__ == "__main__":
    resultat = auditer_completude()
    print(f"{resultat['rules']} règle(s) examinées")
    for statut, nombre in resultat["by_status"].items():
        print(f"  {statut:24} {nombre}")
    print(f"  gold_ready : {resultat['gold_ready']}")
    print(f"  utilisables pour les familles : {resultat['usable_for_families']}")
    print(f"  règles à reversionner : {resultat['rules_modified']}")
    print(f"  rapport : {resultat['report']}")
    print(f"  dossier à signer : {resultat['dossier']}")
