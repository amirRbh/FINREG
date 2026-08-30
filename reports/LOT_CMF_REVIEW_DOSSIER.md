# LOT-CMF — dossier de consultation

12 règles adossées à **Code monétaire et financier**, dont le texte primaire n'a pas
pu être lu depuis l'environnement d'exécution.

> **Aucun de ces textes n'a été consulté.** Ce document n'affirme rien de leur
> contenu : il énumère ce qu'il faudra y vérifier. Aucun statut ne bouge, et
> aucune décision n'est pré-remplie — y compris par défaut.

Établi le 2026-08-30.

## L'empêchement

> Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici

Le tunnel réseau s'établit, puis la source répond `403` : le refus vient du
site, pas de l'environnement d'exécution. Ouvrir davantage la politique réseau
n'y changerait rien. Restent l'API PISTE avec des identifiants, ou une
consultation manuelle.

## Deux décisions par règle, jamais une

Chaque fiche pose **deux** questions distinctes, et confirmer la première ne
répond pas à la seconde :

1. **l'énoncé** est-il soutenu par la disposition citée, telle qu'elle est
   rédigée dans la version applicable ?
2. **les exceptions** : cette disposition, ou une autre du même code, la
   limite-t-elle ?

Une règle confirmée dont les exceptions restent `unknown` ne devient pas
`validated` : elle se testerait comme un absolu qu'elle n'est peut-être pas.

## Comment rendre une décision

Les décisions se portent dans `data/verification/dossier-lot-cmf.csv` — une ligne par règle, colonnes
de décision vides à ce jour. Le vocabulaire de la revue s'y traduit ainsi :

| Décision | Ce qu'elle affirme | Ce qu'il faut écrire |
|---|---|---|
| `NONE_IDENTIFIED` | aucune dérogation dans le périmètre examiné | `verdict=confirme` · `exceptions_statut=none_identified` · `perimetre_exceptions` **obligatoire** |
| `IDENTIFIED_AND_INCORPORATED` | des dérogations existent et sont recopiées dans la règle | `verdict=confirme` · `exceptions_statut=identified_and_incorporated` · `exceptions_constatees` (extraits officiels) · `perimetre_exceptions` · `version_date_constatee` |
| `REQUIRES_CORRECTION` | le texte dit autre chose : l'énoncé est rectifié | `verdict=corrige` · `enonce_corrige` **obligatoire** — la règle est reversionnée, `supersedes` nomme la version remplacée |
| `REJECTED` | le texte contredit la règle, ou la disposition citée n'existe pas | `verdict=refute` · `commentaire` **obligatoire** — la règle reste `draft`, rien n'est promu |
| `(consultée sans conclure)` | texte introuvable, version incertaine : la consultation est consignée | `verdict=non_verifiable` · `commentaire` — la règle reste `draft` |

**Toute décision doit être signée** : `verifie_par` et `date_verification`.
Le schéma refuse une promotion sans elles — ce n'est pas une consigne, c'est
une validation. Il refuse aussi un `none_identified` sans
`perimetre_exceptions` : « je n'ai pas trouvé » ne vaut pas « il n'y en a
pas », et une recherche automatique infructueuse ne fait jamais passer
`unknown` à `none_identified`.

Une ligne laissée vide n'est pas une décision : elle est ignorée. Un dossier
dont une ligne est irrecevable ne s'applique pas à moitié.

Colonnes à remplir : `verdict`, `methode`, `verifie_par`, `date_verification`, `statut_vise`, `enonce_corrige`, `article_corrige`, `paragraphe_corrige`, `url_corrigee`, `version_date_constatee`, `exceptions_statut`, `exceptions_constatees`, `perimetre_exceptions`, `gold_ready`, `gold_ready_motif`, `commentaire`.

## Les règles du lot

### `LCBFT-R-001` — Périmètre des personnes assujetties

**Énoncé actuel (v1)**

> L'article L.561-2 du code monétaire et financier énumère les personnes assujetties aux obligations de lutte contre le blanchiment de capitaux et le financement du terrorisme.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-2
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `SCOPE` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-2 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-001, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-001 existe-t-elle dans le périmètre indiqué — Article L.561-2, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-2, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- étendre l'assujettissement par analogie à une activité non énumérée
- confondre assujettissement LCB-FT et agrément prudentiel

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-2` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-002` — Classification des risques

**Énoncé actuel (v1)**

