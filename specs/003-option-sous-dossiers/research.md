# Research — Option --sous-dossiers

**Feature**: specs/003-option-sous-dossiers | **Date**: 2026-10-28

Phase 0 : décisions techniques fondées, en réponse aux inconnues du
Technical Context et aux clarifications de la spec. Les arbitrages
utilisateur sont déjà tranchés dans `spec.md` (section Clarifications) ;
ce document enregistre les décisions d'implémentation.

## D1 — Nom de l'unité : `NNNN-<préfixe normalisé>`

- **Decision** : l'unité s'appelle `<numéro d'occurrence à 4 chiffres>-
  <préfixe normalisé du nom d'entrée>`, le préfixe étant exactement
  celui du nom du JSON (règle FR-022 spec 001, contrat 002).
- **Rationale** : tranché avec l'utilisateur en session 2026-10-28
  (choix B) ; le numéro en tête préserve le tri chronologique, le nom
  rend l'unité lisible sans l'ouvrir. Exemples : `0068-IFRI`,
  `0069-Ecalle_cours`.
- **Alternatives considered** : numéro seul (`0068`, rejeté : peu
  parlant), nom puis numéro (`IFRI-0068`, rejeté : tri alphabétique
  perd l'ordre chronologique).

## D2 — La copie : nom d'origine, contenu exact, écrasement en cas de collision

- **Decision** : la copie porte le nom d'origine du fichier source et
  son contenu est identique octet pour octet à la création ; si une
  copie de même nom existe déjà dans l'unité cible, elle est écrasée.
- **Rationale** : tranché avec l'utilisateur en session 2026-10-28
  (choix A) ; l'écrasement est cohérent avec la sémantique existante
  du mode plat, où un nouveau JSON de nom identique est écrit par-dessus.
- **Alternatives considered** : conserver la copie existante (rejeté :
  paire potentiellement incohérente), bloquer la création (rejeté :
  nouveau mode d'erreur pour un cas limite).

## D3 — Exclusion du dossier de sortie de la découverte, inconditionnelle

- **Decision** : quand un chemin d'entrée couvre le dossier de sortie,
  le dossier de sortie (chemin résolu) est exclu de la découverte des
  documents — que l'option `--sous-dossiers` soit active ou non.
- **Rationale** : tranché avec l'utilisateur en session 2026-10-28
  (FR-011). La sortie n'est jamais une entrée intentionnelle ; l'exclusion
  inconditionnelle est plus simple qu'une condition sur le flag et
  élimine la boucle de rétroaction identifiée par l'évaluation
  (re-traitement des copies, appels LLM non désirés).
- **Alternatives considered** : exclusion conditionnée au flag actif
  (rejeté : la sortie ne devrait jamais être scannée, copies ou non) ;
  hypothèse d'usage documentée seule (rejeté par le choix A).

## D4 — Ordonnancement de la création : copie avant persistance du numéro

- **Decision** : à la création, l'ordre est : allocation du numéro
  d'occurrence (verrou), création de l'unité, copie de la source,
  écriture du JSON, persistance du compteur. Un échec de lecture du
  source échoue en amont (lecture du texte avant extraction) : aucune
  unité, aucun numéro consommé. Un échec d'écriture disque en cours de
  création relève du cas d'interruption : l'unité créée est nettoyée et
  le numéro consommé n'est pas réutilisé (FR-024 spec 001).
- **Rationale** : préserve à la fois FR-007 de la spec 003 (aucune trace
  partielle pour un document en échec) et FR-024 (un numéro consommé
  n'est jamais réutilisé). Le contenu copié provient du texte déjà lu
  pour l'extraction : la copie elle-même ne relit pas le disque.
- **Alternatives considered** : persistance immédiate du numéro puis
  rollback (rejeté : violerait FR-024 « jamais réutilisé » ou laisserait
  un numéro consommé pour un échec, violant FR-007).

## D5 — Amendement : mécanismes existants, aucune extension

- **Decision** : l'amendement d'une paire rangée passe par le repli
  « paire unique du sous-dossier » (FR-027 spec 001) inchangé ; aucun
  nouveau code d'appariement. La copie n'est jamais modifiée ni
  recréée par un amendement.
- **Rationale** : la décision d'évaluation (option B) borne le périmètre
  ; l'appariement étendu (option C) est un incrément ultérieur. Le repli
  existant reconnaît exactement la forme d'une unité (1 document + 1
  JSON dans un même dossier).
- **Alternatives considered** : appariement étendu depuis la source
  d'origine (option C, hors périmètre, documenté comme incrément
  futur).

## D6 — FR-026 de la spec 001 amendée sur place

- **Decision** : la phrase « aucune copie n'est écrite dans le dossier
  de sortie » (FR-026, session 2026-10-13) est amendée dans la spec 001 :
  une copie de la source est écrite dans le dossier de sortie, à la
  création uniquement et uniquement avec l'option active. README et
  contrat CLI mis à jour dans la même livraison (FR-010).
- **Rationale** : la décision d'évaluation a tranché que l'ancienne
  intention est dépassée pour les créations ; la mise à jour
  documentaire explicite évite toute divergence entre documents de
  référence et outil.
- **Alternatives considered** : laisser FR-026 en l'état avec une note
  de surcharge (rejeté : divergence documentaire, comme pour la spec
  002).

## D7 — Validation réelle limitée à IFRI et Ecalle_cours

- **Decision** : la calibration sur exemples réels se limite à
  `Interne-Dev/Exemples/IFRI` et `Interne-Dev/Exemples/Ecalle_cours`
  (contrainte explicite du demandeur). La création réelle passe par une
  copie temporaire du `.md` (sans JSON à côté), car le dossier IFRI
  contient déjà `IFRI-0042.json` et déclencherait sinon l'amendement.
- **Rationale** : périmètre de validation réduit à la demande. Ecalle
  montre un nom à 12 caractères (`Ecalle_cours`), distinct de
  `Ecalle_ouvrage` (`Ecalle_o`) — les unités restent distinguables.
- **Alternatives considered** : recalibrer les 10 exemples (rejeté :
  coût d'appels LLM réel, hors besoin).

## D8 — Stratégie de test : LLM simulé, déterministe d'abord

- **Decision** : les nouveaux comportements (rangement, copie,
  exclusion, option) sont testés unitairement et en intégration avec un
  LLM simulé (aucun appel réel en CI) ; seuls les scénarios des
  exemples réels IFRI/Ecalle_cours utilisent la clé.
- **Rationale** : le rangement est déterministe (chemins, copie) ; les
  tests existants du mode par défaut ne sont pas modifiés (SC-002).
- **Alternatives considered** : tests réels systématiques (rejeté :
  coût, non reproductible en CI).
