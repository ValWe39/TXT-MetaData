# Concept: Paires autonomes source + métadonnées en sortie

- **Slug**: option-sous-dossiers
- **Created**: 2026-10-28
- **Recommended option**: B — Sous-dossier par document au moment de la création

## Options

### Option A — Ne rien construire (statu quo)

- **Sketch** : aucun changement d'outil. L'utilisateur continue de
  rassembler manuellement le JSON et sa source quand il a besoin d'une
  paire (archivage, partage), ou de deviner la source par le préfixe de
  20 caractères.
- **Appetite**: none
- **Trade-offs** : gagne zéro coût de développement et zéro risque ;
  sacrifie tout l'objectif du problème — la paire reste non autonome,
  les copies manuelles continuent, les JSON dont la source bouge
  deviennent orphelins (coût de l'inaction, problem.md).
- **Rabbit holes** : aucun.

### Option B — Sous-dossier par document au moment de la création

- **Sketch** : un flag optionnel de la CLI active un rangement en
  paires : à la création d'un JSON, celui-ci est placé dans une unité de
  rangement unique nommée d'après le numéro d'occurrence du document,
  accompagné d'une copie de son fichier source (`.md` ou `.txt`), copie
  portant le nom d'origine. Sans le flag, rien ne change : layout plat
  actuel, aucun fichier existant déplacé. L'amendement utilise les
  mécanismes existants : relancer l'outil sur l'unité de rangement
  amende le JSON sur place via le repli « paire unique du sous-dossier »
  (FR-027) ; relancer sur la source d'origine crée une nouvelle paire.
- **Appetite**: small (quelques jours : 1 module de sortie à étendre,
  1 option CLI, tests et documentation)
- **Trade-offs** : gagne la paire autonome demandée, avec le plus petit
  changement possible — aucun impact sur le mode par défaut, aucun
  renommage existant, réutilisation directe du repli d'appariement déjà
  implémenté (research.md, Prior Art). Sacrifie : la sémantique
  d'amendement devient asymétrique (relancer la source d'origine
  consomme un nouveau numéro au lieu d'amender — research.md, Data &
  Constraints) ; la copie est figée à la création et peut diverger de la
  source ; le dossier de sortie contient désormais des copies `.md`
  qui seraient retraitées si un scan récursif couvrait la sortie et les
  sources ensemble.
- **Rabbit holes** : le débat sur le nom exact de l'unité (numéro seul
  vs lisible) ; vouloir « réparer » l'asymétrie d'amendement (glissement
  vers l'option C) ; vouloir synchroniser la copie à chaque amendement.

### Option C — Unités autonomes avec appariement étendu

- **Sketch** : comme B, plus : l'unité de rangement porte un nom lisible
  (ex. dérivé du préfixe et du numéro), et l'appariement d'amendement
  apprend à retrouver le JSON d'une paire à partir de la source
  d'origine (recherche dans les unités existantes), pour que relancer la
  source amende sa paire au lieu de créer un doublon.
- **Appetite**: medium (le cœur reste petit, mais l'extension de
  l'appariement touche `pair_documents`, le contrat 002 et sa suite de
  tests)
- **Trade-offs** : gagne la cohérence d'amendement et des noms
  lisibles ; sacrifie la simplicité : modification des règles
  d'appariement du mode par défaut (contrat 002), surface de tests et
  de documentation nettement plus large, risque d'ambiguïtés nouvelles
  (plusieurs sources de même préfixe dispersées dans des unités).
- **Rabbit holes** : refonte de l'appariement (recherche récursive,
  priorités, égalités) ; questions de migration des usages existants ;
  gonflement du contrat de nommage.

## Recommendation

Recommander **l'option B**. Elle couvre l'objectif central du problème
(paire autonome, zéro manipulation manuelle — problem.md, Goals) avec
l'appétit le plus petit et sans toucher aux non-goals (layout par défaut
inchangé, rien de renommé ni déplacé). La métrique « sans l'option, un
run produit un layout strictement identique à aujourd'hui » est
structurellement satisfaite, et l'exemple IFRI (paire `IFRI.md` +
`IFRI-00NN.json`) en est la démonstration directe. L'asymétrie
d'amendement que B assume est le prix raisonnable d'un premier pas :
si elle devient douloureuse à l'usage, l'extension de l'appariement de
l'option C constitue un incrément ultérieur indépendant, pas un
prérequis. Le nom exact de l'unité de rangement et le sort de la
décision FR-026 sont des arbitrages de spécification, pas de concept.

## Out of Scope (for the recommended option)

- Migration ou réorganisation des 10 JSON existants de `output/` (restent
  à plat).
- Tout changement du mode par défaut : nommage, numérotation, format
  JSON, appariement, dossier de sortie par défaut.
- Extension de l'appariement d'amendement : relancer la source d'origine
  crée une nouvelle paire ; retrouver la paire depuis la source (option C)
  est hors périmètre.
- Synchronisation copie/source : la copie est figée à la création, jamais
  mise à jour ensuite.
- Généralisation : zéro option de configuration du rangement au-delà du
  flag (choix du nom, exclusions, filtrage).

## Assumptions to Validate

- La copie figée à la création suffit au besoin d'archivage (aucune
  attente de synchronisation après amendement de la source).
- L'usage normal ne scanne jamais récursivement un chemin couvrant à la
  fois les sources et le dossier de sortie — sinon les copies seraient
  retraitées (research.md, boucle de rétroaction).
- La décision FR-026 « aucune copie dans le dossier de sortie » sera
  explicitement reconsidée/tranchée en spécification pour les créations.
- L'unité de rangement se crée sous le dossier configuré par
  `--output-folder`, sans interaction particulière.
- La collision de noms d'unités après un cycle complet du compteur
  (> 10 000 sorties au même endroit) est acceptée telle quelle ou tranchée
  en spécification.
