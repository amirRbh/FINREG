# Arbitrage humain — pack P0 / P1

Ce document ne génère aucune question, aucune famille, aucun item : il
prépare des décisions. Chaque dossier nomme la disposition à examiner, le
périmètre qui rend une absence opposable, la question binaire à trancher, et
ce que chaque issue changerait.

**Il ne donne aucun conseil juridique.** `TEXTUAL_FACTS` ne porte que ce qui
est écrit dans les sources ; `INTERPRETIVE_QUESTION` porte ce qui demande un
arbitrage. `mechanical_proposal` dit ce que l'automate a vu — jamais ce que
le droit dit.

**État relu** — audit du Rulebook publié, empreinte `fdd4690dd38601bc`. Préparé le 2026-08-30.

Artefacts relus :

- `data/verification/dossier-completude.csv`
- `data/verification/dossier-audit.csv`
- `reports/RULEBOOK_GOLD_READINESS.csv`
- `reports/RULEBOOK_FAMILY_READINESS.csv`

## Ce qu'il y a à trancher

| Priorité | Ce qu'elle signifie | Règles |
|---|---|---:|
| **P0** | une erreur ici serait dangereuse pour un professionnel | 28 |
| **P1** | affecte la validité du benchmark | 16 |

Total : **44** dossiers, regroupés en **39** questions distinctes.

P2 et P3 ne figurent pas ici : on arbitre dans l'ordre de la gravité.

## Regroupements — 2 questions partagées

Plusieurs règles peuvent dépendre de la même disposition et poser la même
question. Une décision unique peut alors couvrir tout le groupe.

**Le regroupement ne fusionne rien.** Les règles restent distinctes dans le
Rulebook, et chacune garde sa décision, son énoncé et sa version : un article
porte couramment plusieurs obligations, et les confondre en effacerait une.

| Regroupement | Règles | Question partagée |
|---|---|---|
| `CL-32014L0065-ART25-EXC` | `MIFID-R-002`, `MIFID-R-003`, `MIFID-R-004`, `MIFID-R-005` | Une dérogation, exclusion, exemption ou condition applicable à MIFID-R-002 existe-t-elle dans le périmètre indiqué — Article 25, un autre article de Directive 2014/65/UE (MIFID II), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ? |
| `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` | `AMF-R-004`, `AMF-R-002`, `AMF-R-003` | Une dérogation, exclusion, exemption ou condition applicable à AMF-R-004 existe-t-elle dans le périmètre indiqué — Position-recommandation DOC-2020-03, un autre article de Position-recommandation AMF DOC-2020-03, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ? |

## Lots de consultation — 1 source hors d'atteinte

Ces règles ne posent pas la même question : elles butent sur le même
empêchement. Le texte primaire n'est pas atteignable depuis l'environnement
d'exécution, et chacune attend la lecture de **son** article. Une seule
consultation de la source couvre tout le lot ; les décisions restent
individuelles.

| Source | Règles | Articles à lire |
|---|---|---|
| Code monétaire et financier | `LCBFT-R-001`, `LCBFT-R-002`, `LCBFT-R-003`, `LCBFT-R-005`, `LCBFT-R-006`, `LCBFT-R-007`, `LCBFT-R-008`, `LCBFT-R-009`, `LCBFT-R-010`, `LCBFT-R-012`, `LCBFT-R-004`, `LCBFT-R-011` | Article L.561-10, Article L.561-12, Article L.561-15, Article L.561-18, Article L.561-2, Article L.561-4-1, Article L.561-5, Article L.561-5-1, Article L.561-6, Article L.561-8, Articles L.561-10 et R.561-18, Articles L.561-2-2 et R.561-1 et suivants |

## P0 — REVIEW REQUIRED (28 règles)

| ID | Domaine | Ancrage | Blocage | Proposition mécanique | Regroupement |
|---|---|---|---|---|---|
| `AMF-R-001` | AMF | Position-recommandation DOC-2020-03 | `NEGATIVE_CLAIM_UNRESOLVED` | `INSUFFICIENT_SOURCE` | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-NEG` |
| `AMF-R-004` | AMF | Position-recommandation DOC-2020-03 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` |
| `DORA-R-002` | DORA | Article 5 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32022R2554-ART5-EXC` |
| `DORA-R-003` | DORA | Article 6 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32022R2554-ART6-EXC` |
| `DORA-R-007` | DORA | Article 18 | `NEGATIVE_CLAIM_UNRESOLVED` | `INSUFFICIENT_SOURCE` | `CL-32022R2554-ART18-NEG` |
| `DORA-R-008` | DORA | Article 19 | `NEGATIVE_CLAIM_UNRESOLVED` | `INSUFFICIENT_SOURCE` | `CL-32022R2554-ART19-NEG` |
| `DORA-R-010` | DORA | Article 28 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32022R2554-ART28-EXC` |
| `LCBFT-R-001` | LCBFT | Article L.561-2 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-2-SRC` |
| `LCBFT-R-002` | LCBFT | Article L.561-4-1 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-4-1-SRC` |
| `LCBFT-R-003` | LCBFT | Article L.561-5 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-5-SRC` |
| `LCBFT-R-005` | LCBFT | Articles L.561-2-2 et R.561-1 et suivants | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-2-2-ET-R-561-1-ET-SRC` |
| `LCBFT-R-006` | LCBFT | Article L.561-6 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-6-SRC` |
| `LCBFT-R-007` | LCBFT | Article L.561-10 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-10-SRC` |
| `LCBFT-R-008` | LCBFT | Articles L.561-10 et R.561-18 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-10-ET-R-561-18-SRC` |
| `LCBFT-R-009` | LCBFT | Article L.561-15 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-15-SRC` |
| `LCBFT-R-010` | LCBFT | Article L.561-18 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-18-SRC` |
| `LCBFT-R-012` | LCBFT | Article L.561-8 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-8-SRC` |
| `MIFID-R-002` | MIFID | Article 25 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32014L0065-ART25-EXC` |
| `MIFID-R-003` | MIFID | Article 25 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32014L0065-ART25-EXC` |
| `MIFID-R-004` | MIFID | Article 25 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32014L0065-ART25-EXC` |
| `MIFID-R-006` | MIFID | Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié | `TEMPORAL_UNRESOLVED` | `EXCEPTION_SCOPE_UNCLEAR` | `CL-32021R1253-ART2-ET-ARTICLE-54-DU-REGLE-TMP` |
| `MIFID-R-007` | MIFID | Article 54 | `NEGATIVE_CLAIM_UNRESOLVED` | `INSUFFICIENT_SOURCE` | `CL-RD25M-ART54-NEG` |
| `SFDR-R-001` | SFDR | Article 2 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32019R2088-ART2-EXC` |
| `SFDR-R-003` | SFDR | Article 4 | `NEGATIVE_CLAIM_UNRESOLVED` | `INSUFFICIENT_SOURCE` | `CL-32019R2088-ART4-NEG` |
| `SFDR-R-005` | SFDR | Article 6 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32019R2088-ART6-EXC` |
| `SFDR-R-008` | SFDR | Article 8 | `NEGATIVE_CLAIM_UNRESOLVED` | `INSUFFICIENT_SOURCE` | `CL-32019R2088-ART8-NEG` |
| `TAXO-R-001` | SFDR | Article 3 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32020R0852-ART3-EXC` |
| `TAXO-R-003` | SFDR | Articles 17 et 18 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32020R0852-ART17-ET-18-EXC` |

### AMF — 2 règle(s)

#### `AMF-R-001` — AMF · P0 · `review_cluster_id` : `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-NEG`

**RULE**

- ID : `AMF-R-001`
- Domaine : AMF
- Version : v1
- Statut courant : `source_checked`
- Blocage : `NEGATIVE_CLAIM_UNRESOLVED` (affirmations_negatives_resolues)

**CURRENT STATEMENT**

> La position-recommandation AMF DOC-2020-03 subordonne la possibilité pour un placement collectif de communiquer de manière centrale sur la prise en compte de critères extra-financiers au caractère significativement engageant de l'approche mise en œuvre.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- **Article 19 de Position-recommandation AMF DOC-2020-03**
  - Pourquoi elle est potentiellement pertinente : Position-recommandation DOC-2020-03 y renvoie explicitement
  - Relation avec la règle : peut conditionner l'application de la règle
- **Article 8 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits promouvant des caractéristiques environnementales ou sociales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Position-recommandation AMF DOC-2020-03 entier dans sa version applicable au 2020-01-01, et non le seul Position-recommandation DOC-2020-03 : une absence ne s'établit pas sur un extrait

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Position-recommandation DOC-2020-03 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : seuil, renvoi
- renvois relevés dans l'article : 19
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2020-03-11
- affirmation négative non vérifiée : « Le règlement SFDR imposerait lui-même les conditions de communication commerciale applicables en France. »
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Établir qu'une disposition est absente suppose d'avoir couvert un périmètre et de l'attester : l'analyse peut dire qu'elle n'a pas trouvé, jamais que cela n'existe pas.

**NEUTRAL_LEGAL_QUESTION**

> « Le règlement SFDR imposerait lui-même les conditions de communication commerciale applicables en France. » : cette disposition est-elle absente de Position-recommandation AMF DOC-2020-03 dans le périmètre indiqué, ou une disposition la porte-t-elle ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `EXCEPTION_UNRESOLVED` (exceptions_recherchees) — recherche d'exceptions « requires_human_review » : une question construite ici testerait la règle comme un absolu
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'affirmation passe « present_contrary » : la fausse prémisse prévue était vraie, l'item l'aurait comptée à l'envers, et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — l'affirmation passe « verified_absent » avec `searched_in` : elle peut porter une fausse prémisse opposable

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `AMF-R-004` — AMF · P0 · `review_cluster_id` : `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC`

**RULE**

