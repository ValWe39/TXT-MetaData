# Idea Research: Option --sous-dossiers (JSON + copie .md dans un sous-dossier numéroté)

- **Slug**: option-sous-dossiers
- **Created**: 2026-10-28
- **Evidence confidence (overall)**: high

Périmètre : recherche interne au dépôt uniquement (code, spécifications,
historique), cohérent avec le research de `titre-20-chars` ; aucune source
externe n'a été consultée. L'idée et ses inconnues proviennent de
`intake.md`.

## Users & Demand

- Unique demandeur identifié : le propriétaire du dépôt, via le intake.
  Aucun autre signal d'usage (tickets, interviews) n'existe. — [source:
  .specify/assessments/option-sous-dossiers/intake.md] (confidence: high)
- Signal récurrent : c'est la 3e demande consécutive portant sur
  l'organisation de la sortie (002-fonction-pcpale : `--output-folder` ;
  003-titre-20-car : préfixe 20 ; celle-ci : sous-dossiers). Le
  rangement des sorties est une zone de friction active pour l'unique
  utilisateur. — [source: historique des branches, git log] (confidence:
  high)
- Données réelles : `output/` contient 10 JSON à plat, dont
  `IFRI-0036.json` ; les sources `.md` vivent dans
  `Interne-Dev/Exemples/`. Source et métadonnées sont donc physiquement
  séparées aujourd'hui ; la motivation précise (archivage autonome ?
  navigation ?) reste `[NEEDS CLARIFICATION]` dans le intake. — [source:
  output/, Interne-Dev/Exemples/, intake.md] (confidence: high)

## Prior Art

- Décision enregistrée contraire (2026-10-13, spec 001, session de
  clarification) : un JSON amendé est réécrit sur place, à son
  emplacement d'origine, et « aucune copie n'est écrite dans le dossier
  de sortie » — repris tel quel dans FR-026. La décision visait
  l'amendement, pas la création ; mais l'idée réintroduit une copie dans
  le dossier de sortie et devra expliciter ce qu'elle fait de cette
  intention enregistrée. — [source:
  specs/001-txt-metadata-extraction/spec.md, sections « Session
  2026-10-13 » et FR-026] (confidence: high)
- Précédent favorable déjà en production : le repli d'appariement
  « paire unique du sous-dossier » (FR-027, `pair_documents` dans
  inputs.py : un seul document et un seul JSON dans le même dossier).
  Le layout visé par l'idée (1 copie `.md` + 1 JSON par sous-dossier) est
  exactement la forme que ce repli sait apparier sans aucun nouveau
  mécanisme : re-exécuter l'outil sur le sous-dossier amenderait le JSON
  sur place. — [source: src/txt_metadata/inputs.py, FR-027] (confidence:
  high)
- Aucune tentative antérieure de sous-dossiers de sortie dans le dépôt
  (specs 001–002, branches 001–003) : le dossier de sortie a toujours été
  plat. — [source: specs/, git log] (confidence: high)
- Contrat 002 §4 : « Aucun JSON existant n'est renommé, recréé ou
  déplacé » — contrainte de compatibilité que l'option devra respecter
  (le flag ne doit déplacer aucun JSON préexistant). — [source:
  specs/002-titre-20-chars/contracts/naming-and-pairing.md §4]
  (confidence: high)

## Market & Context

- Alternative actuelle : copier le `.md` à la main à côté du JSON, ou
  retrouver la source via le préfixe de 20 caractères. Coût de
  l'inaction : aucune archive autonome par document — le JSON seul ne
  suffit pas à reconstituer la paire si la source est déplacée ou
  renommée. — [source: observation du workflow décrit dans README et
  spec 001] (confidence: medium)
- Prior art externe non consulté (périmètre interne assumé) ;
  l'organisation « un dossier par document, source à côté de la sortie »
  est un pattern courant des chaînes OCR/archivage, mais ce point reste
  une ASSUMPTION non sourcée. — [ASSUMPTION] (confidence: low)

## Data & Constraints

- Compteur : cycle 0001…9999 puis 0000 (`_CYCLE = 10_000`, counter.py ;
  FR-023). Un sous-dossier nommé uniquement par le numéro d'occurrence
  peut donc entrer en collision après un cycle complet dans un même
  dossier de sortie. État actuel du compteur : 0067 — risque lointain
  mais à trancher explicitement. — [source: src/txt_metadata/counter.py,
  counter.txt, FR-023] (confidence: high)
- Parallélisme batch : `write_new` est appelé depuis des threads
  (batch.py) ; un sous-dossier par occurrence est sans collision
  intra-exécution (verrou du compteur), et le pattern
  `mkdir(parents=True, exist_ok=True)` est déjà en place dans
  output.py. — [source: src/txt_metadata/batch.py, counter.py,
  output.py `write_new`] (confidence: high)
