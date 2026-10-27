# Data Model — Préfixe de 20 caractères

**Feature**: specs/002-titre-20-chars | **Date**: 2026-10-27

Le modèle étend les entités de la spécification 001 (InputDocument, Sortie
JSON, Paire texte/JSON) sans en créer de nouvelles : seul le calcul du
préfixe et la sélection d'appariement changent.

## Entités

### NomSource

Nom du fichier d'entrée sans extension, source unique du préfixe.

- **Attributs** :
  - `brut` : nom du fichier sans extension, tel que lu sur le disque.
  - `normalise` : `brut` avec espaces remplacées par `_` et accents
    simplifiés (règle existante, inchangée).
  - `prefixe` : `normalise` tronqué à 20 caractères (si plus court, pris
    tel quel — FR-002).
- **Règles de validation** :
  - `prefixe` n'est jamais vide (un fichier d'entrée a toujours un nom).
  - La troncature compte chaque caractère normalisé, underscore inclus.
- **Cycle de vie** : calculé au moment du nommage de la sortie ; jamais
  persisté.

### NomSortie

Nom du nouveau fichier de sortie.

- **Attributs** :
  - `prefixe` : le `prefixe` de NomSource.
  - `occurrence` : numéro séquentiel à 4 chiffres (règle 001 inchangée,
    FR-007).
- **Format** : `<prefixe>-<NNNN>.json` (FR-001).
- **Invariants** :
  - Jamais renommé après création, y compris lors d'un amendement (FR-006).
  - Aucun padding ni complément si `prefixe` < 20 caractères (FR-002).

### CandidatAppariement

JSON existant au format de sortie, évalué pour un amendement.

- **Attributs** :
  - `chemin` : fichier JSON candidat dans le dossier du document.
  - `format_valide` : reconnaissable comme sortie de l'outil (règle de
    chargement existante, inchangée).
  - `nom_normalise` : nom du fichier sans extension, normalisé (espaces →
    `_`, accents simplifiés — décision D4 de research.md).
  - `longueur_commune` : longueur du préfixe commun entre `nom_normalise`
    et le `prefixe` du document, plafonnée à 20.
- **Règles de validation** :
  - Candidat reconnu si `longueur_commune` >= 8, ou >= la longueur du
    `prefixe` si celui-ci compte moins de 8 caractères (FR-003).
- **Cycle de vie** : évalué pour un document donné, jamais persisté.

### PaireTexteJSON

Association document → JSON à amender.

- **Attributs** :
  - `document` : le document d'entrée.
  - `cible` : le CandidatAppariement retenu, ou aucun.
- **Règles de sélection** (par document, FR-003 à FR-005) :
  1. Parmi les candidats reconnus, retenir celui de `longueur_commune`
     maximale.
  2. En cas d'égalité parfaite entre plusieurs candidats : aucun retenu, le
     document est traité seul.
  3. À défaut de candidat reconnu, appliquer le repli « paire unique du
     sous-dossier » existant (D6).
- **Cycle de vie** : éphémère pendant une exécution ; l'amendement est
  ensuite écrit sur place, sans numéro consommé (règle 001 inchangée).

## Exemples de référence (corpus réel)

| Nom d'entrée | Préfixe 8 (avant) | Préfixe 20 (après) |
| --- | --- | --- |
| Cour_des_comptes_rapport.md | Cour_des | Cour_des_comptes_rappo |
| Cour_de_comptes_pagination.md | Cour_de_ | Cour_de_comptes_pagin |
| IFRI.md | IFRI | IFRI |

Le tableau illustre SC-001 : la paire `Cour_des`/`Cour_de_` devient
distinguable ; `IFRI` (nom court) est inchangé (FR-002).
