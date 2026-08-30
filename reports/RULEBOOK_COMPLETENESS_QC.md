# Rulebook — audit de complétude et de gold-readiness

Rapport généré par `src/bench/rapport_completude.py`. L'audit de sources
établissait qu'une règle cite le bon texte ; celui-ci examine ce que ce texte
contient **autour** d'elle — dérogations, conditions, renvois, temporalité —
et si ce qu'elle en dit suffit à écrire une réponse de référence.

## Deux choses à ne pas confondre

`validated` dit que la règle est juridiquement établie. `gold_ready` dit
qu'elle est assez précise pour qu'on en tire une réponse de référence **sans
nouvelle interprétation juridique**. Les deux sont indépendants : « le
règlement précise les modalités de l'évaluation » peut être parfaitement exact
et ne rien permettre de rédiger.

Ne compter que les `validated` donnerait un faux sentiment de complétude. La
seule population utile à la génération de familles est **`validated` ET
`gold_ready`**.

## Synthèse

- règles examinées : **58**
- `validated` : **12**
- `source_checked` : **33**
- `requires_human_review` : **0**
- `draft` : **13**

- `gold_ready` : **41**
- non `gold_ready` : **17**
- **utilisables pour la génération de familles** (`validated` et `gold_ready`) : **10**

### Recherche d'exceptions

- `none_identified` : **0**
- `identified_and_incorporated` : **15**
- `identified_but_not_incorporated` : **0**
- `not_applicable` : **0**
- `requires_human_review` : **28**
- `unknown` : **15**

> **`none_identified` n'est jamais attribué par cette passe.** Ne pas trouver
> de dérogation dans l'article cité ne prouve pas qu'aucun autre article n'y
> déroge, ni qu'aucun acte ultérieur ne l'a fait. Ce cas ressort en
> `requires_human_review` : c'est un juriste qui peut conclure à l'absence,
> pas une recherche de motifs.

## Structures juridiques trouvées dans les textes cités

| Structure | Règles concernées |
|---|---:|
| derogation | 11 |
| exclusion | 2 |
| exemption | 5 |
| conditions_cumulatives | 29 |
| conditions_alternatives | 2 |
| seuil | 4 |
| delai | 20 |
| regime_particulier | 17 |
| disposition_transitoire | 0 |
| renvoi | 7 |
| definition_necessaire | 7 |

## Critères de validation non remplis

Les huit critères de la spécification §4. Un seul manquant suffit à refuser
la validation.

| Critère | Règles bloquées |
|---|---:|
| `exceptions_recherchees` | 28 |
| `temporalite_etablie` | 7 |
| `conditions_capturees` | 7 |

## Règles utilisables pour la génération de familles

| ID | Domaine | Priorité | Exceptions |
|---|---|---|---|
| `DORA-R-001` | DORA | CRITICAL | identified_and_incorporated |
| `DORA-R-005` | DORA | HIGH | identified_and_incorporated |
| `DORA-R-009` | DORA | HIGH | identified_and_incorporated |
| `DORA-R-011` | DORA | CRITICAL | identified_and_incorporated |
| `MIFID-R-007` | MIFID | CRITICAL | identified_and_incorporated |
| `MIFID-R-008` | MIFID | HIGH | identified_and_incorporated |
| `MIFID-R-009` | MIFID | HIGH | identified_and_incorporated |
| `MIFID-R-011` | MIFID | HIGH | identified_and_incorporated |
| `SFDR-R-009` | SFDR | CRITICAL | identified_and_incorporated |
| `SFDR-R-013` | SFDR | HIGH | identified_and_incorporated |

## Règles modifiées (15)

Exceptions recopiées depuis le texte officiel — recopiées, jamais
reformulées : une exception reformulée est une exception interprétée.
Chaque incorporation **reversionne** la règle, sans écraser l'ancienne.

| ID | Dispositions incorporées |
|---|---:|
| `DORA-R-001` | 2 |
| `DORA-R-005` | 2 |
| `DORA-R-008` | 2 |
| `DORA-R-009` | 3 |
| `DORA-R-011` | 1 |
| `MIFID-R-001` | 2 |
| `MIFID-R-006` | 3 |
| `MIFID-R-007` | 3 |
| `MIFID-R-008` | 5 |
| `MIFID-R-009` | 1 |
| `MIFID-R-010` | 3 |
| `MIFID-R-011` | 3 |
| `SFDR-R-003` | 2 |
| `SFDR-R-009` | 1 |
| `SFDR-R-013` | 1 |

