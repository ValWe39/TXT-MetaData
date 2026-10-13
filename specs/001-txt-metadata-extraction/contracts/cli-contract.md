# Contrat CLI — `txt-metadata`

Date : 2026-10-13 | Spec : [spec.md](../spec.md) (FR-001, FR-019, FR-020, FR-028
à FR-032) | Décisions : [research.md](../research.md) R1, R3, R9

## Syntaxe

```text
txt-metadata [OPTIONS] CHEMIN...
```

- `CHEMIN...` : un ou plusieurs fichiers (`.md`/`.txt`) ou dossiers. Les
  dossiers sont parcourus récursivement (sous-dossiers inclus). Les fichiers
  d'un format non attendu sont ignorés silencieusement. La détection du mode
  (fichier unique, dossier, dossiers multiples, amendement) est automatique :
  aucune commande complémentaire.

## Options

- `--choix modèle-llm` : alias du modèle. Valeurs : `large4` (mistral-large-4),
  `large` (mistral-large-latest), `medium` (mistral-medium-latest), `small`
  (mistral-small-latest, défaut), `14b` (ministral-14b-latest), `8b`
  (ministral-8b-latest), `3b` (ministral-3b-latest), `zai` (zai-glm-5-3).
- `--taille-batch` : taille des lots de requêtes LLM. Entier 0–100, défaut 25.
  `0` = pas de lot : requêtes envoyées une par une.
- `--retry-occurences` : nombre de retries par appel en échec. Entier 0–10,
  défaut 3.
- `--retry-time` : délai (secondes) avant le premier retry. Entier 1–10, défaut
  3. Doublement à chaque essai (3, 6, 12 par défaut).
- `--output-folder` : dossier de sortie. Défaut : `output` à la racine du projet
  ; créé automatiquement s'il n'existe pas, sans confirmation.
- `--temperature-llm` : température d'appel. Décimal 0–1, défaut 0.

## Validation et erreurs

- Toute option hors bornes ou alias inconnu : message explicite sur stderr, code
  retour 2, aucun traitement lancé.
- `MISTRAL_API_KEY` absente du `.env`/environnement : message explicite, code
  retour 2, avant tout appel réseau.
- `counter.txt` corrompu/illisible : message explicite, code retour 2, aucune
  sortie écrite.

## Comportement par lot

- Un document en échec définitif (après retries) ne bloque pas le lot : erreur
  journalisée, traitement continue, aucun fichier ni numéro consommé pour ce
  document.
- Bilan final obligatoire sur stdout : documents créés, amendés, en échec,
  numéros attribués.

## Codes retour

- `0` : tous les documents traités avec succès (créés ou amendés).
- `1` : au moins un document en échec, le reste du lot traité.
- `2` : erreur fatale avant traitement (options invalides, clé absente, compteur
  corrompu).

## Journalisation

- Progression et erreurs sur stderr ; données sensibles exclues (jamais de clé
  API, jamais de contenu de document au-delà de l'extrait nécessaire au
  diagnostic).
