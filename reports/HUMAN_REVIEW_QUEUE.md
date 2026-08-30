# Rulebook — file de revue humaine (P0 / P1)

Chaque dossier dit **quelle disposition examiner**, **quelle exception est
suspectée**, **quelle formulation est concernée** et **quelle décision est
attendue**. Le relecteur n'a rien à deviner.

**Ce document ne donne aucun conseil juridique.** Il sépare strictement ce
qui est écrit dans le texte (`TEXTUAL_FACTS`) de ce qui demande un arbitrage
(`INTERPRETIVE_QUESTION`). La `mechanical_proposal` dit ce que la recherche
automatique a trouvé, dans son propre vocabulaire — `EXCEPTION_LIKELY`
signifie « une disposition limitante cite cet article », pas « il existe une
exception ».

## Ce qui est demandé

- dossiers P0 : **28**
- dossiers P1 : **16**
- arbitrages distincts après regroupement : **22**
- groupes couvrant plusieurs règles : **6**

Une décision d'absence d'exception (`NONE_IDENTIFIED`) n'est acceptée que si
le champ `source_scope` atteste le périmètre réellement examiné. Le schéma
la refuse sinon : « je n'ai pas trouvé » n'est pas « cela n'existe pas ».

## Arbitrages mutualisés

Ces règles dépendent de la même disposition : une seule décision les
couvre toutes. Les règles ne sont pas fusionnées pour autant — seul le
dossier l'est.

| Cluster | Règles | Nombre |
|---|---|---:|
| `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE` | `LCBFT-R-001`, `LCBFT-R-002`, `LCBFT-R-003`, `LCBFT-R-004`, `LCBFT-R-005`, `LCBFT-R-006`, `LCBFT-R-007`, `LCBFT-R-008`, `LCBFT-R-009`, `LCBFT-R-010`, `LCBFT-R-011`, `LCBFT-R-012` | 12 |
| `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A16-A2-A20-A26-A46` | `DORA-R-002`, `DORA-R-004`, `DORA-R-006`, `DORA-R-010`, `DORA-R-013` | 5 |
| `CL-EXC-DIRECTIVE-2014-65-UE-MIFID-I-A1-A19-A20-A24-A3-A30` | `MIFID-R-002`, `MIFID-R-003`, `MIFID-R-004`, `MIFID-R-005` | 4 |
| `CL-EXC-POSITION-RECOMMANDATION-AMF-AUCUNE` | `AMF-R-002`, `AMF-R-003`, `AMF-R-004` | 3 |
| `CL-EXC-R-GLEMENT-UE-2019-2088-SFDR-A13` | `SFDR-R-001`, `SFDR-R-006` | 2 |
| `CL-EXC-R-GLEMENT-UE-2020-852-TAXONO-AUCUNE` | `TAXO-R-001`, `TAXO-R-003` | 2 |

## P0 — REVIEW REQUIRED (28 règles)

### Domaine AMF

### `AMF-R-001` — AMF · P0 · cluster `CL-NEG-POSITION-RECOMMANDATION-AMF-AUCUNE`

**RULE**

- ID : `AMF-R-001`
- Domain : AMF
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> La position-recommandation AMF DOC-2020-03 subordonne la possibilité pour un placement collectif de communiquer de manière centrale sur la prise en compte de critères extra-financiers au caractère significativement engageant de l'approche mise en œuvre.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Position-recommandation AMF DOC-2020-03 », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Position-recommandation DOC-2020-03 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : seuil, renvoi.
- L'article renvoie aux articles 19.
- La règle porte une affirmation négative, à l'état « unverified » : « Le règlement SFDR imposerait lui-même les conditions de communication commerciale applicables en France. ».

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si « Le règlement SFDR imposerait lui-même les conditions de communication commerciale applicab » est réellement absent de Position-recommandation AMF DOC-2020-03, en indiquant le périmètre consulté — un extrait ne suffit pas à établir une absence.

**NEUTRAL_LEGAL_QUESTION**

> « Le règlement SFDR imposerait lui-même les conditions de communication commerciale applicables en France. » est-il absent de l'intégralité de Position-recommandation AMF DOC-2020-03 dans la version consultée, ou une disposition de cet acte le prévoit-elle ?

**mechanical_proposal** : `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'affirmation négative tombe : aucune fausse prémisse ne pourra être construite sur cette absence, et la règle devra dire ce que le texte prévoit réellement
- `if_no_exception` : l'absence devient opposable et pourra fonder une fausse prémisse, avec le périmètre de recherche cité en source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Position-recommandation AMF DOC-2020-03, version du 2020-01-01 ; article cité : Position-recommandation DOC-2020-03 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `AMF-R-004` — AMF · P0 · cluster `CL-EXC-POSITION-RECOMMANDATION-AMF-AUCUNE`

**RULE**

- ID : `AMF-R-004`
- Domain : AMF
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> La doctrine AMF relative aux informations extra-financières des placements collectifs s'applique en complément du règlement (UE) 2019/2088, qui régit l'information réglementaire, la doctrine portant sur la communication.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Position-recommandation AMF DOC-2020-03 », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Position-recommandation DOC-2020-03 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : seuil, renvoi.
- L'article renvoie aux articles 19.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Position-recommandation DOC-2020-03 de Position-recommandation AMF DOC-2020-03 comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> L'acte Position-recommandation AMF DOC-2020-03 comporte-t-il, en dehors de « Position-recommandation DOC-2020-03 », une disposition qui déroge à cette obligation, ou aucune disposition de cet acte n'en limite-t-elle la portée ?

**mechanical_proposal** : `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Position-recommandation AMF DOC-2020-03, version du 2020-01-01 ; article cité : Position-recommandation DOC-2020-03 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine DORA

### `DORA-R-002` — DORA · P0 · cluster `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A16-A2-A20-A26-A46`

**RULE**

- ID : `DORA-R-002`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 5 du règlement (UE) 2022/2554 dispose que l'organe de direction de l'entité financière définit, approuve, supervise et est responsable de la mise en œuvre du cadre de gestion du risque lié aux TIC.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 5
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 5
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 5
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice des paragraphes 3 et 4, le présent règlement s’applique aux entités suivantes: a) les établissements de crédit; »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Lorsqu’elles élaborent ces projets de normes techniques de réglementation, les AES tiennent compte de la taille et du profil de risque global de l’entité financière, ainsi que de la nature, de l’ampleur et de la complexité de ses services, activités et opérations, et en particulier en vue de garantir que, aux fins du point a) ii), du présent alinéa, différents délais puissent refléter, le cas échéant, les spécificité »
- **Article 26**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice du paragraphe 2, premier et deuxième alinéas, lorsque l’on peut raisonnablement s’attendre à ce que la participation d’un prestataire tiers de services TIC au test de pénétration fondé sur la menace, visée au paragraphe 3, ait une incidence négative sur la qualité ou sur la sécurité des services que le prestataire tiers de services TIC fournit à des clients qui sont des entités ne relevant pas du champ »
- **Article 46**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Article 46 Autorités compétentes Sans préjudice des dispositions relatives au cadre de supervision des prestataires tiers critiques de services TIC visés au chapitre V, section II, du présent règlement, le respect du présent règlement est assuré par les autorités compétentes suivantes, conformément aux pouvoirs conférés par les actes juridiques correspondants: a) pour les établissements de crédit et pour les établiss »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 5 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, regime_particulier.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 5.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition cite explicitement l'article 5.
- Article 2 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 26 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 46 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 5 de Règlement (UE) 2022/2554 (DORA) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 16, Article 2 constitue(nt)-t-il(s) une exception applicable à « Article 5 » de Règlement (UE) 2022/2554 (DORA), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle DORA-R-002 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 5 ; dispositions à examiner : Article 1, Article 16, Article 2, Article 20, Article 26, Article 46

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `DORA-R-003` — DORA · P0 · cluster `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A16-A19-A26-A3-A46`

**RULE**

- ID : `DORA-R-003`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 6 impose de disposer d'un cadre de gestion du risque lié aux TIC solide, complet et bien documenté, faisant partie du dispositif global de gestion des risques, et de le réexaminer au moins une fois par an.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 6
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 6
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 6
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 19**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 6
  - Extrait : « Sans préjudice de la déclaration par l’entité financière à l’autorité compétente concernée en vertu du premier alinéa, les États membres peuvent en outre décider que certaines entités financières ou toutes les entités financières fournissent également la notification initiale et chacun des rapports visés au paragraphe 4 du présent article, en utilisant les modèles visés à l’article 20, aux autorités compétentes ou au »
- **Article 26**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 6
  - Extrait : « Sans préjudice du paragraphe 2, premier et deuxième alinéas, lorsque l’on peut raisonnablement s’attendre à ce que la participation d’un prestataire tiers de services TIC au test de pénétration fondé sur la menace, visée au paragraphe 3, ait une incidence négative sur la qualité ou sur la sécurité des services que le prestataire tiers de services TIC fournit à des clients qui sont des entités ne relevant pas du champ »
- **Article 3**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?
  - Relation avec la règle : cette disposition cite explicitement l'article 6
  - Extrait : « 32) établissement exempté en vertu de la directive 2013/36/UE : une entité visée à l’article 2, paragraphe 5, points 4) à 23), de la directive 2013/36/UE; »
- **Article 46**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 6
  - Extrait : « Article 46 Autorités compétentes Sans préjudice des dispositions relatives au cadre de supervision des prestataires tiers critiques de services TIC visés au chapitre V, section II, du présent règlement, le respect du présent règlement est assuré par les autorités compétentes suivantes, conformément aux pouvoirs conférés par les actes juridiques correspondants: a) pour les établissements de crédit et pour les établiss »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 6 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, regime_particulier.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 6.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition cite explicitement l'article 6.
- Article 19 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 6.
- Article 26 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 6.
- Article 3 — porte une formule limitante : exemptée?s? ; cette disposition cite explicitement l'article 6.
- Article 46 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition cite explicitement l'article 6.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 6 de Règlement (UE) 2022/2554 (DORA) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 16, Article 19 constitue(nt)-t-il(s) une exception applicable à « Article 6 » de Règlement (UE) 2022/2554 (DORA), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle DORA-R-003 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 6 ; dispositions à examiner : Article 1, Article 16, Article 19, Article 26, Article 3, Article 46

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `DORA-R-007` — DORA · P0 · cluster `CL-NEG-R-GLEMENT-UE-2022-2554-DORA-A1-A20-A16-A2-A26-A46`

