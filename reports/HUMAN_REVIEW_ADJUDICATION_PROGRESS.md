# Arbitrage humain — progression

Au 2026-08-30. Les décisions sont comptées en relisant
`data/verification/dossier-adjudication.csv` : une ligne vide n'est pas une
décision, et aucune n'est écrite par le générateur.

## Avancement

| Priorité | Total | Arbitrées | Restantes |
|---|---:|---:|---:|
| P0 | 28 | 0 | 28 |
| P1 | 16 | 0 | 16 |

Regroupements : 0 tranché(s) sur 39.

## Effet sur les seuils

| Seuil | Avant | Après |
|---|---:|---|
| `validated` | 12 | — |
| `gold_ready` | 9 | — |
| `family_ready` | 9 | — |

La colonne « après » reste vide tant que les décisions n'ont pas été
appliquées puis l'audit rejoué. Un « après » prévisionnel serait un
`gold_ready` accordé par anticipation — ce que la spécification interdit.

## Ce qui reste bloqué

| Blocage | P0 | P1 |
|---|---:|---:|
| `EXCEPTION_UNRESOLVED` | 11 | 11 |
| `NEGATIVE_CLAIM_UNRESOLVED` | 6 | 0 |
| `SOURCE_INCOMPLETE` | 10 | 5 |
| `TEMPORAL_UNRESOLVED` | 1 | 0 |

## Après chaque décision

1. revalider la règle ; 2. recalculer la gold-readiness ; 3. recalculer la
family-readiness ; 4. rejouer les contrôles d'intégrité ; 5. écrire au
registre append-only. Dans cet ordre, et jamais l'un sans les autres.

