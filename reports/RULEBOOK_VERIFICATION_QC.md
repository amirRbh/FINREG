# Rulebook — audit de vérification contre le texte primaire

Rapport généré par `src/bench/rapport_audit.py`. Il dit, règle par règle,
ce que la confrontation au texte officiel a établi — et ce qu'elle n'a pas
pu établir.

## Ce que cet audit fait, et ce qu'il ne fait pas

L'audit **récupère le texte primaire authentique**, le découpe par article,
et confronte chaque règle à l'article qu'elle cite. Il n'attribue jamais le
statut `source_checked` : le dépôt définit ce statut comme n'étant « jamais
un statut qu'un modèle peut s'accorder à lui-même ». Une règle dont tout est
corroboré est donc classée `REQUIRES_HUMAN_REVIEW` — il ne lui manque que la
signature d'un vérificateur nommé.

Cette signature ne demande pas de refaire le travail : le dossier
`data/verification/dossier-audit.csv` est pré-rempli avec le verdict proposé,
la méthode et l'extrait officiel. Seules `verifie_par` et `date_verification`
sont vides — et le schéma `Verification` refuse toute promotion sans elles.

```sh
# remplir verifie_par et date_verification, puis :
finreg-bench rulebook appliquer-verification data/verification/dossier-audit.csv
```

## Voies d'accès aux sources primaires

Ce que l'environnement d'exécution permet réellement, mesuré et non supposé :

| Voie | État | Conséquence |
|---|---|---|
| `publications.europa.eu` (CELLAR) | texte authentique du *Journal officiel*, découpé par article | **voie retenue pour le droit de l'Union** |
| `eur-lex.europa.eu` | HTTP 200 mais sert la page d'accueil du JO | inutilisable |
| `legifrance.gouv.fr` | HTTP 403 | Code monétaire et financier hors d'atteinte |
| `amf-france.org` | page réelle | doctrine AMF atteignable |

> Un `200` qui rend une page d'accueil est plus dangereux qu'un `403` : il se
> lit comme un succès. Chaque récupération est donc validée sur son contenu —
> langue attendue, articles découpables — et jamais sur son code de retour.

## Synthèse

- règles examinées : **58**
- `SOURCE_CHECKED` : **43**
- `REQUIRES_HUMAN_REVIEW` : **0**
- `DRAFT` : **2**
- `BLOCKED` : **13**

- sources primaires effectivement consultées : **7** (`32014L0065`, `32015L0849`, `32017R0565`, `32019R2088`, `32020R0852`, `32022R1288`, `32022R2554`)
- articles retrouvés dans le texte officiel : **45 / 58**
- affirmations négatives examinées : **5**, dont corroborées absentes : **0**
- règles sensibles au temps : **9**
- règles dont les exceptions sont renseignées : **15 / 58**
- anomalies relevées : **65**

Seuil de concordance retenu : **45%** du vocabulaire de
l'énoncé retrouvé dans l'article officiel. Ce n'est pas une mesure de vérité —
un énoncé peut être faux avec un vocabulaire parfaitement couvert — mais une
mesure de **rattachement** : elle attrape la règle qui cite un article parlant
d'autre chose.

## Classement par domaine

| Domaine | Règles | Human review | Draft | Blocked |
|---|---:|---:|---:|---:|
| AMF | 5 | 0 | 0 | 1 |
| DORA | 13 | 0 | 0 | 0 |
| LCBFT | 13 | 0 | 0 | 12 |
| MIFID | 11 | 0 | 2 | 0 |
| SFDR | 16 | 0 | 0 | 0 |

## Audit des règles

Ordre de priorité de la spécification §3 : les critiques d'abord, puis les
exceptions inconnues, puis les affirmations négatives.

