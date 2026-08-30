# Plan de revue humaine — P0 / P1

Le pack d'arbitrage dit quoi trancher, règle par règle. Ce plan dit par où
commencer, et ce que chaque action débloque. Il ne génère aucune famille,
aucune question, et ne modifie aucun statut.

**État relu** — audit publié, empreinte `5976ed137a380fda`. Établi le 2026-08-30.

## Ce qu'il y a à faire

| Action principale | Règles |
|---|---:|
| `EXCEPTION_ADJUDICATION` | 22 |
| `SOURCE_CONSULTATION` | 12 |
| `NEGATIVE_CLAIM_REVIEW` | 6 |
| `SOURCE_REANCHORING` | 3 |
| `TEMPORAL_REVIEW` | 1 |

44 règles — 28 P0, 16 P1.

## Ordre d'exécution

Classé par rendement — règles débloquées par action de revue. **Les priorités
P0/P1 ne sont pas modifiées** : elles disent la gravité d'une erreur, pas
l'ordre du travail. Une consultation qui débloque douze règles passe en tête
parce qu'elle coûte une action pour douze résultats, pas parce qu'elle serait
plus grave qu'un P0 isolé.

| # | Rang | Action | Objet | Nature | Débloque | Achève |
|---:|---|---|---|---|---:|---:|
| 1 | consultation débloquant plusieurs règles | `SOURCE_CONSULTATION` | `LOT-CMF` | lot de lecture | 12 | 0 |
| 2 | cluster de décision commun | `EXCEPTION_ADJUDICATION` | `CL-32014L0065-ART25-EXC` | cluster de décision | 4 | 4 |
| 3 | cluster de décision commun | `EXCEPTION_ADJUDICATION` | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` | cluster de décision | 3 | 3 |
| 4 | correction de source (réancrage, ou consultation isolée) | `SOURCE_REANCHORING` | `AMF-R-005` | décision individuelle | 1 | 0 |
| 5 | correction de source (réancrage, ou consultation isolée) | `SOURCE_REANCHORING` | `LCBFT-R-013` | décision individuelle | 1 | 1 |
| 6 | correction de source (réancrage, ou consultation isolée) | `SOURCE_REANCHORING` | `SFDR-R-014` | décision individuelle | 1 | 1 |
| 7 | décision individuelle P0 | `NEGATIVE_CLAIM_REVIEW` | `AMF-R-001` | décision individuelle | 1 | 0 |
| 8 | décision individuelle P0 | `EXCEPTION_ADJUDICATION` | `DORA-R-002` | décision individuelle | 1 | 1 |
| 9 | décision individuelle P0 | `EXCEPTION_ADJUDICATION` | `DORA-R-003` | décision individuelle | 1 | 0 |
| 10 | décision individuelle P0 | `NEGATIVE_CLAIM_REVIEW` | `DORA-R-007` | décision individuelle | 1 | 0 |
| 11 | décision individuelle P0 | `NEGATIVE_CLAIM_REVIEW` | `DORA-R-008` | décision individuelle | 1 | 0 |
| 12 | décision individuelle P0 | `EXCEPTION_ADJUDICATION` | `DORA-R-010` | décision individuelle | 1 | 1 |
| 13 | décision individuelle P0 | `TEMPORAL_REVIEW` | `MIFID-R-006` | décision individuelle | 1 | 1 |
| 14 | décision individuelle P0 | `NEGATIVE_CLAIM_REVIEW` | `MIFID-R-007` | décision individuelle | 1 | 1 |
| 15 | décision individuelle P0 | `EXCEPTION_ADJUDICATION` | `SFDR-R-001` | décision individuelle | 1 | 1 |
| 16 | décision individuelle P0 | `NEGATIVE_CLAIM_REVIEW` | `SFDR-R-003` | décision individuelle | 1 | 0 |
| 17 | décision individuelle P0 | `EXCEPTION_ADJUDICATION` | `SFDR-R-005` | décision individuelle | 1 | 1 |
| 18 | décision individuelle P0 | `NEGATIVE_CLAIM_REVIEW` | `SFDR-R-008` | décision individuelle | 1 | 0 |
| 19 | décision individuelle P0 | `EXCEPTION_ADJUDICATION` | `TAXO-R-001` | décision individuelle | 1 | 1 |
| 20 | décision individuelle P0 | `EXCEPTION_ADJUDICATION` | `TAXO-R-003` | décision individuelle | 1 | 1 |
| 21 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `DORA-R-004` | décision individuelle | 1 | 1 |
| 22 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `DORA-R-006` | décision individuelle | 1 | 1 |
| 23 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `DORA-R-012` | décision individuelle | 1 | 1 |
| 24 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `DORA-R-013` | décision individuelle | 1 | 0 |
| 25 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `SFDR-R-002` | décision individuelle | 1 | 1 |
| 26 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `SFDR-R-006` | décision individuelle | 1 | 0 |
| 27 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `SFDR-R-011` | décision individuelle | 1 | 1 |
| 28 | décision individuelle P1 | `EXCEPTION_ADJUDICATION` | `TAXO-R-002` | décision individuelle | 1 | 1 |

« Débloque » compte les règles dont l'action lève le blocage principal.
« Achève » compte celles qui, ensuite, ne porteraient plus aucun blocage de
fond — les autres retomberont dans la file avec le blocage suivant.

## Regroupements

Deux axes qu'il ne faut pas confondre. Un **cluster de décision** partage une
question : une seule décision couvre toutes ses règles. Un **lot de lecture**
partage un empêchement : une seule consultation sert tous ses dossiers, mais
chaque règle garde sa décision. Dans les deux cas, les règles restent
distinctes dans le Rulebook — un article porte couramment plusieurs
obligations, et les confondre en effacerait une.

| cluster_id | Nature | source | article(s) | rules | débloquées | achevées |
|---|---|---|---|---|---:|---:|
| `LOT-CMF` | lot de lecture | Code monétaire et financier | Article L.561-10, Article L.561-12, Article L.561-15, Article L.561-18, Article L.561-2, Article L.561-4-1 | `LCBFT-R-001`, `LCBFT-R-002`, `LCBFT-R-003`, `LCBFT-R-005`, `LCBFT-R-006`, `LCBFT-R-007`, `LCBFT-R-008`, `LCBFT-R-009`, `LCBFT-R-010`, `LCBFT-R-012`, `LCBFT-R-004`, `LCBFT-R-011` | 12 | 0 |
| `CL-32014L0065-ART25-EXC` | cluster de décision | Directive 2014/65/UE (MIFID II) | Article 25 | `MIFID-R-002`, `MIFID-R-003`, `MIFID-R-004`, `MIFID-R-005` | 4 | 4 |
| `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` | cluster de décision | Position-recommandation AMF DOC-2020-03 | Position-recommandation DOC-2020-03 | `AMF-R-004`, `AMF-R-002`, `AMF-R-003` | 3 | 3 |

### Question unique de chaque regroupement

**`LOT-CMF`** (12 règles)

> Le texte de Code monétaire et financier confirme-t-il les énoncés des règles du lot, article par article ? Une consultation sert tout le lot ; chaque règle garde sa décision.

**`CL-32014L0065-ART25-EXC`** (4 règles)

> Une dérogation, exclusion, exemption ou condition applicable à MIFID-R-002 existe-t-elle dans le périmètre indiqué — Article 25, un autre article de Directive 2014/65/UE (MIFID II), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**`CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC`** (3 règles)

> Une dérogation, exclusion, exemption ou condition applicable à AMF-R-004 existe-t-elle dans le périmètre indiqué — Position-recommandation DOC-2020-03, un autre article de Position-recommandation AMF DOC-2020-03, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

## Queue P0 / P1

Une entrée par règle. Le détail juridique de chaque dossier — dispositions à
examiner, faits textuels, périmètre — vit dans `HUMAN_REVIEW_P0_P1.md` ; on ne
le recopie pas ici.

### P0 — 28 règles

#### AMF

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `AMF-R-001` | `NEGATIVE_CLAIM_REVIEW` | `NEGATIVE_CLAIM_UNRESOLVED` | `TEXTE_RECUPERE` | Position-recommandation DOC-2020-03 | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-NEG` | statut inchangé (`source_checked`) : 1 blocage(s) de fond resteraient après cette décision |
| `AMF-R-004` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Position-recommandation DOC-2020-03 | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |

