# FinReg Bench

Harnais d'évaluation : interroge plusieurs LLM sur un corpus de questions de
réglementation financière et produit un classement auditable, publié par le site
[FinReg Compass](https://github.com/amirRbh/finreg-compass).

Les règles du projet sont dans [CLAUDE.md](CLAUDE.md) — elles font autorité.

## Installation

```sh
uv venv --python 3.11
uv pip install -e ".[dev]"
```

## Utilisation

```sh
# Valider le corpus (rapporte toutes les erreurs d'un coup)
uv run finreg valider

# Exécuter le banc : écrit runs/AAAA-MM-JJ-HHMM/
uv run finreg executer

# Corriger à la main runs/<run>/revue.csv, puis réinjecter
uv run finreg revue reinjecter runs/<run>

# Publier vers le site (corpus public uniquement)
uv run finreg exporter runs/<run> --vers ../finreg-compass/public/data

# Vérifier que deux runs sont identiques
uv run finreg verifier-reproductibilite runs/<run_a> runs/<run_b>
```

## Tests

```sh
uv run pytest
```

Aucun test n'accède au réseau : le runner et le juge tournent sur des
fournisseurs factices locaux et déterministes.

## État

Les six étapes de construction sont faites et testées. Le point d'extension
restant est l'ajout d'adaptateurs vers des fournisseurs réels : voir
`src/providers/base.py` (`enregistrer_adaptateur`) et l'exemple
`src/providers/fake.py`.

Le corpus livré dans `corpus/public/amorce.json` est un **jeu d'amorce non
vérifié**, destiné à faire tourner la chaîne. Son champ `verifie_par` le dit
explicitement ; il doit être remplacé par des items réellement validés avant
toute publication.