- ID : `AMF-R-004`
- Domaine : AMF
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> La doctrine AMF relative aux informations extra-financières des placements collectifs s'applique en complément du règlement (UE) 2019/2088, qui régit l'information réglementaire, la doctrine portant sur la communication.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- **Article 19 de Position-recommandation AMF DOC-2020-03**
  - Pourquoi elle est potentiellement pertinente : Position-recommandation DOC-2020-03 y renvoie explicitement
  - Relation avec la règle : peut conditionner l'application de la règle
- **Article 8 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits promouvant des caractéristiques environnementales ou sociales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 13 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-013)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Cohérence des communications publicitaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Position-recommandation AMF DOC-2020-03 entier au 2020-01-01 — articles autres que Position-recommandation DOC-2020-03 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Position-recommandation DOC-2020-03 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : seuil, renvoi
- renvois relevés dans l'article : 19
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2020-03-11
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à AMF-R-004 existe-t-elle dans le périmètre indiqué — Position-recommandation DOC-2020-03, un autre article de Position-recommandation AMF DOC-2020-03, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### DORA — 5 règle(s)

#### `DORA-R-002` — DORA · P0 · `review_cluster_id` : `CL-32022R2554-ART5-EXC`

**RULE**

- ID : `DORA-R-002`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 5 du règlement (UE) 2022/2554 dispose que l'organe de direction de l'entité financière définit, approuve, supervise et est responsable de la mise en œuvre du cadre de gestion du risque lié aux TIC.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 5
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 5 Gouvernance et organisation 1. Les entités financières disposent d’un cadre de gouvernance et de contrôle interne qui garantit une gestion efficace et prudente du risque lié aux TIC, conformément à l’article 6, paragraphe 4, en vue d’atteindre un niveau élevé de résilience opérationnelle numérique. 2. L’organe de direction de l’entité financière définit, approuve, supervise et est responsable de la mise en œuvre de toutes les dispositions relatives au cadre de gestion du risque lié aux TIC visé à l’article 6, paragraphe 1. Aux fins du premier alinéa, l’organe de direction: a) assume

**SUPPORTING PROVISION**

- **Article 30 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-011)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Dispositions contractuelles essentielles avec les prestataires TIC »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 9 de Directive 2014/65/UE (MIFID II) (règle MIFID-R-010)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Responsabilité de l'organe de direction »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier au 2020-01-01 — articles autres que Article 5 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 5 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, regime_particulier
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- extrait officiel disponible (599 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à DORA-R-002 existe-t-elle dans le périmètre indiqué — Article 5, un autre article de Règlement (UE) 2022/2554 (DORA), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `DORA-R-003` — DORA · P0 · `review_cluster_id` : `CL-32022R2554-ART6-EXC`

**RULE**

- ID : `DORA-R-003`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 6 impose de disposer d'un cadre de gestion du risque lié aux TIC solide, complet et bien documenté, faisant partie du dispositif global de gestion des risques, et de le réexaminer au moins une fois par an.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 6
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 6 Cadre de gestion du risque lié aux TIC 1. Les entités financières disposent d’un cadre de gestion du risque lié aux TIC solide, complet et bien documenté, faisant partie de leur système global de gestion des risques, qui leur permet de parer au risque lié aux TIC de manière rapide, efficiente et exhaustive et de garantir un niveau élevé de résilience opérationnelle numérique. 2. Le cadre de gestion du risque lié aux TIC englobe au moins les stratégies, les politiques, les procédures, les protocoles et les outils de TIC qui sont nécessaires pour protéger dûment et de manière approprié

**SUPPORTING PROVISION**

- **Articles 8 à 13 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-004)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Identification, protection, détection, réponse et apprentissage »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 28 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-010)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Registre d'information des accords contractuels TIC »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier au 2020-01-01 — articles autres que Article 6 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 6 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, regime_particulier
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à DORA-R-003 existe-t-elle dans le périmètre indiqué — Article 6, un autre article de Règlement (UE) 2022/2554 (DORA), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `TEMPORAL_UNRESOLVED` (temporalite_etablie) — temporalité « IN_FORCE » non établie : la date d'appréciation de la question serait arbitraire
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `DORA-R-007` — DORA · P0 · `review_cluster_id` : `CL-32022R2554-ART18-NEG`

**RULE**

- ID : `DORA-R-007`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `NEGATIVE_CLAIM_UNRESOLVED` (affirmations_negatives_resolues)

**CURRENT STATEMENT**

> L'article 18 impose de classer les incidents liés aux TIC et de déterminer leur incidence selon des critères tels que le nombre de clients affectés, la durée, la répartition géographique, les pertes de données et la criticité des services touchés, les seuils étant précisés par des normes techniques.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 18
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 18 Classification des incidents liés aux TIC et des cybermenaces 1. Les entités financières classent les incidents liés aux TIC et déterminent leur incidence sur la base des critères suivants: a) le nombre et/ou l’importance des clients ou des contreparties financières touchés et, le cas échéant, le volume ou le nombre de transactions touchées par l’incident lié aux TIC, et si cet incident a porté atteinte à la réputation; b) la durée de l’incident lié aux TIC, y compris les interruptions de service; c) la répartition géographique en ce qui concerne les zones touchées par l’incident li

**SUPPORTING PROVISION**

- **Article 19 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Notification des incidents majeurs à l'autorité compétente »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier dans sa version applicable au 2020-01-01, et non le seul Article 18 : une absence ne s'établit pas sur un extrait

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 18 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai, regime_particulier
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- affirmation négative non vérifiée : « L'article 18 fixerait lui-même un nombre de clients affectés au-delà duquel l'incident est majeur. »
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Établir qu'une disposition est absente suppose d'avoir couvert un périmètre et de l'attester : l'analyse peut dire qu'elle n'a pas trouvé, jamais que cela n'existe pas.

**NEUTRAL_LEGAL_QUESTION**

> « L'article 18 fixerait lui-même un nombre de clients affectés au-delà duquel l'incident est majeur. » : cette disposition est-elle absente de Règlement (UE) 2022/2554 (DORA) dans le périmètre indiqué, ou une disposition la porte-t-elle ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `EXCEPTION_UNRESOLVED` (exceptions_recherchees) — recherche d'exceptions « requires_human_review » : une question construite ici testerait la règle comme un absolu
- `TEMPORAL_UNRESOLVED` (temporalite_etablie) — temporalité « IN_FORCE » non établie : la date d'appréciation de la question serait arbitraire
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'affirmation passe « present_contrary » : la fausse prémisse prévue était vraie, l'item l'aurait comptée à l'envers, et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — l'affirmation passe « verified_absent » avec `searched_in` : elle peut porter une fausse prémisse opposable

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `DORA-R-008` — DORA · P0 · `review_cluster_id` : `CL-32022R2554-ART19-NEG`

**RULE**

- ID : `DORA-R-008`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `NEGATIVE_CLAIM_UNRESOLVED` (affirmations_negatives_resolues)

**CURRENT STATEMENT**

> L'article 19 impose de notifier les incidents majeurs liés aux TIC à l'autorité compétente, selon un processus comportant une notification initiale, un rapport intermédiaire et un rapport final, dont les délais sont précisés par des normes techniques.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 19
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 19 Déclaration des incidents majeurs liés aux TIC et notification volontaire des cybermenaces importantes 1. Les entités financières déclarent à l’autorité compétente pertinente visée à l’article 46 les incidents majeurs liés aux TIC, conformément au paragraphe 4 du présent article. Lorsqu’une entité financière est soumise à la surveillance de plusieurs autorités nationales compétentes visées à l’article 46, les États membres désignent une seule autorité compétente en tant qu’autorité compétente concernée chargée d’exercer les fonctions et missions prévues au présent article. Les établ

**SUPPORTING PROVISION**

- **Article 18 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-007)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Classification des incidents et détermination du caractère majeur »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier dans sa version applicable au 2020-01-01, et non le seul Article 19 : une absence ne s'établit pas sur un extrait

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 19 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : derogation, conditions_cumulatives, conditions_alternatives, definition_necessaire
- recherche d'exceptions à ce jour : « identified_and_incorporated »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- affirmation négative non vérifiée : « Le règlement DORA de niveau 1 fixerait un délai de notification initiale en heures. »
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Établir qu'une disposition est absente suppose d'avoir couvert un périmètre et de l'attester : l'analyse peut dire qu'elle n'a pas trouvé, jamais que cela n'existe pas.

**NEUTRAL_LEGAL_QUESTION**

> « Le règlement DORA de niveau 1 fixerait un délai de notification initiale en heures. » : cette disposition est-elle absente de Règlement (UE) 2022/2554 (DORA) dans le périmètre indiqué, ou une disposition la porte-t-elle ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `TEMPORAL_UNRESOLVED` (temporalite_etablie) — temporalité « IN_FORCE » non établie : la date d'appréciation de la question serait arbitraire
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'affirmation passe « present_contrary » : la fausse prémisse prévue était vraie, l'item l'aurait comptée à l'envers, et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — l'affirmation passe « verified_absent » avec `searched_in` : elle peut porter une fausse prémisse opposable

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `DORA-R-010` — DORA · P0 · `review_cluster_id` : `CL-32022R2554-ART28-EXC`

**RULE**

- ID : `DORA-R-010`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 28 du règlement (UE) 2022/2554 impose de tenir et de mettre à jour un registre d'information relatif à l'ensemble des accords contractuels portant sur l'utilisation de services TIC fournis par des prestataires tiers, en distinguant ceux qui soutiennent des fonctions critiques ou importantes.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 28
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 28 Principes généraux 1. Les entités financières gèrent les risques liés aux prestataires tiers de services TIC en tant que partie intégrante du risque lié aux TIC dans leur cadre de gestion du risque lié aux TIC visé à l’article 6, paragraphe 1, et conformément aux principes suivants: a) les entités financières qui ont conclu des accords contractuels pour l’utilisation de services TIC dans le cadre de leurs activités restent à tout moment pleinement responsables du respect et de l’exécution de toutes les obligations découlant du présent règlement et du droit applicable aux services fi

