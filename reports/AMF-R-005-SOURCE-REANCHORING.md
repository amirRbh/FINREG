# `AMF-R-005` — réancrage de source

Établi le 2026-08-30. **Aucune URL n'est modifiée par ce document**,
et aucune n'y est proposée comme acquise : le réancrage passe par le circuit
de vérification, qui exige une consultation signée.

## La règle

- **Identifiant** : `AMF-R-005` — Portée du règlement général de l'AMF
- **Statut** : `draft` (inchangé)
- **Priorité de revue** : P1
- **Régime** : AMF_RG, applicable depuis le 2004-11-24

**Énoncé enregistré**

> Le règlement général de l'AMF fixe les règles applicables aux acteurs et aux produits relevant de la compétence de l'Autorité des marchés financiers, et se distingue de la doctrine, qui explicite l'interprétation retenue par l'Autorité.

## URL actuelle

> https://www.amf-france.org/fr/reglementation/reglement-general

## Pourquoi elle est invalide

> texte primaire non récupéré : https://www.amf-france.org/fr/reglementation/reglement-general : HTTPError — HTTP Error 404: Not Found

Ce n'est **pas** un refus d'accès : le serveur répond, et répond que la page
n'existe pas. Le site de l'AMF a réorganisé son espace réglementaire ;
l'URL enregistrée pointe vers un emplacement qui ne sert plus de document.
Une consultation depuis un autre environnement donnerait le même résultat —
il n'y a rien à y lire.

## Document recherché

- **Titre exact tel que la règle le cite** : Règlement général de l'AMF
- **Ancrage cité** : Règlement général
- **Version déclarée** : 2020-01-01
- **Nature** : acte réglementaire homologué par arrêté, consolidé et publié
  par l'Autorité des marchés financiers ; il se distingue de la doctrine, que
  la règle mentionne précisément pour l'en distinguer.

## Emplacement probable

L'espace réglementaire du site de l'AMF (`amf-france.org`) reste joignable :
la doctrine y a été récupérée pour d'autres règles. Le règlement général y
est publié, mais **son emplacement courant n'a pas été constaté** : les deux
chemins essayés rendent 404. Le relecteur doit donc établir l'emplacement,
pas le supposer — et c'est l'emplacement constaté, non celui-ci, qui sera
porté au dossier.

Deux voies à considérer, dans cet ordre :

1. la version consolidée publiée par l'AMF elle-même, qui fait foi ;
2. à défaut, le texte homologué tel que publié au *Journal officiel*, qui
   permet d'ancrer un article daté.

## Méthode de réancrage

1. constater l'emplacement du document et sa version consolidée ;
2. vérifier que l'ancrage cité — « Règlement général » — y existe réellement ; l'audit relève déjà que
   cet ancrage ne désigne aucun article précis, et qu'aucun gold ne pourrait
   citer sa disposition en l'état ;
3. porter au dossier de vérification : URL constatée, version, verdict,
   `verifie_par`, `date_verification` ;
4. appliquer le dossier (`finreg-bench rulebook appliquer-verification`) — la
   correction fait avancer la version de la règle et `supersedes` nomme celle
   qu'elle remplace ;
5. rejouer l'audit, la complétude et l'exploitabilité.

## Impact sur la règle

- **Blocage principal** : `SOURCE_INCOMPLETE` — DOCUMENT_INTROUVABLE
- **Action** : `SOURCE_REANCHORING`
- **Après réancrage** : `draft` → `source_checked` si la consultation est signée. Les blocages que le texte révélera ne sont pas connus avant lecture : l'audit les fera apparaître, ils ne se devinent pas ici
- **Ancrage à découper** : « Règlement général » couvre l'acte entier. Même
  réancrée, la règle ne portera pas de gold tant qu'elle ne citera pas un
  article précis — le réancrage lève l'accès, pas l'imprécision.

- **Portance de l'énoncé** : non calculée — la portance s'évalue sur le texte, et le texte n'a pas été lu
