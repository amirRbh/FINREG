# Rulebook — contrôle qualité

Rapport généré par `src/bench/qc_rulebook.py`. Il liste ce qui bloque
l'exploitation du Rulebook et ce qui la limite.

## Synthèse

- règles : **58**
- erreurs bloquantes : **0**
- avertissements : **80**

## État de vérification

- règles dont la source n'a pas été consultée : **13 / 58**
- règles utilisables pour ancrer un gold : **9 / 58**

> **45 règle(s) sur 58** ont été confrontées à leur texte
> primaire, par récupération auprès de CELLAR (Office des publications de
> l'Union), et signées par un vérificateur nommé. Le détail est dans
> `reports/RULEBOOK_VERIFICATION_QC.md`.

## Circuit de vérification

La vérification ne s'improvise pas dans les fichiers de règles : elle passe
par un dossier CSV, relu et réinjecté (`src/bench/verification.py`).

```sh
finreg-bench rulebook exporter-verification --sortie verification.csv
# le vérificateur consulte les textes et remplit les colonnes de constat
finreg-bench rulebook appliquer-verification verification.csv
```

Les constats sont conservés dans `data/verification/rulebook-ledger.json`,
hors de `data/rules/`, pour qu'une régénération du Rulebook ne les efface pas.
Le verrou reste entier : `appliquer` refuse toute promotion sans méthode sur
texte primaire, vérificateur nommé et date, et refuse un statut `validated`
tant que les exceptions de la règle sont inconnues.

## Ce que la vérification doit établir

Constats qui n'exigent pas de lire le texte : ils sont déductibles de la
citation elle-même, et devront être corrigés au passage.

- **date de version antérieure à l'acte cité** — 15 règle(s) : `DORA-R-001`, `DORA-R-002`, `DORA-R-003`, `DORA-R-004`, `DORA-R-005`, `DORA-R-006`, `DORA-R-007`, `DORA-R-008`, `DORA-R-009`, `DORA-R-010`, `DORA-R-011`, `DORA-R-012`, `DORA-R-013`, `MIFID-R-006`, `SFDR-R-014`
- **ancrage couvrant plusieurs dispositions** — 8 règle(s) : `DORA-R-004`, `DORA-R-009`, `LCBFT-R-005`, `LCBFT-R-008`, `LCBFT-R-013`, `MIFID-R-006`, `SFDR-R-014`, `TAXO-R-003`
- **URL désignant un autre acte que la source citée** — 1 règle(s) : `MIFID-R-006`
- **règles distinctes partageant un article** — 3 règle(s) : `AMF-R-003`, `MIFID-R-003`, `MIFID-R-011`

## Avertissements (80)

### `ancrage_imprecis` — 8

- `DORA-R-004` : l'ancrage « Articles 8 à 13 » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article
- `DORA-R-009` : l'ancrage « Articles 24 à 26 » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article
- `LCBFT-R-005` : l'ancrage « Articles L.561-2-2 et R.561-1 et suivants » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article
- `LCBFT-R-008` : l'ancrage « Articles L.561-10 et R.561-18 » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article
- `LCBFT-R-013` : l'ancrage « Ensemble de la directive » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article
- `MIFID-R-006` : l'ancrage « Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article
- `SFDR-R-014` : l'ancrage « Ensemble du règlement délégué » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article
- `TAXO-R-003` : l'ancrage « Articles 17 et 18 » ne désigne pas une disposition unique : un gold ancré ici ne pourra pas citer son article

### `exceptions` — 43

- `AMF-R-001` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-002` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-003` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-004` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-005` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-002` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-003` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-004` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-006` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-007` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-008` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-010` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-012` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-001` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-002` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-003` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-004` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-005` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-006` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-007` : exceptions inconnues : la règle peut produire une question simplifiée
- … et 23 autre(s)

### `url_acte_different` — 1

- `MIFID-R-006` : l'URL désigne l'acte 2021/1253 alors que la source cite 2017/565 : légitime pour un acte modificatif, à confirmer sinon

### `verification` — 13

- `AMF-R-005` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-001` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-002` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-003` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-004` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-005` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-006` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-007` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-008` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-009` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-010` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-011` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-012` : source non consultée (model_knowledge_unverified)

### `version_date_placeholder` — 15

- `DORA-R-001` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-002` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-003` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-004` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-005` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-006` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-007` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-008` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-009` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-010` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-011` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-012` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `DORA-R-013` : version consultée datée 2020-01-01, antérieure à l'acte 2022/2554 lui-même : la date est un placeholder, à établir lors de la vérification
- `MIFID-R-006` : version consultée datée 2020-01-01, antérieure à l'acte 2021/1253 lui-même : la date est un placeholder, à établir lors de la vérification
- `SFDR-R-014` : version consultée datée 2020-01-01, antérieure à l'acte 2022/1288 lui-même : la date est un placeholder, à établir lors de la vérification

## Infos (3)

### `meme_article` — 3

- `AMF-R-003` : partage l'article de « AMF-R-002 » mais dit autre chose (12% de mots communs) : ancrage à préciser au paragraphe
- `MIFID-R-003` : partage l'article de « MIFID-R-002 » mais dit autre chose (33% de mots communs) : ancrage à préciser au paragraphe
- `MIFID-R-011` : partage l'article de « MIFID-R-007 » mais dit autre chose (15% de mots communs) : ancrage à préciser au paragraphe