**SUPPORTING PROVISION**

- **Article 30 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-011)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Dispositions contractuelles essentielles avec les prestataires TIC »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 31 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-012)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Désignation des prestataires tiers critiques de services TIC »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier au 2020-01-01 — articles autres que Article 28 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 28 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai, regime_particulier
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à DORA-R-010 existe-t-elle dans le périmètre indiqué — Article 28, un autre article de Règlement (UE) 2022/2554 (DORA), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### LCBFT — 10 règle(s)

#### `LCBFT-R-001` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-2-SRC`

**RULE**

- ID : `LCBFT-R-001`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-2 du code monétaire et financier énumère les personnes assujetties aux obligations de lutte contre le blanchiment de capitaux et le financement du terrorisme.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-2
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-4-1 de Code monétaire et financier (règle LCBFT-R-002)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Classification des risques »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-2 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-2 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-001, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-002` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-4-1-SRC`

**RULE**

- ID : `LCBFT-R-002`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-4-1 du code monétaire et financier impose aux personnes assujetties de définir et de mettre en place des dispositifs d'identification et d'évaluation des risques de blanchiment et de financement du terrorisme auxquels elles sont exposées, et d'élaborer une classification de ces risques.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-4-1
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-5 de Code monétaire et financier (règle LCBFT-R-003)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Identification et vérification avant l'entrée en relation d'affaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article L.561-6 de Code monétaire et financier (règle LCBFT-R-006)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Vigilance constante pendant toute la relation d'affaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-4-1 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-4-1 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-002, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-003` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-5-SRC`

**RULE**

- ID : `LCBFT-R-003`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-5 du code monétaire et financier impose d'identifier le client et, le cas échéant, le bénéficiaire effectif, et de vérifier ces éléments d'identification avant d'entrer en relation d'affaires.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-5
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-5-1 de Code monétaire et financier (règle LCBFT-R-004)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Recueil d'informations sur l'objet et la nature de la relation d'affaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Articles L.561-2-2 et R.561-1 et suivants de Code monétaire et financier (règle LCBFT-R-005)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Identification du bénéficiaire effectif »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-5 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-5 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-003, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-005` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-2-2-ET-R-561-1-ET-SRC`

**RULE**

- ID : `LCBFT-R-005`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> Le code monétaire et financier impose d'identifier et de vérifier l'identité du bénéficiaire effectif de la relation d'affaires, les modalités et critères de détermination étant fixés par sa partie réglementaire.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Articles L.561-2-2 et R.561-1 et suivants
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-5 de Code monétaire et financier (règle LCBFT-R-003)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Identification et vérification avant l'entrée en relation d'affaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Articles L.561-2-2 et R.561-1 et suivants de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- affirmation négative non vérifiée : « La partie législative du code monétaire et financier fixerait elle-même le seuil de détention du bénéficiaire effectif. »
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Articles L.561-2-2 et R.561-1 et suivants de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-005, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-006` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-6-SRC`

**RULE**

- ID : `LCBFT-R-006`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-6 du code monétaire et financier impose d'exercer une vigilance constante pendant toute la durée de la relation d'affaires et de procéder à un examen attentif des opérations effectuées, en veillant à ce qu'elles soient cohérentes avec la connaissance actualisée du client.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-6
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-4-1 de Code monétaire et financier (règle LCBFT-R-002)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Classification des risques »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article L.561-10 de Code monétaire et financier (règle LCBFT-R-007)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Mesures de vigilance renforcée »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-6 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-6 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-006, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-007` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-10-SRC`

**RULE**

