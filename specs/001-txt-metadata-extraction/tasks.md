# Tasks: TXT-MetaData — Extraction de métadonnées

**Input**: Design documents from `/specs/001-txt-metadata-extraction/`

**Prerequisites**: plan.md (structure `src/txt_metadata/`, Python 3.11+, SDK
`mistralai`, `python-dotenv`, pytest), spec.md (6 user stories), research.md
(décisions R1 à R9), data-model.md, contracts/, quickstart.md

**Tests**: inclus — la spec exige des tests automatisés (SC-001, SC-004) et des
scénarios de validation (quickstart.md V1 à V5).

**Organization**: tâches groupées par user story, livrables et testables
indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: exécutable en parallèle (fichiers différents, pas de dépendance)
- **[Story]**: user story de la tâche (US1 à US6)
- Chemins exacts dans chaque description

## Phase 1: Setup (Infrastructure partagée)

**Purpose**: initialisation du projet

- [x] T001 Créer `pyproject.toml` : packaging (`src/` layout), dépendances
  `mistralai` et `python-dotenv`, dépendances dev `pytest`, point d'entrée
  console `txt-metadata = txt_metadata.__main__:main`
- [x] T002 [P] Créer la structure `src/txt_metadata/` (`__init__.py`,
  `__main__.py`) et `tests/` (`unit/`, `integration/`) avec `__init__.py` et
  fichiers vides initiaux
- [x] T003 [P] Créer `.env.example` à la racine : `MISTRAL_API_KEY=YOUR_API_KEY`
  (placeholder uniquement, constitution I)

---

## Phase 2: Foundational (Prérequis bloquants)

**Purpose**: socle requis avant toute user story

- [x] T004 [P] Implémenter le chargement de configuration dans
  `src/txt_metadata/config.py` : lecture `.env` (python-dotenv) puis variable
  d'environnement `MISTRAL_API_KEY` ; absente → message explicite et échec
  rapide avant tout appel réseau (code retour 2) ; jamais de clé loguée ni
  persistée
- [x] T005 [P] Implémenter le retry exponentiel dans `src/txt_metadata/retry.py`
  : délai initial paramétrable (défaut 3 s), multiplié par 2 à chaque essai (3,
  6, 12 s), nombre d'essais paramétrable (défaut 3), par appel LLM (FR-019, R3)
- [x] T006 [P] Implémenter le compteur d'occurrence dans
  `src/txt_metadata/counter.py` : fichier `counter.txt` à la racine du projet
  contenant uniquement le numéro à 4 chiffres ; premier usage 0001, +1 par
  nouveau fichier, cycle 0001…9999 puis 0000 ; écriture atomique (temporaire +
  remplacement) après chaque document ; fichier absent → reprise 0001 ;
  illisible/corrompu → échec rapide, aucune écriture (FR-023 à FR-025, R6)