> L'article L.561-4-1 du code monétaire et financier impose aux personnes assujetties de définir et de mettre en place des dispositifs d'identification et d'évaluation des risques de blanchiment et de financement du terrorisme auxquels elles sont exposées, et d'élaborer une classification de ces risques.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-4-1
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `OBLIGATION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-4-1 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-002, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-002 existe-t-elle dans le périmètre indiqué — Article L.561-4-1, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-4-1, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- appliquer une vigilance uniforme sans classification préalable
- confondre classification des risques et scoring client

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-4-1` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-003` — Identification et vérification avant l'entrée en relation d'affaires

**Énoncé actuel (v1)**

> L'article L.561-5 du code monétaire et financier impose d'identifier le client et, le cas échéant, le bénéficiaire effectif, et de vérifier ces éléments d'identification avant d'entrer en relation d'affaires.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-5
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `OBLIGATION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-5 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-003, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-003 existe-t-elle dans le périmètre indiqué — Article L.561-5, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-5, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- traiter la vérification différée comme le régime de droit commun
- confondre identification et vérification de l'identité
- omettre le bénéficiaire effectif

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-5` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-005` — Identification du bénéficiaire effectif

**Énoncé actuel (v1)**

> Le code monétaire et financier impose d'identifier et de vérifier l'identité du bénéficiaire effectif de la relation d'affaires, les modalités et critères de détermination étant fixés par sa partie réglementaire.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Articles L.561-2-2 et R.561-1 et suivants
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `DEFINITION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Articles L.561-2-2 et R.561-1 et suivants de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-005, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-005 existe-t-elle dans le périmètre indiqué — Articles L.561-2-2 et R.561-1 et suivants, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Articles L.561-2-2 et R.561-1 et suivants, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Affirmations négatives portées par la règle**

- « La partie législative du code monétaire et financier fixerait elle-même le seuil de détention du bénéficiaire effectif. » — à confirmer ou à contredire sur le texte

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- citer un seuil de détention en l'attribuant à un article législatif
- confondre bénéficiaire effectif et représentant légal
- s'arrêter au premier niveau de détention

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Articles L.561-2-2 et R.561-1 et suivants` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-006` — Vigilance constante pendant toute la relation d'affaires

**Énoncé actuel (v1)**

> L'article L.561-6 du code monétaire et financier impose d'exercer une vigilance constante pendant toute la durée de la relation d'affaires et de procéder à un examen attentif des opérations effectuées, en veillant à ce qu'elles soient cohérentes avec la connaissance actualisée du client.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-6
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `OBLIGATION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-6 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-006, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-006 existe-t-elle dans le périmètre indiqué — Article L.561-6, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-6, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- traiter la vigilance comme un contrôle limité à l'entrée en relation
- confondre vigilance constante et vigilance renforcée

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-6` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-007` — Mesures de vigilance renforcée

**Énoncé actuel (v1)**

> L'article L.561-10 du code monétaire et financier énumère les situations dans lesquelles les personnes assujetties appliquent des mesures de vigilance complémentaires à l'égard de leur client.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-10
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `OBLIGATION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-10 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-007, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-007 existe-t-elle dans le périmètre indiqué — Article L.561-10, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-10, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- confondre vigilance renforcée et refus d'entrer en relation
- croire que la vigilance renforcée est laissée à la seule appréciation de l'établissement

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-10` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-008` — Traitement des personnes politiquement exposées

**Énoncé actuel (v1)**

> Le code monétaire et financier soumet les relations d'affaires avec des personnes politiquement exposées à des mesures de vigilance complémentaires, la définition et le périmètre de ces personnes étant précisés par sa partie réglementaire.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Articles L.561-10 et R.561-18
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `CLASSIFICATION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Articles L.561-10 et R.561-18 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-008, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-008 existe-t-elle dans le périmètre indiqué — Articles L.561-10 et R.561-18, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Articles L.561-10 et R.561-18, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- déduire du statut de PPE une interdiction d'entrer en relation
- déduire du statut de PPE une obligation de déclaration de soupçon
- oublier les membres de la famille et les proches associés

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Articles L.561-10 et R.561-18` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-009` — Déclaration de soupçon à Tracfin

**Énoncé actuel (v1)**

> L'article L.561-15 du code monétaire et financier impose de déclarer au service Tracfin les sommes ou opérations portant sur des sommes dont les personnes assujetties savent, soupçonnent ou ont de bonnes raisons de soupçonner qu'elles proviennent d'une infraction passible d'une peine privative de liberté supérieure à un an ou sont liées au financement du terrorisme.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-15
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `OBLIGATION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-15 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-009, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-009 existe-t-elle dans le périmètre indiqué — Article L.561-15, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-15, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- exiger une certitude ou une preuve avant de déclarer
- croire que le déclarant doit qualifier l'infraction sous-jacente
- confondre déclaration de soupçon et information du client

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-15` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-010` — Interdiction d'informer le client de la déclaration

**Énoncé actuel (v1)**

> Le code monétaire et financier interdit de porter à la connaissance du client ou de tiers l'existence et le contenu d'une déclaration de soupçon adressée à Tracfin, ainsi que les suites qui lui sont données.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-18
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `PROHIBITION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-18 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-010, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-010 existe-t-elle dans le périmètre indiqué — Article L.561-18, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-18, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- croire qu'un client peut être informé au motif de la transparence
- confondre interdiction de divulgation et secret professionnel général

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-18` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-012` — Refus ou cessation de la relation d'affaires

