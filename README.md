# TXT-MetaData

Un outil d'extraction de métadonnées de documents texte (.md / .txt) à
l'aide de l'API Mistral AI.

## Installation

Prérequis : Python 3.11+.

```bash
pip install -e .
pip install -e ".[dev]"   # pour les tests (pytest)
```

Créez un fichier `.env` à la racine du projet (voir `.env.example`) :

```text
MISTRAL_API_KEY=votre_cle
```

La clé n'est jamais copiée, loguée ni persistée ailleurs que dans cette
variable d'environnement.

## Utilisation

```bash
txt-metadata [OPTIONS] CHEMIN...
```

- `CHEMIN...` : un ou plusieurs fichiers `.md`/`.txt`, ou des dossiers
  (parcourus récursivement). Les formats non attendus sont ignorés.
- Un dossier contenant déjà un JSON au format de sortie (apparié par le
  préfixe du nom de fichier, ou paire unique du sous-dossier) est
  amendé sur place plutôt que recréé.

Options :

- `--choix` : modèle LLM — `large4`, `large`, `medium`, `small`
  (défaut), `14b`, `8b`, `3b`, `zai`
- `--taille-batch` : taille des lots de requêtes, 0 à 100 (défaut 25 ;
  0 = une requête à la fois)
- `--retry-occurences` : retries par appel en échec, 0 à 10 (défaut 3)
- `--retry-time` : délai du premier retry en secondes, 1 à 10
  (défaut 3 ; doublement à chaque essai : 3, 6, 12)
- `--output-folder` : dossier de sortie (défaut `output/`, créé
  automatiquement)
- `--temperature-llm` : température d'appel du LLM, 0 à 1 (défaut 0)

Exemple :

```bash
txt-metadata "Interne-Dev/Exemples/IFRI/IFRI.md"
```

## Sortie

Un JSON par document traité, nommé
`<8 premiers caractères du nom du fichier d'entrée, normalisés>-<numéro>.json`,
par exemple `Rapport_-0001.json`, contenant :

- `Typologie` (Article, Rapport, Ouvrage, Cours, Bibliothèque, Extrait,
  Communiqué, Compte-rendu ou Autre) ;
- `Auteur(s)`, `Titre`, `Editeur`, `Date`, `Référence`, `Citation`
  (renseignés uniquement si présents dans le document).

La numérotation est séquentielle (0001, 0002…, cycle après 9999) et
persistée dans `counter.txt` à la racine : un numéro consommé n'est
jamais réutilisé, même en cas d'interruption. Un JSON amendé ne
consomme pas de numéro.

Codes retour : 0 = succès ; 1 = au moins un document en échec (le lot
se poursuit, un bilan final est affiché) ; 2 = erreur fatale avant
traitement (options invalides, clé absente, compteur corrompu).

## Tests

```bash
pytest
```

Les tests unitaires et d'intégration simulent le LLM : aucune clé ni
consommation d'API n'est nécessaire.

## Licence

MIT — voir [LICENSE](LICENSE).
