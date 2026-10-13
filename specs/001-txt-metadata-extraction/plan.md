# Implementation Plan: TXT-MetaData — Extraction de métadonnées

**Branch**: `002-fonction-pcpale` | **Date**: 2026-10-13 | **Spec**:
[spec.md](./spec.md)

**Input**: Feature specification from
`/specs/001-txt-metadata-extraction/spec.md`

## Summary

Outil CLI qui extrait les métadonnées d'un document texte (.md ou .txt) via un
LLM Mistral AI (mistral-small-latest par défaut), en n'envoyant qu'un extrait
début/fin du document, et produit un JSON numéroté séquentiellement dans
`output/`. L'approche technique : un appel LLM principal en mode JSON strict,
complété par une construction déterministe de la citation ; compteur
d'occurrence persistant dans un fichier texte à la racine ; gestion transparente
des multi-entrées (fichiers, dossiers, sous-dossiers) et l'amendement sur place
des JSON existants appariés. Langage : Python 3.11+, SDK officiel `mistralai`,
stockage 100 % fichiers.

## Technical Context

**Language/Version**: Python 3.11+ (Ruff déjà configuré dans le dépôt ; Python
3.14 disponible localement)

**Primary Dependencies**: `mistralai` (SDK officiel, MIT, Mistral AI — éditeur
français, conforme au principe de préférence souveraine) ; `python-dotenv` (MIT)
pour le chargement du `.env`. Aucune autre dépendance d'exécution : argparse et
pathlib pour le CLI (stdlib).

**Storage**: fichiers uniquement — JSON de sortie dans `output/` (défaut, créé
automatiquement), compteur d'occurrence dans un fichier texte à la racine de
l'outil, JSON existants amendés sur place dans le dossier d'entrée.

**Testing**: pytest (unitaire : échantillonnage, citation, compteur, nommage,
appariement ; intégration : CLI de bout en bout sur les exemples
`Interne-Dev/Exemples/`, avec mock des appels LLM pour ne pas consommer d'API en
CI).

**Target Platform**: CLI multiplateforme (Windows/Linux/macOS), local-first.

**Project Type**: cli

**Performance Goals**: 10 documents traités en moins de 15 minutes (SC-009,
objectif par lot) ; moins de 5 appels LLM par document (FR-017).

**Constraints**: clé API uniquement via `MISTRAL_API_KEY` (.env non committé,
jamais loguée ni persistée) ; réseau sortant limité à l'API Mistral ; aucun
tracker/télémétrie ; dépendances open-source à licences permissives.

**Scale/Scope**: entrée = fichiers/dossiers fournis par l'utilisateur ; volume
typique : de 1 à quelques centaines de documents par exécution.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Isolation des secrets — PASS** : clé via `MISTRAL_API_KEY` (`.env`
  gitignoré) ; template `.env.example` avec placeholder ; aucun secret dans le
  code, les tests ou les logs.
- **II. Local-first & confidentialité — PASS** : données, sorties et logs
  restent locaux ; seul appel réseau : l'API Mistral demandée par l'utilisateur
  (finalité même de l'outil, pas une violation du No Cloud).
- **III. Open-source & sans trackers — PASS** : `mistralai` (MIT) et
  `python-dotenv` (MIT), sans télémétrie ; éditeur français (préférence
  souveraine).
- **IV. Simplicité (YAGNI) — PASS** : CLI unique, aucune GUI, pas de plugins,
  stockage fichiers, une seule fonctionnalité.
- **Path Isolation — PASS** : dossier de sortie résolu depuis les options CLI
  (défaut relatif `output`), aucun chemin personnel codé en dur.
- **Network Surface — PASS** : appels sortants limités à l'URL de l'API Mistral.
- **Data Retention — PASS** : pas de copie cachée ; l'utilisateur contrôle la
  rétention via `output/`.

Aucune violation à justifier.

## Project Structure

### Documentation (this feature)

```text
specs/001-txt-metadata-extraction/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── cli-contract.md
│   └── output-schema.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
pyproject.toml           # packaging, dépendances, entrée console "txt-metadata"
.env.example              # template avec MISTRAL_API_KEY=YOUR_API_KEY
src/txt_metadata/
├── __init__.py
├── __main__.py          # python -m txt_metadata
├── cli.py               # argparse, validation des bornes d'options
├── config.py            # chargement .env, validation rapide de la clé
├── inputs.py            # découverte fichiers/dossiers, appariement txt/json
├── sampling.py          # construction de l'extrait début/fin (FR-002 à FR-005)
├── extract.py           # prompt anti-hallucination, appels LLM, JSON mode
├── citation.py          # composition déterministe de la citation (FR-011/12)
├── counter.py           # compteur d'occurrence persistant (FR-023 à FR-025)
├── output.py            # nommage, écriture, amendement sur place (FR-026/27)
├── retry.py             # backoff exponentiel (FR-019)
└── batch.py             # groupement des appels (FR-020)
tests/
├── unit/
└── integration/
```

**Structure Decision**: projet Python unique à la racine (`src/` layout
standard, installable `pip install -e .`), avec point d'entrée console
`txt-metadata` déclaré dans `pyproject.toml`. Un seul paquet, pas de découpage
multi-projets (YAGNI). `Interne-Dev/` (exemples et doc Mistral) reste gitignoré
et sert de corpus de calibration et de test.