**RULE**

- ID : `DORA-R-007`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 18 impose de classer les incidents liés aux TIC et de déterminer leur incidence selon des critères tels que le nombre de clients affectés, la durée, la répartition géographique, les pertes de données et la criticité des services touchés, les seuils étant précisés par des normes techniques.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 18
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 18
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 18
  - Extrait : « Lorsqu’elles élaborent ces projets de normes techniques de réglementation, les AES tiennent compte de la taille et du profil de risque global de l’entité financière, ainsi que de la nature, de l’ampleur et de la complexité de ses services, activités et opérations, et en particulier en vue de garantir que, aux fins du point a) ii), du présent alinéa, différents délais puissent refléter, le cas échéant, les spécificité »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice des paragraphes 3 et 4, le présent règlement s’applique aux entités suivantes: a) les établissements de crédit; »
- **Article 26**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice du paragraphe 2, premier et deuxième alinéas, lorsque l’on peut raisonnablement s’attendre à ce que la participation d’un prestataire tiers de services TIC au test de pénétration fondé sur la menace, visée au paragraphe 3, ait une incidence négative sur la qualité ou sur la sécurité des services que le prestataire tiers de services TIC fournit à des clients qui sont des entités ne relevant pas du champ »
- **Article 46**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Article 46 Autorités compétentes Sans préjudice des dispositions relatives au cadre de supervision des prestataires tiers critiques de services TIC visés au chapitre V, section II, du présent règlement, le respect du présent règlement est assuré par les autorités compétentes suivantes, conformément aux pouvoirs conférés par les actes juridiques correspondants: a) pour les établissements de crédit et pour les établiss »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 18 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai, regime_particulier.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 18.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 18.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 2 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 26 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 46 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- La règle porte une affirmation négative, à l'état « unverified » : « L'article 18 fixerait lui-même un nombre de clients affectés au-delà duquel l'incident est majeur. ».

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si « L'article 18 fixerait lui-même un nombre de clients affectés au-delà duquel l'incident est » est réellement absent de Règlement (UE) 2022/2554 (DORA), en indiquant le périmètre consulté — un extrait ne suffit pas à établir une absence.

**NEUTRAL_LEGAL_QUESTION**

> « L'article 18 fixerait lui-même un nombre de clients affectés au-delà duquel l'incident est majeur. » est-il absent de l'intégralité de Règlement (UE) 2022/2554 (DORA) dans la version consultée, ou une disposition de cet acte le prévoit-elle ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'affirmation négative tombe : aucune fausse prémisse ne pourra être construite sur cette absence, et la règle devra dire ce que le texte prévoit réellement
- `if_no_exception` : l'absence devient opposable et pourra fonder une fausse prémisse, avec le périmètre de recherche cité en source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 18 ; dispositions à examiner : Article 1, Article 20, Article 16, Article 2, Article 26, Article 46

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `DORA-R-008` — DORA · P0 · cluster `CL-NEG-R-GLEMENT-UE-2022-2554-DORA-A1-A20-A22-A19-A16-A2`

**RULE**

- ID : `DORA-R-008`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 19 impose de notifier les incidents majeurs liés aux TIC à l'autorité compétente, selon un processus comportant une notification initiale, un rapport intermédiaire et un rapport final, dont les délais sont précisés par des normes techniques.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 19
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 19
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 19
  - Extrait : « Lorsqu’elles élaborent ces projets de normes techniques de réglementation, les AES tiennent compte de la taille et du profil de risque global de l’entité financière, ainsi que de la nature, de l’ampleur et de la complexité de ses services, activités et opérations, et en particulier en vue de garantir que, aux fins du point a) ii), du présent alinéa, différents délais puissent refléter, le cas échéant, les spécificité »
- **Article 22**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 19
  - Extrait : « Sans préjudice des contributions, avis ou mesures correctives techniques et du suivi correspondant pouvant être fournis, le cas échéant, conformément au droit national, par les CSIRT relevant de la directive (UE) 2022/2555, dès qu’elle reçoit la notification initiale et chaque rapport visé à l’article 19, paragraphe 4, l’autorité compétente en accuse réception et peut, dans la mesure du possible, fournir en temps vou »
- **Article 19**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : disposition interne à l'article cité par la règle
  - Extrait : « Sans préjudice de la déclaration par l’entité financière à l’autorité compétente concernée en vertu du premier alinéa, les États membres peuvent en outre décider que certaines entités financières ou toutes les entités financières fournissent également la notification initiale et chacun des rapports visés au paragraphe 4 du présent article, en utilisant les modèles visés à l’article 20, aux autorités compétentes ou au »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice des paragraphes 3 et 4, le présent règlement s’applique aux entités suivantes: a) les établissements de crédit; »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 19 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : derogation, conditions_cumulatives, conditions_alternatives, definition_necessaire.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 19.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 19.
- Article 22 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 19.
- Article 19 — porte une formule limitante : sans préjudice ; disposition interne à l'article cité par la règle.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 2 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- La règle porte une affirmation négative, à l'état « unverified » : « Le règlement DORA de niveau 1 fixerait un délai de notification initiale en heures. ».

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si « Le règlement DORA de niveau 1 fixerait un délai de notification initiale en heures. » est réellement absent de Règlement (UE) 2022/2554 (DORA), en indiquant le périmètre consulté — un extrait ne suffit pas à établir une absence.

**NEUTRAL_LEGAL_QUESTION**

> « Le règlement DORA de niveau 1 fixerait un délai de notification initiale en heures. » est-il absent de l'intégralité de Règlement (UE) 2022/2554 (DORA) dans la version consultée, ou une disposition de cet acte le prévoit-elle ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'affirmation négative tombe : aucune fausse prémisse ne pourra être construite sur cette absence, et la règle devra dire ce que le texte prévoit réellement
- `if_no_exception` : l'absence devient opposable et pourra fonder une fausse prémisse, avec le périmètre de recherche cité en source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 19 ; dispositions à examiner : Article 1, Article 20, Article 22, Article 19, Article 16, Article 2

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `DORA-R-010` — DORA · P0 · cluster `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A16-A2-A20-A26-A46`

**RULE**

- ID : `DORA-R-010`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 28 du règlement (UE) 2022/2554 impose de tenir et de mettre à jour un registre d'information relatif à l'ensemble des accords contractuels portant sur l'utilisation de services TIC fournis par des prestataires tiers, en distinguant ceux qui soutiennent des fonctions critiques ou importantes.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 28
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 28
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice des paragraphes 3 et 4, le présent règlement s’applique aux entités suivantes: a) les établissements de crédit; »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Lorsqu’elles élaborent ces projets de normes techniques de réglementation, les AES tiennent compte de la taille et du profil de risque global de l’entité financière, ainsi que de la nature, de l’ampleur et de la complexité de ses services, activités et opérations, et en particulier en vue de garantir que, aux fins du point a) ii), du présent alinéa, différents délais puissent refléter, le cas échéant, les spécificité »
- **Article 26**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice du paragraphe 2, premier et deuxième alinéas, lorsque l’on peut raisonnablement s’attendre à ce que la participation d’un prestataire tiers de services TIC au test de pénétration fondé sur la menace, visée au paragraphe 3, ait une incidence négative sur la qualité ou sur la sécurité des services que le prestataire tiers de services TIC fournit à des clients qui sont des entités ne relevant pas du champ »
- **Article 46**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Article 46 Autorités compétentes Sans préjudice des dispositions relatives au cadre de supervision des prestataires tiers critiques de services TIC visés au chapitre V, section II, du présent règlement, le respect du présent règlement est assuré par les autorités compétentes suivantes, conformément aux pouvoirs conférés par les actes juridiques correspondants: a) pour les établissements de crédit et pour les établiss »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 28 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai, regime_particulier.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 28.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 2 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 26 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 46 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 28 de Règlement (UE) 2022/2554 (DORA) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 16, Article 2 constitue(nt)-t-il(s) une exception applicable à « Article 28 » de Règlement (UE) 2022/2554 (DORA), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle DORA-R-010 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 28 ; dispositions à examiner : Article 1, Article 16, Article 2, Article 20, Article 26, Article 46

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine LCBFT

### `LCBFT-R-001` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-001`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-2 du code monétaire et financier énumère les personnes assujetties aux obligations de lutte contre le blanchiment de capitaux et le financement du terrorisme.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-2
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-2 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-2 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-2 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-001 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-2 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-002` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-002`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-4-1 du code monétaire et financier impose aux personnes assujetties de définir et de mettre en place des dispositifs d'identification et d'évaluation des risques de blanchiment et de financement du terrorisme auxquels elles sont exposées, et d'élaborer une classification de ces risques.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-4-1
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-4-1 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-4-1 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-4-1 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-002 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-4-1 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-003` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-003`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-5 du code monétaire et financier impose d'identifier le client et, le cas échéant, le bénéficiaire effectif, et de vérifier ces éléments d'identification avant d'entrer en relation d'affaires.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-5
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-5 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-5 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-5 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-003 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-5 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-005` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-005`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> Le code monétaire et financier impose d'identifier et de vérifier l'identité du bénéficiaire effectif de la relation d'affaires, les modalités et critères de détermination étant fixés par sa partie réglementaire.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Articles L.561-2-2 et R.561-1 et suivants
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Articles L.561-2-2 et R.561-1 et suivants ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.
- La règle porte une affirmation négative, à l'état « unverified » : « La partie législative du code monétaire et financier fixerait elle-même le seuil de détention du bénéficiaire effectif. ».

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Articles L.561-2-2 et R.561-1 et suivants de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Articles L.561-2-2 et R.561-1 et suivants » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-005 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Articles L.561-2-2 et R.561-1 et suivants ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-006` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-006`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-6 du code monétaire et financier impose d'exercer une vigilance constante pendant toute la durée de la relation d'affaires et de procéder à un examen attentif des opérations effectuées, en veillant à ce qu'elles soient cohérentes avec la connaissance actualisée du client.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-6
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-6 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-6 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-6 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-006 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-6 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-007` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-007`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-10 du code monétaire et financier énumère les situations dans lesquelles les personnes assujetties appliquent des mesures de vigilance complémentaires à l'égard de leur client.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-10
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-10 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-10 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-10 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-007 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-10 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-008` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-008`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> Le code monétaire et financier soumet les relations d'affaires avec des personnes politiquement exposées à des mesures de vigilance complémentaires, la définition et le périmètre de ces personnes étant précisés par sa partie réglementaire.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Articles L.561-10 et R.561-18
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Articles L.561-10 et R.561-18 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Articles L.561-10 et R.561-18 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Articles L.561-10 et R.561-18 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-008 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Articles L.561-10 et R.561-18 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-009` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-009`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-15 du code monétaire et financier impose de déclarer au service Tracfin les sommes ou opérations portant sur des sommes dont les personnes assujetties savent, soupçonnent ou ont de bonnes raisons de soupçonner qu'elles proviennent d'une infraction passible d'une peine privative de liberté supérieure à un an ou sont liées au financement du terrorisme.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-15
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-15 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-15 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-15 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-009 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-15 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-010` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-010`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> Le code monétaire et financier interdit de porter à la connaissance du client ou de tiers l'existence et le contenu d'une déclaration de soupçon adressée à Tracfin, ainsi que les suites qui lui sont données.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-18
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-18 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-18 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-18 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-010 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-18 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-012` — LCBFT · P0 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-012`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-8 du code monétaire et financier dispose que, lorsque la personne assujettie n'est pas en mesure d'identifier son client ou d'obtenir les informations sur l'objet et la nature de la relation d'affaires, elle n'exécute aucune opération et n'établit ni ne poursuit aucune relation d'affaires.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-8
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-8 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-8 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-8 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-012 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-8 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine MIFID