## Règles nécessitant un arbitrage humain (28)

| ID | Priorité | Pourquoi |
|---|---|---|
| `AMF-R-001` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; ren |
| `AMF-R-002` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; ren |
| `AMF-R-003` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; ren |
| `AMF-R-004` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; ren |
| `DORA-R-002` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `DORA-R-003` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; tem |
| `DORA-R-004` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `DORA-R-006` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `DORA-R-007` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; tem |
| `DORA-R-010` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `DORA-R-012` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `DORA-R-013` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; tem |
| `MIFID-R-002` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `MIFID-R-003` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `MIFID-R-004` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `MIFID-R-005` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-001` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-002` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-004` | MEDIUM | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-005` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-006` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; tem |
| `SFDR-R-008` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-010` | MEDIUM | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-011` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `SFDR-R-012` | MEDIUM | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `TAXO-R-001` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `TAXO-R-002` | HIGH | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |
| `TAXO-R-003` | CRITICAL | aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste |

## Règles non `gold_ready` (17)

Elles peuvent être juridiquement exactes : ce qui leur manque est la
précision, pas la véracité.

| ID | Priorité | Pourquoi |
|---|---|---|
| `AMF-R-005` | HIGH |  |
| `LCBFT-R-001` | CRITICAL |  |
| `LCBFT-R-002` | CRITICAL |  |
| `LCBFT-R-003` | CRITICAL |  |
| `LCBFT-R-004` | HIGH |  |
| `LCBFT-R-005` | CRITICAL |  |
| `LCBFT-R-006` | CRITICAL |  |
| `LCBFT-R-007` | CRITICAL |  |
| `LCBFT-R-008` | CRITICAL |  |
| `LCBFT-R-009` | CRITICAL |  |
| `LCBFT-R-010` | CRITICAL |  |
| `LCBFT-R-011` | HIGH |  |
| `LCBFT-R-012` | CRITICAL |  |
| `LCBFT-R-013` | HIGH |  |
| `MIFID-R-001` | HIGH | l'énoncé décrit le texte au lieu de le dire (notamment) : une réponse de référence devrait réinterpréter le droit pour être écrite |
| `MIFID-R-010` | MEDIUM | l'énoncé décrit le texte au lieu de le dire (notamment) : une réponse de référence devrait réinterpréter le droit pour être écrite |
| `SFDR-R-014` | HIGH |  |

## Règles CRITICAL non validées (27)

Contrôle renforcé de la spécification §9 : une règle critique n'est validée
que si ses exceptions **et** ses renvois sont établis.

- `AMF-R-001` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; renvois vérifiés dans l
- `AMF-R-004` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; renvois vérifiés dans l
- `DORA-R-002` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `DORA-R-003` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; temporalité non établie
- `DORA-R-007` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste ; temporalité non établie
- `DORA-R-008` : 2 disposition(s) limitante(s) recopiée(s) du texte officiel (derogation) ; temporalité non établie (statut « IN_FORCE »)
- `DORA-R-010` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `LCBFT-R-001` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-002` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-003` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-005` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-006` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-007` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-008` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-009` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-010` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `LCBFT-R-012` : texte de l'article non disponible : la structure juridique n'a pas pu être examinée, et une absence d'exception ne se suppose pas
- `MIFID-R-002` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `MIFID-R-003` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `MIFID-R-004` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `MIFID-R-006` : 3 disposition(s) limitante(s) recopiée(s) du texte officiel (exemption) ; renvois vérifiés dans l'acte : articles 3, 25 ; temporalité non établie (statut « IN_FORCE »)
- `SFDR-R-001` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `SFDR-R-003` : 2 disposition(s) limitante(s) recopiée(s) du texte officiel (derogation) ; temporalité non établie (statut « IN_FORCE »)
- `SFDR-R-005` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `SFDR-R-008` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `TAXO-R-001` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste
- `TAXO-R-003` : aucune structure limitante dans l'article cité — ce qui ne prouve pas qu'aucun autre article n'y déroge : « none_identified » demande un juriste

## Ce que cette passe n'a pas fait

- elle n'a promu aucune règle d'elle-même : le dossier
  `data/verification/dossier-completude.csv` est pré-rempli **sans**
  `verifie_par` ni `date_verification`, et le schéma refuse toute promotion
  sans elles ;
- elle n'a écrasé aucun énoncé : toute incorporation reversionne ;
- elle n'a conclu à aucune absence d'exception.