#### DORA

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `DORA-R-002` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 5 | `CL-32022R2554-ART5-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `DORA-R-003` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 6 | `CL-32022R2554-ART6-EXC` | statut inchangé (`source_checked`) : 1 blocage(s) de fond resteraient après cette décision |
| `DORA-R-007` | `NEGATIVE_CLAIM_REVIEW` | `NEGATIVE_CLAIM_UNRESOLVED` | `TEXTE_RECUPERE` | Article 18 | `CL-32022R2554-ART18-NEG` | statut inchangé (`source_checked`) : 2 blocage(s) de fond resteraient après cette décision |
| `DORA-R-008` | `NEGATIVE_CLAIM_REVIEW` | `NEGATIVE_CLAIM_UNRESOLVED` | `TEXTE_RECUPERE` | Article 19 | `CL-32022R2554-ART19-NEG` | statut inchangé (`source_checked`) : 1 blocage(s) de fond resteraient après cette décision |
| `DORA-R-010` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 28 | `CL-32022R2554-ART28-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |

#### LCBFT

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `LCBFT-R-001` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-2 | `CL-CMF-ARTL-561-2-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-002` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-4-1 | `CL-CMF-ARTL-561-4-1-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-003` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-5 | `CL-CMF-ARTL-561-5-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-005` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Articles L.561-2-2 et R.561-1 et suivants | `CL-CMF-ARTL-561-2-2-ET-R-561-1-ET-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-006` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-6 | `CL-CMF-ARTL-561-6-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-007` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-10 | `CL-CMF-ARTL-561-10-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-008` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Articles L.561-10 et R.561-18 | `CL-CMF-ARTL-561-10-ET-R-561-18-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-009` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-15 | `CL-CMF-ARTL-561-15-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-010` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-18 | `CL-CMF-ARTL-561-18-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-012` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-8 | `CL-CMF-ARTL-561-8-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |

#### MIFID

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `MIFID-R-002` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 25 | `CL-32014L0065-ART25-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `MIFID-R-003` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 25 | `CL-32014L0065-ART25-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `MIFID-R-004` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 25 | `CL-32014L0065-ART25-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `MIFID-R-006` | `TEMPORAL_REVIEW` | `TEMPORAL_UNRESOLVED` | `TEXTE_RECUPERE` | Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié | `CL-32021R1253-ART2-ET-ARTICLE-54-DU-REGLE-TMP` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `MIFID-R-007` | `NEGATIVE_CLAIM_REVIEW` | `NEGATIVE_CLAIM_UNRESOLVED` | `TEXTE_RECUPERE` | Article 54 | `CL-RD25M-ART54-NEG` | `validated` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |

#### SFDR

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `SFDR-R-001` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 2 | `CL-32019R2088-ART2-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `SFDR-R-003` | `NEGATIVE_CLAIM_REVIEW` | `NEGATIVE_CLAIM_UNRESOLVED` | `TEXTE_RECUPERE` | Article 4 | `CL-32019R2088-ART4-NEG` | statut inchangé (`source_checked`) : 1 blocage(s) de fond resteraient après cette décision |
| `SFDR-R-005` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 6 | `CL-32019R2088-ART6-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `SFDR-R-008` | `NEGATIVE_CLAIM_REVIEW` | `NEGATIVE_CLAIM_UNRESOLVED` | `TEXTE_RECUPERE` | Article 8 | `CL-32019R2088-ART8-NEG` | statut inchangé (`source_checked`) : 1 blocage(s) de fond resteraient après cette décision |
| `TAXO-R-001` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 3 | `CL-32020R0852-ART3-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `TAXO-R-003` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Articles 17 et 18 | `CL-32020R0852-ART17-ET-18-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |

### P1 — 16 règles

#### AMF

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `AMF-R-002` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Position-recommandation DOC-2020-03 | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `AMF-R-003` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Position-recommandation DOC-2020-03 | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `AMF-R-005` | `SOURCE_REANCHORING` | `SOURCE_INCOMPLETE` | `DOCUMENT_INTROUVABLE` | Règlement général | `CL-RGA-ARTREGLEMENT-GENERAL-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |

#### DORA

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `DORA-R-004` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Articles 8 à 13 | `CL-32022R2554-ART8-A-13-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `DORA-R-006` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 17 | `CL-32022R2554-ART17-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `DORA-R-012` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 31 | `CL-32022R2554-ART31-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `DORA-R-013` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 64 | `CL-32022R2554-ART64-EXC` | statut inchangé (`source_checked`) : 1 blocage(s) de fond resteraient après cette décision |