### `MIFID-R-002` — MIFID · P0 · cluster `CL-EXC-DIRECTIVE-2014-65-UE-MIFID-I-A1-A19-A20-A24-A3-A30`

**RULE**

- ID : `MIFID-R-002`
- Domain : MIFID
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 25 de la directive 2014/65/UE impose, lorsqu'un conseil en investissement ou un service de gestion de portefeuille est fourni, de se procurer les informations nécessaires sur les connaissances et l'expérience du client, sa situation financière y compris sa capacité à subir des pertes, et ses objectifs d'investissement y compris sa tolérance au risque, afin de recommander les services et instruments qui lui conviennent.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 2
- Version consultée : 2020-01-01
- Date applicable : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « L’article 17, paragraphes 1 à 6, s’applique également aux membres ou participants des marchés réglementés et des MTF qui ne sont pas tenus d’obtenir un agrément au titre de la présente directive en vertu de l’article 2, paragraphe 1, points a), e), i) et j). »
- **Article 19**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : toutefois
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Toutefois, les membres ou participants du MTF respectent les obligations prévues aux articles 24, 25, 27 et 28 vis-à-vis de leurs clients lorsque, en agissant pour le compte de ceux-ci, ils exécutent leurs ordres par le truchement des systèmes d’un MTF. »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Conformément aux paragraphes 1, 2, 4 et 5 et sans préjudice du paragraphe 3, en ce qui concerne un système qui organise des transactions d’instruments financiers autres que des actions ou instruments assimilés, l’entreprise d’investissement ou l’opérateur de marché exploitant l’OTF peut faciliter la négociation entre des clients afin d’assurer la rencontre de deux positions de négociation, ou plus, potentiellement co »
- **Article 24**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Les avantages monétaires mineurs qui sont susceptibles d’améliorer la qualité du service fourni à un client et dont la grandeur et la nature sont telles qu’ils ne peuvent être pas considérés comme empêchant le respect par l’entreprise d’investissement de son devoir d’agir au mieux des intérêts du client, doivent être clairement signalés et sont exclus du présent point. »
- **Article 3**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, par dérogation, sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « ou d) fournissent des services d’investissement portant exclusivement sur des matières premières, des quotas d’émission et/ou des instruments dérivés sur ceux-ci aux seules fins de couvrir les risques commerciaux de leurs clients, lorsque ces clients sont exclusivement des entreprises locales d’électricité au sens de l’article 2, point 35), de la directive 2009/72/CE et/ou des entreprises de gaz naturel au sens de l’ »
- **Article 30**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Le classement comme contrepartie éligible en vertu du premier alinéa est sans préjudice du droit des entités concernées de demander, soit de manière générale, soit pour chaque transaction, à être traitées comme des clients dont les relations d’affaires avec l’entreprise d’investissement relèvent des articles 24, 25, 27 et 28. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Directive 2014/65/UE (MIFID II) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 25 », paragraphe 2.
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire.
- Article 1 — porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 19 — porte une formule limitante : toutefois ; cette disposition cite explicitement l'article 25.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 24 — porte une formule limitante : sont exclus ; cette disposition cite explicitement l'article 25.
- Article 3 — porte une formule limitante : exemptée?s?, par dérogation, sont exclus ; cette disposition cite explicitement l'article 25.
- Article 30 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 25 de Directive 2014/65/UE (MIFID II) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 19, Article 20 constitue(nt)-t-il(s) une exception applicable à « Article 25 » de Directive 2014/65/UE (MIFID II), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle MIFID-R-002 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Directive 2014/65/UE (MIFID II), version du 2020-01-01 ; article cité : Article 25 ; dispositions à examiner : Article 1, Article 19, Article 20, Article 24, Article 3, Article 30

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `MIFID-R-003` — MIFID · P0 · cluster `CL-EXC-DIRECTIVE-2014-65-UE-MIFID-I-A1-A19-A20-A24-A3-A30`

**RULE**

- ID : `MIFID-R-003`
- Domain : MIFID
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 25 impose, pour les services autres que le conseil en investissement et la gestion de portefeuille, de demander au client des informations sur ses connaissances et son expérience afin d'évaluer si le service ou l'instrument est approprié, et de l'avertir lorsque tel n'est pas le cas.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 3
- Version consultée : 2020-01-01
- Date applicable : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « L’article 17, paragraphes 1 à 6, s’applique également aux membres ou participants des marchés réglementés et des MTF qui ne sont pas tenus d’obtenir un agrément au titre de la présente directive en vertu de l’article 2, paragraphe 1, points a), e), i) et j). »
- **Article 19**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : toutefois
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Toutefois, les membres ou participants du MTF respectent les obligations prévues aux articles 24, 25, 27 et 28 vis-à-vis de leurs clients lorsque, en agissant pour le compte de ceux-ci, ils exécutent leurs ordres par le truchement des systèmes d’un MTF. »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Conformément aux paragraphes 1, 2, 4 et 5 et sans préjudice du paragraphe 3, en ce qui concerne un système qui organise des transactions d’instruments financiers autres que des actions ou instruments assimilés, l’entreprise d’investissement ou l’opérateur de marché exploitant l’OTF peut faciliter la négociation entre des clients afin d’assurer la rencontre de deux positions de négociation, ou plus, potentiellement co »
- **Article 24**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Les avantages monétaires mineurs qui sont susceptibles d’améliorer la qualité du service fourni à un client et dont la grandeur et la nature sont telles qu’ils ne peuvent être pas considérés comme empêchant le respect par l’entreprise d’investissement de son devoir d’agir au mieux des intérêts du client, doivent être clairement signalés et sont exclus du présent point. »
- **Article 3**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, par dérogation, sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « ou d) fournissent des services d’investissement portant exclusivement sur des matières premières, des quotas d’émission et/ou des instruments dérivés sur ceux-ci aux seules fins de couvrir les risques commerciaux de leurs clients, lorsque ces clients sont exclusivement des entreprises locales d’électricité au sens de l’article 2, point 35), de la directive 2009/72/CE et/ou des entreprises de gaz naturel au sens de l’ »
- **Article 30**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Le classement comme contrepartie éligible en vertu du premier alinéa est sans préjudice du droit des entités concernées de demander, soit de manière générale, soit pour chaque transaction, à être traitées comme des clients dont les relations d’affaires avec l’entreprise d’investissement relèvent des articles 24, 25, 27 et 28. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Directive 2014/65/UE (MIFID II) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 25 », paragraphe 3.
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire.
- Article 1 — porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 19 — porte une formule limitante : toutefois ; cette disposition cite explicitement l'article 25.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 24 — porte une formule limitante : sont exclus ; cette disposition cite explicitement l'article 25.
- Article 3 — porte une formule limitante : exemptée?s?, par dérogation, sont exclus ; cette disposition cite explicitement l'article 25.
- Article 30 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 25 de Directive 2014/65/UE (MIFID II) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 19, Article 20 constitue(nt)-t-il(s) une exception applicable à « Article 25 » de Directive 2014/65/UE (MIFID II), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle MIFID-R-003 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Directive 2014/65/UE (MIFID II), version du 2020-01-01 ; article cité : Article 25 ; dispositions à examiner : Article 1, Article 19, Article 20, Article 24, Article 3, Article 30

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `MIFID-R-004` — MIFID · P0 · cluster `CL-EXC-DIRECTIVE-2014-65-UE-MIFID-I-A1-A19-A20-A24-A3-A30`

**RULE**

