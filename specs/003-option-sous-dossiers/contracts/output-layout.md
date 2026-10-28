# Contrat de rangement en sortie — option --sous-dossiers

**Feature**: specs/003-option-sous-dossiers | **Date**: 2026-10-28

Contrat comportemental exposé à l'utilisateur du CLI `txt-metadata` :
l'option `--sous-dossiers` et le layout des unités de rangement. Il
complète le contrat CLI de la spécification 001
(`specs/001-txt-metadata-extraction/contracts/cli-contract.md`) dont la
section « Options » est amendée par la présente, et le contrat de nommage
de la spécification 002
(`specs/002-titre-20-chars/contracts/naming-and-pairing.md`), inchangé.

## 1. Option

```text
txt-metadata [OPTIONS] CHEMIN... [--sous-dossiers]
```

- `--sous-dossiers` : flag booléen, sans valeur, **inactif par défaut**.
  Présence = actif, absence = inactif (FR-001).
- Sans l'option : comportement strictement inchangé — sorties à plat
  dans le dossier de sortie, aucun fichier existant renommé, recréé ou
  déplacé (FR-005).

## 2. Layout d'une unité (option active, création uniquement)

```text
<dossier de sortie>/
├── <sorties existantes, à plat, inchangées>
└── <NNNN>-<prefixe>/
    ├── <prefixe>-<NNNN>.json
    └── <nom d'origine du fichier source>
```

- `NNNN` : numéro d'occurrence à 4 chiffres attribué au document (règles
  FR-023 à FR-025 de la spécification 001, inchangées).
- `prefixe` : préfixe normalisé du nom d'entrée, identique à celui du
  nom du JSON (espaces → `_`, accents simplifiés, 20 premiers
  caractères, nom complet si plus court — FR-022 spec 001).
- Le JSON garde son nom (`<prefixe>-<NNNN>.json`) ; seul son rangement
  change (FR-004).
- La copie porte le **nom d'origine** du fichier source et son contenu
  est **identique octet pour octet** à la création (FR-003), pour `.md`
  comme pour `.txt`.

Exemples (numéros indicatifs, compteur à 0067 à la rédaction) :

| Fichier d'entrée | Unité créée | JSON dans l'unité |
| --- | --- | --- |
| `IFRI.md` | `0068-IFRI/` | `IFRI-0068.json` |
| `Ecalle_cours.md` | `0069-Ecalle_cours/` | `Ecalle_cours-0069.json` |

Chaque unité contient aussi la copie du fichier source sous son nom
d'origine (FR-003). Exemple long : `Cour des comptes rapport.md` → unité
`0070-Cour_des_comptes_rappo/` contenant `Cour_des_comptes_rappo-0070.json`
et la copie `Cour des comptes rapport.md`.

## 3. Portée : créations uniquement

- L'option ne s'applique qu'aux **nouvelles sorties**. Un JSON apparié
  dans un dossier d'entrée est amendé sur place à son emplacement
  d'origine, sans unité, sans copie, sans numéro consommé (FR-006,
  FR-026/FR-027 spec 001 inchangés).
- Un document en échec ne laisse aucune trace : ni unité, ni copie, ni
  numéro consommé (FR-007).

## 4. Amendement d'une paire rangée

Relancer l'outil sur une unité (qui contient une copie et un JSON au
format de sortie) amende le JSON **sur place**, par le repli « paire
unique du sous-dossier » (FR-027 spec 001) :

- le JSON conserve son nom et son numéro ; aucun numéro consommé ;
- la copie de la source est inchangée, octet pour octet (FR-008).

Relancer l'outil sur la **source d'origine** (hors unité) crée une
nouvelle paire avec un nouveau numéro : asymétrie assumée par la décision
d'évaluation (option B).

## 5. Exclusion du dossier de sortie de la découverte

Quand un chemin d'entrée couvre le dossier de sortie, le dossier de
sortie (chemin résolu) est exclu de la découverte des documents, que
l'option soit active ou non (FR-011) : les copies présentes dans les
unités ne sont jamais traitées comme des entrées.

## 6. Cas limites

- Unité de nom déjà existant (collision après un cycle complet du
  compteur, > 10 000 sorties au même endroit) : le JSON est écrit dans
  l'unité existante et la copie existante est écrasée — cohérent avec
  l'écrasement d'un JSON de nom identique en mode plat.
- Source illisible : échec avant création (aucune unité, aucun numéro
  consommé).
- `--output-folder` : les unités sont créées sous le dossier configuré,
  créé automatiquement s'il est absent (FR-009).

## 7. Codes retour et journalisation

Inchangés (contrat CLI spec 001) : 0 = tout réussi, 1 = au moins un
échec, 2 = erreur fatale avant traitement. La ligne de bilan « créé : … »
indique le chemin complet du JSON, unité comprise (ex.
`output/0068-IFRI/IFRI-0068.json`).
