# Rulebook — synthèse d'exploitabilité

```
Rulebook
  58 total

Status
  validated:      12
  source_checked: 33
  draft:          13

Readiness
  gold_ready:     9
  family_ready:   9

Blockers
  exception:       25
  temporal:        1
  source:          15
  cross_reference: 0
  abstraction:     2
  other:           6

Human review
  P0: 28
  P1: 16
  P2: 4
  P3: 1

Critical integrity tests
  passed: 11
  failed: 0

Recommendation
  READY_AFTER_HUMAN_REVIEW
```

**READY_AFTER_HUMAN_REVIEW** — 9 règle(s) prêtes, mais 44 arbitrage(s) P0/P1 en attente : générer maintenant figerait des familles sur des règles dont la portée reste à trancher.

## Les trois seuils, et pourquoi ils diffèrent

| Seuil | Ce qu'il affirme | Ce qu'il exige en plus |
|---|---|---|
| `validated` | la règle est juridiquement établie | les huit critères de validation |
| `gold_ready` | on peut en tirer une réponse de référence sans réinterpréter le droit | portance de l'énoncé **et** prérequis probatoires |
| `family_ready` | elle peut ancrer une famille de questions | statut `validated` **et** de quoi construire des angles |

## Correction apportée à `gold_ready`

`gold_ready` était calculé sur la seule précision de l'énoncé. Le chiffre
le trahissait : quarante et une règles étaient dites prêtes, dont treize
dont la source n'était pas vérifiée. Un énoncé porteur adossé à une source
non consultée ne donne pas un gold prêt, il donne un gold qui a l'air prêt.

`gold_ready` exige désormais, en plus de la portance : source primaire
vérifiée, article retrouvé, recherche d'exceptions aboutie, temporalité
établie, renvois vérifiés, affirmations négatives résolues. **La logique a
été corrigée, pas le rapport.**

## Blocages, par catégorie normalisée

| Catégorie | Règles | Ce qu'elle recouvre |
|---|---:|---|
| `EXCEPTION_UNRESOLVED` | 25 | dérogations non tranchées |
| `SOURCE_INCOMPLETE` | 15 | source non consultée, ou article non retrouvé |
| `TEMPORAL_UNRESOLVED` | 1 | version applicable non établie |
| `RULE_TOO_ABSTRACT` | 2 | énoncé qui décrit le texte au lieu de le dire |
| `CROSS_REFERENCE_UNRESOLVED` | 0 | renvois non résolus |
| `NEGATIVE_CLAIM_UNRESOLVED` | 6 | une absence affirmée sans être attestée |
| `SCHEMA_INCOMPLETE` | 0 | rien à quoi accrocher un angle de question |
| `HUMAN_REVIEW_REQUIRED` | 0 | une décision humaine reste à porter |
| `OTHER` | 0 | hors des catégories ci-dessus |

## `gold_ready` sans `family_ready` (0)

Aucune : toute règle prête pour un gold l'est aussi pour une famille. L'écart observé auparavant venait du calcul de `gold_ready`, corrigé depuis.

## Anomalies d'intégrité

Aucune.

