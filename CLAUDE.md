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
  est refusé.** La validation échoue, elle n'avertit pas. `date_verification`
  est obligatoire pour les mêmes raisons.
- Les identifiants dupliqués sont refusés, **tous corpus confondus** (le cache
  est indexé par item : un id partagé mélangerait deux questions).
- Un item déposé dans le mauvais dossier (`corpus: private` sous `public/`) est
  refusé : c'est un glissement que le garde-fou ne pourrait plus rattraper.
- Un champ inconnu est refusé (`extra="forbid"`).
- La validation d'un corpus rapporte **toutes** les erreurs d'un coup
  (pas d'arrêt à la première).

Le vocabulaire de `type` du harnais fait foi. Le site public doit savoir
afficher ces cinq valeurs ; ce n'est pas au corpus de s'aligner sur le site.

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
   La correspondance des erreurs disqualifiantes est **littérale** : pas de
   rapprochement approximatif sur un critère qui met un axe à zéro. Une entrée
   préfixée par `re:` est traitée comme une expression régulière, ce qui permet
   à l'item d'exprimer explicitement ses variantes de formulation.

   L'étage déterministe pose des **plafonds**, jamais des notes : une borne
   haute que le juge ne peut pas dépasser. Barème des plafonds :

   | Constat | Plafonds imposés | Flag |
   |---|---|---|
   | Référence inventée | sourcing 0, exactitude 1, calibration 1 | `hallucination_source` |
   | Erreur disqualifiante | exactitude 0 | `erreur_disqualifiante` |
   | Aucune référence citée | sourcing 0 | `sourcing_incomplet` |
   | Texte cité sans article | sourcing 1 | `sourcing_incomplet` |
   | Item `abstention` auquel le modèle a répondu | calibration 0 | `surconfiance` |
   | Abstention explicite détectée | — | `abstention` |

2. **Juge LLM ensuite**, pour ce que le déterministe ne tranche pas.
   - Le barème est dans le prompt (`prompts/judge.txt`, versionné, haché).
   - **Sortie JSON stricte**, validée par pydantic. Une sortie non conforme est
     une erreur, pas une note par défaut.
   - Le juge reçoit le texte des items : il est soumis au **même garde-fou de
     non-rétention** que les modèles évalués.
   - Quand les quatre axes sont déjà plafonnés à 0, aucun appel n'est émis.

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
- un run existant n'est jamais réécrit en place ;
- la latence et le fait d'avoir été servie par le cache décrivent l'exécution,
  pas la réponse : elles vont dans `execution.json`, hors du périmètre comparé.

Fichiers du dossier de run :

| Fichier | Contenu | Comparé |
|---|---|---|
| `config.json` | la config gelée, telle qu'utilisée | oui |
| `empreintes.json` | hashes des prompts, du registre et du corpus | oui |
| `reponses.json` | les réponses brutes | oui |
| `scores.json` | les scores détaillés (déterministe, juge, humain) | oui |
| `resume.json` | classement et agrégats | oui |
| `revue.csv` | file de revue humaine | non |
| `execution.json` | latences, cache, erreurs | non |
| `scores_revus.json` | scores après réinjection d'une revue | non |

Une réinjection de revue **n'écrase jamais** `scores.json` : elle écrit à côté.
`finreg verifier-reproductibilite <run_a> <run_b>` compare deux runs.

## 8. Export

Une commande génère `results.json` et `questions.json` au format attendu par le
site public, en n'incluant **QUE** les items du corpus public.
Un item privé qui apparaîtrait dans un export est un bug bloquant ; un test
garde cette frontière.

## 9. Ordre de construction

On ne passe à l'étape suivante que quand la précédente **a ses tests qui passent**.

1. `schema` + `loader` + tests de validation — fait
2. Garde-fou de sécurité + son test — fait
3. Runner avec cache, sur un faux fournisseur local — fait
4. Scoring déterministe — fait
5. Juge LLM et file de revue — fait
6. Agrégation et export — fait

## 9 bis. Format du site public

L'export vise le contrat de données de **FinReg Compass**
(`src/lib/finreg.ts` du dépôt `amirRbh/finreg-compass`). Ce fichier fait foi
pour la forme de `results.json` et `questions.json` ; l'export ne doit pas s'en
écarter, et un test vérifie les clés produites.

Conventions de publication, choisies une fois pour toutes :

- **Note publiée (0–10)** : moyenne des runs, ramenée de 0–8 sur 0–10.
- **Texte publié** : celui du **run médian** en note. Publier le meilleur
  flatterait le modèle, publier le pire l'accablerait ; l'écart-type affiché à
  côté dit ce que la dispersion coûte.
- **Flags publiés** : union des signalements sur l'ensemble des runs. Un défaut
  apparu sur un seul run reste un défaut.
- **Écart-type** : dispersion du score global d'un run à l'autre — l'instabilité
  du modèle, pas la dispersion entre questions.
- **Taux d'abstention correcte** : parmi les items de type `abstention`, ceux où
  le modèle s'est abstenu sur **tous** ses runs.
- Un domaine absent de `domaines_publics` **bloque** l'export : le site ne
  saurait pas l'afficher, mieux vaut une erreur qu'une page muette.

## 9 ter. FinReg-FR Bench V0.2 (`src/bench/`)

La V0.2 refond le modèle de données autour d'un **protocole d'évaluation**, pas
d'un dataset. Elle vit dans `src/bench/`, à côté du pipeline V0.1 qui reste en
service jusqu'à ce que les phases 6 à 12 l'y migrent.

Hiérarchie : `RULE → CONCEPT → QUESTION FAMILY → TWIN GROUP → ITEM`.
Une question n'est jamais créée sans être rattachée à des règles **validées**.

**Les noms de champs de la V0.2 sont en anglais**, contrairement à la V0.1 : ils
sont fixés par la spécification V0.2 et font partie de son contrat. Les
commentaires et les messages restent en français. Ne pas mélanger les deux
conventions à l'intérieur d'un même module.

Invariants tenus par le schéma (`src/bench/items.py`) :

- `expected_behavior` doit être admis par `question_type`, et `answerability`
  par `expected_behavior` (tables dans `vocabulaires.py`).
- `false_premise` et `true_premise_adversarial` exigent un `reasoning_trap`
  nommé : sans piège, l'item ne mesure rien de particulier.
- Un piège qui affirme une disposition inexistante (`FALSE_ARTICLE`,
  `FALSE_THRESHOLD`, `NEGATIVE_ASSERTION`) impose `negative_claim` et sa
  `negative_claim_verification` : **on ne source pas une absence en citant un
  texte**.
- `abstain` et `request_missing_information` exigent `abstention_requirements` :
  une abstention se note sur ce qu'elle réclame, pas sur le fait de se taire.
- `reframe_required` est réservé aux fausses prémisses et impose de dire quelle
  règle correcte la réponse doit rétablir.
- Versionnement : `base_id` + `version`, `id = base_id-vN`. Au-delà de v1,
  `supersedes` est obligatoire et le registre refuse une suite de versions
  discontinue. **Un gold n'est jamais écrasé, il est reversionné.**
- Cycle de vie : public `draft → review → validated → published`, privé
  `draft → review → validated → locked`. `validated` exige les six contrôles de
  la grille, un relecteur nommé et une source primaire vérifiée. `published` et
  `locked` sont figés : on reversionne au lieu de modifier.

Isolation du privé (`src/bench/isolation.py`, `registre.py`) :

- Chargeurs **séparés**. `charger_prive` exige `je_confirme_usage_local=True` ;
  aucune fonction ne charge les deux corpus d'un coup.
- `ids_publics_et_prives` lit les identifiants sans charger le contenu, pour que
  les contrôles de fuite n'aient jamais à ouvrir le privé.
- Un groupe de jumeaux à cheval sur les deux corpus est refusé : publier un
  jumeau révélerait la structure de son jumeau privé.
- `Item.redacted()` est la seule forme journalisable.
- Aucun message d'erreur de fuite ne reproduit le contenu fautif.

Les pondérations (`src/bench/plan.py`) sont des données, jamais des constantes
dans le scoring. Les cibles par domaine du public sont imposées explicitement
par la spécification §3 (DORA 22 / LCB-FT 23, une égalité à 22,5 que la
répartition proportionnelle trancherait dans l'autre sens).

**Ne pas inventer le droit.** Les fixtures de test sont explicitement fictives
(`SYNTH-*`, `example.invalid`). Une information juridique non vérifiée reste en
`status: draft`.

### Jugement, métriques et QA (phases 6 à 9)

`jugement.py` → `juge.py` → `metriques.py` → `qa.py`.

L'étage déterministe **ne conclut que vers l'erreur**. Il établit ce que le
modèle a fait (répondu, réfuté, demandé une information, s'est abstenu), les
références inventées et les erreurs disqualifiantes. Rien de mécanique ne permet
de conclure qu'une réponse est juste sur le fond : ça, c'est le juge.

Le juge est un composant faillible, encadré deux fois :

- **Il ne reçoit pas le nom du modèle.** `JudgePacket` ne contient que question,
  gold, points clés, erreurs disqualifiantes, comportement attendu, réponse. Un
  test vérifie l'absence du `model_id`.
- **Escalade obligatoire** sur les six motifs de la spécification §16, dont
  l'audit aléatoire, tiré d'un hash et non d'un générateur : deux exécutions du
  même run auditent les mêmes réponses, sinon le run n'est pas reproductible.

Asymétrie assumée sur l'abstention : demander précisément ce qui manque vaut
pour un item qui n'attendait qu'un retrait ; se taire ne remplit pas une attente
de demande d'information.

**Aucune métrique n'est publiée sans son dénominateur.** Chaque `Metric` porte
numérateur, dénominateur et la phrase qui les définit. Un dénominateur vide rend
`None`, jamais `0.0` : zéro sur zéro n'est pas zéro pour cent.

`Over-Refusal Rate` et `Premise Sensitivity` sont ce qui empêche de bien scorer
en réfutant tout : la sensibilité exige de réfuter le faux **et** d'accepter le
vrai dans le même groupe de jumeaux.

Le `Dangerous Answer Rate` exige les quatre conditions de la §15 :
incorrect + affirmatif + `item.actionable` + `item.materially_regulatory`.

`qa.py` : Cohen à deux annotateurs, Fleiss au-delà. Un désaccord sans arbitrage
n'est pas tranché — il reste en attente plutôt que résolu au hasard. `publiable`
ne rend jamais un booléen sans ses raisons chiffrées.

### Runner, rapports et jeu synthétique (phases 10 à 12)

`config.py` → `fournisseurs.py` → `runner.py` → `campagne.py` → `rapport.py`.

`ModelProvider.run(request) -> ProviderResult` est tout ce que le harnais connaît
d'un fournisseur. Brancher un modèle réel se fait dans `fournisseurs.py`, via
`enregistrer_adaptateur`, sans toucher au reste.

Le garde-fou de non-rétention s'applique au **lot entier avant** qu'un prompt
soit assemblé, au runner comme au juge. `zero_retention` n'accepte qu'un booléen
`true` littéral. L'exception réutilisée est `PrivateCorpusLeakError` de la V0.1 :
la règle non négociable n'a qu'une seule définition dans le dépôt.

Dossier de run V0.2 :

| Fichier | Comparé |
|---|---|
| `config.json`, `fingerprints.json`, `responses.json` | oui |
| `judgments.json`, `metrics.json`, `public_report.json` | oui |
| `escalations.csv`, `execution.json` | non |

`public_report.json` est le seul artefact destiné à sortir de la machine. Il est
**contrôlé avant écriture** contre les identifiants et les contenus privés : un
artefact fautif ne doit pas exister, même une seconde. Le contrôle porte sur le
résultat construit, pas sur la confiance qu'on accorde à sa construction.

La latence sort du périmètre comparé : elle décrit l'exécution, pas la réponse.

**Jeu synthétique** (`fixtures/synthetic/`) — 9 items publics couvrant les six
types de question, un groupe de jumeaux, un gold versionné (v1 et v2), un
brouillon, et un item privé pour éprouver l'isolation. Il est **hors de
`corpus/`** pour ne pas pouvoir être chargé à la place du corpus réel. Tout y est
reconnaissable comme fictif : `SYNTH-*`, `example.invalid`, « Texte
synthétique ». Son sous-dossier `corpus/private/` n'est volontairement pas
couvert par le `.gitignore` du corpus réel — celui-ci est ancré à la racine, et
le contenu synthétique doit être versionné pour que les tests tournent.

CLI : `finreg-bench valider|executer|verifier-reproductibilite`, et
`finreg-bench rulebook qc|exporter-verification|appliquer-verification`.

### Regulatory Rulebook (phase 6)

`rulebook.py` (vocabulaires) + `regles.py` (modèle `Rule`) + `qc_rulebook.py`
(contrôle qualité). Données dans `data/rules/`, un fichier par domaine, plus
`rulebook-manifest.json` — que le chargeur ignore explicitement.

Une règle sépare **trois choses qu'il ne faut jamais confondre** :

| Champ | Contenu |
|---|---|
| `statement` | ce que le texte dit, au plus près de sa lettre |
| `operational_rule` | ce que cela implique pour un professionnel |
| `common_confusions` | ce avec quoi un modèle le confond |

Écrire une inférence dans `statement`, c'est faire dire au texte ce qu'il ne dit
pas — puis construire des questions sur cette invention.

**Verrou de vérification.** Un statut au-delà de `draft` exige
`verification_method ∈ {primary_text_fetched, primary_text_review}` **et** une
source portant `verified_by` + `verification_date`. Aucune règle ne peut
progresser parce qu'un modèle a écrit une référence de mémoire, ni parce qu'une
page web la mentionne. Seul `validated` rend une règle utilisable pour ancrer un
gold (`Rule.is_usable`).

**Exceptions.** `exceptions_status` distingue `none_identified` (on a cherché,
il n'y en a pas) de `unknown` (on n'a pas cherché). Les confondre produit des
questions dangereusement simplifiées.

**Connaissance négative.** Une `NegativeClaim` ne peut passer en
`verified_absent` sans méthode suffisante **et** `searched_in`. C'est ce qui
empêche de transformer « je n'ai pas trouvé » en « cela n'existe pas ».

**État du Rulebook V0 : 58 règles, toutes en `draft`, aucune utilisable.** Les
sources primaires sont inaccessibles depuis l'environnement de génération
(EUR-Lex, Légifrance, AMF, ACPR, TRACFIN, ESMA bloqués par le proxy réseau). Les
références proviennent de la connaissance du modèle et doivent être confrontées
au texte par un humain. Le rapport `RULEBOOK_QC.md` le dit en tête.

### Circuit de vérification (`verification.py`)

Le verrou dit ce qu'une règle ne peut pas faire ; le circuit dit comment elle le
fait. La vérification ne s'écrit jamais à la main dans `data/rules/` :

```sh
finreg-bench rulebook exporter-verification --sortie verification.csv
finreg-bench rulebook appliquer-verification verification.csv
finreg-bench rulebook qc --ecrire
```

- **Dossier de vérification** : un CSV (UTF-8 BOM, séparateur `;`, comme la file
  de revue), une ligne par règle, trié par priorité — on vérifie d'abord ce
  dont l'erreur coûte le plus cher.
- **Quatre verdicts**, dont deux seulement promeuvent : `confirme` et `corrige`.
  `refute` et `non_verifiable` enregistrent une consultation qui n'a rien
  promu — on ne monte pas une règle en grade parce que sa vérification s'est
  mal passée.
- **Une correction reversionne** : `version` avance, `supersedes` nomme la
  version remplacée. Un énoncé n'est jamais écrasé, pas plus qu'un gold.
- **Lecture tout ou rien** : un dossier dont une ligne est irrecevable ne
  s'applique pas à moitié, et rien n'est écrit.
- **`validated` exige des exceptions connues** : une règle validée dont les
  exceptions restent `unknown` se testerait comme un absolu qu'elle n'est pas.
- **Registre** : `data/verification/rulebook-ledger.json`, hors de
  `data/rules/`. `scripts/generer_rulebook.py` le réapplique après génération —
  sans lui, régénérer le Rulebook effacerait le travail du vérificateur, seul
  travail que le script ne sait pas refaire. `data/rules/*.json` est désormais
  la sérialisation complète du modèle `Rule`, pour qu'une réinjection ne
  produise pas de diff parasite.

### Ce que le QC vérifie sans le texte primaire

Quatre constats se déduisent de la citation elle-même :

| Contrôle | Ce qu'il attrape |
|---|---|
| `version_date_placeholder` | version consultée antérieure à l'acte cité (l'année est dans son numéro) |
| `url_acte_different` | l'URL désigne un autre acte que `source.text` — légitime pour un acte modificatif |
| `ancrage_imprecis` | « Articles 8 à 13 », « Ensemble de la directive » : aucun gold ne pourra citer son article |
| `verification_sans_promotion` | règle consultée mais restée `draft` — elle ne revient plus d'elle-même dans le dossier |

`doublon_conceptuel` ne se déclenche que si deux règles du même article ont
*aussi* des énoncés proches : un article porte couramment plusieurs obligations
distinctes, et les signaler toutes noierait le vrai doublon dans le bruit. Le
cas ordinaire ressort en `INFO meme_article`.

## 10. Conventions

- Commentaires, noms de champs et messages utilisateur **en français**
  (les noms de champs du schéma sont en français et font partie du contrat).
- Types annotés partout ; pydantic en mode strict là où c'est possible.
- Toute écriture de fichier passe par une fonction utilitaire commune
  (JSON trié, UTF-8) pour garantir la reproductibilité.
- Pas de secret en dur : les clés API viennent de l'environnement, et ne sont
  jamais écrites dans `runs/`.
