# Idea Intake: Préfixe de 20 caractères pour la sortie JSON

- **Slug**: titre-20-chars
- **Created**: 2026-10-27
- **Source**: pasted text (repo : TXT-MetaData, branche `003-readme`)
- **Type**: improvement

## Idea (as captured)

> Je souhaiterais que la sortie .json prenne les 20 premiers au lieux des 8
> premiers caractères du titre de l'entrée, sans changer le reste de l'outil
> ni les autre critères de création du titre.

## Restated

Le nom du fichier JSON produit par TXT-MetaData utiliserait les 20 premiers
caractères du « titre de l'entrée » au lieu des 8 premiers, sans modifier les
autres règles de construction de ce nom ni le comportement de l'outil.

## Origin & Context

- **Raised by**: l'utilisateur (propriétaire du dépôt), via la commande
  `/speckit-assess-intake`
- **Trigger**: [NEEDS CLARIFICATION: ce qui a motivé le changement — collisions
  de préfixes à 8 caractères ? lisibilité des noms de fichiers ?]

Contexte code (lecture seule, pour situer l'idée) :

- `src/txt_metadata/output.py` : `_PREFIX_LENGTH = 8` ; `output_prefix()` prend
  les 8 premiers caractères normalisés du nom du fichier d'entrée sans
  extension (espaces remplacées par `_`, accents simplifiés — FR-022) ; le
  fichier de sortie est `<préfixe>-<NNNN>.json`.
- `src/txt_metadata/inputs.py` : l'appariement d'amendement d'un JSON existant
  se fait par préfixe de 8 caractères normalisés.
- Documenté dans `README.md` et `specs/001-txt-metadata-extraction/`
  (FR-021/FR-022, `contracts/output-schema.md`).

## First-Glance Unknowns

- [NEEDS CLARIFICATION: « titre de l'entrée » désigne-t-il le nom du fichier
  d'entrée (comme aujourd'hui dans `output_prefix`, basé sur `input_path.stem`)
  ou le champ `title` extrait par le LLM dans les métadonnées ?]
- [NEEDS CLARIFICATION: l'appariement d'amendement dans `inputs.py` (préfixe
  de 8 caractères) doit-il passer à 20 aussi, ou rester à 8 alors que le
  nommage passe à 20 ? Passer le nommage à 20 sans toucher l'appariement
  change la relation « nom de fichier ↔ JSON existant » et peut empêcher
  d'amender des JSON existants.]
- [NEEDS CLARIFICATION: que faire des fichiers JSON existants déjà nommés
  avec un préfixe de 8 caractères — renommage, cohabitation, ou aucune
  migration ?]
- [NEEDS CLARIFICATION: les règles de normalisation (espaces → `_`,
  simplification des accents) et le plafond restent-ils inchangés
  (l'utilisateur indique oui, à confirmer) ?]
- [NEEDS CLARIFICATION: mise à jour documentaire attendue (README, spec
  FR-022, contrat de sortie, tests existants sur la longueur du préfixe) ?]
