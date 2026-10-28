# Problem Definition: Sorties JSON difficilement rattachables à leur source

- **Slug**: titre-20-chars
- **Created**: 2026-10-27
- **Inputs used**: intake.md | research.md

## Problem Statement

L'utilisateur de TXT-MetaData ne peut pas identifier visuellement un JSON de
sortie à partir de son nom : le préfixe de 8 caractères tronque des noms de
fichiers d'entrée longs et proches, au point que des sources distinctes
produisent des sorties quasi indiscernables. Cela touche déjà le corpus réel
du dépôt (2 paires de JSON sur 10 partagent des préfixes quasi identiques) et
dégrade le rattachement d'une sortie à son document, sans que l'extraction
elle-même soit en cause.

## Affected Users & Stakeholders

- **Users**: le propriétaire du dépôt, unique utilisateur connu de l'outil —
  il trie et rapproche des dizaines de JSON de sortie dans un dossier
  `output/`, avec des documents d'entrée aux noms longs et structurés
  (`Cour_des_comptes_rapport.md`, `Cour_de_comptes_pagination.md`). —
  [source: research.md, output/, Interne-Dev/Exemples/]
- **Stakeholders**: le propriétaire du dépôt — décideur unique du projet
  (spécifications, priorités). Aucun autre partie prenante identifiée.
  [NEEDS CLARIFICATION: existence d'autres utilisateurs ou destinataires des
  JSON produits]

## Goals

- Chaque JSON de sortie du corpus réel (les 10 exemples du dépôt) doit être
  rattachable à son document source par son seul nom de fichier.
- Les nouveaux noms de sortie restent produits par les mêmes critères que
  aujourd'hui (nom du fichier d'entrée sans extension, espaces remplacées
  par `_`, accents simplifiés) — seule la longueur retenue change.
- L'amendement des JSON existants (FR-026) continue de fonctionner sur les
  corpus déjà traités.

## Non-Goals

- Ne pas changer les autres critères de nommage : normalisation (espaces,
  accents), format `<préfixe>-<NNNN>.json`, numérotation séquentielle et
  compteur d'occurrence (FR-023 à FR-025).
- Ne pas toucher à l'extraction, aux prompts, aux modèles LLM, au batch ni
  à l'interface CLI.
- Ne pas renommer ni migrer les JSON déjà produits dans `output/`
  (FR-031 : un JSON conserve son nom d'origine une fois créé).
- Ne pas rendre l'appariement tolerant aux ambiguïtés au-delà du
  comportement actuel (un appariement ambigu reste non lié).

## Success Metrics

- Paires de sorties indiscernables par leur préfixe sur le corpus des
  10 exemples : 0 (baseline : 2 paires — `Cour_des`/`Cour_de_` et
  `Ecalle_c`/`Ecalle_o`). (mesurable)
- Suites de tests sans régression de l'appariement d'amendement
  (baseline : 92 tests au vert sur main). (mesurable)
- README, spec FR-022 et contrat de sortie décrivent le comportement réel
  de nommage, sans divergence. (mesurable, baseline : 4 documents
  décrivent « 8 premiers caractères » aujourd'hui)

## Cost of Inaction

Les sorties restent identifiables seulement en ouvrant le JSON ou en
maintenant une correspondance mentale fichier ↔ source ; le risque de
confondre deux documents d'une même série (rapports de la Cour des comptes,
ouvrages d'un même auteur) persiste et s'aggrave à mesure que le corpus
grossit. L'appariement d'amendement reste fonctionnel mais aveugle sur des
préfixes ambigus, et l'ambiguïté est gérée par refus d'appariement, ce qui
prive certains documents d'amendement. — [source: research.md]

## Open Questions

- [NEEDS CLARIFICATION: « titre de l'entrée » = nom du fichier d'entrée
  (lecture de FR-022 et de l'implémentation actuelle, la plus probable) ou
  champ `Titre` extrait par le LLM ?]
- [NEEDS CLARIFICATION: l'appariement doit-il suivre à 20 (constante
  partagée) ou rester à 8 pour préserver l'amendement des JSON existants ?]
- [NEEDS CLARIFICATION: que faire des JSON déjà produits — cohabitation
  (suggérée par FR-031), renommage manuel, ou autre ?]
