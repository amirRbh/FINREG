# FinReg Bench — Règles du projet

Banc de test qui interroge plusieurs LLM sur un corpus de questions de
réglementation financière et produit un classement **auditable et opposable**.
Ce fichier fait autorité : en cas de conflit avec une habitude de code, c'est
ce fichier qui gagne.

---

## 1. Stack

- **Python 3.11** (exclusivement ; pas de syntaxe 3.12+).
- **uv** pour les dépendances et l'exécution (`uv sync`, `uv run ...`).
  Jamais de `pip install` direct, jamais de `requirements.txt` édité à la main.
- **pydantic** (v2) pour tous les schémas de données.
- **typer** pour la CLI.
- **pytest** pour les tests.
- **Aucun appel réseau dans les tests.** Aucune exception. Les tests qui
  touchent au runner passent par un faux fournisseur local (`FakeProvider`).
  Toute tentative de sortie réseau dans la suite de tests doit échouer bruyamment.

## 2. Structure du dépôt

```
corpus/
  public/*.json        # versionné, publiable
  private/*.json       # .gitignore — ne quitte JAMAIS la machine
registry/
  references.json      # registre local des références réglementaires valides
prompts/
  system.txt           # prompt système unique, versionné
  judge.txt            # prompt du juge LLM, versionné
src/
  schema.py            # modèles pydantic (Item, Source, Config, Réponse, Score…)
  loader.py            # chargement + validation du corpus
  runner.py            # exécution des appels modèles (cache, reprise, débit)
  providers/           # adaptateurs fournisseurs + FakeProvider
  scoring/             # étage déterministe puis juge LLM
  aggregate.py         # agrégation, classement
  export.py            # export site public
runs/
  AAAA-MM-JJ-HHMM/     # une exécution = un dossier horodaté, immuable
tests/
```

## 3. Règle de sécurité NON NÉGOCIABLE

**Les items du corpus privé ne doivent jamais être envoyés à un fournisseur
qui ne garantit pas la non-rétention des données.**

- Chaque fournisseur déclare un booléen `zero_retention` dans la config.
- Le runner **lève une exception avant tout appel réseau** si
  `corpus == "private"` et `zero_retention is False`.
- L'exception dédiée est `PrivateCorpusLeakError`. Elle n'est jamais rattrapée
  silencieusement, jamais transformée en avertissement, jamais contournée par
  un drapeau CLI.
- `zero_retention` est un booléen strict : absent, `None` ou non booléen ⇒
  traité comme `False` (refus par défaut).
- Un test vérifie que cette exception se déclenche. Ce test ne peut pas être
  supprimé ni marqué `skip`.
- `corpus/private/` est dans `.gitignore`. Aucun contenu d'item privé
  (question, réponse de référence, points clés) ne doit apparaître dans
  `runs/` exporté, dans les logs, ni dans un message d'erreur.

## 4. Schéma d'item

Champs obligatoires :

| Champ | Type | Notes |
|---|---|---|
| `id` | str | unique sur l'ensemble des corpus |
| `corpus` | `public` \| `private` | |
| `domaine` | str | |
| `type` | `fait` \| `qualification` \| `calcul` \| `piege` \| `abstention` | |
| `difficulte` | int | |
| `question` | str | |
| `reponse_reference` | str | |
| `points_cles` | list[str] | |
| `erreurs_disqualifiantes` | list[str] | |
| `source` | objet | `texte`, `article`, `url`, `date_version`, `verifie_par`, `date_verification` |
| `date_validite` | date | |
| `sensible_au_temps` | bool | |

Règles de validation :

- **Tout item du corpus public dont `source.verifie_par` est vide (ou blanc)
  est refusé.** La validation échoue, elle n'avertit pas.
- Les identifiants dupliqués sont refusés.
- La validation d'un corpus rapporte **toutes** les erreurs d'un coup
  (pas d'arrêt à la première).

## 5. Runner

- **3 exécutions par item**, **température 0**.
- **Un seul prompt système**, lu depuis `prompts/system.txt` (fichier versionné).
  Son hash SHA-256 est enregistré dans chaque run.
- Appels **concurrents** avec limite de débit **paramétrable** (config).
- **Reprise après interruption** : relancer une exécution ne refait que ce qui
  manque.
- **Cache disque** des réponses indexé sur `(hash du prompt, modèle, index du run)`.
  On ne repaie jamais deux fois la même requête.
- Le cache et les runs sont séparés par corpus : rien de privé ne fuit dans un
  artefact public.

## 6. Scoring

Quatre axes notés **0–2** : `exactitude`, `sourcing`, `calibration`,
`exploitabilite`.

Deux étages, dans cet ordre :

1. **Déterministe d'abord**
   - Détection des **références inventées** : tout numéro d'article cité dans la
     réponse est confronté au registre local `registry/references.json`.
     Une référence absente du registre est une hallucination de source.
   - Détection des **erreurs disqualifiantes** par correspondance sur la liste
     `erreurs_disqualifiantes` de l'item.
2. **Juge LLM ensuite**, pour ce que le déterministe ne tranche pas.
   - Le barème est dans le prompt (`prompts/judge.txt`, versionné, haché).
   - **Sortie JSON stricte**, validée par pydantic. Une sortie non conforme est
     une erreur, pas une note par défaut.

**File de revue humaine** : tout item dont le score du juge s'écarte de **plus
d'un point entre deux runs** part en revue humaine, exporté en **CSV**. Le CSV
doit pouvoir être corrigé à la main puis **réinjecté** ; la correction humaine
prime sur le juge et est tracée dans le run.

## 7. Auditabilité

Chaque exécution produit `runs/AAAA-MM-JJ-HHMM/` contenant :

- la **config gelée** (telle qu'utilisée, pas la config par défaut) ;
- le **hash du prompt système** (et du prompt juge) ;
- la **version du corpus** (hash du contenu + identifiants) ;
- **toutes les réponses brutes** ;
- les **scores détaillés** (déterministe et juge séparés, avec justification) ;
- un **résumé**.

Ce dossier est ce qui rend le rapport opposable à un audit interne :
il doit être **reproductible à l'identique**. Concrètement :

- pas d'horodatage ni de chemin absolu à l'intérieur des artefacts comparés ;
- JSON écrit trié par clé, encodage UTF-8, fin de ligne `\n` ;
- un run existant n'est jamais réécrit en place.

## 8. Export

Une commande génère `results.json` et `questions.json` au format attendu par le
site public, en n'incluant **QUE** les items du corpus public.
Un item privé qui apparaîtrait dans un export est un bug bloquant ; un test
garde cette frontière.

## 9. Ordre de construction

On ne passe à l'étape suivante que quand la précédente **a ses tests qui passent**.

1. `schema` + `loader` + tests de validation
2. Garde-fou de sécurité + son test
3. Runner avec cache, sur un faux fournisseur local
4. Scoring déterministe
5. Juge LLM et file de revue
6. Agrégation et export

## 10. Conventions

- Commentaires, noms de champs et messages utilisateur **en français**
  (les noms de champs du schéma sont en français et font partie du contrat).
- Types annotés partout ; pydantic en mode strict là où c'est possible.
- Toute écriture de fichier passe par une fonction utilitaire commune
  (JSON trié, UTF-8) pour garantir la reproductibilité.
- Pas de secret en dur : les clés API viennent de l'environnement, et ne sont
  jamais écrites dans `runs/`.