**Énoncé actuel (v1)**

> L'article L.561-8 du code monétaire et financier dispose que, lorsque la personne assujettie n'est pas en mesure d'identifier son client ou d'obtenir les informations sur l'objet et la nature de la relation d'affaires, elle n'exécute aucune opération et n'établit ni ne poursuit aucune relation d'affaires.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-8
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `PROHIBITION` · priorité `CRITICAL` · revue P0

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-8 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-012, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-012 existe-t-elle dans le périmètre indiqué — Article L.561-8, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-8, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- déduire mécaniquement une déclaration de soupçon de l'impossibilité d'identifier
- croire qu'une opération peut être exécutée en attendant les pièces

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-8` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-004` — Recueil d'informations sur l'objet et la nature de la relation d'affaires

**Énoncé actuel (v1)**

> L'article L.561-5-1 du code monétaire et financier impose de recueillir, avant d'entrer en relation d'affaires, les informations relatives à l'objet et à la nature de cette relation et tout élément d'information pertinent.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-5-1
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `OBLIGATION` · priorité `HIGH` · revue P1

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-5-1 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-004, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-004 existe-t-elle dans le périmètre indiqué — Article L.561-5-1, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-5-1, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- réduire la connaissance client à la collecte d'une pièce d'identité

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-5-1` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

### `LCBFT-R-011` — Conservation des documents et informations

**Énoncé actuel (v1)**

> L'article L.561-12 du code monétaire et financier impose de conserver pendant cinq ans à compter de la clôture des comptes ou de la cessation des relations les documents et informations relatifs à l'identité des clients et aux opérations effectuées.

**Source, article, disposition attendue**

- Texte : Code monétaire et financier
- Article : Article L.561-12
- Disposition attendue : article entier — aucun paragraphe désigné
- Emplacement déclaré : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177
- Type de règle : `RECORD_KEEPING` · priorité `HIGH` · revue P1

**Version / date pertinente**

- Version déclarée dans la règle : 2020-01-01
- Règle applicable depuis le 2020-02-14
- Régime : CMF_LCBFT · statut réglementaire `in_force`
- La version à lire est celle applicable à la date ci-dessus ; si la
  consolidation consultée diffère, c'est elle qu'il faut porter au dossier
  (`version_date_constatee`).

**Questions exactes à trancher**

1. Le texte de Article L.561-12 de Code monétaire et financier, consulté hors de cet environnement, soutient-il l'énoncé de LCBFT-R-011, ou l'énoncé vise-t-il une autre disposition ?
2. Une dérogation, exclusion, exemption ou condition applicable à LCBFT-R-011 existe-t-elle dans le périmètre indiqué — Article L.561-12, un autre article de Code monétaire et financier, ou un acte pris sur son fondement — ou n'en existe-t-il aucune dans ce périmètre ?

**Exceptions à rechercher**

- état actuel : `unknown` — personne n'a cherché sur le texte, et aucune recherche automatique n'a pu avoir lieu ;
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à **cette** obligation ;
- dans Article L.561-12, mais aussi ailleurs dans l'acte et dans les textes pris pour son application — une dérogation s'écrit rarement dans l'article qu'elle limite ;
- périmètre à attester quelle que soit la conclusion.

**Confusions typiques déjà consignées** (à confirmer ou infirmer)

- faire courir le délai depuis la date de l'opération
- confondre ce délai avec les obligations de conservation MiFID II

**Ce qui constitue une preuve suffisante**

- le texte de la disposition dans sa version applicable, sa référence de publication, et la signature (verifie_par + date_verification) portée au dossier de vérification ;
- pour les exceptions : les phrases limitantes **recopiées telles quelles** du texte officiel — une exception reformulée est une exception interprétée ;
- pour une absence : le périmètre exact examiné (articles, acte, version), porté dans `perimetre_exceptions` ;
- méthode `primary_text_review`, avec `verifie_par` et `date_verification`.

**Décision actuellement manquante**

- **consultation de la source** : aucune. `Article L.561-12` n'a jamais été lu ; `verification_method` vaut `model_knowledge_unverified` et la règle reste `draft` ;
- **recherche d'exceptions** : aucune. `exceptions_status` vaut `unknown` ;
- ces deux décisions sont indépendantes, et aucune ne se déduit de l'autre.

---