- ID : `LCBFT-R-007`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-10 du code monétaire et financier énumère les situations dans lesquelles les personnes assujetties appliquent des mesures de vigilance complémentaires à l'égard de leur client.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-10
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Articles L.561-10 et R.561-18 de Code monétaire et financier (règle LCBFT-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Traitement des personnes politiquement exposées »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article L.561-15 de Code monétaire et financier (règle LCBFT-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Déclaration de soupçon à Tracfin »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-10 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-10 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-007, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-008` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-10-ET-R-561-18-SRC`

**RULE**

- ID : `LCBFT-R-008`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> Le code monétaire et financier soumet les relations d'affaires avec des personnes politiquement exposées à des mesures de vigilance complémentaires, la définition et le périmètre de ces personnes étant précisés par sa partie réglementaire.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Articles L.561-10 et R.561-18
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-10 de Code monétaire et financier (règle LCBFT-R-007)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Mesures de vigilance renforcée »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article L.561-15 de Code monétaire et financier (règle LCBFT-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Déclaration de soupçon à Tracfin »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Articles L.561-10 et R.561-18 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Articles L.561-10 et R.561-18 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-008, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-009` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-15-SRC`

**RULE**

- ID : `LCBFT-R-009`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-15 du code monétaire et financier impose de déclarer au service Tracfin les sommes ou opérations portant sur des sommes dont les personnes assujetties savent, soupçonnent ou ont de bonnes raisons de soupçonner qu'elles proviennent d'une infraction passible d'une peine privative de liberté supérieure à un an ou sont liées au financement du terrorisme.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-15
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-18 de Code monétaire et financier (règle LCBFT-R-010)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Interdiction d'informer le client de la déclaration »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-15 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-15 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-009, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-010` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-18-SRC`

**RULE**

- ID : `LCBFT-R-010`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> Le code monétaire et financier interdit de porter à la connaissance du client ou de tiers l'existence et le contenu d'une déclaration de soupçon adressée à Tracfin, ainsi que les suites qui lui sont données.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-18
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-15 de Code monétaire et financier (règle LCBFT-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Déclaration de soupçon à Tracfin »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-18 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-18 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-010, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-012` — LCBFT · P0 · `review_cluster_id` : `CL-CMF-ARTL-561-8-SRC`

**RULE**

- ID : `LCBFT-R-012`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-8 du code monétaire et financier dispose que, lorsque la personne assujettie n'est pas en mesure d'identifier son client ou d'obtenir les informations sur l'objet et la nature de la relation d'affaires, elle n'exécute aucune opération et n'établit ni ne poursuit aucune relation d'affaires.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-8
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-5 de Code monétaire et financier (règle LCBFT-R-003)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Identification et vérification avant l'entrée en relation d'affaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article L.561-15 de Code monétaire et financier (règle LCBFT-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Déclaration de soupçon à Tracfin »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-8 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-8 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-012, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### MIFID — 5 règle(s)

#### `MIFID-R-002` — MIFID · P0 · `review_cluster_id` : `CL-32014L0065-ART25-EXC`

**RULE**

- ID : `MIFID-R-002`
- Domaine : MIFID
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 25 de la directive 2014/65/UE impose, lorsqu'un conseil en investissement ou un service de gestion de portefeuille est fourni, de se procurer les informations nécessaires sur les connaissances et l'expérience du client, sa situation financière y compris sa capacité à subir des pertes, et ses objectifs d'investissement y compris sa tolérance au risque, afin de recommander les services et instruments qui lui conviennent.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 2
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**Extrait officiel**

> 2. Lorsqu’elle fournit des conseils en investissement ou des services de gestion de portefeuille, l’entreprise d’investissement se procure les informations nécessaires concernant les connaissances et l’expérience du client ou du client potentiel en matière d’investissement en rapport avec le type spécifique de produit ou de service, sa situation financière, y compris sa capacité à subir des pertes, et ses objectifs d’investissement, y compris sa tolérance au risque, de manière à pouvoir lui recommander les services d’investissement et les instruments financiers qui lui conviennent et, en parti

**SUPPORTING PROVISION**

- **Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253 (règle MIFID-R-006)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Préférences en matière de durabilité »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Directive 2014/65/UE (MIFID II) entier au 2020-01-01 — articles autres que Article 25 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 25 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2018-01-03
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à MIFID-R-002 existe-t-elle dans le périmètre indiqué — Article 25, un autre article de Directive 2014/65/UE (MIFID II), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `MIFID-R-003` — MIFID · P0 · `review_cluster_id` : `CL-32014L0065-ART25-EXC`

**RULE**

- ID : `MIFID-R-003`
- Domaine : MIFID
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 25 impose, pour les services autres que le conseil en investissement et la gestion de portefeuille, de demander au client des informations sur ses connaissances et son expérience afin d'évaluer si le service ou l'instrument est approprié, et de l'avertir lorsque tel n'est pas le cas.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 3
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**Extrait officiel**

> 3. Lorsque les entreprises d’investissement fournissent des services d’investissement autres que ceux visés au paragraphe 2, les États membres veillent à ce qu’elles demandent au client ou au client potentiel de donner des informations sur ses connaissances et sur son expérience en matière d’investissement en rapport avec le type spécifique de produit ou de service proposé ou demandé pour être en mesure de déterminer si le service ou le produit d’investissement envisagé convient au client. Lorsqu’une offre groupée de services ou de produits est envisagée conformément à l’article 24, paragraphe

**SUPPORTING PROVISION**

- **Directive 2014/65/UE (MIFID II) — hors Article 25**
  - Pourquoi elle est potentiellement pertinente : l'analyse n'a repéré aucune disposition candidate dans l'article cité : il n'y a donc rien à confirmer, seulement un périmètre à balayer
  - Relation avec la règle : périmètre de recherche, aucune disposition désignée

**Périmètre à examiner** — Directive 2014/65/UE (MIFID II) entier au 2020-01-01 — articles autres que Article 25 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 25 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2018-01-03
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à MIFID-R-003 existe-t-elle dans le périmètre indiqué — Article 25, un autre article de Directive 2014/65/UE (MIFID II), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `MIFID-R-004` — MIFID · P0 · `review_cluster_id` : `CL-32014L0065-ART25-EXC`

**RULE**

- ID : `MIFID-R-004`
- Domaine : MIFID
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 25 permet, à certaines conditions, de fournir des services de réception-transmission ou d'exécution d'ordres sans procéder à l'évaluation du caractère approprié, lorsque le service porte sur des instruments financiers non complexes, qu'il est fourni à l'initiative du client et que celui-ci a été averti.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 4
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**Extrait officiel**

> 4. Les États membres autorisent les entreprises d’investissement, lorsqu’elles fournissent des services d’investissement qui comprennent uniquement l’exécution ou la réception et la transmission d’ordres de clients, avec ou sans services auxiliaires, à l’exclusion de l’octroi des crédits ou des prêts visés à la section B.1 de l’annexe I, dans le cadre desquels les limites existantes concernant les prêts, les comptes courants et les découverts pour les clients ne s’appliquent pas, à fournir ces services d’investissement à leurs clients sans devoir obtenir les informations ni procéder à l’évalua

**SUPPORTING PROVISION**

- **Directive 2014/65/UE (MIFID II) — hors Article 25**
  - Pourquoi elle est potentiellement pertinente : l'analyse n'a repéré aucune disposition candidate dans l'article cité : il n'y a donc rien à confirmer, seulement un périmètre à balayer
  - Relation avec la règle : périmètre de recherche, aucune disposition désignée

**Périmètre à examiner** — Directive 2014/65/UE (MIFID II) entier au 2020-01-01 — articles autres que Article 25 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 25 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2018-01-03
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à MIFID-R-004 existe-t-elle dans le périmètre indiqué — Article 25, un autre article de Directive 2014/65/UE (MIFID II), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `MIFID-R-006` — MIFID · P0 · `review_cluster_id` : `CL-32021R1253-ART2-ET-ARTICLE-54-DU-REGLE-TMP`

**RULE**

- ID : `MIFID-R-006`
- Domaine : MIFID
- Version : v1
- Statut courant : `source_checked`
- Blocage : `TEMPORAL_UNRESOLVED` (temporalite_etablie)

**CURRENT STATEMENT**

> Le règlement délégué (UE) 2021/1253, qui modifie le règlement délégué (UE) 2017/565, introduit la notion de préférences en matière de durabilité et impose de les recueillir dans le cadre de l'évaluation de l'adéquation.

**PRIMARY SOURCE**

- Texte : Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253
- Article : Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2022-08-02
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32021R1253

**Extrait officiel**

> Article 2 Définitions Aux fins du présent règlement, on entend par: 1) «personne concernée» : dans le cas d'une entreprise d'investissement, l'une quelconque des personnes suivantes: a) un administrateur, associé ou équivalent, gérant ou agent lié de l'entreprise; b) un administrateur, associé ou équivalent, ou gérant de tout agent lié de l'entreprise; c) un membre du personnel de l'entreprise ou d'un agent lié de l'entreprise, ainsi que toute autre personne physique dont les services sont mis à la disposition et placés sous le contrôle de l'entreprise ou d'un agent lié de l'entreprise et qui

**SUPPORTING PROVISION**

- **Article 3 de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253**
  - Pourquoi elle est potentiellement pertinente : Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié y renvoie explicitement
  - Relation avec la règle : peut conditionner l'application de la règle
- **Article 25 de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253**
  - Pourquoi elle est potentiellement pertinente : Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié y renvoie explicitement
  - Relation avec la règle : peut conditionner l'application de la règle
- **Article 25 de Directive 2014/65/UE (MIFID II) (règle MIFID-R-002)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Évaluation de l'adéquation dans le conseil et la gestion de portefeuille »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 54 de Règlement délégué (UE) 2017/565 modifié (règle MIFID-R-007)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Adaptation des préférences de durabilité »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 8 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits promouvant des caractéristiques environnementales ou sociales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — les versions successives de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253 couvrant Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié, et la date de consolidation applicable

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : exemption, conditions_cumulatives, conditions_alternatives, regime_particulier, renvoi, definition_necessaire
- renvois relevés dans l'article : 3, 25
- recherche d'exceptions à ce jour : « identified_and_incorporated »
- statut réglementaire « in_force », en vigueur depuis le 2022-08-02
- extrait officiel disponible (599 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Choisir la version applicable engage la date à laquelle une question se placera : l'analyse constate qu'aucune consolidation ne correspond à la date déclarée, elle ne désigne pas celle qui fait foi.

**NEUTRAL_LEGAL_QUESTION**

> La version de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253 qui fait foi pour MIFID-R-006 est-elle celle déclarée au 2020-01-01, ou une version consolidée postérieure s'applique-t-elle à Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié ?

**mechanical_proposal** — `EXCEPTION_SCOPE_UNCLEAR` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — une version consolidée postérieure fait foi : la date d'appréciation des items change, et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — la version déclarée fait foi : les items se placent à cette date sans réserve

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `MIFID-R-007` — MIFID · P0 · `review_cluster_id` : `CL-RD25M-ART54-NEG`

**RULE**

- ID : `MIFID-R-007`
- Domaine : MIFID
- Version : v3
- Statut courant : `validated`
- Blocage : `NEGATIVE_CLAIM_UNRESOLVED` (affirmations_negatives_resolues)

**CURRENT STATEMENT**

> L'article 54, paragraphe 10, du règlement délégué (UE) 2017/565, dans sa version applicable à partir du 2 août 2022, prévoit que lorsque aucun instrument financier ne répond aux préférences du client ou du client potentiel en matière de durabilité, et que le client décide de modifier ces préférences, l'entreprise d'investissement conserve un enregistrement de la décision du client et des motifs de cette dernière.

**PRIMARY SOURCE**

- Texte : Règlement délégué (UE) 2017/565 modifié
- Article : Article 54
- Paragraphe : paragraphe 10
- Version du texte déclarée : 2022-08-02
- Date d'application de la règle : 2022-08-02
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02017R0565-20220802

**Extrait officiel**

> 10. Lorsqu’elle fournit à un client un service de conseil en investissement ou de gestion de portefeuille, une entreprise d’investissement s’abstient de lui faire une recommandation ou de prendre une décision de négociation portant sur des services ou instruments si aucun d’entre eux n’est adapté à ce client. Une entreprise d’investissement s’abstient de recommander ou de décider de négocier des instruments financiers comme correspondant aux préférences d’un client ou d’un client potentiel en matière de durabilité, si tel n’est pas le cas. Elle explique au client ou client potentiel les motifs

**SUPPORTING PROVISION**

- **Article 54 — phrase recopiée du texte officiel**
  - Pourquoi elle est potentiellement pertinente : porte une structure limitante repérée par l'analyse : « Lorsqu'une entreprise d'investissement fournit un service d'investissement à un client professionnel, elle est autorisée à présumer qu'en ce qui concerne les produits, les transactions et les services pour lesquels il es »
  - Relation avec la règle : limite peut-être la portée de l'obligation énoncée
- **Article 54 — phrase recopiée du texte officiel**
  - Pourquoi elle est potentiellement pertinente : porte une structure limitante repérée par l'analyse : « Lorsque ce service d'investissement consiste en la fourniture d'un conseil en investissement à un client professionnel relevant de l'annexe II, section 1, de la directive 2014/65/UE, l'entreprise d'investissement est aut »
  - Relation avec la règle : limite peut-être la portée de l'obligation énoncée
- **Article 54 — phrase recopiée du texte officiel**
  - Pourquoi elle est potentiellement pertinente : porte une structure limitante repérée par l'analyse : « Lorsqu'une entreprise d'investissement fournit un service qui implique de mener périodiquement des évaluations de l'adéquation et d'établir les rapports connexes, les rapports établis après la mise en place du service in »
  - Relation avec la règle : limite peut-être la portée de l'obligation énoncée
- **Article 25 de Règlement délégué (UE) 2017/565 modifié**
  - Pourquoi elle est potentiellement pertinente : Article 54 y renvoie explicitement
  - Relation avec la règle : peut conditionner l'application de la règle
- **Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié de Règlement délégué (UE) 2017/565, modifié par le règlement délégué (UE) 2021/1253 (règle MIFID-R-006)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Préférences en matière de durabilité »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement délégué (UE) 2017/565 modifié entier dans sa version applicable au 2022-08-02, et non le seul Article 54 : une absence ne s'établit pas sur un extrait

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 54 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : exemption, conditions_cumulatives, regime_particulier, renvoi
- 3 phrase(s) limitante(s) recopiée(s) telles quelles du texte officiel
- renvois relevés dans l'article : 25
- recherche d'exceptions à ce jour : « identified_and_incorporated »
- statut réglementaire « in_force », en vigueur depuis le 2022-08-02
- affirmation négative non vérifiée : « Le texte fixerait une proportion minimale chiffrée d'investissements durables à proposer. »
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Établir qu'une disposition est absente suppose d'avoir couvert un périmètre et de l'attester : l'analyse peut dire qu'elle n'a pas trouvé, jamais que cela n'existe pas.

**NEUTRAL_LEGAL_QUESTION**

> « Le texte fixerait une proportion minimale chiffrée d'investissements durables à proposer. » : cette disposition est-elle absente de Règlement délégué (UE) 2017/565 modifié dans le périmètre indiqué, ou une disposition la porte-t-elle ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'affirmation passe « present_contrary » : la fausse prémisse prévue était vraie, l'item l'aurait comptée à l'envers, et la règle est reversionnée (v4, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — l'affirmation passe « verified_absent » avec `searched_in` : elle peut porter une fausse prémisse opposable

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### SFDR — 6 règle(s)

#### `SFDR-R-001` — SFDR · P0 · `review_cluster_id` : `CL-32019R2088-ART2-EXC`

**RULE**

- ID : `SFDR-R-001`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 2 du règlement (UE) 2019/2088 définit l'« investissement durable » comme un investissement dans une activité économique qui contribue à un objectif environnemental ou social, sous réserve que cet investissement ne cause de préjudice important à aucun de ces objectifs et que les sociétés bénéficiaires appliquent des pratiques de bonne gouvernance.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 2
- Paragraphe : point 17
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**Extrait officiel**

> 17) investissement durable : un investissement dans une activité économique qui contribue à un objectif environnemental, mesuré par exemple au moyen d’indicateurs clés en matière d’utilisation efficace des ressources concernant l’utilisation d’énergie, d’énergies renouvelables, de matières premières, d’eau et de terres, en matière de production de déchets et d’émissions de gaz à effet de serre ou en matière d’effets sur la biodiversité et l’économie circulaire, ou un investissement dans une activité économique qui contribue à un objectif social, en particulier un investissement qui contribue à

**SUPPORTING PROVISION**

- **Article 8 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits promouvant des caractéristiques environnementales ou sociales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 9 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits ayant l'investissement durable pour objectif »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 3 de Règlement (UE) 2020/852 (Taxonomie) (règle TAXO-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Critères d'une activité économique durable sur le plan environnemental »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2019/2088 (SFDR) entier au 2020-01-01 — articles autres que Article 2 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 2 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : definition_necessaire
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2021-03-10
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à SFDR-R-001 existe-t-elle dans le périmètre indiqué — Article 2, un autre article de Règlement (UE) 2019/2088 (SFDR), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `SFDR-R-003` — SFDR · P0 · `review_cluster_id` : `CL-32019R2088-ART4-NEG`

**RULE**

- ID : `SFDR-R-003`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `NEGATIVE_CLAIM_UNRESOLVED` (affirmations_negatives_resolues)

**CURRENT STATEMENT**

> L'article 4 impose de publier une déclaration sur les politiques de diligence raisonnable relatives aux principales incidences négatives des décisions d'investissement sur les facteurs de durabilité, ou d'expliquer clairement pourquoi ces incidences ne sont pas prises en compte.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 4
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**Extrait officiel**

> Article 4 Transparence des incidences négatives en matière de durabilité au niveau des entités 1. Les acteurs des marchés financiers publient et tiennent à jour sur leur site internet: a) lorsqu’ils prennent en compte les principales incidences négatives des décisions d’investissement sur les facteurs de durabilité, une déclaration sur les politiques de diligence raisonnable en ce qui concerne ces incidences, compte tenu de leur taille, de la nature et de l’étendue de leurs activités ainsi que des types de produits financiers qu’ils mettent à disposition; ou b) lorsqu’ils ne prennent pas en co

**SUPPORTING PROVISION**

- **Article 7 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-006)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Incidences négatives au niveau du produit »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2019/2088 (SFDR) entier dans sa version applicable au 2020-01-01, et non le seul Article 4 : une absence ne s'établit pas sur un extrait

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 4 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : derogation, conditions_cumulatives, delai
- recherche d'exceptions à ce jour : « identified_and_incorporated »
- statut réglementaire « in_force », en vigueur depuis le 2021-03-10
- affirmation négative non vérifiée : « L'article 4 fixerait lui-même un seuil chiffré d'encours déclenchant la prise en compte des PAI. »
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Établir qu'une disposition est absente suppose d'avoir couvert un périmètre et de l'attester : l'analyse peut dire qu'elle n'a pas trouvé, jamais que cela n'existe pas.

**NEUTRAL_LEGAL_QUESTION**

> « L'article 4 fixerait lui-même un seuil chiffré d'encours déclenchant la prise en compte des PAI. » : cette disposition est-elle absente de Règlement (UE) 2019/2088 (SFDR) dans le périmètre indiqué, ou une disposition la porte-t-elle ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `TEMPORAL_UNRESOLVED` (temporalite_etablie) — temporalité « IN_FORCE » non établie : la date d'appréciation de la question serait arbitraire
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'affirmation passe « present_contrary » : la fausse prémisse prévue était vraie, l'item l'aurait comptée à l'envers, et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — l'affirmation passe « verified_absent » avec `searched_in` : elle peut porter une fausse prémisse opposable

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `SFDR-R-005` — SFDR · P0 · `review_cluster_id` : `CL-32019R2088-ART6-EXC`

**RULE**

- ID : `SFDR-R-005`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 6 impose d'inclure dans les informations précontractuelles la manière dont les risques en matière de durabilité sont intégrés dans les décisions d'investissement et les résultats de l'évaluation de leurs incidences probables sur le rendement, ou d'expliquer pourquoi ces risques sont jugés non pertinents.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 6
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**Extrait officiel**

> Article 6 Transparence de l’intégration des risques en matière de durabilité 1. Dans les informations précontractuelles publiées, les acteurs des marchés financiers décrivent: a) la manière dont les risques en matière de durabilité sont intégrés dans leurs décisions d’investissement; et b) les résultats de l’évaluation des incidences probables des risques en matière de durabilité sur le rendement des produits financiers qu’ils mettent à disposition. Lorsque les acteurs des marchés financiers estiment que les risques en matière de durabilité ne sont pas pertinents, les descriptions visées au pr

**SUPPORTING PROVISION**

- **Article 8 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits promouvant des caractéristiques environnementales ou sociales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 9 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits ayant l'investissement durable pour objectif »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2019/2088 (SFDR) entier au 2020-01-01 — articles autres que Article 6 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 6 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2021-03-10
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à SFDR-R-005 existe-t-elle dans le périmètre indiqué — Article 6, un autre article de Règlement (UE) 2019/2088 (SFDR), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `SFDR-R-008` — SFDR · P0 · `review_cluster_id` : `CL-32019R2088-ART8-NEG`

**RULE**

- ID : `SFDR-R-008`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `NEGATIVE_CLAIM_UNRESOLVED` (affirmations_negatives_resolues)

**CURRENT STATEMENT**

> L'article 8 vise les produits financiers qui promeuvent, entre autres caractéristiques, des caractéristiques environnementales ou sociales, et impose de préciser dans l'information précontractuelle comment ces caractéristiques sont respectées.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 8
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**Extrait officiel**

> Article 8 Transparence de la promotion des caractéristiques environnementales ou sociales dans les informations précontractuelles publiées 1. Lorsqu’un produit financier promeut, entre autres caractéristiques, des caractéristiques environnementales ou sociales, ou une combinaison de ces caractéristiques, pour autant que les sociétés dans lesquelles les investissements sont réalisés appliquent des pratiques de bonne gouvernance, les informations à publier en vertu de l’article 6, paragraphes 1 et 3, comprennent: a) des informations sur la manière dont ces caractéristiques sont respectées; b) si

**SUPPORTING PROVISION**

- **Article 2 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Définition de l'investissement durable »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 9 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits ayant l'investissement durable pour objectif »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Position-recommandation DOC-2020-03 de Position-recommandation AMF DOC-2020-03 (règle AMF-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Condition d'une communication centrale sur les critères extra-financiers »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2019/2088 (SFDR) entier dans sa version applicable au 2020-01-01, et non le seul Article 8 : une absence ne s'établit pas sur un extrait

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 8 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2021-03-10
- affirmation négative non vérifiée : « L'article 8 imposerait une part minimale d'investissements durables. »
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Établir qu'une disposition est absente suppose d'avoir couvert un périmètre et de l'attester : l'analyse peut dire qu'elle n'a pas trouvé, jamais que cela n'existe pas.

**NEUTRAL_LEGAL_QUESTION**

> « L'article 8 imposerait une part minimale d'investissements durables. » : cette disposition est-elle absente de Règlement (UE) 2019/2088 (SFDR) dans le périmètre indiqué, ou une disposition la porte-t-elle ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `EXCEPTION_UNRESOLVED` (exceptions_recherchees) — recherche d'exceptions « requires_human_review » : une question construite ici testerait la règle comme un absolu
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'affirmation passe « present_contrary » : la fausse prémisse prévue était vraie, l'item l'aurait comptée à l'envers, et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — l'affirmation passe « verified_absent » avec `searched_in` : elle peut porter une fausse prémisse opposable

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `TAXO-R-001` — SFDR · P0 · `review_cluster_id` : `CL-32020R0852-ART3-EXC`

**RULE**

- ID : `TAXO-R-001`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 3 du règlement (UE) 2020/852 énonce les critères cumulatifs permettant de qualifier une activité économique de durable sur le plan environnemental : contribution substantielle à un ou plusieurs objectifs environnementaux, absence de préjudice important aux autres objectifs, respect de garanties minimales et conformité aux critères d'examen technique.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2020/852 (Taxonomie)
- Article : Article 3
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-07-12
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32020R0852

**Extrait officiel**

> Article 3 Critères de durabilité environnementale des activités économiques Aux fins de la détermination du degré de durabilité environnementale d’un investissement, une activité économique est considérée comme durable sur le plan environnemental si cette activité économique: a) contribue substantiellement à un ou plusieurs des objectifs environnementaux énoncés à l’article 9, conformément aux articles 10 à 16; b) ne cause de préjudice important à aucun des objectifs environnementaux énoncés à l’article 9, conformément à l’article 17; c) est exercée dans le respect des garanties minimales prév

**SUPPORTING PROVISION**

- **Article 2 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Définition de l'investissement durable »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 9 de Règlement (UE) 2020/852 (Taxonomie) (règle TAXO-R-002)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Les six objectifs environnementaux »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Articles 17 et 18 de Règlement (UE) 2020/852 (Taxonomie) (règle TAXO-R-003)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Préjudice important et garanties minimales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2020/852 (Taxonomie) entier au 2020-01-01 — articles autres que Article 3 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 3 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2020-07-12
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à TAXO-R-001 existe-t-elle dans le périmètre indiqué — Article 3, un autre article de Règlement (UE) 2020/852 (Taxonomie), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `TAXO-R-003` — SFDR · P0 · `review_cluster_id` : `CL-32020R0852-ART17-ET-18-EXC`

**RULE**

- ID : `TAXO-R-003`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 17 du règlement (UE) 2020/852 définit ce qu'il faut entendre par préjudice important causé aux objectifs environnementaux, et l'article 18 fixe les garanties minimales que doit respecter l'activité, en référence à des standards internationaux en matière de droits humains et de travail.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2020/852 (Taxonomie)
- Article : Articles 17 et 18
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-07-12
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32020R0852

**Extrait officiel**

> Article 17 Préjudice important causé aux objectifs environnementaux 1. Aux fins de l’article 3, point b), compte tenu du cycle de vie des produits et des services fournis par une activité économique, y compris des éléments de fait tirés d’analyses du cycle de vie existantes, cette activité économique est considérée comme causant un préjudice important: a) à l’atténuation du changement climatique, lorsque cette activité génère des émissions importantes de gaz à effet de serre; b) à l’adaptation au changement climatique, lorsque cette activité entraîne une augmentation des incidences négatives d

**SUPPORTING PROVISION**

- **Article 2 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Définition de l'investissement durable »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 3 de Règlement (UE) 2020/852 (Taxonomie) (règle TAXO-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Critères d'une activité économique durable sur le plan environnemental »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2020/852 (Taxonomie) entier au 2020-01-01 — articles autres que Articles 17 et 18 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Articles 17 et 18 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2020-07-12
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à TAXO-R-003 existe-t-elle dans le périmètre indiqué — Articles 17 et 18, un autre article de Règlement (UE) 2020/852 (Taxonomie), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

## P1 — REVIEW REQUIRED (16 règles)

| ID | Domaine | Ancrage | Blocage | Proposition mécanique | Regroupement |
|---|---|---|---|---|---|
| `AMF-R-002` | AMF | Position-recommandation DOC-2020-03 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` |
| `AMF-R-003` | AMF | Position-recommandation DOC-2020-03 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC` |
| `AMF-R-005` | AMF | Règlement général | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-RGA-ARTREGLEMENT-GENERAL-SRC` |
| `DORA-R-004` | DORA | Articles 8 à 13 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32022R2554-ART8-A-13-EXC` |
| `DORA-R-006` | DORA | Article 17 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32022R2554-ART17-EXC` |
| `DORA-R-012` | DORA | Article 31 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32022R2554-ART31-EXC` |
| `DORA-R-013` | DORA | Article 64 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32022R2554-ART64-EXC` |
| `LCBFT-R-004` | LCBFT | Article L.561-5-1 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-5-1-SRC` |
| `LCBFT-R-011` | LCBFT | Article L.561-12 | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-CMF-ARTL-561-12-SRC` |
| `LCBFT-R-013` | LCBFT | Ensemble de la directive | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-32015L0849-ARTENSEMBLE-DE-LA-DIRECTIVE-SRC` |
| `MIFID-R-005` | MIFID | Article 25 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32014L0065-ART25-EXC` |
| `SFDR-R-002` | SFDR | Article 3 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32019R2088-ART3-EXC` |
| `SFDR-R-006` | SFDR | Article 7 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32019R2088-ART7-EXC` |
| `SFDR-R-011` | SFDR | Article 11 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32019R2088-ART11-EXC` |
| `SFDR-R-014` | SFDR | Ensemble du règlement délégué | `SOURCE_INCOMPLETE` | `INSUFFICIENT_SOURCE` | `CL-32022R1288-ARTENSEMBLE-DU-REGLEMENT-DE-SRC` |
| `TAXO-R-002` | SFDR | Article 9 | `EXCEPTION_UNRESOLVED` | `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` | `CL-32020R0852-ART9-EXC` |

### AMF — 3 règle(s)

#### `AMF-R-002` — AMF · P1 · `review_cluster_id` : `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC`

**RULE**

- ID : `AMF-R-002`
- Domaine : AMF
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> La position-recommandation AMF DOC-2020-03 distingue plusieurs niveaux de communication sur la prise en compte de critères extra-financiers, du niveau central au niveau réduit, selon le degré d'engagement du produit.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- **Article 19 de Position-recommandation AMF DOC-2020-03**
  - Pourquoi elle est potentiellement pertinente : Position-recommandation DOC-2020-03 y renvoie explicitement
  - Relation avec la règle : peut conditionner l'application de la règle
- **Article 13 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-013)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Cohérence des communications publicitaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Position-recommandation AMF DOC-2020-03 entier au 2020-01-01 — articles autres que Position-recommandation DOC-2020-03 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Position-recommandation DOC-2020-03 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : seuil, renvoi
- renvois relevés dans l'article : 19
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2020-03-11
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à AMF-R-002 existe-t-elle dans le périmètre indiqué — Position-recommandation DOC-2020-03, un autre article de Position-recommandation AMF DOC-2020-03, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `AMF-R-003` — AMF · P1 · `review_cluster_id` : `CL-DOC-2020-03-ARTPOSITION-RECOMMANDATION-EXC`

**RULE**

- ID : `AMF-R-003`
- Domaine : AMF
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> La position-recommandation AMF DOC-2020-03 traite de la cohérence entre la dénomination d'un placement collectif faisant référence à des considérations extra-financières et la réalité de l'approche mise en œuvre.

**PRIMARY SOURCE**

- Texte : Position-recommandation AMF DOC-2020-03
- Article : Position-recommandation DOC-2020-03
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-03-11
- URL : https://www.amf-france.org/fr/reglementation/doctrine/doc-2020-03

**SUPPORTING PROVISION**

- **Article 19 de Position-recommandation AMF DOC-2020-03**
  - Pourquoi elle est potentiellement pertinente : Position-recommandation DOC-2020-03 y renvoie explicitement
  - Relation avec la règle : peut conditionner l'application de la règle

**Périmètre à examiner** — Position-recommandation AMF DOC-2020-03 entier au 2020-01-01 — articles autres que Position-recommandation DOC-2020-03 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Position-recommandation DOC-2020-03 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : seuil, renvoi
- renvois relevés dans l'article : 19
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2020-03-11
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à AMF-R-003 existe-t-elle dans le périmètre indiqué — Position-recommandation DOC-2020-03, un autre article de Position-recommandation AMF DOC-2020-03, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `AMF-R-005` — AMF · P1 · `review_cluster_id` : `CL-RGA-ARTREGLEMENT-GENERAL-SRC`

**RULE**

- ID : `AMF-R-005`
- Domaine : AMF
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> Le règlement général de l'AMF fixe les règles applicables aux acteurs et aux produits relevant de la compétence de l'Autorité des marchés financiers, et se distingue de la doctrine, qui explicite l'interprétation retenue par l'Autorité.

**PRIMARY SOURCE**

- Texte : Règlement général de l'AMF
- Article : Règlement général
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2004-11-24
- URL : https://www.amf-france.org/fr/reglementation/reglement-general

**SUPPORTING PROVISION**

- **Position-recommandation DOC-2020-03 de Position-recommandation AMF DOC-2020-03 (règle AMF-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Condition d'une communication centrale sur les critères extra-financiers »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement général de Règlement général de l'AMF, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2004-11-24
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Règlement général de Règlement général de l'AMF, consulté hors de cet environnement, soutient-il l'énoncé de AMF-R-005, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### DORA — 4 règle(s)

#### `DORA-R-004` — DORA · P1 · `review_cluster_id` : `CL-32022R2554-ART8-A-13-EXC`

**RULE**

- ID : `DORA-R-004`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> Les articles 8 à 13 du règlement (UE) 2022/2554 organisent les fonctions du cadre de gestion du risque TIC : identification des fonctions et actifs, protection et prévention, détection des activités anormales, réponse et rétablissement, politiques de sauvegarde et de restauration, apprentissage et évolution.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Articles 8 à 13
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 8 Identification 1. Aux fins du cadre de gestion du risque lié aux TIC visé à l’article 6, paragraphe 1, les entités financières identifient, classent et documentent de manière adéquate toutes les fonctions métiers , tous les rôles et toutes les responsabilités s’appuyant sur les TIC, les actifs informationnels et les actifs de TIC qui soutiennent ces fonctions, ainsi que leurs rôles et dépendances en ce qui concerne le risque lié aux TIC. Les entités financières examinent si nécessaire, et au moins une fois par an, le caractère adéquat de cette classification et de toute documentation

**SUPPORTING PROVISION**

- **Article 6 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-003)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Cadre de gestion du risque lié aux TIC »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier au 2020-01-01 — articles autres que Articles 8 à 13 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Articles 8 à 13 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai, regime_particulier
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à DORA-R-004 existe-t-elle dans le périmètre indiqué — Articles 8 à 13, un autre article de Règlement (UE) 2022/2554 (DORA), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `DORA-R-006` — DORA · P1 · `review_cluster_id` : `CL-32022R2554-ART17-EXC`

**RULE**

- ID : `DORA-R-006`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 17 impose de définir, d'établir et de mettre en œuvre un processus de gestion des incidents liés aux TIC permettant de les détecter, de les gérer et de les notifier.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 17
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 17 Processus de gestion des incidents liés aux TIC 1. Les entités financières définissent, établissent et mettent en œuvre un processus de gestion des incidents liés aux TIC afin de détecter, de gérer et de notifier les incidents liés aux TIC. 2. Les entités financières enregistrent tous les incidents liés aux TIC et les cybermenaces importantes. Les entités financières mettent en place des procédures et des processus adéquats pour assurer une surveillance, un traitement et un suivi cohérents et intégrés des incidents liés aux TIC, pour veiller à ce que les causes originelles soient id

**SUPPORTING PROVISION**

- **Article 18 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-007)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Classification des incidents et détermination du caractère majeur »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 19 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Notification des incidents majeurs à l'autorité compétente »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier au 2020-01-01 — articles autres que Article 17 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 17 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à DORA-R-006 existe-t-elle dans le périmètre indiqué — Article 17, un autre article de Règlement (UE) 2022/2554 (DORA), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `DORA-R-012` — DORA · P1 · `review_cluster_id` : `CL-32022R2554-ART31-EXC`

**RULE**

- ID : `DORA-R-012`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 31 organise la désignation, par les autorités européennes de surveillance, des prestataires tiers de services TIC critiques, et les soumet à un cadre de supervision spécifique.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 31
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 31 Désignation de prestataires tiers critiques de services TIC 1. Les AES, agissant par l’intermédiaire du comité mixte et sur recommandation du forum de supervision établi conformément à l’article 32, paragraphe 1: a) désignent les prestataires tiers de services TIC qui sont critiques pour les entités financières, à l’issue d’une évaluation tenant compte des critères précisés au paragraphe 2; b) désignent comme superviseur principal pour chaque prestataire tiers critique de services TIC l’AES responsable, conformément aux règlements (UE) n o 1093/2010, (UE) n o 1094/2010 ou (UE) n o 1

**SUPPORTING PROVISION**

- **Article 28 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-010)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Registre d'information des accords contractuels TIC »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 30 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-011)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Dispositions contractuelles essentielles avec les prestataires TIC »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier au 2020-01-01 — articles autres que Article 31 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 31 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à DORA-R-012 existe-t-elle dans le périmètre indiqué — Article 31, un autre article de Règlement (UE) 2022/2554 (DORA), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `DORA-R-013` — DORA · P1 · `review_cluster_id` : `CL-32022R2554-ART64-EXC`

**RULE**

- ID : `DORA-R-013`
- Domaine : DORA
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> Le règlement (UE) 2022/2554 est entré en vigueur après sa publication et s'applique à compter du 17 janvier 2025.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2022/2554 (DORA)
- Article : Article 64
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2025-01-17
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R2554

**Extrait officiel**

> Article 64 Entrée en vigueur et application Le présent règlement entre en vigueur le vingtième jour suivant celui de sa publication au Journal officiel de l’Union européenne . Il s’applique à partir du 17 janvier 2025 .

**SUPPORTING PROVISION**

- **Article 2 de Règlement (UE) 2022/2554 (DORA) (règle DORA-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Entités financières couvertes par DORA »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2022/2554 (DORA) entier au 2020-01-01 — articles autres que Article 64 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 64 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2025-01-17
- extrait officiel disponible (219 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à DORA-R-013 existe-t-elle dans le périmètre indiqué — Article 64, un autre article de Règlement (UE) 2022/2554 (DORA), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `TEMPORAL_UNRESOLVED` (temporalite_etablie) — temporalité « IN_FORCE » non établie : la date d'appréciation de la question serait arbitraire
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### LCBFT — 3 règle(s)

#### `LCBFT-R-004` — LCBFT · P1 · `review_cluster_id` : `CL-CMF-ARTL-561-5-1-SRC`

**RULE**

- ID : `LCBFT-R-004`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-5-1 du code monétaire et financier impose de recueillir, avant d'entrer en relation d'affaires, les informations relatives à l'objet et à la nature de cette relation et tout élément d'information pertinent.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-5-1
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article L.561-5 de Code monétaire et financier (règle LCBFT-R-003)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Identification et vérification avant l'entrée en relation d'affaires »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-5-1 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-5-1 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-004, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-011` — LCBFT · P1 · `review_cluster_id` : `CL-CMF-ARTL-561-12-SRC`

**RULE**

- ID : `LCBFT-R-011`
- Domaine : LCBFT
- Version : v1
- Statut courant : `draft`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> L'article L.561-12 du code monétaire et financier impose de conserver pendant cinq ans à compter de la clôture des comptes ou de la cessation des relations les documents et informations relatifs à l'identité des clients et aux opérations effectuées.

**PRIMARY SOURCE**

- Texte : Code monétaire et financier
- Article : Article L.561-12
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-02-14
- URL : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**SUPPORTING PROVISION**

- **Article 16 de Directive 2014/65/UE (MIFID II) (règle MIFID-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Conservation des enregistrements »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Article L.561-12 de Code monétaire et financier, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- aucune consultation signée de la source primaire
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2020-02-14
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Article L.561-12 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-011, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « draft » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `LCBFT-R-013` — LCBFT · P1 · `review_cluster_id` : `CL-32015L0849-ARTENSEMBLE-DE-LA-DIRECTIVE-SRC`

**RULE**

- ID : `LCBFT-R-013`
- Domaine : LCBFT
- Version : v1
- Statut courant : `source_checked`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> La directive (UE) 2015/849, modifiée notamment par la directive (UE) 2018/843, constitue le cadre européen relatif à la prévention de l'utilisation du système financier aux fins du blanchiment de capitaux et du financement du terrorisme, transposé en droit français dans le code monétaire et financier.

**PRIMARY SOURCE**

- Texte : Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843
- Article : Ensemble de la directive
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2015-06-05
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32015L0849

**SUPPORTING PROVISION**

- **Article L.561-2 de Code monétaire et financier (règle LCBFT-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Périmètre des personnes assujetties »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Ensemble de la directive de Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843, consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2015-06-05
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Ensemble de la directive de Directive (UE) 2015/849, modifiée par la directive (UE) 2018/843, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-013, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### MIFID — 1 règle(s)

#### `MIFID-R-005` — MIFID · P1 · `review_cluster_id` : `CL-32014L0065-ART25-EXC`

**RULE**

- ID : `MIFID-R-005`
- Domaine : MIFID
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 25 impose, en cas de conseil en investissement à un client de détail, de lui fournir une déclaration d'adéquation précisant le conseil fourni et la manière dont il répond à ses préférences, objectifs et autres caractéristiques.

**PRIMARY SOURCE**

- Texte : Directive 2014/65/UE (MIFID II)
- Article : Article 25
- Paragraphe : paragraphe 6
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2018-01-03
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32014L0065

**Extrait officiel**

> 6. L’entreprise d’investissement fournit au client des rapports adéquats sur le service qu’elle dispense sur un support durable. Ces rapports incluent des communications périodiques aux clients, en fonction du type et de la complexité des instruments financiers concernés ainsi que de la nature du service fourni aux clients, et comprennent, lorsqu’il y a lieu, les coûts liés aux transactions effectuées et aux services fournis au nom du client. Lorsqu’elle fournit des conseils en investissement, l’entreprise d’investissement remet au client, avant que la transaction ne soit effectuée, une déclar

**SUPPORTING PROVISION**

- **Directive 2014/65/UE (MIFID II) — hors Article 25**
  - Pourquoi elle est potentiellement pertinente : l'analyse n'a repéré aucune disposition candidate dans l'article cité : il n'y a donc rien à confirmer, seulement un périmètre à balayer
  - Relation avec la règle : périmètre de recherche, aucune disposition désignée

**Périmètre à examiner** — Directive 2014/65/UE (MIFID II) entier au 2020-01-01 — articles autres que Article 25 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 25 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai, regime_particulier, definition_necessaire
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2018-01-03
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à MIFID-R-005 existe-t-elle dans le périmètre indiqué — Article 25, un autre article de Directive 2014/65/UE (MIFID II), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

### SFDR — 5 règle(s)

#### `SFDR-R-002` — SFDR · P1 · `review_cluster_id` : `CL-32019R2088-ART3-EXC`

**RULE**

- ID : `SFDR-R-002`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 3 impose aux acteurs des marchés financiers et aux conseillers financiers de publier sur leur site internet des informations sur leurs politiques d'intégration des risques en matière de durabilité dans leur processus de décision d'investissement ou de conseil.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 3
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**Extrait officiel**

> Article 3 Transparence des politiques relatives aux risques en matière de durabilité 1. Les acteurs des marchés financiers publient sur leur site internet des informations concernant leurs politiques relatives à l’intégration des risques en matière de durabilité dans leur processus de prise de décision en matière d’investissement. 2. Les conseillers financiers publient sur leur site internet des informations concernant leurs politiques relatives à l’intégration des risques en matière de durabilité dans leurs conseils en investissement ou leurs conseils en assurance.

**SUPPORTING PROVISION**

- **Article 6 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-005)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Intégration des risques de durabilité dans l'information précontractuelle »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2019/2088 (SFDR) entier au 2020-01-01 — articles autres que Article 3 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 3 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2021-03-10
- extrait officiel disponible (572 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à SFDR-R-002 existe-t-elle dans le périmètre indiqué — Article 3, un autre article de Règlement (UE) 2019/2088 (SFDR), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `SFDR-R-006` — SFDR · P1 · `review_cluster_id` : `CL-32019R2088-ART7-EXC`

**RULE**

- ID : `SFDR-R-006`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 7 impose d'indiquer dans l'information précontractuelle si un produit financier prend en compte les principales incidences négatives sur les facteurs de durabilité, et le cas échéant comment.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 7
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**Extrait officiel**

> Article 7 Transparence des incidences négatives en matière de durabilité au niveau des produits financiers 1. Au plus tard le 30 décembre 2022 , pour chaque produit financier, lorsqu’un acteur des marchés financiers applique l’article 4, paragraphe 1, point a), ou l’article 4, paragraphe 3 ou 4, les informations à publier visées à l’article 6, paragraphe 3, comprennent ce qui suit: a) une explication claire et motivée indiquant si un produit financier prend en compte les principales incidences négatives sur les facteurs de durabilité et, dans l’affirmative, la manière dont il le fait; b) une d

**SUPPORTING PROVISION**

- **Article 4 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-003)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Transparence des principales incidences négatives au niveau de l'entité »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2019/2088 (SFDR) entier au 2020-01-01 — articles autres que Article 7 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 7 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : delai
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2021-03-10
- extrait officiel disponible (600 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à SFDR-R-006 existe-t-elle dans le périmètre indiqué — Article 7, un autre article de Règlement (UE) 2019/2088 (SFDR), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `TEMPORAL_UNRESOLVED` (temporalite_etablie) — temporalité « IN_FORCE » non établie : la date d'appréciation de la question serait arbitraire
- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `SFDR-R-011` — SFDR · P1 · `review_cluster_id` : `CL-32019R2088-ART11-EXC`

**RULE**

- ID : `SFDR-R-011`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 11 impose d'inclure dans les rapports périodiques des produits relevant des articles 8 et 9 une description de la mesure dans laquelle les caractéristiques environnementales ou sociales sont respectées, ou de l'incidence globale du produit en matière de durabilité.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2019/2088 (SFDR)
- Article : Article 11
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2021-03-10
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32019R2088

**Extrait officiel**

> Article 11 Transparence de la promotion des caractéristiques environnementales ou sociales et des investissements durables dans les rapports périodiques 1. Lorsque les acteurs des marchés financiers mettent à disposition un produit financier visé à l’article 8, paragraphe 1, ou à l’article 9, paragraphe 1, 2 ou 3, ils décrivent notamment dans les rapports périodiques: a) pour un produit financier visé à l’article 8, paragraphe 1, la mesure dans laquelle les caractéristiques environnementales ou sociales sont respectées; b) pour un produit financier visé à l’article 9, paragraphe 1, 2 ou 3: i)