- ID : `MIFID-R-004`
- Domain : MIFID
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 25 permet, à certaines conditions, de fournir des services de réception-transmission ou d'exécution d'ordres sans procéder à l'évaluation du caractère approprié, lorsque le service porte sur des instruments financiers non complexes, qu'il est fourni à l'initiative du client et que celui-ci a été averti.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 4
- Version consultée : 2020-01-01
- Date applicable : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « L’article 17, paragraphes 1 à 6, s’applique également aux membres ou participants des marchés réglementés et des MTF qui ne sont pas tenus d’obtenir un agrément au titre de la présente directive en vertu de l’article 2, paragraphe 1, points a), e), i) et j). »
- **Article 19**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : toutefois
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Toutefois, les membres ou participants du MTF respectent les obligations prévues aux articles 24, 25, 27 et 28 vis-à-vis de leurs clients lorsque, en agissant pour le compte de ceux-ci, ils exécutent leurs ordres par le truchement des systèmes d’un MTF. »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Conformément aux paragraphes 1, 2, 4 et 5 et sans préjudice du paragraphe 3, en ce qui concerne un système qui organise des transactions d’instruments financiers autres que des actions ou instruments assimilés, l’entreprise d’investissement ou l’opérateur de marché exploitant l’OTF peut faciliter la négociation entre des clients afin d’assurer la rencontre de deux positions de négociation, ou plus, potentiellement co »
- **Article 24**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Les avantages monétaires mineurs qui sont susceptibles d’améliorer la qualité du service fourni à un client et dont la grandeur et la nature sont telles qu’ils ne peuvent être pas considérés comme empêchant le respect par l’entreprise d’investissement de son devoir d’agir au mieux des intérêts du client, doivent être clairement signalés et sont exclus du présent point. »
- **Article 3**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, par dérogation, sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « ou d) fournissent des services d’investissement portant exclusivement sur des matières premières, des quotas d’émission et/ou des instruments dérivés sur ceux-ci aux seules fins de couvrir les risques commerciaux de leurs clients, lorsque ces clients sont exclusivement des entreprises locales d’électricité au sens de l’article 2, point 35), de la directive 2009/72/CE et/ou des entreprises de gaz naturel au sens de l’ »
- **Article 30**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Le classement comme contrepartie éligible en vertu du premier alinéa est sans préjudice du droit des entités concernées de demander, soit de manière générale, soit pour chaque transaction, à être traitées comme des clients dont les relations d’affaires avec l’entreprise d’investissement relèvent des articles 24, 25, 27 et 28. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Directive 2014/65/UE (MIFID II) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 25 », paragraphe 4.
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire.
- Article 1 — porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 19 — porte une formule limitante : toutefois ; cette disposition cite explicitement l'article 25.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 24 — porte une formule limitante : sont exclus ; cette disposition cite explicitement l'article 25.
- Article 3 — porte une formule limitante : exemptée?s?, par dérogation, sont exclus ; cette disposition cite explicitement l'article 25.
- Article 30 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 25 de Directive 2014/65/UE (MIFID II) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 19, Article 20 constitue(nt)-t-il(s) une exception applicable à « Article 25 » de Directive 2014/65/UE (MIFID II), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle MIFID-R-004 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Directive 2014/65/UE (MIFID II), version du 2020-01-01 ; article cité : Article 25 ; dispositions à examiner : Article 1, Article 19, Article 20, Article 24, Article 3, Article 30

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `MIFID-R-006` — MIFID · P0 · cluster `CL-TMP-R-GLEMENT-D-L-GU-UE-2017-565-A19-A4-A5-A91-A72-A79`

**RULE**

- ID : `MIFID-R-006`
- Domain : MIFID
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> Le règlement délégué (UE) 2021/1253, qui modifie le règlement délégué (UE) 2017/565, introduit la notion de préférences en matière de durabilité et impose de les recueillir dans le cadre de l'évaluation de l'adéquation.

**PRIMARY SOURCE**

- Texte : Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253
- Article : Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2022-08-02
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32021R1253

**SUPPORTING PROVISION**

- **Article 19**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 2
  - Extrait : « Aux fins du paragraphe 1, pour le calcul du débit intrajournalier élevé de messages en ce qui concerne les fournisseurs d'accès électronique direct, les messages soumis par leurs clients avec accès électronique direct sont exclus des calculs. »
- **Article 4**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : excepté
  - Relation avec la règle : cette disposition cite explicitement l'article 2
  - Extrait : « et c) la personne exerçant l'activité professionnelle ne commercialise pas ni ne fait en aucune autre façon la promotion de sa capacité à fournir des services d'investissement, excepté si ces derniers sont présentés au client comment étant accessoires à l'activité professionnelle principale. »
- **Article 5**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 2
  - Extrait : « d) les obligations au titre du contrat ne peuvent être compensées par des obligations découlant d'autres contrats entre les parties concernées, sans préjudice des droits des parties au contrat à compenser leurs obligations de paiement en espèces. »
- **Article 91**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : excepté
  - Relation avec la règle : cette disposition cite explicitement l'article 2
  - Extrait : « ANNEXE I Enregistrements Liste minimale des enregistrements que doivent conserver les entreprises d'investissement en fonction de la nature de leurs activités Nature de l'obligation Type d'enregistrement Résumé du contenu Référence législative Évaluation du client Information aux clients Contenu visé à l'article 24, paragraphe 4, de la directive 2014/65/UE et aux articles 39 à 45 du présent règlement Article 24, para »
- **Article 72**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « La liste d'enregistrements figurant à l'annexe I du présent règlement s'entend sans préjudice de toute autre obligation en matière d'enregistrement découlant d'un autre texte législatif. »
- **Article 79**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « En ce qui concerne la proportion de PME, et sans préjudice des autres conditions visées à l'article 33, paragraphe 3, points b) à g), de la directive 2014/65/UE et à l'article 78, paragraphe 2, du présent règlement, il ne peut être mis fin à l'enregistrement d'un marché de croissance des PME par l'autorité compétente de son État membre d'origine que si la proportion de PME, telle que déterminée conformément à l'artic »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253 », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : exemption, conditions_cumulatives, conditions_alternatives, regime_particulier, renvoi, definition_necessaire.
- L'article renvoie aux articles 3, 25.
- Article 19 — porte une formule limitante : sont exclus ; cette disposition cite explicitement l'article 2.
- Article 4 — porte une formule limitante : excepté ; cette disposition cite explicitement l'article 2.
- Article 5 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 2.
- Article 91 — porte une formule limitante : excepté ; cette disposition cite explicitement l'article 2.
- Article 72 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 79 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider quelle version de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253 fait foi pour cette règle (statut « IN_FORCE »), et à quelle date une question devrait se placer.

**NEUTRAL_LEGAL_QUESTION**

> La version de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253 qui fait foi pour la règle MIFID-R-006 est-elle celle consultée le 2020-01-01, ou une version consolidée postérieure s'applique-t-elle ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront porter une date d'appréciation explicite, et une famille temporelle deviendra possible
- `if_no_exception` : les items pourront omettre la date, la règle étant stable sur la période

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253, version du 2020-01-01 ; article cité : Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié ; dispositions à examiner : Article 19, Article 4, Article 5, Article 91, Article 72, Article 79

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `MIFID-R-007` — MIFID · P0 · cluster `CL-NEG-R-GLEMENT-D-L-GU-UE-2017-565-A54-A72-A79`

**RULE**

- ID : `MIFID-R-007`
- Domain : MIFID
- Version : v3
- Current status : `validated`

**CURRENT STATEMENT**

> L'article 54, paragraphe 10, du règlement délégué (UE) 2017/565, dans sa version applicable à partir du 2 août 2022, prévoit que lorsque aucun instrument financier ne répond aux préférences du client ou du client potentiel en matière de durabilité, et que le client décide de modifier ces préférences, l'entreprise d'investissement conserve un enregistrement de la décision du client et des motifs de cette dernière.

**PRIMARY SOURCE**

- Texte : Règlement délégué (UE) 2017/565 modifié
- Article : Article 54
- Paragraphe : paragraphe 10
- Version consultée : 2022-08-02
- Date applicable : 2022-08-02
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02017R0565-20220802

**SUPPORTING PROVISION**

- **Article 54**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : autorisée?s? à présumer, peu(?:t|vent) ne pas
  - Relation avec la règle : disposition interne à l'article cité par la règle
  - Extrait : « Lorsqu'une entreprise d'investissement fournit un service d'investissement à un client professionnel, elle est autorisée à présumer qu'en ce qui concerne les produits, les transactions et les services pour lesquels il est classé comme tel, le client possède le niveau requis d'expérience et de connaissance aux fins du paragraphe 2, point c). »
- **Article 72**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « La liste d'enregistrements figurant à l'annexe I du présent règlement s'entend sans préjudice de toute autre obligation en matière d'enregistrement découlant d'un autre texte législatif. »
- **Article 79**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « En ce qui concerne la proportion de PME, et sans préjudice des autres conditions visées à l'article 33, paragraphe 3, points b) à g), de la directive 2014/65/UE et à l'article 78, paragraphe 2, du présent règlement, il ne peut être mis fin à l'enregistrement d'un marché de croissance des PME par l'autorité compétente de son État membre d'origine que si la proportion de PME, telle que déterminée conformément à l'artic »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement délégué (UE) 2017/565 modifié », consulté dans sa version du 2022-08-02.
- L'ancrage déclaré est « Article 54 », paragraphe 10.
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : exemption, conditions_cumulatives, regime_particulier, renvoi.
- L'article renvoie aux articles 25.
- Article 54 — porte une formule limitante : autorisée?s? à présumer, peu(?:t|vent) ne pas ; disposition interne à l'article cité par la règle.
- Article 72 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 79 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- La règle porte une affirmation négative, à l'état « unverified » : « Le texte fixerait une proportion minimale chiffrée d'investissements durables à proposer. ».

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si « Le texte fixerait une proportion minimale chiffrée d'investissements durables à proposer. » est réellement absent de Règlement délégué (UE) 2017/565 modifié, en indiquant le périmètre consulté — un extrait ne suffit pas à établir une absence.

**NEUTRAL_LEGAL_QUESTION**

> « Le texte fixerait une proportion minimale chiffrée d'investissements durables à proposer. » est-il absent de l'intégralité de Règlement délégué (UE) 2017/565 modifié dans la version consultée, ou une disposition de cet acte le prévoit-elle ?

**mechanical_proposal** : `EXCEPTION_SCOPE_UNCLEAR` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'affirmation négative tombe : aucune fausse prémisse ne pourra être construite sur cette absence, et la règle devra dire ce que le texte prévoit réellement
- `if_no_exception` : l'absence devient opposable et pourra fonder une fausse prémisse, avec le périmètre de recherche cité en source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement délégué (UE) 2017/565 modifié, version du 2022-08-02 ; article cité : Article 54 ; dispositions à examiner : Article 54, Article 72, Article 79

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine SFDR

### `SFDR-R-001` — SFDR · P0 · cluster `CL-EXC-R-GLEMENT-UE-2019-2088-SFDR-A13`

**RULE**

- ID : `SFDR-R-001`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 2 du règlement (UE) 2019/2088 définit l'« investissement durable » comme un investissement dans une activité économique qui contribue à un objectif environnemental ou social, sous réserve que cet investissement ne cause de préjudice important à aucun de ces objectifs et que les sociétés bénéficiaires appliquent des pratiques de bonne gouvernance.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 2
- Paragraphe : point 17
- Version consultée : 2020-01-01
- Date applicable : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**SUPPORTING PROVISION**

