---

description: "Task list for feature implementation"

---

# Tasks: Préfixe de 20 caractères pour les sorties JSON

**Input**: Design documents from `/specs/002-titre-20-chars/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/naming-and-pairing.md, quickstart.md

**Tests**: inclus — la mise à jour des tests existants et les nouveaux tests
font partie du périmètre (plan.md, Technical Context > Testing) ; chaque
phase écrit ses tests AVANT l'implémentation correspondante (TDD).

**Organization**: tâches groupées par user story (US-1 à US-3 de la spec),
chaque story livrable et testable indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]** : parallélisable (fichiers différents, pas de dépendance)
- **[Story]** : user story de rattachement (US-1, US-2, US-3)
- Chemins exacts dans chaque description

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: confirmer le point de départ sur une base verte

- [x] T001 Exécuter `python -m pytest -q` à la racine et vérifier que les
  92 tests existants passent (base de référence avant tout changement)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: découpler nommage et appariement — bloque toutes les stories

- [x] T002 Dans `src/txt_metadata/output.py`, remplacer la constante
  `_PREFIX_LENGTH = 8` par `_NAME_PREFIX_LENGTH = 20` (longueur de nommage,
  décision D2 de research.md) et mettre à jour le docstring de
  `output_prefix` ; aucune autre modification
- [x] T003 Dans `src/txt_metadata/inputs.py`, introduire les constantes
  d'appariement `_MATCH_MIN = 8` et `_MATCH_MAX = 20` (fenêtre de
  reconnaissance, décision D2) et une fonction utilitaire
  `common_prefix_length(document, json_stem)` calculant le préfixe commun
  le plus long entre le nom normalisé du document et le nom (normalisé :
  espaces → `_`, accents simplifiés, décision D4) du JSON, plafonné à 20 ;
  non utilisée avant la Phase 4

**Checkpoint**: les deux réglages existent et sont découplés ; les stories
peuvent démarrer

---

## Phase 3: User Story 1 - Sorties identifiables par leur nom (P1) — MVP

**Goal**: les nouvelles sorties sont nommées sur 20 caractères normalisés

**Independent Test**: `python -m pytest tests/unit/test_output.py -q` —
troncature à 20, pas de padding pour les noms courts, format
`<préfixe>-<NNNN>.json`

### Tests for User Story 1

- [x] T004 [US-1] Mettre à jour les tests de préfixe dans
  `tests/unit/test_output.py` : `test_prefix_limite_huit_caracteres`
  attend `Rapport_information` pour `Rapport_information.md` (20 caractères,
  underscore compté), `IFRI` pour `IFRI.md` (FR-002, sans padding) ;
  `test_nom_de_sortie` attend `Rapport_info-0007.json` pour
  `Rapport info.md` ; vérifier l'échec avant implémentation

### Implementation for User Story 1

- [x] T005 [US-1] Appliquer la longueur 20 dans `output_prefix`
  (`src/txt_metadata/output.py`, dépend de T002) et faire passer
  `tests/unit/test_output.py`
- [x] T006 [US-1] Mettre à jour les noms attendus dans
  `tests/integration/test_multi.py` : `Troisieme-0003.json` (le nom
  « Troisieme », 9 caractères, n'est plus tronqué) ; vérifier que
  `Deuxieme-0001.json` et `Premier-0002.json` sont inchangés (noms ≤ 8) et
  que `bon-` (stem court) l'est aussi

**Checkpoint**: US-1 livrée — sortie nommée sur 20, suite verte

---

## Phase 4: User Story 2 - Amendement des corpus déjà traités (P2)

**Goal**: un ancien JSON (nom 8 caractères) reste reconnu et amendé

**Independent Test**: `python -m pytest tests/unit/test_pairing.py -q` —
`Rapport info.md` apparié à `Rapport_-0001.json` (8 caractères partagés)

### Tests for User Story 2

- [x] T007 [US-2] Mettre à jour `tests/unit/test_pairing.py` :
  `test_appariement_par_prefixe` documente la reconnaissance à partir de 8
  caractères entre le préfixe 20 `Rapport_info` et l'ancien
  `Rapport_-0001.json` ; conserver les tests `paire_unique`,
  `ambigu_non_lie` et `hors_format` ; vérifier l'échec avant implémentation

### Implementation for User Story 2

- [x] T008 [US-2] Brancher la reconnaissance dans `pair_documents`
  (`src/txt_metadata/inputs.py`, dépend de T003) : un JSON au format de
  sortie est candidat si `common_prefix_length` >= 8 (ou >= la longueur du
  nom du document si plus court, FR-003) ; candidat unique → apparié ;
  faire passer `tests/unit/test_pairing.py`

**Checkpoint**: US-2 livrée — les anciens JSON restent amendés

---

## Phase 5: User Story 3 - Départage ancien/nouveau et normalisation (P3)

**Goal**: analyse prolongée jusqu'à 20, candidat le plus proche retenu,
égalité → non-liage, noms de JSON normalisés avant comparaison

**Independent Test**: `python -m pytest tests/unit/test_pairing.py -q` —
coexistence ancien/nouveau départagée, nom accentué reconnu, égalité
parfaite non liée

### Tests for User Story 3

- [x] T009 [P] [US-3] Ajouter dans `tests/unit/test_pairing.py` les tests de
  départage (FR-004, FR-005, décision D3/D5) : (a) `Rapport info.md` +
  `Rapport_-0001.json` + `Rapport_info-0007.json` → seul le nouveau (12
  caractères partagés) apparié ; (b) nom accentué `Rapport infó-0002.json`
  reconnu après normalisation (décision D4) ; (c) deux candidats à égalité
  parfaite → aucun appariement ; vérifier l'échec avant implémentation
- [x] T010 [P] [US-3] Ajouter dans `tests/integration/test_multi.py` un test
  d'amendement avec coexistence ancien/nouveau JSON (LLM simulé) : le
  nouveau JSON est amendé sur place, l'ancien ignoré, aucun numéro consommé

### Implementation for User Story 3

- [x] T011 [US-3] Implémenter la sélection dans `pair_documents`
  (`src/txt_metadata/inputs.py`, dépend de T008) : retenir le candidat de
  `common_prefix_length` maximale, égalité parfaite → `paired_json` à
  `None` (document traité seul, FR-005) ; repli « paire unique » inchangé
  à défaut de candidat reconnu (décision D6) ; faire passer les tests

**Checkpoint**: US-3 livrée — appariement progressif complet

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: conformité documentaire et validation de bout en bout

- [x] T012 [P] Mettre à jour `README.md` (section Sortie) : « 20 premiers
  caractères du nom du fichier d'entrée, normalisés » + mention de la
  fenêtre d'appariement 8 → 20 dans la section amendement
- [x] T013 [P] Amender la spécification 001
  `specs/001-txt-metadata-extraction/spec.md` : FR-022 (8 → 20),
  FR-027 (mention de la fenêtre 8 → 20) et l'entité « Sortie JSON »
  (section Key Entities)
- [x] T014 [P] Mettre à jour
  `specs/001-txt-metadata-extraction/contracts/output-schema.md` : nom du
  fichier sur 20 caractères, conforme à
  `specs/002-titre-20-chars/contracts/naming-and-pairing.md`
- [x] T015 Mettre à jour les docstrings d'en-tête de
  `src/txt_metadata/output.py` et `src/txt_metadata/inputs.py` (règles 20
  caractères et appariement 8 → 20)
- [x] T016 Exécuter `python -m pytest -q` (suite complète verte) et
  `pre-commit run --all-files` (lint, secrets, constitution) à la racine
- [x] T017 Exécuter la validation de
  `specs/002-titre-20-chars/quickstart.md` : scénarios 1 et 2 (tests
  déterministes), puis scénario 3 sur `Interne-Dev/Exemples/IFRI` avec
  `MISTRAL_API_KEY` (contrainte utilisateur : IFRI uniquement) ; vérifier
  SC-001, SC-002, SC-003

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: aucune dépendance — démarrage immédiat
- **Phase 2**: dépend de Phase 1 — BLOQUE toutes les stories
- **Phase 3 (US-1)**: dépend de T002 ; MVP
- **Phase 4 (US-2)**: dépend de T003 et de Phase 3 (base verte du nommage)
- **Phase 5 (US-3)**: dépend de T008 (reconnaissance) — prolonge l'appariement
- **Phase 6**: dépend de toutes les stories ; T015 avant T016

### User Story Dependencies

- **US-1 (P1)**: indépendante après Phase 2 — MVP
- **US-2 (P2)**: s'appuie sur l'assistant commun (T003) ; testable seule
- **US-3 (P3)**: étend US-2 (`pair_documents`) ; testable seule

### Parallel Opportunities

- T002 et T003 (Phase 2) touchent deux fichiers différents : parallélisables
- T009 et T010 (Phase 5) : tests unitaires vs intégration, fichiers
  différents
- T012, T013, T014 (Phase 6) : trois documents différents

---

## Parallel Example: User Story 3

```bash
# Une fois T008 terminé, lancer en parallèle :
Task: "T009 [P] [US-3] Tests de départage dans tests/unit/test_pairing.py"
Task: "T010 [P] [US-3] Test intégration coexistence dans tests/integration/test_multi.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 : base verte (T001)
2. Phase 2 : constantes découplées (T002, T003)
3. Phase 3 : nommage à 20 (T004-T006)
4. **STOP et VALIDER** : `pytest tests/unit/test_output.py` — SC-001
   atteint sur les noms longs

### Incremental Delivery

1. Phase 1-2 → fondations
2. Ajouter US-1 → noms de sortie à 20 caractères (MVP)
3. Ajouter US-2 → anciens JSON toujours amendés (SC-002)
4. Ajouter US-3 → départage complet ancien/nouveau
5. Phase 6 → conformité documentaire (SC-003) et validation IFRI

---

## Notes

- Chaque test écrit avant son implémentation doit échouer d'abord (TDD)
- Les 10 JSON de `output/` ne sont ni renommés ni migrés (FR-006)
- La validation réelle est limitée à `Interne-Dev/Exemples/IFRI`
  (contrainte utilisateur, décision D8)
- Committer après chaque tâche ou groupe logique (hooks pre-commit actifs)