**SUPPORTING PROVISION**

- **Article 8 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits promouvant des caractéristiques environnementales ou sociales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 9 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits ayant l'investissement durable pour objectif »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2019/2088 (SFDR) entier au 2020-01-01 — articles autres que Article 11 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 11 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- structures juridiques repérées dans l'article : conditions_cumulatives, delai
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2021-03-10
- extrait officiel disponible (599 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à SFDR-R-011 existe-t-elle dans le périmètre indiqué — Article 11, un autre article de Règlement (UE) 2019/2088 (SFDR), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `SFDR-R-014` — SFDR · P1 · `review_cluster_id` : `CL-32022R1288-ARTENSEMBLE-DU-REGLEMENT-DE-SRC`

**RULE**

- ID : `SFDR-R-014`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `SOURCE_INCOMPLETE` (source_primaire_verifiee)

**CURRENT STATEMENT**

> Le règlement délégué (UE) 2022/1288 précise le contenu, les méthodes et la présentation des informations SFDR, et fixe des modèles obligatoires en annexe pour les informations précontractuelles et périodiques des produits relevant des articles 8 et 9.

**PRIMARY SOURCE**

- Texte : Règlement délégué (UE) 2022/1288 (RTS SFDR)
- Article : Ensemble du règlement délégué
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2023-01-01
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022R1288

**SUPPORTING PROVISION**

- **Article 8 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-008)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits promouvant des caractéristiques environnementales ou sociales »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier
- **Article 9 de Règlement (UE) 2019/2088 (SFDR) (règle SFDR-R-009)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Produits ayant l'investissement durable pour objectif »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Ensemble du règlement délégué de Règlement délégué (UE) 2022/1288 (RTS SFDR), consulté hors de cet environnement d'exécution (le texte primaire n'y est pas atteignable)

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- le texte de l'article n'a pas pu être lu : aucun critère n'a été coché
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « unknown »
- statut réglementaire « in_force », en vigueur depuis le 2023-01-01
- aucun extrait officiel disponible : le texte n'a pas été récupéré

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Le texte primaire n'est pas atteignable depuis cet environnement : aucune vérification mécanique n'est possible, et la consultation doit être faite puis signée par un humain.

**NEUTRAL_LEGAL_QUESTION**

> Le texte de Ensemble du règlement délégué de Règlement délégué (UE) 2022/1288 (RTS SFDR), consulté hors de cet environnement, soutient-il l'énoncé de SFDR-R-014, ou l'énoncé vise-t-il une autre disposition ?

**mechanical_proposal** — `INSUFFICIENT_SOURCE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — le texte consulté contredit l'énoncé : la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner
- `if_no_exception` — le texte consulté soutient l'énoncé : la consultation est portée au dossier de vérification et la règle peut progresser

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

#### `TAXO-R-002` — SFDR · P1 · `review_cluster_id` : `CL-32020R0852-ART9-EXC`

**RULE**

- ID : `TAXO-R-002`
- Domaine : SFDR
- Version : v1
- Statut courant : `source_checked`
- Blocage : `EXCEPTION_UNRESOLVED` (exceptions_recherchees)

**CURRENT STATEMENT**

> L'article 9 du règlement (UE) 2020/852 énumère six objectifs environnementaux : atténuation du changement climatique, adaptation au changement climatique, utilisation durable et protection des ressources aquatiques et marines, transition vers une économie circulaire, prévention et réduction de la pollution, et protection et restauration de la biodiversité et des écosystèmes.

**PRIMARY SOURCE**

- Texte : Règlement (UE) 2020/852 (Taxonomie)
- Article : Article 9
- Paragraphe : —
- Version du texte déclarée : 2020-01-01
- Date d'application de la règle : 2020-07-12
- URL : https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32020R0852

**Extrait officiel**

> Article 9 Objectifs environnementaux Aux fins du présent règlement, constituent des objectifs environnementaux: a) l’atténuation du changement climatique; b) l’adaptation au changement climatique; c) l’utilisation durable et la protection des ressources aquatiques et marines; d) la transition vers une économie circulaire; e) la prévention et la réduction de la pollution; f) la protection et la restauration de la biodiversité et des écosystèmes.

**SUPPORTING PROVISION**

- **Article 3 de Règlement (UE) 2020/852 (Taxonomie) (règle TAXO-R-001)**
  - Pourquoi elle est potentiellement pertinente : règle rattachée du Rulebook, sur une autre disposition : « Critères d'une activité économique durable sur le plan environnemental »
  - Relation avec la règle : régime voisin, susceptible de poser une exception ou un cas particulier

**Périmètre à examiner** — Règlement (UE) 2020/852 (Taxonomie) entier au 2020-01-01 — articles autres que Article 9 compris — ainsi que les actes délégués et d'exécution pris sur son fondement

**TEXTUAL_FACTS** — ce qui est explicitement écrit dans les sources

- source consultée et signée le 2026-08-30 par amirRbh (méthode : primary_text_fetched)
- « Article 9 » existe dans l'acte cité
- le vocabulaire de l'énoncé se retrouve dans l'article
- aucune structure juridique repérée dans l'article cité
- recherche d'exceptions à ce jour : « requires_human_review »
- statut réglementaire « in_force », en vigueur depuis le 2020-07-12
- extrait officiel disponible (448 caractères)

**INTERPRETIVE_QUESTION** — ce qui demande un arbitrage humain

Déterminer si une disposition limitante vise l'obligation énoncée ici ou une obligation voisine relève d'une lecture juridique : l'analyse ne compare que des formes de phrase et du vocabulaire, et ne sait pas à quelle obligation une dérogation se rapporte.

**NEUTRAL_LEGAL_QUESTION**

> Une dérogation, exclusion, exemption ou condition applicable à TAXO-R-002 existe-t-elle dans le périmètre indiqué — Article 9, un autre article de Règlement (UE) 2020/852 (Taxonomie), ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**mechanical_proposal** — `NO_EXCEPTION_IDENTIFIED_IN_REVIEWED_SCOPE` (aide à la lecture, jamais une conclusion juridique)

**Autres blocages de la règle** — trancher celui-ci ne les lève pas

- `HUMAN_REVIEW_REQUIRED` (statut_non_validated) — règle en « source_checked » : seul « validated » ancre une famille

**IMPACT SUR LE BENCHMARK**

- `if_exception_exists` — l'exception est recopiée dans `exceptions`, `exceptions_status` passe à « identified_and_incorporated » et la règle est reversionnée (v2, `supersedes` nommant la version remplacée) et tout item déjà ancré dessus est à reversionner ; un item qui testerait la règle comme un absolu compterait en erreur un modèle qui mentionne la dérogation
- `if_no_exception` — `exceptions_status` passe à « none_identified » avec le périmètre attesté ; la règle peut alors porter des items qui la testent sans réserve, et `gold_ready` est recalculé — il ne devient pas vrai pour autant

**DÉCISION DU RELECTEUR** — à remplir dans `data/verification/dossier-adjudication.csv`

| Champ | Valeur |
|---|---|
| `reviewer_decision` | |
| `reviewer_name` | |
| `review_date` | |
| `source_scope` | |
| `review_notes` | |

---

## Traçabilité

Une décision rendue s'enregistre au registre append-only
`data/verification/rulebook-ledger.json`, qui se rejoue dans l'ordre. Une
décision n'écrase jamais la précédente : elle s'y ajoute.

| Champ du registre | Provenance |
|---|---|
| `rule_id` | le dossier |
| `previous_status`, `previous_version` | l'état du Rulebook au moment de la décision |
| `decision` | `reviewer_decision` |
| `new_version` | avancée seulement si l'énoncé ou les exceptions changent |
| `reviewer`, `review_date` | `reviewer_name`, `review_date` |
| `review_notes` | `review_notes` |
| `source_scope` | `source_scope` — obligatoire pour `NONE_IDENTIFIED` |

### Après chaque décision appliquée

Une décision humaine ne rend pas une règle exploitable. Elle lève un
blocage ; les seuils se recalculent, ils ne se déduisent pas :

1. revalider la règle (`finreg-bench rulebook qc`) ;
2. recalculer la gold-readiness (`rulebook completude`) ;
3. recalculer la family-readiness (`rulebook readiness`) ;
4. rejouer les contrôles d'intégrité, registre compris ;
5. n'écrire au registre qu'ensuite.

Une règle ne passe `validated` qu'après décision humaine, et seulement si
`exception_status` vaut `NONE_IDENTIFIED` — périmètre attesté — ou
`IDENTIFIED_AND_INCORPORATED` — exceptions recopiées. Un `gold_ready` ne
s'accorde jamais par le fait qu'une décision a été rendue.

