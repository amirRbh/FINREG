"""Audite le Rulebook contre le texte primaire et écrit les rapports.

Sorties :

- `reports/RULEBOOK_VERIFICATION_QC.md` — ce que l'audit a établi, anomalies comprises ;
- `reports/RULEBOOK_VERIFICATION_MATRIX.csv` — une ligne par règle ;
- `data/verification/dossier-audit.csv` — le dossier pré-rempli, **sans signature**,
  prêt pour `finreg-bench rulebook appliquer-verification`.

Le script ne modifie jamais `data/rules/` : il rassemble la preuve, il ne promeut
rien. La promotion passe par le circuit de vérification, qui exige un
vérificateur nommé — et le dossier pré-rempli laisse justement ces deux colonnes
vides pour qu'aucun chemin ne contourne cette exigence.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from src.bench.audit_rulebook import ClassementAudit, auditer
from src.bench.qc_rulebook import RACINE_RULEBOOK, charger_rulebook
from src.bench.rapport_audit import (
    DOSSIER_AUDIT,
    MATRICE_VERIFICATION,
    RAPPORT_VERIFICATION,
    ecrire_matrice,
    exporter_dossier_prerempli,
    rapport_markdown,
)
from src.bench.sources_primaires import CACHE_PRIMAIRE, recuperateur_http


def auditer_et_rapporter(
    racine: Path = RACINE_RULEBOOK,
    rapport: Path = RAPPORT_VERIFICATION,
    matrice: Path = MATRICE_VERIFICATION,
    dossier: Path = DOSSIER_AUDIT,
    recuperateur=recuperateur_http,
    cache: Path | None = CACHE_PRIMAIRE,
) -> dict:
    """Audite, écrit les trois artefacts, et rend le compte rendu chiffré."""
    regles = charger_rulebook(racine)
    constats = auditer(regles, recuperateur, cache)

    Path(rapport).parent.mkdir(parents=True, exist_ok=True)
    Path(rapport).write_text(rapport_markdown(constats, regles), encoding="utf-8")
    ecrire_matrice(constats, regles, Path(matrice))
    exporter_dossier_prerempli(constats, regles, Path(dossier))

    par_classement = Counter(c.classement.value for c in constats)
    return {
        "rules": len(regles),
        "by_classification": dict(sorted(par_classement.items())),
        "acts_consulted": sorted(
            {c.preuve.celex for c in constats if c.preuve and c.preuve.celex}
        ),
        "articles_found": sum(1 for c in constats if c.preuve and c.preuve.article_found),
        "anomalies": sum(len(c.problemes) for c in constats),
        "report": str(rapport),
        "matrix": str(matrice),
        "dossier": str(dossier),
    }


if __name__ == "__main__":
    resultat = auditer_et_rapporter()
    print(f"{resultat['rules']} règle(s) auditées")
    for classement, nombre in resultat["by_classification"].items():
        print(f"  {classement:24} {nombre}")
    print(f"  actes consultés : {len(resultat['acts_consulted'])}")
    print(f"  articles retrouvés : {resultat['articles_found']}")
    print(f"  anomalies : {resultat['anomalies']}")
    print(f"  rapport : {resultat['report']}")
    print(f"  dossier pré-rempli : {resultat['dossier']}")