- Appariement futur asymétrique : `pair_documents` ne cherche les JSON
  candidats que dans le dossier parent du texte d'entrée (glob non
  récursif). Avec `--sous-dossiers`, le JSON vit dans
  `output/<NNNN>/`, pas à côté de la source : re-traiter la source
  d'origine consommerait un NOUVEAU numéro au lieu d'amender, sauf à
  exécuter l'outil sur le sous-dossier (où le repli « paire unique »
  s'applique). Ce changement de sémantique d'amendement est le point de
  conception le plus lourd de l'idée. — [source:
  src/txt_metadata/inputs.py `pair_documents`, `__main__.py`
  `process_document`] (confidence: high)
- Copie du `.md` : aucune copie de fichier n'existe aujourd'hui dans le
  code (pas d'import shutil) ; les entrées `.txt` sont aussi supportées
  (FR-001), la copie doit donc viser le fichier d'entrée quelle que soit
  son extension. — [source: src/txt_metadata/, FR-001] (confidence:
  high)
- Boucle de rétroaction : `discover()` parcourt récursivement (rglob)
  tous les `.md`/`.txt` des chemins donnés. Si le dossier de sortie (ou
  un parent commun aux sources et à la sortie) est scanné un jour, les
  copies `.md` seraient redécouvertes et retraitées (appels LLM,
  amendements des copies). Aujourd'hui, sans copie, seuls les originaux
  existent côté source. — [source: src/txt_metadata/inputs.py
  `_iter_supported`] (confidence: high)
- Divergence copie/source : l'amendement réécrit le JSON sur place
  (`amend_in_place`) mais ne toucherait pas la copie `.md` si la source
  évolue — deux copies du même document peuvent diverger. — [source:
  src/txt_metadata/output.py `amend_in_place`] (confidence: high)
- Surface d'implémentation : cli.py (flag booléen + champ `Options` —
  aucune nouvelle validation de bornes nécessaire), output.py
  (sous-dossier + copie à la création), tests (10 fichiers unitaires
  existants à compléter), documentation (README, cli-contract FR-029,
  spec). `--output-folder` préexistant : les sous-dossiers se créeraient
  naturellement sous le dossier configuré. — [source: cli.py, tests/,
  specs/001/contracts/cli-contract.md] (confidence: high)

## Evidence Against the Idea

- L'intention enregistrée de la spec 001 dit « aucune copie n'est
  écrite dans le dossier de sortie » (FR-026, session 2026-10-13) ;
  l'idée contredit au moins l'esprit de cette décision pour les
  créations. — [source: specs/001/spec.md] (confidence: high)
- Duplication de données : chaque source `.md` existerait en deux
  exemplaires pouvant diverger (source éditée, copie figée à la date de
  création). — [source: déduction du code actuel `amend_in_place`,
  ASSUMPTION sur l'évolution des sources] (confidence: medium)
- Risque de re-traitement des copies lors d'un scan récursif du dossier
  de sortie ou d'un parent commun — coût LLM et amendements non
  désirés. — [source: inputs.py `_iter_supported` rglob] (confidence:
  high)
- Éclatement de la sortie : deux layouts possibles (plat par défaut,
  sous-dossiers optionnel) à documenter, tester et maintenir ; le
  dossier plat actuel sert de référence aux tests et au README. —
  [source: tests/, README.md] (confidence: high)
- Collision de noms de sous-dossiers après un cycle complet du compteur
  (10 000 créations dans le même dossier). — [source: counter.py,
  FR-023] (confidence: high)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: nom exact du sous-dossier — `0036` seul, ou
  préfixe lisible (ex. `IFRI-0036`) ? Arbitrage à faire, non tranché
  ici.]
- [NEEDS CLARIFICATION: la copie `.md` garde-t-elle son nom d'origine ?
  Est-elle une copie exacte ? Est-elle mise à jour lors d'un amendement
  ou jamais retouchée après création ?]
- [NEEDS CLARIFICATION: sémantique d'amendement — re-traiter la source
  d'origine doit-il retrouver le JSON du sous-dossier (recherche
  récursive ou par numéro), ou l'appariement reste-t-il strictement
  local au dossier du texte ?]
- [NEEDS CLARIFICATION: que faire de la décision FR-026 « aucune copie
  dans le dossier de sortie » — assumée comme dépassée pour les
  créations, ou contournée ?]
- [NEEDS CLARIFICATION: bornes/usage du flag (booléen simple sans
  valeur, aucune validation de bornes nécessaire) et interaction avec
  `--output-folder` (sous-dossiers sous le dossier configuré — présumé
  oui).]
- [NEEDS CLARIFICATION: comportement inchangé sans le flag, à confirmer
  explicitement (aucun renommage ni déplacement des JSON existants).]

## Sources

- Recherche interne uniquement ; aucune URL consultée, aucun fetch
  effectué. Sources citées dans le texte : `.specify/assessments/
  option-sous-dossiers/intake.md`, `src/txt_metadata/` (cli.py,
  output.py, inputs.py, counter.py, batch.py, `__main__.py`),
  `specs/001-txt-metadata-extraction/` (spec.md, contracts/
  cli-contract.md), `specs/002-titre-20-chars/contracts/
  naming-and-pairing.md`, `output/`, `counter.txt`, `Interne-Dev/
  Exemples/`, `git log`.
