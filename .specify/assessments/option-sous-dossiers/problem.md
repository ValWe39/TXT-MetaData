# Problem Definition: Sorties non autonomes — le JSON produit est séparé de sa source

- **Slug**: option-sous-dossiers
- **Created**: 2026-10-28
- **Inputs used**: intake.md | research.md

## Problem Statement

L'unique utilisateur de TXT-MetaData obtient, après traitement, des
métadonnées JSON rangées à plat dans un dossier de sortie
(`output/`, 10 JSON réels) pendant que les documents sources `.md`/`.txt`
vivent ailleurs (`Interne-Dev/Exemples/`) : la paire « source ↔
métadonnées » n'est pas autonome, et la reconstituer (archivage, partage,
relecture côte à côte) exige aujourd'hui une copie manuelle ou une
reconnaissance par préfixe de nom de fichier.

## Affected Users & Stakeholders

- **Users** : le propriétaire-opérateur du CLI (unique utilisateur
  identifié, demandeur du intake) — il doit rassembler manuellement le
  JSON et sa source pour archiver ou exploiter un document traité. —
  [source: research.md, Users & Demand]
- **Stakeholders** : le propriétaire du dépôt — décideur unique du
  périmètre ; les consommateurs futurs des dossiers de sortie
  (relecture humaine, tests, scripts) — impactés par tout changement de
  layout, mais aucun consommateur tiers identifié aujourd'hui. —
  [source: research.md, ASSUMPTION sur les consommateurs futurs]

## Goals

- Chaque document traité peut être archivé ou partagé comme une paire
  autonome « source + métadonnées », sans manipulation manuelle.
- La possibilité est facultative : le comportement actuel (sortie à
  plat) reste disponible et inchangé pour ceux qui n'en veulent pas. —
  [source: intake.md, « commande optionelle »]
- Aucun fichier existant n'est renommé, recréé ou déplacé. — [source:
  research.md, contrat 002 §4]

## Non-Goals

- Migrer ou réorganiser les JSON déjà présents dans `output/` (les 10
  sorties existantes restent à plat).
- Modifier le format JSON, la numérotation d'occurrence (FR-023 à
  FR-025) ou les règles de nommage et d'appariement du mode par défaut
  (contrat 002).
- Faire de TXT-MetaData un outil de gestion de fichiers général
  (synchronisation copie/source, détection de doublons, nettoyage).
- Changer la sémantique de l'amendement sur place (FR-026) pour les
  dossiers d'entrée existants.

## Success Metrics

- Après un traitement avec l'option, chaque nouvelle paire « source +
  JSON » est retrouvée sans étape manuelle, dans une unité de rangement
  unique par document (qualitatif aujourd'hui : la mesure précise
  dépendra du choix de rangement retenu en spécification). (baseline :
  0 paire autonome ; 100 % de copie manuelle)
- Le résultat de l'exemple réel IFRI : le JSON issu de `IFRI.md` et son
  source forment une unité autonome identifiable. (baseline : JSON seul
  dans `output/`, source dans `Interne-Dev/Exemples/IFRI/`)
- Sans l'option, un run produit un layout strictement identique à
  aujourd'hui : les 96 tests existants restent au vert sans
  modification de leurs assertions de layout par défaut. (baseline :
  96 tests verts)
- Aucun JSON existant déplacé : le contenu de `output/` avant/après
  installation de l'option est identique en dehors des nouvelles
  sorties. (baseline : 10 JSON à plats inchangés)

## Cost of Inaction

La paire « source ↔ métadonnées » reste à reconstituer à la main à
chaque besoin d'archivage ou de partage ; un JSON dont la source est
déplacée ou renommée devient orphelin (seul le préfixe de 20 caractères
permet de deviner la source, et il n'est pas fiable pour les noms
proches). — [source: research.md, Market & Context ; ex.
`Cour_des-0037.json` vs `Cour_de_-0039.json`]

## Open Questions

- [NEEDS CLARIFICATION: rangement exact — le research n'a pas tranché
  l'identité de l'unité autonome (nom du sous-dossier : numéro seul ou
  lisible, etc.) ; décision de spécification, pas de problème.]
- [NEEDS CLARIFICATION: sémantique d'amendement — re-traiter la source
  d'origine doit-il retrouver le JSON de la paire, ou l'appariement
  reste-t-il strictement local ? (research.md, Data & Constraints)]
- [NEEDS CLARIFICATION: la copie de la source doit-elle être mise à
  jour (ou recréée) lors d'un amendement, ou figée à la création ?
  (divergence copie/source, research.md)]
- [NEEDS CLARIFICATION: sort de la décision enregistrée « aucune copie
  dans le dossier de sortie » (FR-026, session 2026-10-13) — assumée
  dépassée pour les créations, ou contournée ? (research.md, Prior
  Art)]
- [NEEDS CLARIFICATION: collision possible des noms d'unités après un
  cycle complet du compteur (> 10 000 sorties dans un même dossier) —
  acceptable ou à prévenir ? (research.md, Data & Constraints)]
- [NEEDS CLARIFICATION: motivation précise du demandeur (archivage,
  navigation, pipeline aval ?) — non renseignée dans le intake.]