- [x] T007 [P] Créer les entités dans `src/txt_metadata/models.py` :
  `MetadataOutput` (7 clés : `Typologie` obligatoire parmi les 9 valeurs
  Article, Rapport, Ouvrage, Cours, Bibliothèque, Extrait, Communiqué,
  Compte-rendu, Autre ; `Auteur(s)` liste de chaînes ; `Titre` chaîne ≤ 150
  caractères tronquée au-delà ; `Editeur`, `Date`, `Référence`, `Citation`
  chaînes), `RunReport` (statuts succès créé / amendé / échec, messages
  d'erreur), `InputDocument`, `Extrait` (head/tail/ marker/is_full_text)
  conformes à data-model.md
- [x] T008 [P] Implémenter le nommage et l'écriture des sorties dans
  `src/txt_metadata/output.py` : 8 premiers caractères du nom du fichier
  d'entrée sans extension, espaces → `_`, accents simplifiés (é→e), + `-` +
  numéro 4 chiffres + `.json` ; écriture UTF-8 dans le dossier de sortie (défaut
  `output/`, créé automatiquement sans confirmation) (FR-021, FR-022)

**Checkpoint**: socle prêt — les user stories peuvent commencer.

---

## Phase 3: User Story 1 — Métadonnées d'un fichier texte unique (P1) — MVP

**Goal**: pipeline de bout en bout sur un fichier unique : config →
échantillonnage minimal → appel LLM → JSON numéroté dans `output/`.

**Independent Test**: quickstart V1 — `txt-metadata` sur
`Interne-Dev/Exemples/IFRI/IFRI.md` produit un JSON conforme au schéma de sortie
dans `output/`, `counter.txt` créé/incrémenté, code retour 0.

### Tests for User Story 1

- [x] T009 [P] [US1] Test d'intégration du parcours fichier unique dans
  `tests/integration/test_single_file.py` : mock du client LLM, vérifier JSON
  créé, nommage, compteur incrémenté, code retour 0

### Implementation for User Story 1

- [x] T010 [US1] Implémenter le squelette CLI dans `src/txt_metadata/cli.py` :
  argparse, un ou plusieurs chemins positionnels, options avec valeurs par
  défaut (small, 25, 3, 3, output, 0), appel du pipeline
- [x] T011 [US1] Implémenter l'échantillonnage minimal dans
  `src/txt_metadata/sampling.py` : lecture UTF-8 (repli sur encodage détecté),
  extrait 20 000 premiers / 16 000 derniers caractères, texte intégral si
  document plus court que la somme des bornes (FR-002, FR-005)
- [x] T012 [US1] Implémenter l'appel LLM dans `src/txt_metadata/extract.py` :
  SDK `mistralai`, `chat/completions` avec `mistral-small-latest`, température
  0, prompt demandant les 7 champs JSON, intégration du retry T005 (FR-014,
  FR-015)
- [x] T013 [US1] Orchestrer le pipeline dans `src/txt_metadata/__main__.py` :
  config → lecture document → échantillonnage → extraction → validation models →
  numérotation counter → écriture output ; codes retour 0/2 ; branchement du
  point d'entrée console

**Checkpoint**: US1 fonctionnel — MVP validable indépendamment (quickstart V1).

---

## Phase 4: User Story 2 — Échantillonnage du texte (P2)

**Goal**: coupures propres et marquage des deux segments pour que le modèle ne
confonde pas la fin du document avec la suite du début.

**Independent Test**: unitaire — un document long produit un extrait à deux
segments marqués ; les coupures ne séparent jamais un mot et insèrent « ... » si
une phrase est coupée.

### Tests for User Story 2

- [x] T014 [P] [US2] Tests unitaires de la hiérarchie de coupure dans
  `tests/unit/test_sampling.py` : sous-partie, paragraphe, phrase, mot,
  insertion « ... », texte intégral si court

### Implementation for User Story 2

- [x] T015 [US2] Implémenter la hiérarchie de préservation des coupures dans
  `src/txt_metadata/sampling.py` : reculer la coupure vers l'unité la plus large
  sous la borne — sous-partie (titre markdown), à défaut paragraphe (double saut
  de ligne), à défaut phrase (ponctuation finale), à défaut mot ; jamais couper
  un mot ; « ... » inséré si une phrase est séparée (FR-003, R5)
- [x] T016 [US2] Implémenter le dispositif de séparation des segments dans
  `src/txt_metadata/sampling.py` : marqueurs explicites début/fin d'extrait
  entre les deux segments pour que la fin du document ne soit pas lue comme la
  suite hiérarchique du début ; pas de marqueur si texte intégral (FR-004, R5)

**Checkpoint**: US2 fonctionnel et testable indépendamment.

---

## Phase 5: User Story 3 — Identification des métadonnées par LLM (P2)

**Goal**: extraction fiable et sans hallucination, citation exacte ou composée
de façon déterministe.

**Independent Test**: quickstart V5 partiel — sur les exemples avec sortie de
référence, typologies exactes ≥ 8/10 et ≥ 80 % des champs non vides corrects ;
unitaire — citation conforme FR-012.

### Tests for User Story 3

- [x] T017 [P] [US_3] Tests unitaires de la validation d'extraction dans
  `tests/unit/test_extract.py` : enum 9 valeurs, Titre ≤ 150, champs vides si
  absents, rejet des valeurs invalides, plafond 5 appels
- [x] T018 [P] [US_3] Tests unitaires de la citation dans
  `tests/unit/test_citation.py` : composition, guillemets droits, « et al. »
  au-delà de 3 auteurs, ordre d'apparition, référence omise si vide, vide si
  champs insuffisants

### Implementation for User Story 3

- [x] T019 [US_3] Durcir le prompt dans `src/txt_metadata/extract.py` :
  anti-hallucination (ne remplir que ce qui est présent dans l'extrait), schéma
  JSON explicite des 7 clés, définitions des 9 typologies, règles métier auteurs
  (rapporteurs, parlementaires, société/revue) (FR-006 à FR-008, FR-015, R2)
- [x] T020 [US_3] Activer le JSON mode dans `src/txt_metadata/extract.py` :
  `response_format={"type": "json_object"}` et valider la réponse contre
  `MetadataOutput` ; valeurs invalides → rejouage dans la limite de 5 appels LLM
  par document (FR-017, R2)
- [x] T021 [US_3] Implémenter la détection du paragraphe « comment citer » dans
  `src/txt_metadata/citation.py` : si présent, reprise exacte du contenu et du
  format depuis le texte source (recherche locale), et seulement celui-ci
  (FR-011 cas 1, R4)
- [x] T022 [US_3] Implémenter la composition déterministe de la citation dans
  `src/txt_metadata/citation.py` : `<auteur>, <titre>, <référence>, <éditeur>,
  <date>` (référence omise si vide) ; minuscules sauf noms propres, acronymes,
  initiales ; auteurs dans l'ordre d'apparition, dernier relié par « et » si
  noms propres ; plus de trois auteurs → premier + « et al. » ; guillemets
  droits autour du titre ; vide si aucun paragraphe de citation et champs
  insuffisants (FR-011, FR-012, FR-013, R4)

**Checkpoint**: US_3 fonctionnel — extraction et citation robustes.

---

## Phase 6: User Story 4 — Multi-entrées transparent (P3)

**Goal**: un fichier, un dossier ou plusieurs dossiers traités en un processus
unique ; lots de requêtes ; échec sans blocage.

**Independent Test**: quickstart V2 (sans JSON existant) et V3 — un dossier de
10 `.md` produit 10 sorties numérotées séquentiellement ; clé invalide → chaque
document échoue après retries, lot poursuivi, bilan final, code retour 1.

### Tests for User Story 4

- [x] T023 [P] [US4] Tests unitaires de la découverte d'entrées dans
  `tests/unit/test_inputs.py` : filtrage `.md`/`.txt`, ignore les autres
  formats, récursivité sous-dossiers, plusieurs dossiers
- [x] T024 [P] [US4] Tests unitaires du groupement par lots dans
  `tests/unit/test_batch.py` : lots de N, 0 = séquentiel

### Implementation for User Story 4

- [x] T025 [US4] Implémenter la découverte des entrées dans
  `src/txt_metadata/inputs.py` : chemins positionnels (fichiers ou dossiers),
  parcours récursif, filtrage `.md`/`.txt`, silence sur les autres formats,
  détection automatique du mode (FR-001)
- [x] T026 [US4] Implémenter le groupement des appels dans
  `src/txt_metadata/batch.py` : requêtes envoyées par lots de taille
  `--taille-batch` (0–100, défaut 25) en parallèle, chaque requête restant un
  appel individuel ; 0 = une par une (FR-020, R1)
- [x] T027 [US4] Implémenter la politique d'échec en lot dans
  `src/txt_metadata/__main__.py` : échec définitif → journaliser l'erreur,
  poursuivre, aucun fichier ni numéro consommé pour ce document, bilan final
  (créés/amendés/échecs) via `RunReport`, codes retour 0/1/2 (FR-032, R9)

**Checkpoint**: US4 fonctionnel — multi-entrées et résilience.

---

## Phase 7: User Story 5 — Amendement d'un JSON existant (P3)

**Goal**: compléter sur place les sorties existantes sans écraser le travail
manuel.

**Independent Test**: quickstart V2 — un dossier contenant `IFRI.md` et un JSON
partiel au même préfixe : champs vides complétés, champs remplis conservés sauf
haut degré d'assurance, aucune copie dans `output/`, aucun numéro consommé.

### Tests for User Story 5

- [x] T028 [P] [US5] Tests unitaires d'appariement dans
  `tests/unit/test_pairing.py` : lien par préfixe 8 caractères normalisés, paire
  unique dans un sous-dossier, non-appariable traité seul
- [x] T029 [P] [US5] Tests unitaires d'amendement dans
  `tests/unit/test_amend.py` : champs vides complétés en priorité, champs
  remplis remplacés seulement si haut degré d'assurance, écriture sur place,
  sans numéro

### Implementation for User Story 5

- [x] T030 [US5] Implémenter l'appariement texte/JSON dans
  `src/txt_metadata/inputs.py` : lier un `.md`/`.txt` au JSON dont le nom
  commence par les 8 premiers caractères normalisés du nom de base (espaces →
  `_`, accents simplifiés) ; sinon paire unique du sous-dossier ; sinon texte
  traité seul (FR-027, R7)
- [x] T031 [US5] Implémenter l'amendement dans `src/txt_metadata/output.py` :
  fusion des métadonnées — champs vides complétés en priorité ; champs remplis
  challengés seulement à haut degré d'assurance (typologie validée + cohérence
  des champs adjacents) ; écriture sur place à l'emplacement d'origine, sans
  nouveau numéro ni copie dans `output/` (FR-026, R7)

**Checkpoint**: US5 fonctionnel — amendement non destructif.

---

## Phase 8: User Story 6 — Configuration CLI (P4)

**Goal**: options complètes, validation stricte des bornes, journalisation
propre.

**Independent Test**: quickstart — chaque option prise en compte (modèle appelé,
délais de retry observés, dossier de sortie) ; option hors bornes → rejet code 2
avant tout traitement.

### Tests for User Story 6

- [x] T032 [P] [US6] Tests unitaires de validation des options dans
  `tests/unit/test_cli.py` : alias 8 modèles, `--taille-batch` 0–100,
  `--retry-occurences` 0–10, `--retry-time` 1–10, `--temperature-llm` 0–1, rejet
  explicite hors bornes, code 2

### Implementation for User Story 6

- [x] T033 [US6] Implémenter la validation des bornes dans
  `src/txt_metadata/cli.py` : `--choix modèle-llm` (large4, large, medium,
  small, 14b, 8b, 3b, zai → mistral-large-4, mistral-large-latest,
  mistral-medium-latest, mistral-small-latest, ministral-14b-latest,
  ministral-8b-latest, ministral-3b-latest, zai-glm-5-3), `--taille-batch`
  0–100, `--retry-occurences` 0–10, `--retry-time` 1–10, `--output-folder`
  chemin, `--temperature-llm` 0–1 ; hors bornes → message explicite, code 2,
  aucun traitement (FR-028, FR-029, FR-030)
- [x] T034 [US6] Brancher les options sur le pipeline dans
  `src/txt_metadata/__main__.py` : modèle choisi, température, batch, retry
  paramétrés, dossier de sortie personnalisé
- [x] T035 [US6] Implémenter la journalisation dans
  `src/txt_metadata/__main__.py` : progression et erreurs sur stderr, bilan
  final sur stdout, aucune donnée sensible (clé, contenu de document au-delà du
  nécessaire au diagnostic)

**Checkpoint**: US6 fonctionnel — CLI complet et robuste.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [x] T036 [P] Documenter l'usage dans `README.md` : installation, commandes,
  options, format de sortie, compteur
- [x] T037 [P] Revue de conformité constitution : aucun secret ni chemin
  personnel dans le diff, `.gitignore` couvre `.env` et `output/`
- [x] T038 Exécuter la validation complète quickstart V1 à V5 et corriger les
  écarts
- [x] T039 Calibrer sur les 10 exemples (`Interne-Dev/Exemples/`) et produire le
  rapport de test dans `specs/001-txt-metadata-extraction/test-report.md` :
  comparaison aux sorties de référence, documentation des divergences attendues
  (`Grand_Continent_article` : « et al. » ; `IFRI` : guillemets droits ;
  `Corsen_ai` : sans référence), typologies exactes ≥ 8/10 (SC-001)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: aucune dépendance, démarrage immédiat
- **Phase 2 (Foundational)**: dépend de la Phase 1 — BLOQUE toutes les user
  stories
- **Phases 3 à 8 (US1 à US6)**: dépendent de la Phase 2 ; exécution séquentielle
  recommandée dans l'ordre des priorités (US1 → US2 → US_3 → US4 → US5 → US6)
- **Phase 9 (Polish)**: dépend de la complétude des user stories visées

### User Story Dependencies

- **US1 (P1)**: après la Phase 2 ; MVP de bout en bout (pipeline minimal).
  Testable indépendamment via quickstart V1
- **US2 (P2)**: après la Phase 2 ; affine le module sampling de US1 (fichier
  différent de US_3)
- **US_3 (P2)**: après la Phase 2 ; affine extract.py et citation.py
- **US4 (P3)**: après US1 (pipeline de base réutilisé) ; s'appuie sur inputs.py
  et batch.py
- **US5 (P3)**: après US4 (découverte d'entrées réutilisée pour l'appariement)
- **US6 (P4)**: après US1 ; validation et journalisation transverses

### Within Each User Story

- Tests écrits et en échec avant l'implémentation (TDD sur les tâches de test)
- Modèles avant services, services avant orchestration
- Implémentation cœur avant intégration
- Story complète avant la priorité suivante

### Parallel Opportunities

- Phase 1 : T002 et T003 en parallèle
- Phase 2 : T004 à T008 toutes en parallèle (fichiers distincts)
- Phase 3 : T009 en parallèle des tâches d'implémentation US1
- Phase 4 : T014 en parallèle de T015/T016 en cours
- Phase 5 : T017 et T018 en parallèle ; T019 et T020 en parallèle (fichiers
  d'entrée distincts) ; T021 puis T022 séquentiels (même fichier citation.py)
- Phase 6 : T023 et T024 en parallèle ; T025 et T026 en parallèle
- Phase 7 : T028 et T029 en parallèle ; T030 avant T031
- Phase 8 : T032 en parallèle de T033/T034
- Phase 9 : T036 et T037 en parallèle

---

## Parallel Example: User Story 1

```bash
# Lancer les tests US1 ensemble :
Task: "T009 [P] [US1] Test d'intégration du parcours fichier unique dans tests/integration/test_single_file.py"

# Lancer les implémentations US1 en parallèle :
Task: "T011 [US1] Implémenter l'échantillonnage minimal dans src/txt_metadata/sampling.py"
Task: "T012 [US1] Implémenter l'appel LLM dans src/txt_metadata/extract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Compléter la Phase 1 (Setup)
2. Compléter la Phase 2 (Foundational) — bloquant
3. Compléter la Phase 3 (US1)
4. **STOP et VALIDER** : quickstart V1 sur `IFRI.md`
5. Démontrable : un fichier → un JSON numéroté

### Incremental Delivery

1. Setup + Foundational → socle prêt
2. US1 → test V1 → MVP
3. US2 → coupures propres → test unitaire
4. US_3 → extraction robuste + citation → calibration V5
5. US4 → multi-entrées → test V2/V3
6. US5 → amendement → test V2 complet
7. US6 → options complètes → bilan et codes retour
8. Polish → rapport de calibration et quickstart complet

---

## Notes

- [P] = fichiers différents, pas de dépendance
- [Story] = traçabilité vers spec.md
- Committer après chaque tâche ou groupe logique
- S'arrêter aux checkpoints pour valider chaque story indépendamment
- La calibration (T039) ne doit pas durcir l'outil sur les exemples : l'outil
  reste généraliste (spec, Assumptions)