#### LCBFT

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `LCBFT-R-004` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-5-1 | `CL-CMF-ARTL-561-5-1-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-011` | `SOURCE_CONSULTATION` | `SOURCE_INCOMPLETE` | `REFUS_DE_LA_SOURCE` | Article L.561-12 | `CL-CMF-ARTL-561-12-SRC` | `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici |
| `LCBFT-R-013` | `SOURCE_REANCHORING` | `SOURCE_INCOMPLETE` | `TEXTE_RECUPERE` | Ensemble de la directive | `CL-32015L0849-ARTENSEMBLE-DE-LA-DIRECTIVE-SRC` | statut inchangé (`source_checked`) tant que l'ancrage ne désigne pas une disposition ; une fois l'article cité, l'audit rejoué dira ce qui reste — il ne se devine pas ici |

#### MIFID

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `MIFID-R-005` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 25 | `CL-32014L0065-ART25-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |

#### SFDR

| rule_id | action | blocker | accès | article | cluster | statut projeté |
|---|---|---|---|---|---|---|
| `SFDR-R-002` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 3 | `CL-32019R2088-ART3-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `SFDR-R-006` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 7 | `CL-32019R2088-ART7-EXC` | statut inchangé (`source_checked`) : 1 blocage(s) de fond resteraient après cette décision |
| `SFDR-R-011` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 11 | `CL-32019R2088-ART11-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |
| `SFDR-R-014` | `SOURCE_REANCHORING` | `SOURCE_INCOMPLETE` | `TEXTE_RECUPERE` | Ensemble du règlement délégué | `CL-32022R1288-ARTENSEMBLE-DU-REGLEMENT-DE-SRC` | statut inchangé (`source_checked`) tant que l'ancrage ne désigne pas une disposition ; une fois l'article cité, l'audit rejoué dira ce qui reste — il ne se devine pas ici |
| `TAXO-R-002` | `EXCEPTION_ADJUDICATION` | `EXCEPTION_UNRESOLVED` | `TEXTE_RECUPERE` | Article 9 | `CL-32020R0852-ART9-EXC` | `source_checked` → `validated` possible si la décision est signée ; `gold_ready` est alors recalculé, il n'est pas accordé par la décision |

## Simulation — PROJECTED_ONLY

**PROJECTED_ONLY.** Rien de ce qui suit n'est un statut. Les seuils se
recalculent en rejouant l'audit sur un Rulebook corrigé ; ils ne se déduisent
pas d'un plan, et aucune décision n'a été rendue à ce jour.

| Seuil | État réel |
|---|---:|
| `validated` | 12 |
| `gold_ready` | 9 |
| `family_ready` | 9 |

Si **tous** les arbitrages P0/P1 étaient rendus et signés, 23 règle(s) ne porteraient plus de blocage de fond, dont 21 dont l'énoncé porte déjà assez pour qu'un gold s'y adosse — PROJECTED_ONLY.

| Si ce regroupement est résolu | Règles concernées | Sans blocage de fond ensuite |
|---|---:|---:|
| `LOT-CMF` | 12 | 0 |
| `CL-32014L0065-ART25-EXC` | 4 | 4 |
| `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` | 3 | 3 |

Lecture (PROJECTED_ONLY) : « résolu » veut dire *décision rendue et*
*signée*. Une règle « sans blocage de fond ensuite » devient **éligible** à
`validated` ; elle ne le devient pas d'office, et `gold_ready` reste un calcul
à refaire, jamais un acquis de la décision.

## BLOCKING ITEMS

Ce qui empêche encore `READY_FOR_FAMILY_GENERATION` :

1. 44 arbitrage(s) en attente (28 P0, 16 P1) : générer maintenant figerait des familles sur des règles dont la portée reste à trancher
2. 13 règle(s) dont le texte primaire n'a pas été lu (Code monétaire et financier, Règlement général de l'AMF) : aucune réponse de référence ne pourrait leur être opposée

## NEXT ACTION

> SOURCE_CONSULTATION sur LOT-CMF (lot de lecture) — 12 règle(s) débloquée(s) : LCBFT-R-001, LCBFT-R-002, LCBFT-R-003, LCBFT-R-005, LCBFT-R-006, LCBFT-R-007, LCBFT-R-008, LCBFT-R-009, LCBFT-R-010, LCBFT-R-012, LCBFT-R-004, LCBFT-R-011

