# Jeu de données SYNTHÉTIQUE

**Aucune règle de droit réelle ici.** Ce jeu sert uniquement à faire tourner la
chaîne complète — runner, juge, métriques, rapport — sans appeler de modèle et
sans dépendre du corpus réel.

Tout est volontairement fictif et reconnaissable comme tel :

- identifiants préfixés `SYNTH-`, `RULE-SYNTH-`, `FAM-SYNTH-`, `TWIN-SYNTH-` ;
- URL sur le domaine réservé `example.invalid`, qui ne résout jamais ;
- textes cités nommés « Texte synthétique », sans correspondance avec un texte
  réel.

Ce jeu est **hors de `corpus/`** pour qu'il ne puisse pas être chargé par
inadvertance à la place du corpus réel, ni finir dans un export public.

Le dossier `corpus/private/` de ce jeu contient un item marqué privé : il sert
à vérifier que les garde-fous d'isolation se déclenchent. Il ne contient rien de
confidentiel.
