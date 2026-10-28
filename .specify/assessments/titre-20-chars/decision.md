# Decision: Préfixe de sortie lisible et rattachable à la source

- **Slug**: titre-20-chars
- **Decided**: 2026-10-27
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md | concept.md

## Scorecard

| Criterion | Rating | Justification |
| --- | --- | --- |
| Problem validity | adequate | 2 paires sur 10 indiscernables (réel) |
| Evidence strength | adequate | Sources internes citées, confiance high |
| Value vs. inaction | strong | Correctif small vs douleur constatée |
| Feasibility / appetite | strong | Constante, ~5 tests, 4 docs (small) |
| Strategic fit | strong | Aligne sur la contrainte du demandeur |
| Risk posture | adequate | FR-026 couvert par B ; nuance à préciser |

Justifications détaillées :

- **Problem validity (adequate)** : problème constaté sur données réelles du
  dépôt — 2 paires de JSON sur 10 quasi indiscernables à 8 caractères
  (research.md, output/) ; projet mono-utilisateur, périmètre borné par la
  demande elle-même.
- **Evidence strength (adequate)** : toutes les affirmations sont citées
  depuis le code et le corpus réel (confiance globale high, research.md) ;
  seule lacune : le déclencheur précis de la demande, non bloquant.
- **Value vs. inaction (strong)** : coût de l'inaction documenté
  (identification par ouverture des JSON, confusion entre documents d'une
  même série, s'aggrave avec le corpus) contre un correctif small.
- **Feasibility / appetite (strong)** : option B en appétit small —
  dédoubler la constante, ~5 assertions de tests, 4 documents ;
  compatibilité descendante démontrée par la logique `startswith`
  (research.md, Data & Constraints).
- **Strategic fit (strong)** : aligné sur la contrainte explicite du
  demandeur (« sans changer le reste de l'outil ni les autres critères »)
  et sur FR-031 ; amendement de FR-022 assumé comme objet du changement.
- **Risk posture (adequate)** : risque principal (régression FR-026)
  couvert par l'option B ; cas limite « ancien + nouveau JSON coexistent »
  documenté (ambiguïté → non lié) ; la nuance du décideur (appariement
  progressif 8 → 20) ajoute une complexité sémantique à préciser en
  spécification.

## Verdict & Rationale

**Go.** Le problème est réel et observé sur le corpus du projet (problem.md,
métrique : 2 paires indiscernables), les preuves sont internes mais complètes
et citées (research.md, confiance high), et l'option B tient les trois buts du
problème dans un appétit small. Les options A (régression de l'amendement des
corpus existants) et C (le problème persiste) sont écartées. La décision est
prise avec la nuance du décideur : l'appariement reconnaît un JSON à partir
de 8 caractères mais prolonge l'analyse jusqu'à 20 — ce qui affine l'option B
(en plain `startswith` à 8) et devra être précisé en spécification.

## If go — Handoff to `/speckit-specify`

- **Problem**: les JSON de sortie ne sont pas rattachables visuellement à
  leur document source, le préfixe de 8 caractères rendant des noms longs
  et proches quasi identiques (2 paires sur 10 dans le corpus réel).
- **Chosen approach**: Option B avec nuance — nommage des nouvelles sorties
  sur les 20 premiers caractères normalisés du nom d'entrée ; appariement
  d'amendement qui reconnaît un JSON à partir de 8 caractères et prolonge
  l'analyse jusqu'à 20 (sémantique exacte à définir en spécification :
  comparaison progressive, longueur de comparaison effective,
  désambiguïsation ancien 8 / nouveau 20).
- **In scope**: constante de longueur de nommage (20), appariement progressif
  8 → 20, mise à jour des tests concernés (~5 assertions) et des documents
  (README, FR-022, contrat de sortie, docstrings). **Out of scope**:
  renommage des JSON existants, option CLI de longueur, normalisation,
  numérotation/compteur, extraction/LLM/batch/CLI, appariement flou.
- **Success metrics**: 0 paire indiscernable sur les 10 exemples (baseline
  2) ; suite de tests sans régression d'appariement (baseline 92 tests au
  vert) ; docs conformes au comportement réel (4 documents à jour).
- **Carried-forward open questions**:
  - [NEEDS CLARIFICATION: sémantique exacte de l'appariement progressif
    8 → 20 : longueur de comparaison effective, traitement des noms plus
    courts que 8, préférence entre candidats ancien (8) et nouveau (20)
    pour un même document.]
  - [NEEDS CLARIFICATION: confirmer que « titre de l'entrée » = nom du
    fichier d'entrée sans extension (lecture FR-022, très probable) et non
    le champ `Titre` extrait.]
  - [NEEDS CLARIFICATION: cas « ancien et nouveau JSON coexistent pour un
    même document » — l'appariement progressif doit-il départager (match le
    plus long) ou rester non lié ?]
