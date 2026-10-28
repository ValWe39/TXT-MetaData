# Research — Préfixe de 20 caractères (Phase 0)

**Feature**: specs/002-titre-20-chars | **Date**: 2026-10-27

Aucun marqueur NEEDS CLARIFICATION ne subsiste dans la spec : chaque décision
ci-dessous est fondée sur l'évaluation (`decision.md`, verdict go), la session
de clarification du 2026-10-27 et la lecture du code existant.

## D1 — Longueur de nommage : 20 caractères normalisés

- **Decision** : les nouvelles sorties sont nommées sur les 20 premiers
  caractères normalisés du nom du fichier d'entrée sans extension.
- **Rationale** : les 10 sorties réelles du dépôt comptent 2 paires quasi
  indiscernables à 8 caractères (`Cour_des`/`Cour_de_`, `Ecalle_c`/
  `Ecalle_o`) ; à 20, toutes les paires du corpus se séparent. Le demandeur a
  formulé cette valeur.
- **Alternatives considered** : statu quo 8 (option C de l'évaluation —
  rejetée : le problème constaté persiste) ; longueur configurable via CLI
  (rejetée : contrainte explicite « sans changer le reste de l'outil »,
  YAGNI).

## D2 — Constantes dédoublées : nommage 20, appariement 8→20

- **Decision** : la longueur de nommage (20) et la fenêtre d'appariement
  (reconnaissance à partir de 8, analyse jusqu'à 20) sont deux réglages
  distincts ; l'appariement ne réutilise pas aveuglément la constante de
  nommage.
- **Rationale** : `inputs.py` appelle aujourd'hui `output_prefix` : porter la
  constante à 20 sans les découpler casserait l'appariement des JSON
  existants nommés sur 8 caractères (régression FR-026, documentée dans
  l'évaluation). La fenêtre 8→20 préserve la compatibilité descendante et
  départage ancien/nouveau.
- **Alternatives considered** : constante partagée à 20 (option A de
  l'évaluation — rejetée) ; appariement figé à 8 pur et simple (option B
  brute — affinée par la nuance du décideur : prolonger l'analyse jusqu'à
  20).

## D3 — Métrique d'appariement : préfixe commun le plus long (max 20)

- **Decision** : un JSON est candidat si son nom normalisé partage au moins
  8 caractères avec le nom normalisé du document (ou le nom complet si plus
  court) ; parmi les candidats, est retenu celui qui partage le préfixe
  commun le plus long, plafonné à 20 caractères.
- **Rationale** : traduction directe de la nuance du décideur (« reconnaît à
  partir de 8 mais prolonge l'analyse jusqu'à 20 ») ; départage
  ancien/nouveau sans ambiguïté (US-3).
- **Alternatives considered** : premier candidat trouvé selon l'ordre
  alphabétique (non déterministe fonctionnellement, fragile) ; comparaison
  de « caractères partagés » hors préfixe (sous-déterminée, pourrait lier des
  noms sans rapport).

## D4 — Nom du JSON candidat normalisé avant comparaison

- **Decision** : le nom du fichier JSON candidat est normalisé (espaces →
  `_`, accents simplifiés) avant la comparaison d'appariement.
- **Rationale** : réponse B de la session de clarification du 2026-10-27 ;
  reconnaît aussi des JSON renommés manuellement avec accents ou espaces,
  cohérent avec le fait que la normalisation est déjà une règle du produit.
- **Alternatives considered** : comparaison telle quelle (option A —
  rejetée par le décideur après recommandation initiale).

## D5 — Égalité parfaite → non-liage

- **Decision** : si plusieurs candidats partagent exactement le même
  préfixe commun le plus long, aucun n'est retenu ; le document est traité
  seul.
- **Rationale** : comportement sûr déjà en place (refus d'appariement
  ambigu) ; empêche un amendement silencieux du mauvais JSON.
- **Alternatives considered** : départage par numéro d'occurrence le plus
  ancien/récent (heuristique opaque, risque d'amender le mauvais corpus).

## D6 — Ordre de priorité d'appariement conservé

- **Decision** : candidats par préfixe d'abord ; repli « paire unique du
  sous-dossier » seulement à défaut de candidat retenu, exactement comme
  aujourd'hui.
- **Rationale** : le repli actuel (un document + un JSON dans le dossier)
  rattrape les JSON hors préfixe commun ; le changer sortirait du périmètre.
- **Alternatives considered** : repli prioritaire sur candidats (inversion
  de sémantique, non demandée).

## D7 — Mise à jour documentaire en place

- **Decision** : FR-022 de la spec 001 est amendée sur place (8 → 20,
  mention de la fenêtre d'appariement), le contrat de sortie
  (`contracts/output-schema.md`) et le README sont mis à jour dans la même
  livraison.
- **Rationale** : FR-008 de la spec 002 exige une conformité docs/outil sans
  divergence ; trois documents décrivent « 8 premiers caractères ».
- **Alternatives considered** : laisser la spec 001 en l'état avec note de
  surcharge (risque de divergence entre documents de référence, rejeté).

## D8 — Validation réelle limitée à l'exemple IFRI

- **Decision** : la calibration sur exemple réel se limite à
  `Interne-Dev/Exemples/IFRI` (contrainte explicite du demandeur) ; l'effet
  des 20 caractères, invisible sur le nom court « IFRI » (4 caractères,
  FR-002), est démontré par un document synthétique à nom long.
- **Rationale** : périmètre de validation réduit à la demande ; le cas IFRI
  couvre en réel la voie « nom plus court que 8/20 » et l'amendement.
- **Alternatives considered** : recalibrer les 10 exemples (rejeté : coût
  d'appels LLM réel pour un changement de nommage déterministe, hors besoin).
