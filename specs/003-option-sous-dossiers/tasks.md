---

description: "Task list for feature implementation"

---

# Tasks: Option --sous-dossiers — paires autonomes en sortie

**Input**: Design documents from `/specs/003-option-sous-dossiers/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/output-layout.md, quickstart.md

**Tests**: inclus — la convention du projet (spec 002) applique le TDD ;
chaque phase écrit ses tests AVANT l'implémentation correspondante.

**Organization**: tâches groupées par user story (US-1 à US-3 de la
spec), chaque story livrable et testable indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]** : parallélisable (fichiers différents, pas de dépendance)
- **[Story]** : user story de rattachement (US-1, US-2, US-3)
- Chemins exacts dans chaque description

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmer le point de départ sur une base verte

- [ ] T001 Exécuter `python -m pytest -q` à la racine et vérifier que la
  suite existante passe (96 tests, base de référence avant tout
  changement)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: l'option CLI, le rangement en unité et l'exclusion du
 dossier de sortie — bloquent toutes les stories

- [ ] T002 Dans `src/txt_metadata/cli.py`, ajouter le flag booléen
  `--sous-dossiers` (sans valeur, inactif par défaut, FR-001) au
  parseur et le champ `sous_dossiers: bool` au dataclass `Options` ;
  mettre à jour le docstring d'en-tête du module
- [ ] T003 Dans `src/txt_metadata/output.py`, ajouter
  `build_unit_name(input_path, occurrence)` retournant
  `NNNN-<prefixe>` (préfixe = `output_prefix`, décision D1 de
  research.md) et étendre `write_new` d'un paramètre `unit: bool =
  False` : si actif, créer l'unité `output_dir/<NNNN>-<prefixe>/`
  (`mkdir(parents=True, exist_ok=True)`), y écrire le JSON (nom
  inchangé, FR-004) puis copier le fichier source sous son nom
  d'origine avec un contenu identique octet pour octet (FR-003,
  `shutil` stdlib ; écraser une copie existante, D2) ; si inactif,
  comportement strictement inchangé (FR-005)
- [ ] T004 Dans `src/txt_metadata/inputs.py`, ajouter à `discover` un
  paramètre `exclude: Path | None = None` : exclure le chemin résolu du
  dossier de sortie de la découverte quand un chemin d'entrée le couvre
  (FR-011, décision D3 — inconditionnel, option active ou non) ; passer
  `options.output_folder` depuis `_run` dans `src/txt_metadata/
  __main__.py`

**Checkpoint**: l'option existe, le rangement est prêt, l'exclusion est
en place ; les stories peuvent démarrer

---

## Phase 3: User Story 1 - Paire autonome à la création (P1) — MVP

**Goal**: avec `--sous-dossiers`, chaque nouvelle sortie est rangée dans
une unité `NNNN-<prefixe>/` contenant le JSON et une copie exacte de la
source

**Independent Test**: `python -m pytest tests/unit/test_output.py
tests/unit/test_cli.py tests/unit/test_inputs.py -q` — unité créée,
copie identique, option inactive par défaut, exclusion du dossier de
sortie

### Tests for User Story 1

- [ ] T005 [P] [US-1] Ajouter dans `tests/unit/test_cli.py` : le parse
  de `--sous-dossiers` active `options.sous_dossiers` ; sans le flag,
  `sous_dossiers` vaut `False` (FR-001) ; vérifier l'échec avant
  implémentation
- [ ] T006 [P] [US-1] Ajouter dans `tests/unit/test_output.py` :
  `build_unit_name` (`IFRI.md` + `0068` → `0068-IFRI` ;
  `Cour des comptes rapport.md` + `0070` → `0070-Cour_des_comptes_rappo`,
  FR-002/D1) ; `write_new(unit=True)` crée l'unité avec le JSON
  (nom inchangé, FR-004) et une copie identique octet pour octet
  (FR-003, `.md` et `.txt`) ; `write_new(unit=False)` écrit à plat sans
  unité ni copie (FR-005) ; unité existante → copie écrasée (D2) ;
  vérifier l'échec avant implémentation
- [ ] T007 [P] [US-1] Ajouter dans `tests/unit/test_inputs.py` :
  `discover` exclut le dossier de sortie résolu quand un chemin
  d'entrée le couvre (FR-011, D3), option active ou non ; vérifier
  l'échec avant implémentation

### Implementation for User Story 1

- [ ] T008 [US-1] Dans `src/txt_metadata/__main__.py`
  (`process_document`, dépend de T002-T004), passer
  `unit=options.sous_dossiers` à `write_new` à la création
  uniquement — l'amendement reste sur place, sans unité ni copie
  (FR-006) ; en cas d'échec de copie, nettoyer l'unité créée et ne pas
  persister le numéro (FR-007, D4) ; faire passer les tests
- [ ] T009 [US-1] Ajouter dans `tests/integration/test_multi.py` un
  test de bout en bout (LLM simulé) : création en unité avec copie
  identique ; source illisible → document en échec, aucune unité, aucun
  numéro consommé (FR-007)

**Checkpoint**: US-1 livrée — paire autonome créée avec l'option

---

## Phase 4: User Story 2 - Comportement par défaut inchangé (P2)

**Goal**: sans l'option, le layout plat actuel est strictement
identique ; aucun fichier existant n'est déplacé

**Independent Test**: `python -m pytest -q` — suite complète verte,
tests existants du mode par défaut non modifiés (SC-002) ; nouveau test
de non-régression à plat

### Tests for User Story 2

- [ ] T010 [US-2] Ajouter dans `tests/unit/test_output.py` un test de
  non-régression : sans unité demandée, `write_new` écrit à plat dans
  le dossier de sortie et aucun sous-dossier n'est créé (FR-005,
  SC-002/SC-003) ; puis exécuter la suite complète et vérifier que les
  tests existants passent sans modification

**Checkpoint**: US-2 livrée — le mode par défaut est prouvé inchangé

---

## Phase 5: User Story 3 - Amendement d'une paire rangée (P3)

**Goal**: relancer l'outil sur une unité amende le JSON sur place par
le repli « paire unique » existant, copie inchangée, aucun numéro
consommé

**Independent Test**: `python -m pytest tests/integration -q` — unité
re-traitée amendée sur place, copie identique, compteur inchangé

### Tests for User Story 3

- [ ] T011 [P] [US-3] Ajouter dans `tests/integration/test_multi.py`
  (LLM simulé) : une unité (copie + JSON au format de sortie) re-traitée
  → le JSON est amendé sur place via le repli « paire unique du
  sous-dossier » (FR-027 spec 001, D5), nom et numéro conservés, aucun
  numéro consommé, copie inchangée octet pour octet (FR-008) ; vérifier
  l'échec avant implémentation
- [ ] T012 [P] [US-3] Ajouter dans `tests/integration/test_multi.py`
  (LLM simulé) : re-traitement de la source d'origine hors unité →
  nouvelle paire créée avec un nouveau numéro (asymétrie assumée, US-3
  scénario 3, hors périmètre : retrouver la paire depuis la source)

**Checkpoint**: US-3 livrée — l'amendement des paires rangées est prouvé

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: conformité documentaire et validation de bout en bout

- [ ] T013 [P] Mettre à jour `README.md` (sections Sortie et Options) :
  option `--sous-dossiers`, layout d'une unité `NNNN-<prefixe>/`,
  copie de la source, périmètre créations uniquement (FR-010)
- [ ] T014 [P] Amender la spécification 001
  `specs/001-txt-metadata-extraction/spec.md` : FR-026 (une copie de la
  source est écrite dans le dossier de sortie, à la création uniquement
  et uniquement avec l'option — D6), FR-029 (liste des options :
  ajouter `--sous-dossiers`), entité « Sortie JSON » (Key Entities) et
  session de clarification 2026-10-28
- [ ] T015 [P] Mettre à jour
  `specs/001-txt-metadata-extraction/contracts/cli-contract.md` :
  ajouter `--sous-dossiers` à la section Options, conforme à
  `specs/003-option-sous-dossiers/contracts/output-layout.md`
- [ ] T016 Mettre à jour les docstrings d'en-tête de
  `src/txt_metadata/cli.py`, `src/txt_metadata/output.py` et
  `src/txt_metadata/inputs.py` (option, unité, exclusion)
- [ ] T017 Exécuter `python -m pytest -q` (suite complète verte) et
  `pre-commit run --all-files` (lint, secrets, constitution) à la racine
- [ ] T018 Exécuter la validation de
  `specs/003-option-sous-dossiers/quickstart.md` : scénarios 1 et 5
  (tests déterministes), puis scénarios 2 à 4 sur
  `Interne-Dev/Exemples/IFRI` et `Interne-Dev/Exemples/Ecalle_cours`
  avec `MISTRAL_API_KEY` (contrainte utilisateur : ces deux exemples
  uniquement, décision D7) ; vérifier SC-001 à SC-004

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: aucune dépendance — démarrage immédiat
- **Phase 2**: dépend de Phase 1 — BLOQUE toutes les stories
- **Phase 3 (US-1)**: dépend de T002, T003, T004 ; MVP
- **Phase 4 (US-2)**: dépend de Phase 3 (valide l'isolation du mode
  par défaut une fois le code conditionnel en place)
- **Phase 5 (US-3)**: dépend de Phase 3 (une unité doit exister pour
  être amendée)
- **Phase 6**: dépend de toutes les stories ; T016 avant T017

### User Story Dependencies

- **US-1 (P1)**: indépendante après Phase 2 — MVP
- **US-2 (P2)**: story de non-régression — testable seule après US-1
- **US-3 (P3)**: prolonge US-1 (amendement d'une unité créée) — testable
  seule

### Parallel Opportunities

- T005, T006, T007 (Phase 3) : trois fichiers de tests différents
- T011 et T012 (Phase 5) : deux scénarios d'intégration, même fichier
  mais indépendants (peuvent être écrits en parallèle, committés
  séparément)
- T013, T014, T015 (Phase 6) : trois documents différents

---

## Parallel Example: User Story 1

```bash
# Une fois la Phase 2 terminée, lancer en parallèle :
Task: "T005 [P] [US-1] Tests CLI de l'option dans tests/unit/test_cli.py"
Task: "T006 [P] [US-1] Tests de rangement/copie dans tests/unit/test_output.py"
Task: "T007 [P] [US-1] Tests d'exclusion dans tests/unit/test_inputs.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 : base verte (T001)
2. Phase 2 : option, rangement, exclusion (T002-T004)
3. Phase 3 : création en unité avec copie (T005-T009)
4. **STOP et VALIDER** : `pytest tests/unit/test_output.py
   tests/unit/test_cli.py tests/unit/test_inputs.py` — SC-001 atteint
   sur la création d'unités

### Incremental Delivery

1. Phase 1-2 → fondations
2. Ajouter US-1 → paires autonomes à la création (MVP)
3. Ajouter US-2 → non-régression du mode par défaut prouvée (SC-002)
4. Ajouter US-3 → amendement des paires rangées (SC-001 complet)
5. Phase 6 → conformité documentaire (SC-004) et validation réelle
   IFRI + Ecalle_cours

---

## Notes

- Chaque test écrit avant son implémentation doit échouer d'abord (TDD)
- Les 10 JSON de `output/` ne sont ni renommés ni déplacés (FR-005)
- L'amendement ne crée jamais d'unité ni de copie (FR-006)
- La validation réelle est limitée à `Interne-Dev/Exemples/IFRI` et
  `Interne-Dev/Exemples/Ecalle_cours` (contrainte utilisateur, D7) ; la
  création réelle passe par une copie temporaire du `.md` car le
  dossier IFRI contient déjà `IFRI-0042.json`
- Committer après chaque tâche ou groupe logique (hooks pre-commit
  actifs)