- **Article 13**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice d’une législation sectorielle plus stricte, en particulier les directives 2009/65/CE, 2014/65/UE et (UE) 2016/97 et le règlement (UE) n o 1286/2014, les acteurs des marchés financiers et les conseillers financiers veillent à ce que leurs communications publicitaires ne contredisent pas les informations publiées en vertu du présent règlement. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2019/2088 (SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 2 », point 17.
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : definition_necessaire.
- Article 13 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 2 de Règlement (UE) 2019/2088 (SFDR) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 13 constitue(nt)-t-il(s) une exception applicable à « Article 2 » de Règlement (UE) 2019/2088 (SFDR), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle SFDR-R-001 ?

**mechanical_proposal** : `EXCEPTION_SCOPE_UNCLEAR` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2019/2088 (SFDR), version du 2020-01-01 ; article cité : Article 2 ; dispositions à examiner : Article 13

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `SFDR-R-003` — SFDR · P0 · cluster `CL-NEG-R-GLEMENT-UE-2019-2088-SFDR-A20-A4-A13`

**RULE**

- ID : `SFDR-R-003`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 4 impose de publier une déclaration sur les politiques de diligence raisonnable relatives aux principales incidences négatives des décisions d'investissement sur les facteurs de durabilité, ou d'expliquer clairement pourquoi ces incidences ne sont pas prises en compte.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 4
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**SUPPORTING PROVISION**

- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 4
  - Extrait : « Par dérogation au paragraphe 2 du présent article, l’article 4, paragraphes 6 et 7, l’article 8, paragraphe 3, l’article 9, paragraphe 5, l’article 10, paragraphe 2, l’article 11, paragraphe 4, et l’article 13, paragraphe 2, s’appliquent à partir du 29 décembre 2019 , et l’article 11, paragraphes 1 à 3, s’applique à partir du 1 er janvier 2022 . »
- **Article 4**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : disposition interne à l'article cité par la règle
  - Extrait : « Par dérogation au paragraphe 1, à partir du 30 juin 2021 , les acteurs des marchés financiers dépassant, à la date de clôture de leur bilan, le critère du nombre moyen de cinq cents salariés sur l’exercice publient et tiennent à jour sur leur site internet une déclaration sur leurs politiques de diligence raisonnable en ce qui concerne les principales incidences négatives des décisions d’investissement sur les facteu »
- **Article 13**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice d’une législation sectorielle plus stricte, en particulier les directives 2009/65/CE, 2014/65/UE et (UE) 2016/97 et le règlement (UE) n o 1286/2014, les acteurs des marchés financiers et les conseillers financiers veillent à ce que leurs communications publicitaires ne contredisent pas les informations publiées en vertu du présent règlement. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2019/2088 (SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 4 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : derogation, conditions_cumulatives, delai.
- Article 20 — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 4.
- Article 4 — porte une formule limitante : par dérogation ; disposition interne à l'article cité par la règle.
- Article 13 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- La règle porte une affirmation négative, à l'état « unverified » : « L'article 4 fixerait lui-même un seuil chiffré d'encours déclenchant la prise en compte des PAI. ».

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si « L'article 4 fixerait lui-même un seuil chiffré d'encours déclenchant la prise en compte de » est réellement absent de Règlement (UE) 2019/2088 (SFDR), en indiquant le périmètre consulté — un extrait ne suffit pas à établir une absence.

**NEUTRAL_LEGAL_QUESTION**

> « L'article 4 fixerait lui-même un seuil chiffré d'encours déclenchant la prise en compte des PAI. » est-il absent de l'intégralité de Règlement (UE) 2019/2088 (SFDR) dans la version consultée, ou une disposition de cet acte le prévoit-elle ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'affirmation négative tombe : aucune fausse prémisse ne pourra être construite sur cette absence, et la règle devra dire ce que le texte prévoit réellement
- `if_no_exception` : l'absence devient opposable et pourra fonder une fausse prémisse, avec le périmètre de recherche cité en source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2019/2088 (SFDR), version du 2020-01-01 ; article cité : Article 4 ; dispositions à examiner : Article 20, Article 4, Article 13

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `SFDR-R-005` — SFDR · P0 · cluster `CL-EXC-R-GLEMENT-UE-2019-2088-SFDR-A9-A13`

**RULE**

- ID : `SFDR-R-005`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 6 impose d'inclure dans les informations précontractuelles la manière dont les risques en matière de durabilité sont intégrés dans les décisions d'investissement et les résultats de l'évaluation de leurs incidences probables sur le rendement, ou d'expliquer pourquoi ces risques sont jugés non pertinents.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 6
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**SUPPORTING PROVISION**

- **Article 9**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 6
  - Extrait : « Par dérogation au paragraphe 2 du présent article, lorsqu’aucun indice de référence transition climatique de l’Union ou indice de référence accord de Paris de l’Union conformément au règlement (UE) 2016/1011 du Parlement européen et du Conseil Règlement (UE) 2016/1011 du Parlement européen et du Conseil du 8 juin 2016 concernant les indices utilisés comme indices de référence dans le cadre d’instruments et de contrat »
- **Article 13**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice d’une législation sectorielle plus stricte, en particulier les directives 2009/65/CE, 2014/65/UE et (UE) 2016/97 et le règlement (UE) n o 1286/2014, les acteurs des marchés financiers et les conseillers financiers veillent à ce que leurs communications publicitaires ne contredisent pas les informations publiées en vertu du présent règlement. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2019/2088 (SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 6 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.
- Article 9 — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 6.
- Article 13 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 6 de Règlement (UE) 2019/2088 (SFDR) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 9, Article 13 constitue(nt)-t-il(s) une exception applicable à « Article 6 » de Règlement (UE) 2019/2088 (SFDR), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle SFDR-R-005 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2019/2088 (SFDR), version du 2020-01-01 ; article cité : Article 6 ; dispositions à examiner : Article 9, Article 13

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `SFDR-R-008` — SFDR · P0 · cluster `CL-NEG-R-GLEMENT-UE-2019-2088-SFDR-A20-A13`

**RULE**

- ID : `SFDR-R-008`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 8 vise les produits financiers qui promeuvent, entre autres caractéristiques, des caractéristiques environnementales ou sociales, et impose de préciser dans l'information précontractuelle comment ces caractéristiques sont respectées.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 8
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**SUPPORTING PROVISION**

- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 8
  - Extrait : « Par dérogation au paragraphe 2 du présent article, l’article 4, paragraphes 6 et 7, l’article 8, paragraphe 3, l’article 9, paragraphe 5, l’article 10, paragraphe 2, l’article 11, paragraphe 4, et l’article 13, paragraphe 2, s’appliquent à partir du 29 décembre 2019 , et l’article 11, paragraphes 1 à 3, s’applique à partir du 1 er janvier 2022 . »
- **Article 13**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice d’une législation sectorielle plus stricte, en particulier les directives 2009/65/CE, 2014/65/UE et (UE) 2016/97 et le règlement (UE) n o 1286/2014, les acteurs des marchés financiers et les conseillers financiers veillent à ce que leurs communications publicitaires ne contredisent pas les informations publiées en vertu du présent règlement. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2019/2088 (SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 8 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai.
- Article 20 — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 8.
- Article 13 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- La règle porte une affirmation négative, à l'état « unverified » : « L'article 8 imposerait une part minimale d'investissements durables. ».

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si « L'article 8 imposerait une part minimale d'investissements durables. » est réellement absent de Règlement (UE) 2019/2088 (SFDR), en indiquant le périmètre consulté — un extrait ne suffit pas à établir une absence.

**NEUTRAL_LEGAL_QUESTION**

> « L'article 8 imposerait une part minimale d'investissements durables. » est-il absent de l'intégralité de Règlement (UE) 2019/2088 (SFDR) dans la version consultée, ou une disposition de cet acte le prévoit-elle ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'affirmation négative tombe : aucune fausse prémisse ne pourra être construite sur cette absence, et la règle devra dire ce que le texte prévoit réellement
- `if_no_exception` : l'absence devient opposable et pourra fonder une fausse prémisse, avec le périmètre de recherche cité en source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2019/2088 (SFDR), version du 2020-01-01 ; article cité : Article 8 ; dispositions à examiner : Article 20, Article 13

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `TAXO-R-001` — SFDR · P0 · cluster `CL-EXC-R-GLEMENT-UE-2020-852-TAXONO-AUCUNE`

**RULE**

- ID : `TAXO-R-001`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 3 du règlement (UE) 2020/852 énonce les critères cumulatifs permettant de qualifier une activité économique de durable sur le plan environnemental : contribution substantielle à un ou plusieurs objectifs environnementaux, absence de préjudice important aux autres objectifs, respect de garanties minimales et conformité aux critères d'examen technique.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2020/852 (Taxonomie)
- Article : Article 3
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-07-12
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32020R0852

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2020/852 (Taxonomie) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 3 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 3 de Règlement (UE) 2020/852 (Taxonomie) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> L'acte Règlement (UE) 2020/852 (Taxonomie) comporte-t-il, en dehors de « Article 3 », une disposition qui déroge à cette obligation, ou aucune disposition de cet acte n'en limite-t-elle la portée ?

**mechanical_proposal** : `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2020/852 (Taxonomie), version du 2020-01-01 ; article cité : Article 3 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `TAXO-R-003` — SFDR · P0 · cluster `CL-EXC-R-GLEMENT-UE-2020-852-TAXONO-AUCUNE`

**RULE**

- ID : `TAXO-R-003`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 17 du règlement (UE) 2020/852 définit ce qu'il faut entendre par préjudice important causé aux objectifs environnementaux, et l'article 18 fixe les garanties minimales que doit respecter l'activité, en référence à des standards internationaux en matière de droits humains et de travail.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2020/852 (Taxonomie)
- Article : Articles 17 et 18
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-07-12
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32020R0852

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2020/852 (Taxonomie) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Articles 17 et 18 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Articles 17 et 18 de Règlement (UE) 2020/852 (Taxonomie) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> L'acte Règlement (UE) 2020/852 (Taxonomie) comporte-t-il, en dehors de « Articles 17 et 18 », une disposition qui déroge à cette obligation, ou aucune disposition de cet acte n'en limite-t-elle la portée ?

**mechanical_proposal** : `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2020/852 (Taxonomie), version du 2020-01-01 ; article cité : Articles 17 et 18 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

## P1 — REVIEW REQUIRED (16 règles)

### Domaine AMF

### `AMF-R-002` — AMF · P1 · cluster `CL-EXC-POSITION-RECOMMANDATION-AMF-AUCUNE`

**RULE**

- ID : `AMF-R-002`
- Domain : AMF
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> La position-recommandation AMF DOC-2020-03 distingue plusieurs niveaux de communication sur la prise en compte de critères extra-financiers, du niveau central au niveau réduit, selon le degré d'engagement du produit.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Position-recommandation AMF DOC-2020-03 », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Position-recommandation DOC-2020-03 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : seuil, renvoi.
- L'article renvoie aux articles 19.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Position-recommandation DOC-2020-03 de Position-recommandation AMF DOC-2020-03 comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> L'acte Position-recommandation AMF DOC-2020-03 comporte-t-il, en dehors de « Position-recommandation DOC-2020-03 », une disposition qui déroge à cette obligation, ou aucune disposition de cet acte n'en limite-t-elle la portée ?

**mechanical_proposal** : `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Position-recommandation AMF DOC-2020-03, version du 2020-01-01 ; article cité : Position-recommandation DOC-2020-03 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `AMF-R-003` — AMF · P1 · cluster `CL-EXC-POSITION-RECOMMANDATION-AMF-AUCUNE`

**RULE**

- ID : `AMF-R-003`
- Domain : AMF
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> La position-recommandation AMF DOC-2020-03 traite de la cohérence entre la dénomination d'un placement collectif faisant référence à des considérations extra-financières et la réalité de l'approche mise en œuvre.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Position-recommandation AMF DOC-2020-03 », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Position-recommandation DOC-2020-03 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : seuil, renvoi.
- L'article renvoie aux articles 19.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Position-recommandation DOC-2020-03 de Position-recommandation AMF DOC-2020-03 comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> L'acte Position-recommandation AMF DOC-2020-03 comporte-t-il, en dehors de « Position-recommandation DOC-2020-03 », une disposition qui déroge à cette obligation, ou aucune disposition de cet acte n'en limite-t-elle la portée ?

**mechanical_proposal** : `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Position-recommandation AMF DOC-2020-03, version du 2020-01-01 ; article cité : Position-recommandation DOC-2020-03 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `AMF-R-005` — AMF · P1 · cluster `CL-SRC-R-GLEMENT-G-N-RAL-DE-L-AMF-AUCUNE`

**RULE**

- ID : `AMF-R-005`
- Domain : AMF
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> Le règlement général de l'AMF fixe les règles applicables aux acteurs et aux produits relevant de la compétence de l'Autorité des marchés financiers, et se distingue de la doctrine, qui explicite l'interprétation retenue par l'Autorité.

**PRIMARY SOURCE**

- Texte : Règlement général de l'AMF
- Article : Règlement général
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2004-11-24
- URL : https://www.amf-france.org/fr/reglementation/reglement-general

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement général de l'AMF », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Règlement général ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Règlement général de Règlement général de l'AMF, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Règlement général » de Règlement général de l'AMF existe-t-il dans la version applicable et énonce-t-il ce que la règle AMF-R-005 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement général de l'AMF, version du 2020-01-01 ; article cité : Règlement général ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine DORA

### `DORA-R-004` — DORA · P1 · cluster `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A16-A2-A20-A26-A46`

**RULE**

- ID : `DORA-R-004`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> Les articles 8 à 13 du règlement (UE) 2022/2554 organisent les fonctions du cadre de gestion du risque TIC : identification des fonctions et actifs, protection et prévention, détection des activités anormales, réponse et rétablissement, politiques de sauvegarde et de restauration, apprentissage et évolution.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Articles 8 à 13
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 8
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 8
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice des paragraphes 3 et 4, le présent règlement s’applique aux entités suivantes: a) les établissements de crédit; »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Lorsqu’elles élaborent ces projets de normes techniques de réglementation, les AES tiennent compte de la taille et du profil de risque global de l’entité financière, ainsi que de la nature, de l’ampleur et de la complexité de ses services, activités et opérations, et en particulier en vue de garantir que, aux fins du point a) ii), du présent alinéa, différents délais puissent refléter, le cas échéant, les spécificité »
- **Article 26**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice du paragraphe 2, premier et deuxième alinéas, lorsque l’on peut raisonnablement s’attendre à ce que la participation d’un prestataire tiers de services TIC au test de pénétration fondé sur la menace, visée au paragraphe 3, ait une incidence négative sur la qualité ou sur la sécurité des services que le prestataire tiers de services TIC fournit à des clients qui sont des entités ne relevant pas du champ »
- **Article 46**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Article 46 Autorités compétentes Sans préjudice des dispositions relatives au cadre de supervision des prestataires tiers critiques de services TIC visés au chapitre V, section II, du présent règlement, le respect du présent règlement est assuré par les autorités compétentes suivantes, conformément aux pouvoirs conférés par les actes juridiques correspondants: a) pour les établissements de crédit et pour les établiss »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Articles 8 à 13 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai, regime_particulier.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 8.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition cite explicitement l'article 8.
- Article 2 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 26 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 46 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Articles 8 à 13 de Règlement (UE) 2022/2554 (DORA) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 16, Article 2 constitue(nt)-t-il(s) une exception applicable à « Articles 8 à 13 » de Règlement (UE) 2022/2554 (DORA), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle DORA-R-004 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Articles 8 à 13 ; dispositions à examiner : Article 1, Article 16, Article 2, Article 20, Article 26, Article 46

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `DORA-R-006` — DORA · P1 · cluster `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A16-A2-A20-A26-A46`

