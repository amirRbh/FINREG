# Rulebook — avancement de la revue humaine

```
P0 total     : 28
P0 reviewed  : 0
P0 remaining : 28

P1 total     : 16
P1 reviewed  : 0
P1 remaining : 16
```

## Effet sur l'exploitabilité

| | avant | après |
|---|---:|---:|
| `validated` | 12 | 12 |
| `gold_ready` | 9 | 9 |
| `family_ready` | 9 | 9 |

Aucune décision n'a encore été portée : le bordereau
`data/verification/dossier-revue-p0p1.csv` sort avec ses colonnes de
décision vides, comme prévu. Les colonnes « après » reproduisent donc
l'état actuel.

## Après chaque décision appliquée

L'application d'un bordereau rejoue toute la chaîne, dans cet ordre :

1. la règle est revalidée par le schéma ;
2. la gold-readiness est recalculée, jamais héritée de la décision ;
3. la family-readiness est recalculée ;
4. les contrôles d'intégrité sont réexécutés ;
5. le registre append-only enregistre la décision, sans écraser la précédente.

Une décision humaine ne vaut donc jamais `gold_ready` par elle-même : elle
lève un blocage, et le calcul dit ensuite ce que la règle est devenue.

