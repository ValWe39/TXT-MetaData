# Implementation Plan: TXT-MetaData — Option --sous-dossiers

**Branch**: `004-option-sous-dossiers` (cible d'implémentation, indiquée
dans la spec ; plan rédigé sur `003-titre-20-car`) | **Date**: 2026-10-28 |
**Spec**: [spec.md](./spec.md)

**Input**: Feature specification from
`/specs/003-option-sous-dossiers/spec.md`

## Summary

Une option CLI booléenne `--sous-dossiers`, inactive par défaut, range
chaque nouvelle sortie dans une unité unique nommée `NNNN-<préfixe
normalisé>` (numéro d'occurrence en tête), contenant le JSON (nom
inchangé, FR-022 de la spec 001) et une copie exacte du fichier source
sous son nom d'origine. Sans l'option, le comportement est strictement
inchangé. L'amendement réutilise le repli « paire unique du
sous-dossier » existant (FR-027) ; le dossier de sortie est exclu de la
découverte quand un chemin d'entrée le couvre (FR-011). Aucune
dépendance nouvelle : la copie est du stdlib (`shutil`). Validation sur
les exemples réels `Interne-Dev/Exemples/IFRI` et
`Interne-Dev/Exemples/Ecalle_cours` (contrainte utilisateur).

## Technical Context

**Language/Version**: Python 3.11+ (inchangé ; Ruff et pre-commit déjà
configurés dans le dépôt)

**Primary Dependencies**: aucune nouvelle. La copie de fichier repose
sur `shutil` (stdlib) ; le reste de la feature touche `cli.py`
(parseur/Options), `output.py` (rangement + copie), `inputs.py`
(exclusion du dossier de sortie), `__main__.py` (orchestration).

**Storage**: inchangé — sorties dans le dossier de sortie (défaut
`output/`, override `--output-folder`), unités en sous-dossiers de ce
dossier, compteur d'occurrence à la racine, JSON existants amendés sur
place.

**Testing**: pytest. Nouveaux tests unitaires (rangement, copie,
exclusion, option CLI) et tests d'intégration (scénario de bout en
bout, LLM simulé) ; les tests existants du mode par défaut ne sont pas
modifiés. Calibration sur exemples réels : IFRI et Ecalle_cours
uniquement (contrainte utilisateur).

**Target Platform**: CLI multiplateforme (Windows/Linux/macOS),
local-first — inchangé.

**Project Type**: cli

**Performance Goals**: aucun objectif nouveau — création d'un
sous-dossier et copie d'un fichier texte sont des opérations locales au
coût négligeable devant l'appel LLM.

**Constraints**: limites de longueur de chemin (Windows : 260 caractères
par défaut ; l'unité ajoute un niveau de répertoire et un segment
`NNNN-` ≈ 5 caractères au chemin) ; aucune clé ni chemin personnel dans
le code ; offline pour toutes les parties locales.

**Scale/Scope**: corpus typique de 1 à quelques centaines de documents ;
une unité par document créé ; collision de noms d'unités possible après
un cycle complet du compteur (> 10 000 sorties au même endroit),
sémantique documentée (écrasement, cohérent avec le mode plat).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Isolation des secrets — PASS** : aucun secret manipulé par cette
  feature (chemins et contenus de fichiers uniquement).
- **II. Local-first & confidentialité — PASS** : les copies restent sur
  la machine locale ; aucun appel réseau ajouté ou modifié.
- **III. Open-source & sans trackers — PASS** : aucune dépendance
  nouvelle (`shutil`, stdlib).
- **IV. Simplicité (YAGNI) — PASS** : un seul flag booléen, sans valeur
  ni paramètre ; l'appariement étendu (option C de l'évaluation) est
  explicitement rejeté du périmètre.
- **Path Isolation — PASS** : les chemins restent résolus depuis les
  options CLI ; aucun chemin personnel codé en dur.
- **Network Surface — PASS** : surface réseau inchangée (API Mistral
  uniquement, non concernée par cette feature).
- **Data Retention — PASS** : la copie est explicite, visible dans le
  dossier de sortie et supprimable par l'utilisateur ; aucune copie
  cachée hors de ce dossier.

Aucune violation à justifier.

## Project Structure

### Documentation (this feature)

```text
specs/003-option-sous-dossiers/
├── plan.md              # Ce fichier
├── research.md          # Phase 0 : décisions fondées
├── data-model.md        # Phase 1 : entités du rangement
├── quickstart.md        # Phase 1 : guide de validation (IFRI, Ecalle_cours)
├── contracts/
│   └── output-layout.md # Contrat de rangement en unités
└── tasks.md             # Sortie de /speckit-tasks (non créé ici)
```

### Source Code (repository root)

```text
src/txt_metadata/
├── cli.py               # --sous-dossiers (flag booléen) + Options
├── output.py            # rangement en unité + copie de la source
├── inputs.py            # exclusion du dossier de sortie (FR-011)
└── __main__.py          # orchestration : copie à la création uniquement

tests/
├── unit/
│   ├── test_output.py   # rangement en unité, copie, collision
│   ├── test_cli.py      # option --sous-dossiers (défaut inactif)
│   └── test_inputs.py   # exclusion du dossier de sortie
└── integration/
    └── test_multi.py    # scénario de bout en bout (LLM simulé)

# Documents de référence à mettre à jour (FR-010)
README.md
specs/001-txt-metadata-extraction/spec.md            # FR-026 amendé
specs/001-txt-metadata-extraction/contracts/cli-contract.md

# Exemples réels de validation (contrainte utilisateur)
Interne-Dev/Exemples/IFRI/IFRI.md
Interne-Dev/Exemples/Ecalle_cours/Ecalle_cours.md
```

**Structure Decision** : structure existante du dépôt reprise telle
quelle (paquet unique `src/txt_metadata`, tests unit/intégration) ;
aucun nouveau répertoire hors `specs/003-option-sous-dossiers/contracts/`.

## Suivi de complexité

> Aucune violation de la constitution à justifier — section vide.