**RULE**

- ID : `DORA-R-006`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 17 impose de définir, d'établir et de mettre en œuvre un processus de gestion des incidents liés aux TIC permettant de les détecter, de les gérer et de les notifier.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 17
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 17
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice des paragraphes 3 et 4, le présent règlement s’applique aux entités suivantes: a) les établissements de crédit; »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Lorsqu’elles élaborent ces projets de normes techniques de réglementation, les AES tiennent compte de la taille et du profil de risque global de l’entité financière, ainsi que de la nature, de l’ampleur et de la complexité de ses services, activités et opérations, et en particulier en vue de garantir que, aux fins du point a) ii), du présent alinéa, différents délais puissent refléter, le cas échéant, les spécificité »
- **Article 26**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice du paragraphe 2, premier et deuxième alinéas, lorsque l’on peut raisonnablement s’attendre à ce que la participation d’un prestataire tiers de services TIC au test de pénétration fondé sur la menace, visée au paragraphe 3, ait une incidence négative sur la qualité ou sur la sécurité des services que le prestataire tiers de services TIC fournit à des clients qui sont des entités ne relevant pas du champ »
- **Article 46**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Article 46 Autorités compétentes Sans préjudice des dispositions relatives au cadre de supervision des prestataires tiers critiques de services TIC visés au chapitre V, section II, du présent règlement, le respect du présent règlement est assuré par les autorités compétentes suivantes, conformément aux pouvoirs conférés par les actes juridiques correspondants: a) pour les établissements de crédit et pour les établiss »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 17 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 17.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 2 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 26 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 46 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 17 de Règlement (UE) 2022/2554 (DORA) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 16, Article 2 constitue(nt)-t-il(s) une exception applicable à « Article 17 » de Règlement (UE) 2022/2554 (DORA), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle DORA-R-006 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 17 ; dispositions à examiner : Article 1, Article 16, Article 2, Article 20, Article 26, Article 46

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `DORA-R-012` — DORA · P1 · cluster `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A3-A32-A36-A57-A16`

**RULE**

- ID : `DORA-R-012`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 31 organise la désignation, par les autorités européennes de surveillance, des prestataires tiers de services TIC critiques, et les soumet à un cadre de supervision spécifique.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 31
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 31
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 3**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?
  - Relation avec la règle : cette disposition cite explicitement l'article 31
  - Extrait : « 32) établissement exempté en vertu de la directive 2013/36/UE : une entité visée à l’article 2, paragraphe 5, points 4) à 23), de la directive 2013/36/UE; »
- **Article 32**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 31
  - Extrait : « Les exigences énoncées dans la présente section sont sans préjudice de l’application de la directive (UE) 2022/2555 et des autres règles de l’Union en matière de supervision applicables aux fournisseurs de services d’informatique en nuage. »
- **Article 36**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 31
  - Extrait : « Sans préjudice des compétences respectives des institutions de l’Union et des États membres, aux fins du paragraphe 1, l’ABE, l’AEMF ou l’AEAPP conclut des accords de coopération administrative avec l’autorité compétente du pays tiers afin de permettre le bon déroulement des inspections menées dans le pays tiers concerné par le superviseur principal et son équipe désignée pour sa mission dans ce pays tiers. »
- **Article 57**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sauf
  - Relation avec la règle : cette disposition cite explicitement l'article 31
  - Extrait : « La délégation de pouvoir est tacitement prorogée pour des périodes d’une durée identique, sauf si le Parlement européen ou le Conseil s’oppose à cette prorogation trois mois au plus tard avant la fin de chaque période. »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 31 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 31.
- Article 3 — porte une formule limitante : exemptée?s? ; cette disposition cite explicitement l'article 31.
- Article 32 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 31.
- Article 36 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 31.
- Article 57 — porte une formule limitante : sauf ; cette disposition cite explicitement l'article 31.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 31 de Règlement (UE) 2022/2554 (DORA) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 3, Article 32 constitue(nt)-t-il(s) une exception applicable à « Article 31 » de Règlement (UE) 2022/2554 (DORA), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle DORA-R-012 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 31 ; dispositions à examiner : Article 1, Article 3, Article 32, Article 36, Article 57, Article 16

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `DORA-R-013` — DORA · P1 · cluster `CL-EXC-R-GLEMENT-UE-2022-2554-DORA-A1-A16-A2-A20-A26-A46`

**RULE**

- ID : `DORA-R-013`
- Domain : DORA
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> Le règlement (UE) 2022/2554 est entré en vigueur après sa publication et s'applique à compter du 17 janvier 2025.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 64
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 64
  - Extrait : « Le présent règlement est sans préjudice de la responsabilité des États membres pour ce qui est des fonctions essentielles de l’État en matière de sécurité publique, de défense et de sécurité nationale conformément au droit de l’Union. »
