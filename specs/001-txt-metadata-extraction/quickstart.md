# Quickstart — TXT-MetaData

Date : 2026-10-13 | Contrats : [cli-contract.md](./contracts/cli-contract.md),
[output-schema.md](./contracts/output-schema.md) | Modèle :
[data-model.md](./data-model.md)

## Prérequis

- Python 3.11+ ; pip.
- Clé API Mistral dans `.env` à la racine du projet : `MISTRAL_API_KEY=...` (le
  `.env` est gitignoré ; template : `.env.example`).
- Connexion à l'API Mistral (seul appel réseau autorisé).

## Installation

```bash
pip install -e .
```

## Scénarios de validation

### V1 — Document unique (User Story 1)

```bash
txt-metadata "Interne-Dev/Exemples/IFRI/IFRI.md"
```

Attendu : un JSON créé dans `output/`, nommé du préfixe du fichier d'entrée +
`-NNNN.json`, conforme au schéma de sortie ; `counter.txt` créé ou incrémenté ;
code retour 0. Les 7 clés présentes, `Typologie` parmi les 9 valeurs autorisées.

### V2 — Dossier multi-entrées avec appariement (User Stories 4 et 5)

1. Créer un dossier de test contenant `IFRI.md` et un JSON au format de sortie
   partiellement rempli (même préfixe de 8 caractères normalisés).
2. Lancer :

   ```bash
   txt-metadata dossier-de-test/
   ```

Attendu : le JSON existant est amendé sur place (champs vides complétés, champs
remplis conservés sauf haut degré d'assurance), sans nouveau numéro ; les autres
`.md`/`.txt` reçoivent chacun un nouveau JSON numéroté séquentiellement ; les
fichiers hors format ignorés ; bilan final affiché.

### V3 — Échec en lot (User Story 3, FR-032)

Retirer `MISTRAL_API_KEY` (ou utiliser une clé invalide), puis lancer sur un
dossier contenant plusieurs `.md`.

Attendu : chaque document échoue après les retries (3, 6, 12 s par défaut), le
lot se poursuit, bilan final listant les échecs, code retour 1, aucun JSON ni
numéro consommé.

### V4 — Compteur robuste (FR-023 à FR-025, SC-004)

1. Supprimer `counter.txt` → un traitement repart à 0001.
2. Corrompre `counter.txt` (contenu non numérique) → échec rapide, code retour
   2, aucune sortie.
3. Interrompre un lot en cours (Ctrl+C) → reprendre : le numéro suivant continue
   la séquence, aucun doublon.

### V5 — Calibration sur les exemples (SC-001)

```bash
txt-metadata "Interne-Dev/Exemples/"
```

Attendu : 10 JSON produits. Comparer avec les sorties manuelles de référence :
au moins 8 typologies exactes sur 10 ; au moins 80 % des champs non vides de
référence corrects. Divergences attendues et à documenter dans le rapport de
test : `Grand_Continent_article` (règle « et al. ») et `IFRI` (guillemets
droits). `Corsen_ai` n'a pas de référence : sortie à revue manuelle. Rapport à
produire dans `specs/001-txt-metadata-extraction/`.

## Tests automatisés

```bash
pip install -e ".[dev]"
pytest
```

Attendu : tests unitaires verts (échantillonnage, citation, compteur, nommage,
appariement, validation des options) et tests d'intégration verts avec appels
LLM simulés (mock) — aucune consommation d'API en CI.
