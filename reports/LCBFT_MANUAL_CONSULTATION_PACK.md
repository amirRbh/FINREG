# LCB-FT — pack de consultation manuelle

12 règles adossées au **Code monétaire et financier**, dont le
texte n'a pas pu être lu depuis l'environnement d'exécution.

> **Aucun de ces textes n'a été consulté.** Ce document n'affirme rien du
> contenu des articles cités : il énumère ce qu'il faudra y vérifier. Le
> statut des règles reste `draft` tant que personne n'a lu et signé.

Établi le 2026-08-30.

## L'empêchement

> Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici

Le tunnel réseau s'établit, puis le site répond `403` : le refus vient de la
source, pas de l'environnement. Ouvrir davantage la politique réseau n'y
changerait rien. Les voies restantes : l'API PISTE avec des identifiants, ou
une consultation manuelle.

## Ce qu'une consultation doit rapporter

Pour chaque article, et dans cet ordre :

1. le texte de la disposition **dans sa version applicable**, avec sa date de
   consolidation ;
2. la confirmation — ou l'infirmation — de l'énoncé de la règle ;
3. les dérogations, exclusions et exemptions applicables, **recopiées telles
   quelles** : une exception reformulée est une exception interprétée ;
4. les renvois vers d'autres articles dont l'application dépend ;
5. la signature : `verifie_par` et `date_verification` au dossier de
   vérification. Sans elle, aucune règle ne progresse.

## `LCBFT-R-001` — Périmètre des personnes assujetties

- **Article exact** : Article L.561-2
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-2 du code monétaire et financier énumère les personnes assujetties aux obligations de lutte contre le blanchiment de capitaux et le financement du terrorisme.

**À confirmer sur le texte**

- « Article L.561-2 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-002` — Classification des risques

- **Article exact** : Article L.561-4-1
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-4-1 du code monétaire et financier impose aux personnes assujetties de définir et de mettre en place des dispositifs d'identification et d'évaluation des risques de blanchiment et de financement du terrorisme auxquels elles sont exposées, et d'élaborer une classification de ces risques.

**À confirmer sur le texte**

- « Article L.561-4-1 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-003` — Identification et vérification avant l'entrée en relation d'affaires

- **Article exact** : Article L.561-5
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-5 du code monétaire et financier impose d'identifier le client et, le cas échéant, le bénéficiaire effectif, et de vérifier ces éléments d'identification avant d'entrer en relation d'affaires.

**À confirmer sur le texte**

- « Article L.561-5 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-005` — Identification du bénéficiaire effectif

- **Article exact** : Articles L.561-2-2 et R.561-1 et suivants
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> Le code monétaire et financier impose d'identifier et de vérifier l'identité du bénéficiaire effectif de la relation d'affaires, les modalités et critères de détermination étant fixés par sa partie réglementaire.

**À confirmer sur le texte**

- « Articles L.561-2-2 et R.561-1 et suivants » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Affirmations négatives à trancher**

- « La partie législative du code monétaire et financier fixerait elle-même le seuil de détention du bénéficiaire effectif. »

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-006` — Vigilance constante pendant toute la relation d'affaires

- **Article exact** : Article L.561-6
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-6 du code monétaire et financier impose d'exercer une vigilance constante pendant toute la durée de la relation d'affaires et de procéder à un examen attentif des opérations effectuées, en veillant à ce qu'elles soient cohérentes avec la connaissance actualisée du client.

**À confirmer sur le texte**

- « Article L.561-6 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-007` — Mesures de vigilance renforcée

- **Article exact** : Article L.561-10
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-10 du code monétaire et financier énumère les situations dans lesquelles les personnes assujetties appliquent des mesures de vigilance complémentaires à l'égard de leur client.

**À confirmer sur le texte**

- « Article L.561-10 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-008` — Traitement des personnes politiquement exposées

- **Article exact** : Articles L.561-10 et R.561-18
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> Le code monétaire et financier soumet les relations d'affaires avec des personnes politiquement exposées à des mesures de vigilance complémentaires, la définition et le périmètre de ces personnes étant précisés par sa partie réglementaire.

**À confirmer sur le texte**

- « Articles L.561-10 et R.561-18 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-009` — Déclaration de soupçon à Tracfin

- **Article exact** : Article L.561-15
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-15 du code monétaire et financier impose de déclarer au service Tracfin les sommes ou opérations portant sur des sommes dont les personnes assujetties savent, soupçonnent ou ont de bonnes raisons de soupçonner qu'elles proviennent d'une infraction passible d'une peine privative de liberté supérieure à un an ou sont liées au financement du terrorisme.

**À confirmer sur le texte**

- « Article L.561-15 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-010` — Interdiction d'informer le client de la déclaration

- **Article exact** : Article L.561-18
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> Le code monétaire et financier interdit de porter à la connaissance du client ou de tiers l'existence et le contenu d'une déclaration de soupçon adressée à Tracfin, ainsi que les suites qui lui sont données.

**À confirmer sur le texte**

- « Article L.561-18 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-012` — Refus ou cessation de la relation d'affaires

- **Article exact** : Article L.561-8
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-8 du code monétaire et financier dispose que, lorsque la personne assujettie n'est pas en mesure d'identifier son client ou d'obtenir les informations sur l'objet et la nature de la relation d'affaires, elle n'exécute aucune opération et n'établit ni ne poursuit aucune relation d'affaires.

**À confirmer sur le texte**

- « Article L.561-8 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-004` — Recueil d'informations sur l'objet et la nature de la relation d'affaires

- **Article exact** : Article L.561-5-1
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-5-1 du code monétaire et financier impose de recueillir, avant d'entrer en relation d'affaires, les informations relatives à l'objet et à la nature de cette relation et tout élément d'information pertinent.

**À confirmer sur le texte**

- « Article L.561-5-1 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

## `LCBFT-R-011` — Conservation des documents et informations

- **Article exact** : Article L.561-12
- **Disposition** : article entier — aucun paragraphe désigné
- **Version / date** : version déclarée 2020-01-01 ; règle applicable depuis le 2020-02-14
- **Statut actuel** : `draft` — inchangé par ce document
- **Emplacement déclaré** : https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000020196177

**Énoncé de la règle, tel qu'il est enregistré**

> L'article L.561-12 du code monétaire et financier impose de conserver pendant cinq ans à compter de la clôture des comptes ou de la cessation des relations les documents et informations relatifs à l'identité des clients et aux opérations effectuées.

**À confirmer sur le texte**

- « Article L.561-12 » porte-t-il bien cette obligation, dans ces termes ?
- l'énoncé en dit-il plus, ou moins, que le texte ?
- la version applicable à la date déclarée est-elle celle qui a été lue ?

**Exceptions à rechercher**

- recherche d'exceptions à ce jour : `unknown` — personne n'a cherché sur le texte
- dérogations, exclusions, exemptions, seuils et régimes particuliers applicables à cette obligation, dans l'article **et ailleurs dans le code** ;
- s'il n'y en a aucune, le périmètre examiné doit être attesté : « je n'ai pas trouvé » ne vaut pas « il n'y en a pas ».

**Résultat attendu pour pouvoir signer**

- verdict (`confirme` / `corrige` / `refute` / `non_verifiable`), méthode `primary_text_review`, `verifie_par` et `date_verification` ;
- si `corrige` : l'énoncé rectifié, qui fera avancer la version de la règle ;
- `exceptions_statut` motivé, avec le périmètre couvert.

---