- **Article 16**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Les articles 5 à 15 du présent règlement ne s’appliquent pas aux petites entreprises d’investissement non interconnectées et aux établissements de paiement exemptés en vertu de la directive (UE) 2015/2366; »
- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice des paragraphes 3 et 4, le présent règlement s’applique aux entités suivantes: a) les établissements de crédit; »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Lorsqu’elles élaborent ces projets de normes techniques de réglementation, les AES tiennent compte de la taille et du profil de risque global de l’entité financière, ainsi que de la nature, de l’ampleur et de la complexité de ses services, activités et opérations, et en particulier en vue de garantir que, aux fins du point a) ii), du présent alinéa, différents délais puissent refléter, le cas échéant, les spécificité »
- **Article 26**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice du paragraphe 2, premier et deuxième alinéas, lorsque l’on peut raisonnablement s’attendre à ce que la participation d’un prestataire tiers de services TIC au test de pénétration fondé sur la menace, visée au paragraphe 3, ait une incidence négative sur la qualité ou sur la sécurité des services que le prestataire tiers de services TIC fournit à des clients qui sont des entités ne relevant pas du champ »
- **Article 46**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Article 46 Autorités compétentes Sans préjudice des dispositions relatives au cadre de supervision des prestataires tiers critiques de services TIC visés au chapitre V, section II, du présent règlement, le respect du présent règlement est assuré par les autorités compétentes suivantes, conformément aux pouvoirs conférés par les actes juridiques correspondants: a) pour les établissements de crédit et pour les établiss »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2022/2554 (DORA) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 64 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.
- Article 1 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 64.
- Article 16 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 2 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 26 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 46 — porte une formule limitante : exemptée?s?, sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 64 de Règlement (UE) 2022/2554 (DORA) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 16, Article 2 constitue(nt)-t-il(s) une exception applicable à « Article 64 » de Règlement (UE) 2022/2554 (DORA), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle DORA-R-013 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2022/2554 (DORA), version du 2020-01-01 ; article cité : Article 64 ; dispositions à examiner : Article 1, Article 16, Article 2, Article 20, Article 26, Article 46

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine LCBFT

