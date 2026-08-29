# Question Family Map — contrôle qualité

Rapport généré par `src/bench/qc_familles.py` (phase 7). Il dit ce que le
Rulebook permet de mesurer, ce qu'il ne permet pas encore, et pourquoi.

**Aucune question n'est rédigée à ce stade.** La carte décrit des angles
d'interrogation et leurs conditions ; la rédaction des items est la phase
suivante.

## Synthèse

- règles au Rulebook : **58**
- règles utilisables pour ancrer un gold (`validated`) : **0**
- règles ayant au moins une famille intéressante : **58**
- familles candidates retenues (score ≥ 2) : **316**
- familles prêtes (`ready`) : **0**
- familles bloquées (`blocked`) : **316**
- groupes de jumeaux : **58**
- familles critiques : **87**
- erreurs bloquantes : **0**
- avertissements : **13**

> Aucune règle du Rulebook n'est validée : les 316 familles de la carte sont toutes « blocked » et aucune ne peut engendrer un item du benchmark. La carte décrit ce qui sera mesurable une fois la vérification faite, pas ce qui l'est aujourd'hui.

## Familles par domaine

| Domaine | Familles | Prêtes | Bloquées | Jumeaux | Critiques |
|---|---:|---:|---:|---:|---:|
| AMF | 30 | 0 | 30 | 10 | 8 |
| DORA | 65 | 0 | 65 | 26 | 18 |
| LCBFT | 67 | 0 | 67 | 26 | 23 |
| MIFID | 58 | 0 | 58 | 22 | 15 |
| SFDR | 96 | 0 | 96 | 32 | 23 |

## Familles par type

| Code | Famille | Retenues | Score moyen | Difficulté moyenne |
|---|---|---:|---:|---:|
| F1 | FACT_RECALL | 46 | 2.41 | 2.2 |
| F2 | QUALIFICATION | 54 | 2.61 | 4.1 |
| F3 | CALCULATION | 1 | 3.00 | 3.0 |
| F4 | FALSE_PREMISE | 58 | 2.33 | 4.1 |
| F5 | TRUE_PREMISE_ADVERSARIAL | 58 | 2.33 | 4.1 |
| F6 | CALIBRATED_ABSTENTION | 3 | 2.00 | 4.3 |
| F7 | CONDITIONAL_ANSWER | 12 | 2.00 | 3.3 |
| F8 | TEMPORAL | 16 | 2.00 | 4.1 |
| F9 | CROSS_REGULATORY | 17 | 2.47 | 5.0 |
| F10 | EXCEPTION | 0 | — | — |
| F11 | NEGATIVE_ASSERTION | 7 | 2.00 | 4.1 |
| F12 | MISSING_INFORMATION | 44 | 2.43 | 4.1 |

## Distribution visée (§10)

Hypothèse de rendement — **une hypothèse de planification, pas une promesse** :
une famille de score 3 est réputée engendrer 3 items,
une famille de score 2 en engendrer 2.

Cible : **150 items publics**.

| Type | Cible | Familles | Items estimés | Écart | Atteignable |
|---|---:|---:|---:|---:|:--:|
| calculation | 15 | 1 | 3 | -12 | **non** |
| calibrated_abstention | 22 | 47 | 113 | +91 | oui |
| fact | 30 | 62 | 143 | +113 | oui |
| false_premise | 22 | 65 | 149 | +127 | oui |
| qualification | 38 | 83 | 207 | +169 | oui |
| true_premise_adversarial | 22 | 58 | 135 | +113 | oui |

| Domaine | Cible | Familles | Items estimés | Écart | Atteignable |
|---|---:|---:|---:|---:|:--:|
| AMF | 30 | 30 | 77 | +47 | oui |
| DORA | 22 | 65 | 162 | +140 | oui |
| LCBFT | 23 | 67 | 159 | +136 | oui |
| MIFID | 30 | 58 | 133 | +103 | oui |
| SFDR | 45 | 96 | 219 | +174 | oui |

## Lacunes de couverture

- **familles absentes de toute la carte** : `EXCEPTION`
- **pièges jamais mesurés** : `CAUSAL_INFERENCE`