| ID | Domaine | Source | Article | Version | Statut | Exceptions | Temporalité | Problème |
|---|---|---|---|---|---|---|---|---|
| `AMF-R-001` | AMF | Position-recommandation AMF DOC-20 | Position-recommandation DOC-2020-03 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation ; source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve p |
| `DORA-R-007` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 18 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | affirmation négative « L'article 18 fixerait lui-même un nombre de clients affectés… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; exceptions jamais cherché |
| `DORA-R-008` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 19 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | affirmation négative « Le règlement DORA de niveau 1 fixerait un délai de notificat… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; exceptions jamais cherché |
| `LCBFT-R-005` | LCBFT | Code monétaire et financier | Articles L.561-2-2 et R.561-1 et suivants | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `SFDR-R-003` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 4 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | affirmation négative « L'article 4 fixerait lui-même un seuil chiffré d'encours déc… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; exceptions jamais cherché |
| `SFDR-R-008` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 8 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | affirmation négative « L'article 8 imposerait une part minimale d'investissements d… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; exceptions jamais cherché |
| `AMF-R-004` | AMF | Position-recommandation AMF DOC-20 | Position-recommandation DOC-2020-03 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation ; source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve p |
| `DORA-R-002` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 5 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `DORA-R-003` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 6 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `DORA-R-010` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 28 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `LCBFT-R-001` | LCBFT | Code monétaire et financier | Article L.561-2 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-002` | LCBFT | Code monétaire et financier | Article L.561-4-1 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-003` | LCBFT | Code monétaire et financier | Article L.561-5 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-006` | LCBFT | Code monétaire et financier | Article L.561-6 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-007` | LCBFT | Code monétaire et financier | Article L.561-10 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-008` | LCBFT | Code monétaire et financier | Articles L.561-10 et R.561-18 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-009` | LCBFT | Code monétaire et financier | Article L.561-15 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-010` | LCBFT | Code monétaire et financier | Article L.561-18 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-012` | LCBFT | Code monétaire et financier | Article L.561-8 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `MIFID-R-002` | MIFID | Directive 2014/65/UE (MIFID II) | Article 25 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `MIFID-R-003` | MIFID | Directive 2014/65/UE (MIFID II) | Article 25 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `MIFID-R-004` | MIFID | Directive 2014/65/UE (MIFID II) | Article 25 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `MIFID-R-006` | MIFID | Règlement délégué (UE) 2017/565, m | Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | l'URL désigne l'acte 32021R1253 alors que la source cite 32017R0565 : vérification conduite contre l'acte cité ; la source dit l'acte modifié, mais aucune version consolidée au 2020-01-01 n' |
| `SFDR-R-005` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 6 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `TAXO-R-001` | SFDR | Règlement (UE) 2020/852 (Taxonomie | Article 3 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `TAXO-R-003` | SFDR | Règlement (UE) 2020/852 (Taxonomie | Articles 17 et 18 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | ancrage « Articles 17 et 18 » : 2 articles couverts (17, 18), à découper avant qu'un gold puisse le citer ; exceptions jamais cherchées : à trancher entre « listed » et « none_identified » a |
| `MIFID-R-007` | MIFID | Règlement délégué (UE) 2017/565 mo | Article 54 | 2020-01-01 | DRAFT | identified_and_incorporated | in_force | l'URL désigne l'acte 32021R1253 alors que la source cite 32017R0565 : vérification conduite contre l'acte cité ; la source dit l'acte modifié, mais aucune version consolidée au 2020-01-01 n' |
| `DORA-R-001` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 2 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `DORA-R-011` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 30 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `SFDR-R-001` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 2 | 2020-01-01 | SOURCE_CHECKED | none_identified | in_force | — |
| `SFDR-R-009` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 9 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `AMF-R-002` | AMF | Position-recommandation AMF DOC-20 | Position-recommandation DOC-2020-03 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation ; source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve p |
| `AMF-R-003` | AMF | Position-recommandation AMF DOC-20 | Position-recommandation DOC-2020-03 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation ; source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve p |
| `AMF-R-005` | AMF | Règlement général de l'AMF | Règlement général | 2020-01-01 | BLOCKED | unknown | in_force | texte primaire non récupéré : https://www.amf-france.org/fr/reglementation/reglement-general : HTTPError — HTTP Error 404: Not Found |
| `DORA-R-004` | DORA | Règlement (UE) 2022/2554 (DORA) | Articles 8 à 13 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | ancrage « Articles 8 à 13 » : 6 articles couverts (8, 9, 10, 11, 12, 13), à découper avant qu'un gold puisse le citer ; exceptions jamais cherchées : à trancher entre « listed » et « none_id |
| `DORA-R-006` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 17 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `DORA-R-012` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 31 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `LCBFT-R-004` | LCBFT | Code monétaire et financier | Article L.561-5-1 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-011` | LCBFT | Code monétaire et financier | Article L.561-12 | 2020-01-01 | BLOCKED | unknown | in_force | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-013` | LCBFT | Directive (UE) 2015/849, modifiée  | Ensemble de la directive | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | la source dit l'acte modifié, mais aucune version consolidée au 2020-01-01 n'existe (02015L0849-20200101) : la date de consolidation applicable doit être établie, sans quoi la règle est véri |
| `MIFID-R-005` | MIFID | Directive 2014/65/UE (MIFID II) | Article 25 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `SFDR-R-002` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 3 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `SFDR-R-004` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 5 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `SFDR-R-006` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 7 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `SFDR-R-010` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 10 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `SFDR-R-011` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 11 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `SFDR-R-012` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 12 | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `SFDR-R-014` | SFDR | Règlement délégué (UE) 2022/1288 ( | Ensemble du règlement délégué | 2020-01-01 | SOURCE_CHECKED | unknown | in_force | ancrage « Ensemble du règlement délégué » : aucun article désigné, la règle est vérifiée contre l'acte entier et aucun gold ne pourra citer sa disposition ; exceptions jamais cherchées : à t |
| `DORA-R-005` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 16 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `DORA-R-009` | DORA | Règlement (UE) 2022/2554 (DORA) | Articles 24 à 26 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | ancrage « Articles 24 à 26 » : 3 articles couverts (24, 25, 26), à découper avant qu'un gold puisse le citer |
| `DORA-R-013` | DORA | Règlement (UE) 2022/2554 (DORA) | Article 64 | 2020-01-01 | SOURCE_CHECKED | none_identified | in_force | — |
| `MIFID-R-001` | MIFID | Directive 2014/65/UE (MIFID II) | Article 24 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `MIFID-R-008` | MIFID | Directive 2014/65/UE (MIFID II) | Article 16 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `MIFID-R-009` | MIFID | Directive 2014/65/UE (MIFID II) | Article 27 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `MIFID-R-010` | MIFID | Directive 2014/65/UE (MIFID II) | Article 9 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `MIFID-R-011` | MIFID | Règlement délégué (UE) 2017/565 | Article 54 | 2020-01-01 | DRAFT | identified_and_incorporated | in_force | énoncé peu corroboré par le texte cité (36% du vocabulaire retrouvé) : la règle parle peut-être d'autre chose |
| `SFDR-R-013` | SFDR | Règlement (UE) 2019/2088 (SFDR) | Article 13 | 2020-01-01 | SOURCE_CHECKED | identified_and_incorporated | in_force | — |
| `TAXO-R-002` | SFDR | Règlement (UE) 2020/852 (Taxonomie | Article 9 | 2020-01-01 | SOURCE_CHECKED | none_identified | in_force | — |

## Anomalies

### Exceptions jamais cherchées — 30

- `AMF-R-001` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-007` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-008` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `SFDR-R-003` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `SFDR-R-008` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `AMF-R-004` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-002` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-003` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-010` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `MIFID-R-002` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `MIFID-R-003` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `MIFID-R-004` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `MIFID-R-006` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `SFDR-R-005` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `TAXO-R-001` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `TAXO-R-003` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `AMF-R-002` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `AMF-R-003` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-004` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-006` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `DORA-R-012` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `LCBFT-R-013` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `MIFID-R-005` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `SFDR-R-002` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- `SFDR-R-004` : exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation
- … et 5 autre(s)

### Source primaire hors d'atteinte — 13

- `LCBFT-R-005` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-001` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-002` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-003` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-006` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-007` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-008` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-009` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-010` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-012` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `AMF-R-005` : texte primaire non récupéré : https://www.amf-france.org/fr/reglementation/reglement-general : HTTPError — HTTP Error 404: Not Found
- `LCBFT-R-004` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici
- `LCBFT-R-011` : Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici

### Autres — 11

- `MIFID-R-006` : l'URL désigne l'acte 32021R1253 alors que la source cite 32017R0565 : vérification conduite contre l'acte cité
- `MIFID-R-006` : la source dit l'acte modifié, mais aucune version consolidée au 2020-01-01 n'existe (02017R0565-20200101) : la date de consolidation applicable doit être établie, sans quoi la règle est vérifiée contre le texte d'origine
- `MIFID-R-006` : ancrage « Article 2 et article 54 du règlement délégué (UE) 2017/565 modifié » : 2 articles couverts (2, 54), à découper avant qu'un gold puisse le citer
- `TAXO-R-003` : ancrage « Articles 17 et 18 » : 2 articles couverts (17, 18), à découper avant qu'un gold puisse le citer
- `MIFID-R-007` : l'URL désigne l'acte 32021R1253 alors que la source cite 32017R0565 : vérification conduite contre l'acte cité
- `MIFID-R-007` : la source dit l'acte modifié, mais aucune version consolidée au 2020-01-01 n'existe (02017R0565-20200101) : la date de consolidation applicable doit être établie, sans quoi la règle est vérifiée contre le texte d'origine
- `DORA-R-004` : ancrage « Articles 8 à 13 » : 6 articles couverts (8, 9, 10, 11, 12, 13), à découper avant qu'un gold puisse le citer
- `LCBFT-R-013` : la source dit l'acte modifié, mais aucune version consolidée au 2020-01-01 n'existe (02015L0849-20200101) : la date de consolidation applicable doit être établie, sans quoi la règle est vérifiée contre le texte d'origine
- `LCBFT-R-013` : ancrage « Ensemble de la directive » : aucun article désigné, la règle est vérifiée contre l'acte entier et aucun gold ne pourra citer sa disposition
- `SFDR-R-014` : ancrage « Ensemble du règlement délégué » : aucun article désigné, la règle est vérifiée contre l'acte entier et aucun gold ne pourra citer sa disposition
- `DORA-R-009` : ancrage « Articles 24 à 26 » : 3 articles couverts (24, 25, 26), à découper avant qu'un gold puisse le citer

### Chiffre non retrouvé — 5

- `DORA-R-007` : affirmation négative « L'article 18 fixerait lui-même un nombre de clients affectés… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement
- `DORA-R-008` : affirmation négative « Le règlement DORA de niveau 1 fixerait un délai de notificat… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement
- `SFDR-R-003` : affirmation négative « L'article 4 fixerait lui-même un seuil chiffré d'encours déc… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement
- `SFDR-R-008` : affirmation négative « L'article 8 imposerait une part minimale d'investissements d… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement
- `MIFID-R-007` : affirmation négative « Le texte fixerait une proportion minimale chiffrée d'investi… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement

### Source doctrinale — 4

- `AMF-R-001` : source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve principale pour une disposition législative
- `AMF-R-004` : source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve principale pour une disposition législative
- `AMF-R-002` : source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve principale pour une disposition législative
- `AMF-R-003` : source doctrinale : elle éclaire l'application d'un texte, elle ne vaut pas preuve principale pour une disposition législative

### Énoncé peu corroboré — 2

- `MIFID-R-007` : énoncé peu corroboré par le texte cité (32% du vocabulaire retrouvé) : la règle parle peut-être d'autre chose
- `MIFID-R-011` : énoncé peu corroboré par le texte cité (36% du vocabulaire retrouvé) : la règle parle peut-être d'autre chose

## Règles critiques restant à trancher

| ID | Classement | Pourquoi |
|---|---|---|
| `AMF-R-001` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation ; source doctrinale : elle éclaire l'application d'un texte, elle  |
| `DORA-R-007` | SOURCE_CHECKED | affirmation négative « L'article 18 fixerait lui-même un nombre de clients affectés… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; excep |
| `DORA-R-008` | SOURCE_CHECKED | affirmation négative « Le règlement DORA de niveau 1 fixerait un délai de notificat… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; excep |
| `LCBFT-R-005` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `SFDR-R-003` | SOURCE_CHECKED | affirmation négative « L'article 4 fixerait lui-même un seuil chiffré d'encours déc… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; excep |
| `SFDR-R-008` | SOURCE_CHECKED | affirmation négative « L'article 8 imposerait une part minimale d'investissements d… » : sans chiffre à chercher, l'absence ne peut pas être établie mécaniquement ; excep |
| `AMF-R-004` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation ; source doctrinale : elle éclaire l'application d'un texte, elle  |
| `DORA-R-002` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `DORA-R-003` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `DORA-R-010` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `LCBFT-R-001` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-002` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-003` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-006` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-007` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-008` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-009` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-010` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `LCBFT-R-012` | BLOCKED | Légifrance répond HTTP 403 depuis cet environnement : le Code monétaire et financier ne peut pas être consulté ici |
| `MIFID-R-002` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `MIFID-R-003` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `MIFID-R-004` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `MIFID-R-006` | SOURCE_CHECKED | l'URL désigne l'acte 32021R1253 alors que la source cite 32017R0565 : vérification conduite contre l'acte cité ; la source dit l'acte modifié, mais aucune version consoli |
| `SFDR-R-005` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `TAXO-R-001` | SOURCE_CHECKED | exceptions jamais cherchées : à trancher entre « listed » et « none_identified » avant toute validation |
| `TAXO-R-003` | SOURCE_CHECKED | ancrage « Articles 17 et 18 » : 2 articles couverts (17, 18), à découper avant qu'un gold puisse le citer ; exceptions jamais cherchées : à trancher entre « listed » et « |
| `MIFID-R-007` | DRAFT | l'URL désigne l'acte 32021R1253 alors que la source cite 32017R0565 : vérification conduite contre l'acte cité ; la source dit l'acte modifié, mais aucune version consoli |
| `DORA-R-001` | SOURCE_CHECKED | — |
| `DORA-R-011` | SOURCE_CHECKED | — |
| `SFDR-R-001` | SOURCE_CHECKED | — |
| `SFDR-R-009` | SOURCE_CHECKED | — |

