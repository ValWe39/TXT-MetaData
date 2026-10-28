# Data Model — Option --sous-dossiers

**Feature**: specs/003-option-sous-dossiers | **Date**: 2026-10-28

Le modèle étend les entités de la spécification 001 (InputDocument,
Sortie JSON, PaireTexteJSON) sans modifier les règles existantes :
l'unité de rangement et la copie de source sont nouvelles, le nommage et
l'appariement restent ceux du contrat 002.

## Entités

### UniteRangement

Sous-dossier du dossier de sortie, unique par document créé.

- **Attributs** :
  - `nom` : `NNNN-<prefixe>` — numéro d'occurrence à 4 chiffres, suivi
    d'un tiret puis du préfixe normalisé du nom d'entrée (même préfixe
    que le JSON, FR-002).
  - `chemin` : dossier de sortie + `nom` (FR-009).
  - `json` : chemin du JSON de sortie dans l'unité (nom inchangé,
    FR-004).
  - `copie` : chemin de la copie de la source dans l'unité (FR-003).
- **Règles de validation** :
  - `nom` n'est jamais vide ; le numéro est celui attribué au document
    (unique au sein d'une exécution, verrou du compteur).
  - À la création, l'unité contient exactement le JSON et la copie.
  - Si l'unité existe déjà (collision de cycle ou création manuelle) :
    le JSON est écrit par-dessus et la copie existante est écrasée
    (D2, cas limite de la spec).
- **Cycle de vie** : créée à la création d'une sortie avec l'option
  active ; jamais renommée ni déplacée ensuite ; amendable in place via
  le repli « paire unique » (D5).

### CopieSource

Réplique exacte du fichier d'entrée, figée à la création.

- **Attributs** :
  - `source` : chemin du fichier d'entrée (`.md` ou `.txt`, FR-003).
  - `nom` : nom d'origine du fichier, conservé tel quel.
  - `contenu` : octets du fichier au moment de la création, identiques
    à la source.
- **Règles de validation** :
  - Créée en même temps que le JSON, dans la même unité (FR-003).
  - Jamais modifiée, recréée ni supprimée par un amendement (FR-008).
  - Un échec de lecture du source échoue avant la création : aucune
    unité, aucun numéro consommé (FR-007, D4).
- **Cycle de vie** : figée à la création ; divergence avec la source
  possible ensuite (hypothèse documentée de la spec).

### OptionSousDossiers

Flag CLI booléen.

- **Attributs** :
  - `active` : booléen, défaut `False` (FR-001).
- **Règles de validation** :
  - Sans valeur ni paramètre : présence = active, absence = inactive.
  - Hors bornes : sans objet (pas de validation de bornes).
- **Portée** : le rangement en unités ne s'applique qu'aux créations ;
  l'amendement, la numérotation et l'appariement sont inchangés
  (FR-006).

## Relations

- `InputDocument` 1 — 0..1 `UniteRangement` : un document créé avec
  l'option produit exactement une unité ; un document amendé n'en
  produit aucune.
- `UniteRangement` 1 — 1 `Sortie JSON` (spécification 001) : le JSON
  garde son nom (`<prefixe>-<NNNN>.json`), seul son rangement change.
- `UniteRangement` 1 — 1 `CopieSource`.
- `PaireTexteJSON` (spécification 001) : inchangée ; le repli « paire
  unique du sous-dossier » reconnaît naturellement une unité
  (1 document + 1 JSON dans un même dossier).

## Exemples de référence (corpus réel)

| Nom d'entrée | Unité créée | Contenu de l'unité |
| --- | --- | --- |
| IFRI.md | 0068-IFRI | IFRI-0068.json + IFRI.md (copie) |
| Ecalle_cours.md | 0069-Ecalle_cours | Ecalle_cours-0069.json + copie |

Les numéros 0068/0069 sont indicatifs (compteur à 0067 au moment de la
rédaction). `Ecalle_cours` (12 caractères) reste distinct de
`Ecalle_ouvrage` (`Ecalle_o`) : les unités ne se confondent pas.