### Familles manquantes par domaine

| Domaine | Familles absentes |
|---|---|
| AMF | CALIBRATED_ABSTENTION, CONDITIONAL_ANSWER, EXCEPTION, TEMPORAL |
| DORA | CALCULATION, EXCEPTION |
| LCBFT | CALCULATION, CALIBRATED_ABSTENTION, EXCEPTION |
| MIFID | CALCULATION, CALIBRATED_ABSTENTION, EXCEPTION |
| SFDR | CALCULATION, EXCEPTION |

### Exploitation des règles

| Règle | Familles |
|---|---:|
| `AMF-R-001` | 8 |
| `SFDR-R-008` | 8 |
| `DORA-R-007` | 7 |
| `MIFID-R-007` | 7 |
| `SFDR-R-003` | 7 |

## Redondances

- groupes de redondance : **55**
- groupes couvrant plusieurs règles : **3**
- collisions d'ancrage (même concept, même famille, même piège) : **13**
- dont doublons réels (énoncés proches à 50% ou plus) : **0**

| Groupe | Règles | Familles |
|---|---|---:|
| `RG-AMF-POSITION-RECOMMANDATION-OBLIGATION` | `AMF-R-002`, `AMF-R-003` | 11 |
| `RG-MIFID-ARTICLE-25-OBLIGATION` | `MIFID-R-002`, `MIFID-R-003` | 12 |
| `RG-MIFID-ARTICLE-54-PROCEDURE` | `MIFID-R-007`, `MIFID-R-011` | 11 |

### Collisions d'ancrage

- `RG-AMF-POSITION-RECOMMANDATION-OBLIGATION` — FACT_RECALL / NONE — ancrage commun (12% de mots communs) : `AMF-R-002-F1`, `AMF-R-003-F1`
- `RG-AMF-POSITION-RECOMMANDATION-OBLIGATION` — MISSING_INFORMATION / MISSING_INFORMATION — ancrage commun (12% de mots communs) : `AMF-R-002-F12`, `AMF-R-003-F12`
- `RG-AMF-POSITION-RECOMMANDATION-OBLIGATION` — QUALIFICATION / NONE — ancrage commun (12% de mots communs) : `AMF-R-002-F2`, `AMF-R-003-F2`
- `RG-AMF-POSITION-RECOMMANDATION-OBLIGATION` — TRUE_PREMISE_ADVERSARIAL / NONE — ancrage commun (12% de mots communs) : `AMF-R-002-F5`, `AMF-R-003-F5`
- `RG-MIFID-ARTICLE-25-OBLIGATION` — CONDITIONAL_ANSWER / NONE — ancrage commun (33% de mots communs) : `MIFID-R-002-F7`, `MIFID-R-003-F7`
- `RG-MIFID-ARTICLE-25-OBLIGATION` — FACT_RECALL / NONE — ancrage commun (33% de mots communs) : `MIFID-R-002-F1`, `MIFID-R-003-F1`
- `RG-MIFID-ARTICLE-25-OBLIGATION` — FALSE_PREMISE / SCOPE_CONFUSION — ancrage commun (33% de mots communs) : `MIFID-R-002-F4`, `MIFID-R-003-F4`
- `RG-MIFID-ARTICLE-25-OBLIGATION` — MISSING_INFORMATION / MISSING_INFORMATION — ancrage commun (33% de mots communs) : `MIFID-R-002-F12`, `MIFID-R-003-F12`
- `RG-MIFID-ARTICLE-25-OBLIGATION` — QUALIFICATION / NONE — ancrage commun (33% de mots communs) : `MIFID-R-002-F2`, `MIFID-R-003-F2`
- `RG-MIFID-ARTICLE-25-OBLIGATION` — TRUE_PREMISE_ADVERSARIAL / NONE — ancrage commun (33% de mots communs) : `MIFID-R-002-F5`, `MIFID-R-003-F5`
- `RG-MIFID-ARTICLE-54-PROCEDURE` — MISSING_INFORMATION / MISSING_INFORMATION — ancrage commun (8% de mots communs) : `MIFID-R-007-F12`, `MIFID-R-011-F12`
- `RG-MIFID-ARTICLE-54-PROCEDURE` — QUALIFICATION / NONE — ancrage commun (8% de mots communs) : `MIFID-R-007-F2`, `MIFID-R-011-F2`
- `RG-MIFID-ARTICLE-54-PROCEDURE` — TRUE_PREMISE_ADVERSARIAL / NONE — ancrage commun (8% de mots communs) : `MIFID-R-007-F5`, `MIFID-R-011-F5`