### `LCBFT-R-004` — LCBFT · P1 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-004`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-5-1 du code monétaire et financier impose de recueillir, avant d'entrer en relation d'affaires, les informations relatives à l'objet et à la nature de cette relation et tout élément d'information pertinent.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-5-1
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-5-1 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-5-1 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-5-1 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-004 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-5-1 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-011` — LCBFT · P1 · cluster `CL-SRC-CODE-MON-TAIRE-ET-FINANCIER-AUCUNE`

**RULE**

- ID : `LCBFT-R-011`
- Domain : LCBFT
- Version : v1
- Current status : `draft`

**CURRENT STATEMENT**

> L'article L.561-12 du code monétaire et financier impose de conserver pendant cinq ans à compter de la clôture des comptes ou de la cessation des relations les documents et informations relatifs à l'identité des clients et aux opérations effectuées.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-12
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- Aucune disposition limitante de cet acte ne cite l'article de la règle ni ne déroge à l'acte entier. **Ce n'est pas une preuve d'absence** : le périmètre à examiner reste l'acte complet.

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Code monétaire et financier », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article L.561-12 ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Article L.561-12 de Code monétaire et financier, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Article L.561-12 » de Code monétaire et financier existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-011 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Code monétaire et financier, version du 2020-01-01 ; article cité : Article L.561-12 ; acte entier, à défaut de disposition limitante identifiée

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `LCBFT-R-013` — LCBFT · P1 · cluster `CL-SRC-DIRECTIVE-UE-2015-849-MODIFI-A2-A58`

**RULE**

- ID : `LCBFT-R-013`
- Domain : LCBFT
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> La directive (UE) 2015/849, modifiée notamment par la directive (UE) 2018/843, constitue le cadre européen relatif à la prévention de l'utilisation du système financier aux fins du blanchiment de capitaux et du financement du terrorisme, transposé en droit français dans le code monétaire et financier.

**PRIMARY SOURCE**

- Texte : Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843
- Article : Ensemble de la directive
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2015-06-05
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32015L0849

**SUPPORTING PROVISION**

- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : ne s'appliquen?t? pas, à l'exception d
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « À l'exception des casinos, les États membres peuvent décider, à l'issue d'une évaluation appropriée des risques, d'exempter totalement ou partiellement les prestataires de certains services de jeux d'argent et de hasard des dispositions nationales transposant la présente directive, en se fondant sur le faible risque avéré que représente l'exploitation de ces services de par sa nature et, le cas échéant, son ampleur. »
- **Article 58**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice du droit des États membres de prévoir et d'imposer des sanctions pénales, les États membres établissent des règles relatives aux sanctions et aux mesures administratives et veillent à ce que leurs autorités compétentes puissent imposer ces sanctions et mesures à l'égard des infractions aux dispositions nationales transposant la présente directive, et ils s'assurent qu'elles sont appliquées. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843 », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Ensemble de la directive ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.
- Article 2 — porte une formule limitante : ne s'appliquen?t? pas, à l'exception d ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 58 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Ensemble de la directive de Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843, dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Ensemble de la directive » de Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843 existe-t-il dans la version applicable et énonce-t-il ce que la règle LCBFT-R-013 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843, version du 2020-01-01 ; article cité : Ensemble de la directive ; dispositions à examiner : Article 2, Article 58

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine MIFID

### `MIFID-R-005` — MIFID · P1 · cluster `CL-EXC-DIRECTIVE-2014-65-UE-MIFID-I-A1-A19-A20-A24-A3-A30`

**RULE**

- ID : `MIFID-R-005`
- Domain : MIFID
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 25 impose, en cas de conseil en investissement à un client de détail, de lui fournir une déclaration d'adéquation précisant le conseil fourni et la manière dont il répond à ses préférences, objectifs et autres caractéristiques.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 6
- Version consultée : 2020-01-01
- Date applicable : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**SUPPORTING PROVISION**

- **Article 1**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « L’article 17, paragraphes 1 à 6, s’applique également aux membres ou participants des marchés réglementés et des MTF qui ne sont pas tenus d’obtenir un agrément au titre de la présente directive en vertu de l’article 2, paragraphe 1, points a), e), i) et j). »
- **Article 19**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : toutefois
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Toutefois, les membres ou participants du MTF respectent les obligations prévues aux articles 24, 25, 27 et 28 vis-à-vis de leurs clients lorsque, en agissant pour le compte de ceux-ci, ils exécutent leurs ordres par le truchement des systèmes d’un MTF. »
- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Conformément aux paragraphes 1, 2, 4 et 5 et sans préjudice du paragraphe 3, en ce qui concerne un système qui organise des transactions d’instruments financiers autres que des actions ou instruments assimilés, l’entreprise d’investissement ou l’opérateur de marché exploitant l’OTF peut faciliter la négociation entre des clients afin d’assurer la rencontre de deux positions de négociation, ou plus, potentiellement co »
- **Article 24**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Les avantages monétaires mineurs qui sont susceptibles d’améliorer la qualité du service fourni à un client et dont la grandeur et la nature sont telles qu’ils ne peuvent être pas considérés comme empêchant le respect par l’entreprise d’investissement de son devoir d’agir au mieux des intérêts du client, doivent être clairement signalés et sont exclus du présent point. »
- **Article 3**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : exemptée?s?, par dérogation, sont exclus
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « ou d) fournissent des services d’investissement portant exclusivement sur des matières premières, des quotas d’émission et/ou des instruments dérivés sur ceux-ci aux seules fins de couvrir les risques commerciaux de leurs clients, lorsque ces clients sont exclusivement des entreprises locales d’électricité au sens de l’article 2, point 35), de la directive 2009/72/CE et/ou des entreprises de gaz naturel au sens de l’ »
- **Article 30**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition cite explicitement l'article 25
  - Extrait : « Le classement comme contrepartie éligible en vertu du premier alinéa est sans préjudice du droit des entités concernées de demander, soit de manière générale, soit pour chaque transaction, à être traitées comme des clients dont les relations d’affaires avec l’entreprise d’investissement relèvent des articles 24, 25, 27 et 28. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Directive 2014/65/UE (MIFID II) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 25 », paragraphe 6.
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire.
- Article 1 — porte une formule limitante : exemptée?s?, ne sont pas tenu, sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 19 — porte une formule limitante : toutefois ; cette disposition cite explicitement l'article 25.
- Article 20 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.
- Article 24 — porte une formule limitante : sont exclus ; cette disposition cite explicitement l'article 25.
- Article 3 — porte une formule limitante : exemptée?s?, par dérogation, sont exclus ; cette disposition cite explicitement l'article 25.
- Article 30 — porte une formule limitante : sans préjudice ; cette disposition cite explicitement l'article 25.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 25 de Directive 2014/65/UE (MIFID II) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 1, Article 19, Article 20 constitue(nt)-t-il(s) une exception applicable à « Article 25 » de Directive 2014/65/UE (MIFID II), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle MIFID-R-005 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Directive 2014/65/UE (MIFID II), version du 2020-01-01 ; article cité : Article 25 ; dispositions à examiner : Article 1, Article 19, Article 20, Article 24, Article 3, Article 30

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### Domaine SFDR

### `SFDR-R-002` — SFDR · P1 · cluster `CL-EXC-R-GLEMENT-UE-2019-2088-SFDR-A4-A13`

**RULE**

- ID : `SFDR-R-002`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 3 impose aux acteurs des marchés financiers et aux conseillers financiers de publier sur leur site internet des informations sur leurs politiques d'intégration des risques en matière de durabilité dans leur processus de décision d'investissement ou de conseil.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 3
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**SUPPORTING PROVISION**

- **Article 4**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 3
  - Extrait : « Par dérogation au paragraphe 1, à partir du 30 juin 2021 , les acteurs des marchés financiers dépassant, à la date de clôture de leur bilan, le critère du nombre moyen de cinq cents salariés sur l’exercice publient et tiennent à jour sur leur site internet une déclaration sur leurs politiques de diligence raisonnable en ce qui concerne les principales incidences négatives des décisions d’investissement sur les facteu »
- **Article 13**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice d’une législation sectorielle plus stricte, en particulier les directives 2009/65/CE, 2014/65/UE et (UE) 2016/97 et le règlement (UE) n o 1286/2014, les acteurs des marchés financiers et les conseillers financiers veillent à ce que leurs communications publicitaires ne contredisent pas les informations publiées en vertu du présent règlement. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2019/2088 (SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 3 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.
- Article 4 — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 3.
- Article 13 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 3 de Règlement (UE) 2019/2088 (SFDR) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 4, Article 13 constitue(nt)-t-il(s) une exception applicable à « Article 3 » de Règlement (UE) 2019/2088 (SFDR), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle SFDR-R-002 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2019/2088 (SFDR), version du 2020-01-01 ; article cité : Article 3 ; dispositions à examiner : Article 4, Article 13

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `SFDR-R-006` — SFDR · P1 · cluster `CL-EXC-R-GLEMENT-UE-2019-2088-SFDR-A13`

**RULE**

- ID : `SFDR-R-006`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 7 impose d'indiquer dans l'information précontractuelle si un produit financier prend en compte les principales incidences négatives sur les facteurs de durabilité, et le cas échéant comment.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 7
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**SUPPORTING PROVISION**

- **Article 13**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice d’une législation sectorielle plus stricte, en particulier les directives 2009/65/CE, 2014/65/UE et (UE) 2016/97 et le règlement (UE) n o 1286/2014, les acteurs des marchés financiers et les conseillers financiers veillent à ce que leurs communications publicitaires ne contredisent pas les informations publiées en vertu du présent règlement. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2019/2088 (SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 7 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : delai.
- Article 13 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 7 de Règlement (UE) 2019/2088 (SFDR) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 13 constitue(nt)-t-il(s) une exception applicable à « Article 7 » de Règlement (UE) 2019/2088 (SFDR), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle SFDR-R-006 ?

**mechanical_proposal** : `EXCEPTION_SCOPE_UNCLEAR` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2019/2088 (SFDR), version du 2020-01-01 ; article cité : Article 7 ; dispositions à examiner : Article 13

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `SFDR-R-011` — SFDR · P1 · cluster `CL-EXC-R-GLEMENT-UE-2019-2088-SFDR-A20-A4-A9-A13`

**RULE**

- ID : `SFDR-R-011`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 11 impose d'inclure dans les rapports périodiques des produits relevant des articles 8 et 9 une description de la mesure dans laquelle les caractéristiques environnementales ou sociales sont respectées, ou de l'incidence globale du produit en matière de durabilité.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 11
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**SUPPORTING PROVISION**

- **Article 20**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 11
  - Extrait : « Par dérogation au paragraphe 2 du présent article, l’article 4, paragraphes 6 et 7, l’article 8, paragraphe 3, l’article 9, paragraphe 5, l’article 10, paragraphe 2, l’article 11, paragraphe 4, et l’article 13, paragraphe 2, s’appliquent à partir du 29 décembre 2019 , et l’article 11, paragraphes 1 à 3, s’applique à partir du 1 er janvier 2022 . »
- **Article 4**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 11
  - Extrait : « Par dérogation au paragraphe 1, à partir du 30 juin 2021 , les acteurs des marchés financiers dépassant, à la date de clôture de leur bilan, le critère du nombre moyen de cinq cents salariés sur l’exercice publient et tiennent à jour sur leur site internet une déclaration sur leurs politiques de diligence raisonnable en ce qui concerne les principales incidences négatives des décisions d’investissement sur les facteu »
- **Article 9**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 11
  - Extrait : « Par dérogation au paragraphe 2 du présent article, lorsqu’aucun indice de référence transition climatique de l’Union ou indice de référence accord de Paris de l’Union conformément au règlement (UE) 2016/1011 du Parlement européen et du Conseil Règlement (UE) 2016/1011 du Parlement européen et du Conseil du 8 juin 2016 concernant les indices utilisés comme indices de référence dans le cadre d’instruments et de contrat »
- **Article 13**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sans préjudice
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Sans préjudice d’une législation sectorielle plus stricte, en particulier les directives 2009/65/CE, 2014/65/UE et (UE) 2016/97 et le règlement (UE) n o 1286/2014, les acteurs des marchés financiers et les conseillers financiers veillent à ce que leurs communications publicitaires ne contredisent pas les informations publiées en vertu du présent règlement. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2019/2088 (SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 11 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Structures juridiques relevées dans l'article : conditions_cumulatives, delai.
- Article 20 — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 11.
- Article 4 — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 11.
- Article 9 — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 11.
- Article 13 — porte une formule limitante : sans préjudice ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 11 de Règlement (UE) 2019/2088 (SFDR) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 20, Article 4, Article 9 constitue(nt)-t-il(s) une exception applicable à « Article 11 » de Règlement (UE) 2019/2088 (SFDR), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle SFDR-R-011 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2019/2088 (SFDR), version du 2020-01-01 ; article cité : Article 11 ; dispositions à examiner : Article 20, Article 4, Article 9, Article 13

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `SFDR-R-014` — SFDR · P1 · cluster `CL-SRC-R-GLEMENT-D-L-GU-UE-2022-128-A2-A49`

**RULE**

- ID : `SFDR-R-014`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> Le règlement délégué (UE) 2022/1288 précise le contenu, les méthodes et la présentation des informations SFDR, et fixe des modèles obligatoires en annexe pour les informations précontractuelles et périodiques des produits relevant des articles 8 et 9.

**PRIMARY SOURCE**

- Texte : Règlement délégué (UE) 2022/1288 (RTS SFDR)
- Article : Ensemble du règlement délégué
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2023-01-01
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R1288

**SUPPORTING PROVISION**

- **Article 2**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : sauf
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Les acteurs des marchés financiers et les conseillers financiers fournissent les informations requises par le présent règlement sous une forme électronique permettant les recherches, sauf exigences contraires énoncées dans la législation sectorielle visée à l’article 6, paragraphe 3, et à l’article 11, paragraphe 2, du règlement (UE) 2019/2088. »
- **Article 49**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition déroge à l'acte entier, donc potentiellement à cet article
  - Extrait : « Par dérogation au paragraphe 1, point a), lorsque les informations visées audit point sont publiées sur le site internet de l’administrateur de l’indice de référence, un hyperlien dirigeant vers ces informations est fourni. »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement délégué (UE) 2022/1288 (RTS SFDR) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Ensemble du règlement délégué ».
- Cet article n'a pas été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.
- Article 2 — porte une formule limitante : sauf ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.
- Article 49 — porte une formule limitante : par dérogation ; cette disposition déroge à l'acte entier, donc potentiellement à cet article.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider comment établir Ensemble du règlement délégué de Règlement délégué (UE) 2022/1288 (RTS SFDR), dont le texte primaire n'est pas atteignable depuis l'environnement d'exécution.

**NEUTRAL_LEGAL_QUESTION**

> « Ensemble du règlement délégué » de Règlement délégué (UE) 2022/1288 (RTS SFDR) existe-t-il dans la version applicable et énonce-t-il ce que la règle SFDR-R-014 affirme, ou l'ancrage doit-il être corrigé ?

**mechanical_proposal** : `INSUFFICIENT_SOURCE` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : l'ancrage sera corrigé et les items citeront la disposition exacte
- `if_no_exception` : la règle restera inexploitable : aucun item ne pourra citer sa source

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement délégué (UE) 2022/1288 (RTS SFDR), version du 2020-01-01 ; article cité : Ensemble du règlement délégué ; dispositions à examiner : Article 2, Article 49

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

### `TAXO-R-002` — SFDR · P1 · cluster `CL-EXC-R-GLEMENT-UE-2020-852-TAXONO-A2bis`

**RULE**

- ID : `TAXO-R-002`
- Domain : SFDR
- Version : v1
- Current status : `source_checked`

**CURRENT STATEMENT**

> L'article 9 du règlement (UE) 2020/852 énumère six objectifs environnementaux : atténuation du changement climatique, adaptation au changement climatique, utilisation durable et protection des ressources aquatiques et marines, transition vers une économie circulaire, prévention et réduction de la pollution, et protection et restauration de la biodiversité et des écosystèmes.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2020/852 (Taxonomie)
- Article : Article 9
- Paragraphe : —
- Version consultée : 2020-01-01
- Date applicable : 2020-07-12
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32020R0852

**SUPPORTING PROVISION**

- **Article 2bis**
  - Pourquoi elle est potentiellement pertinente : porte une formule limitante : par dérogation
  - Relation avec la règle : cette disposition cite explicitement l'article 9
  - Extrait : « 5) À l’article 20, le paragraphe 3 est remplacé par le texte suivant: «3 Par dérogation au paragraphe 2 du présent article: a) l’article 4, paragraphes 6 et 7, l’article 8, paragraphe 3, l’article 9, paragraphe 5, l’article 10, paragraphe 2, l’article 11, paragraphe 4, et l’article 13, paragraphe 2, s’appliquent à partir du 29 décembre 2019; »

**TEXTUAL_FACTS** — ce qui est écrit ou mécaniquement constaté

- L'acte cité est « Règlement (UE) 2020/852 (Taxonomie) », consulté dans sa version du 2020-01-01.
- L'ancrage déclaré est « Article 9 ».
- Cet article a été retrouvé dans le texte officiel récupéré.
- Aucune structure limitante n'a été relevée dans l'article lui-même.
- Article 2bis — porte une formule limitante : par dérogation ; cette disposition cite explicitement l'article 9.

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

- Le relecteur humain doit décider si Article 9 de Règlement (UE) 2020/852 (Taxonomie) comporte des dérogations, exclusions ou exemptions que la recherche automatique n'a pas repérées — y compris posées par un autre article ou un acte ultérieur — et, s'il n'y en a aucune, l'attester en portant « none_identified ».

**NEUTRAL_LEGAL_QUESTION**

> Article 2bis constitue(nt)-t-il(s) une exception applicable à « Article 9 » de Règlement (UE) 2020/852 (Taxonomie), ou s'agit-il d'obligations distinctes sans incidence sur la portée de la règle TAXO-R-002 ?

**mechanical_proposal** : `EXCEPTION_LIKELY` — proposition de recherche, jamais une conclusion juridique.

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` : les items devront poser le cas sous condition, et une réponse qui omettrait l'exception deviendra une erreur disqualifiante ; une famille « exception » deviendra possible sur cette règle
- `if_no_exception` : les items pourront poser la règle comme un absolu, et une réponse qui inventerait une dérogation deviendra une erreur disqualifiante

**PÉRIMÈTRE À ATTESTER** (obligatoire pour conclure à l'absence)

> Règlement (UE) 2020/852 (Taxonomie), version du 2020-01-01 ; article cité : Article 9 ; dispositions à examiner : Article 2bis

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-revue-p0p1.csv`

| champ | valeur |
|---|---|
| `reviewer_decision` | `NONE_IDENTIFIED` · `IDENTIFIED_AND_INCORPORATED` · `RULE_REFORMULATED` · `REQUIRES_FURTHER_REVIEW` |
| `reviewer_name` | |
| `review_date` | |
| `review_notes` | |
| `source_scope` | |

---

