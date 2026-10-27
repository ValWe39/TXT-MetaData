# Contrat de nommage et d'appariement des sorties

**Feature**: specs/002-titre-20-chars | **Date**: 2026-10-27

Contrat comportemental exposé à l'utilisateur du CLI `txt-metadata` : le nom
des nouveaux fichiers de sortie et la sélection des JSON existants à
amender. Il complète le contrat de sortie JSON de la spécification 001
(`specs/001-txt-metadata-extraction/contracts/output-schema.md`) dont la
section « nom du fichier » est amendée par la présente.

## 1. Nommage d'une nouvelle sortie

Le nom d'un nouveau fichier de sortie est :

```text
<préfixe>-<NNNN>.json
```

- **préfixe** : les 20 premiers caractères du nom du fichier d'entrée sans
  extension, normalisés (espaces remplacées par `_`, accents simplifiés) ;
  si le nom normalisé compte moins de 20 caractères, il est pris en entier.
- **NNNN** : numéro d'occurrence à 4 chiffres, séquentiel et persistant
  (règles FR-023 à FR-025 de la spécification 001, inchangées).

Exemples :

| Fichier d'entrée | Nom de sortie |
| --- | --- |
| `Cour des comptes rapport.md` | `Cour_des_comptes_rappo-0001.json` |
| `IFRI.md` | `IFRI-0002.json` |
| `première séance.md` | `premiere_seance-0003.json` |

## 2. Appariement d'un JSON existant (amendement)

Pour chaque document d'entrée, les JSON existants au format de sortie du
même dossier sont évalués ainsi :

1. **Normalisation du candidat** : le nom du fichier JSON sans extension est
   normalisé (espaces → `_`, accents simplifiés) avant toute comparaison.
2. **Reconnaissance (à partir de 8)** : un candidat est reconnu si son nom
   normalisé partage au moins les 8 premiers caractères du nom normalisé du
   document — ou le nom complet du document si celui-ci compte moins de 8
   caractères.
3. **Prolongation (jusqu'à 20)** : parmi les candidats reconnus, celui qui
   partage le préfixe commun le plus long avec le nom du document (plafonné
   à 20 caractères) est retenu et amendé sur place.
4. **Égalité parfaite** : si plusieurs candidats partagent exactement le
   même préfixe commun le plus long, aucun n'est retenu ; le document est
   traité seul.
5. **Repli** : à défaut de candidat reconnu, la règle existante « paire
   unique du sous-dossier » (un seul document et un seul JSON dans le
   dossier) s'applique, inchangée.

Un JSON amendé conserve son nom d'origine et ne consomme aucun numéro
d'occurrence (FR-031 de la spécification 001, inchangée).

## 3. Exemples d'appariement

- `Rapport info.md` + ancien `Rapport_-0001.json` → apparié : 8 caractères
  partagés, candidat unique.
- `Rapport info.md` + `Rapport_-0001.json` + `Rapport_info-0007.json` →
  le nouveau (12 caractères partagés) est retenu ; l'ancien est ignoré.
- `Rapport info.md` + `Rapport infó-0002.json` (nom accentué) → apparié :
  le nom du JSON est normalisé avant comparaison.
- `Rapport A.md` et `Rapport B.md` + `Rapport-0001.json` → aucun
  appariement : candidat unique partagé par deux documents (égalité).

## 4. Compatibilité et périmètre

- Aucun JSON existant n'est renommé, recréé ou déplacé.
- La longueur du préfixe (20) et la fenêtre de reconnaissance (8 à 20) ne
  sont pas configurables par option CLI.
- Ce contrat ne modifie ni le format JSON, ni la numérotation, ni la
  fusion d'amendement décrits par la spécification 001.