## Constats

### Avertissements (13)

#### `meme_ancrage` — 13

- `AMF-R-003-F1` : partage l'ancrage et la famille de « AMF-R-002-F1 » mais porte une autre disposition (12% de mots communs) : questions à écrire sur des faits distincts
- `AMF-R-003-F12` : partage l'ancrage et la famille de « AMF-R-002-F12 » mais porte une autre disposition (12% de mots communs) : questions à écrire sur des faits distincts
- `AMF-R-003-F2` : partage l'ancrage et la famille de « AMF-R-002-F2 » mais porte une autre disposition (12% de mots communs) : questions à écrire sur des faits distincts
- `AMF-R-003-F5` : partage l'ancrage et la famille de « AMF-R-002-F5 » mais porte une autre disposition (12% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-003-F1` : partage l'ancrage et la famille de « MIFID-R-002-F1 » mais porte une autre disposition (33% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-003-F12` : partage l'ancrage et la famille de « MIFID-R-002-F12 » mais porte une autre disposition (33% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-003-F2` : partage l'ancrage et la famille de « MIFID-R-002-F2 » mais porte une autre disposition (33% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-003-F4` : partage l'ancrage et la famille de « MIFID-R-002-F4 » mais porte une autre disposition (33% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-003-F5` : partage l'ancrage et la famille de « MIFID-R-002-F5 » mais porte une autre disposition (33% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-003-F7` : partage l'ancrage et la famille de « MIFID-R-002-F7 » mais porte une autre disposition (33% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-011-F12` : partage l'ancrage et la famille de « MIFID-R-007-F12 » mais porte une autre disposition (8% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-011-F2` : partage l'ancrage et la famille de « MIFID-R-007-F2 » mais porte une autre disposition (8% de mots communs) : questions à écrire sur des faits distincts
- `MIFID-R-011-F5` : partage l'ancrage et la famille de « MIFID-R-007-F5 » mais porte une autre disposition (8% de mots communs) : questions à écrire sur des faits distincts

### Infos (25)

#### `verification_negative` — 25

- `AMF-R-001-F11` : piège « NEGATIVE_ASSERTION » : l'item exigera une vérification d'absence avant rédaction
- `AMF-R-001-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- `AMF-R-005-F4` : piège « FALSE_ARTICLE » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-001-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-003-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-004-F4` : piège « FALSE_ARTICLE » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-005-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-006-F4` : piège « FALSE_ARTICLE » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-007-F11` : piège « NEGATIVE_ASSERTION » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-007-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-008-F11` : piège « NEGATIVE_ASSERTION » : l'item exigera une vérification d'absence avant rédaction
- `DORA-R-008-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- `LCBFT-R-005-F11` : piège « NEGATIVE_ASSERTION » : l'item exigera une vérification d'absence avant rédaction
- `LCBFT-R-005-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- `LCBFT-R-011-F4` : piège « FALSE_THRESHOLD » : l'item exigera une vérification d'absence avant rédaction
- … et 10 autre(s)

## Ce que la carte n'est pas

- Elle ne contient **aucune question rédigée** : la phase 7 s'arrête à ce qui
  est mesurable.
- Elle n'affecte **rien au public ni au privé** : `public_eligible` et
  `private_eligible` restent tous deux vrais, et `holdout_recommendation`
  ne fait que transporter le signal jusqu'à l'arbitrage.
- Elle ne promeut **aucune règle** : une famille `blocked` le reste jusqu'à
  ce que la vérification du Rulebook fasse passer sa règle en `validated`.

