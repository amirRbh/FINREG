# Rulebook — contrôle qualité

Rapport généré par `src/bench/qc_rulebook.py`. Il liste ce qui bloque
l'exploitation du Rulebook et ce qui la limite.

## Synthèse

- règles : **58**
- erreurs bloquantes : **0**
- avertissements : **116**

## État de vérification

- règles dont la source n'a pas été consultée : **58 / 58**
- règles utilisables pour ancrer un gold : **0 / 58**

> Les sources primaires (EUR-Lex, Légifrance, AMF, ACPR, TRACFIN, ESMA) sont
> inaccessibles depuis l'environnement de génération. Aucune règle ne peut donc
> dépasser le statut `draft`, et **aucune n'est utilisable pour ancrer un gold**.
> C'est une propriété tenue par le schéma, pas une convention.

## Avertissements (116)

### `doublon_conceptuel` — 3

- `AMF-R-003` : même domaine, même article et même type que « AMF-R-002 »
- `MIFID-R-003` : même domaine, même article et même type que « MIFID-R-002 »
- `MIFID-R-011` : même domaine, même article et même type que « MIFID-R-007 »

### `exceptions` — 55

- `AMF-R-001` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-002` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-003` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-004` : exceptions inconnues : la règle peut produire une question simplifiée
- `AMF-R-005` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-001` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-002` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-003` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-004` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-005` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-006` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-007` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-008` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-009` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-010` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-011` : exceptions inconnues : la règle peut produire une question simplifiée
- `DORA-R-012` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-001` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-002` : exceptions inconnues : la règle peut produire une question simplifiée
- `LCBFT-R-003` : exceptions inconnues : la règle peut produire une question simplifiée
- … et 35 autre(s)

### `verification` — 58

- `AMF-R-001` : source non consultée (model_knowledge_unverified)
- `AMF-R-002` : source non consultée (model_knowledge_unverified)
- `AMF-R-003` : source non consultée (model_knowledge_unverified)
- `AMF-R-004` : source non consultée (model_knowledge_unverified)
- `AMF-R-005` : source non consultée (model_knowledge_unverified)
- `DORA-R-001` : source non consultée (model_knowledge_unverified)
- `DORA-R-002` : source non consultée (model_knowledge_unverified)
- `DORA-R-003` : source non consultée (model_knowledge_unverified)
- `DORA-R-004` : source non consultée (model_knowledge_unverified)
- `DORA-R-005` : source non consultée (model_knowledge_unverified)
- `DORA-R-006` : source non consultée (model_knowledge_unverified)
- `DORA-R-007` : source non consultée (model_knowledge_unverified)
- `DORA-R-008` : source non consultée (model_knowledge_unverified)
- `DORA-R-009` : source non consultée (model_knowledge_unverified)
- `DORA-R-010` : source non consultée (model_knowledge_unverified)
- `DORA-R-011` : source non consultée (model_knowledge_unverified)
- `DORA-R-012` : source non consultée (model_knowledge_unverified)
- `DORA-R-013` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-001` : source non consultée (model_knowledge_unverified)
- `LCBFT-R-002` : source non consultée (model_knowledge_unverified)
- … et 38 autre(s)

