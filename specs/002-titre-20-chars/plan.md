# Implementation Plan: TXT-MetaData — Préfixe de 20 caractères

**Branch**: `003-titre-20-car` | **Date**: 2026-10-27 | **Spec**:
[spec.md](./spec.md)

**Input**: Feature specification from
`/specs/002-titre-20-chars/spec.md`

## Summary

Les nouvelles sorties JSON sont nommées sur les 20 premiers caractères
normalisés du nom du fichier d'entrée (au lieu de 8), sans autre changement
des critères de nommage. L'appariement d'amendement reconnaît un JSON
candidat dès 8 caractères partagés et prolonge l'analyse jusqu'à 20 : le
nom du JSON candidat est normalisé, le candidat retenu est celui qui
partage le préfixe commun le plus long avec le document (égalité parfaite →
non-liage). Aucune dépendance nouvelle : le changement se concentre dans
`src/txt_metadata/output.py` (longueur de nommage), `src/txt_metadata/
inputs.py` (appariement progressif), les tests concernés et les documents
de référence. Validation sur l'exemple réel `Interne-Dev/Exemples/IFRI`
uniquement (contrainte utilisateur), complétée par un document à nom long
synthétique pour démontrer l'effet des 20 caractères.

## Technical Context

**Language/Version**: Python 3.11+ (inchangé ; Ruff et pre-commit déjà
configurés dans le dépôt)

**Primary Dependencies**: aucune nouvelle. Les dépendances existantes
(`mistralai`, `python-dotenv`) ne sont pas touchées par cette feature ;
nomenclature et appariement sont du pur stdlib (`pathlib`, `unicodedata`).

**Storage**: inchangé — JSON de sortie dans le dossier de sortie (défaut
`output/`), compteur d'occurrence à la racine, JSON existants amendés sur
place dans leur dossier d'origine.

**Testing**: pytest. Tests unitaires existants à mettre à jour
(`tests/unit/test_output.py`, `tests/unit/test_pairing.py`), tests
d'intégration à mettre à jour (`tests/integration/test_multi.py`), nouveaux
tests pour FR-001 à FR-005 et les cas d'égalité. LLM simulé (aucun appel
réel en CI) ; calibration sur l'exemple réel limitée à
`Interne-Dev/Exemples/IFRI`.

**Target Platform**: CLI multiplateforme (Windows/Linux/macOS),
local-first — inchangé.

**Project Type**: cli

**Performance Goals**: aucun objectif nouveau — nommage et appariement
sont des opérations locales sur des noms de fichiers (coût négligeable).

**Constraints**: limites de longueur de chemin (Windows : 260 caractères
par défaut ; +12 caractères max par nom de sortie) ; aucune clé ni chemin
personnel dans le code ; offline pour toutes les parties locales.

**Scale/Scope**: corpus typique de 1 à quelques centaines de documents ;
le préfixe est plafonné à 20 caractères par document.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Isolation des secrets — PASS** : aucun secret manipulé par cette
  feature (noms de fichiers uniquement).
- **II. Local-first & confidentialité — PASS** : aucune donnée ne quitte
  la machine ; aucun appel réseau ajouté ou modifié.
- **III. Open-source & sans trackers — PASS** : aucune dépendance nouvelle.
- **IV. Simplicité (YAGNI) — PASS** : pas d'option CLI de longueur de
  préfixe (rejetée explicitement), pas d'abstraction nouvelle : deux
  constantes et la fonction de comparaison existante.
- **Path Isolation — PASS** : les chemins restent résolus depuis les
  options CLI ; aucun chemin personnel codé en dur.
- **Network Surface — PASS** : surface réseau inchangée (API Mistral
  uniquement, non concernée par cette feature).
- **Data Retention — PASS** : aucun renommage ni copie des JSON existants
  (FR-006).

Aucune violation à justifier.

## Project Structure

### Documentation (this feature)

```text
specs/002-titre-20-chars/
├── plan.md              # Ce fichier
├── research.md          # Phase 0 : décisions fondées
├── data-model.md        # Phase 1 : entités du nommage/appariement
├── quickstart.md        # Phase 1 : guide de validation (exemple IFRI)
├── contracts/
│   └── naming-and-pairing.md  # Contrat de nommage et d'appariement
└── tasks.md             # Sortie de /speckit-tasks (non créé ici)
```

### Source Code (repository root)

```text
src/txt_metadata/
├── output.py            # _PREFIX_LENGTH (nommage) → 20 ; output_prefix
├── inputs.py            # pair_documents : appariement progressif 8→20

tests/
├── unit/
│   ├── test_output.py   # Préfixe 20 : assertions à mettre à jour
│   └── test_pairing.py  # Appariement progressif : à mettre à jour + cas neufs
├── integration/
│   ├── test_multi.py    # Noms de sortie à 20 : assertions à mettre à jour
│   └── test_single_file.py

# Documents de référence à mettre à jour (FR-008)
README.md
specs/001-txt-metadata-extraction/spec.md            # FR-022
specs/001-txt-metadata-extraction/contracts/output-schema.md

# Exemple réel de validation (contrainte utilisateur)
Interne-Dev/Exemples/IFRI/IFRI.md
```

**Structure Decision** : structure existante du dépôt reprise telle quelle
(paquet unique `src/txt_metadata`, tests unit/intégration) ; aucun nouveau
répertoire hors `specs/002-titre-20-chars/contracts/`.

## Suivi de complexité

> Aucune violation de la constitution à justifier — section vide.
