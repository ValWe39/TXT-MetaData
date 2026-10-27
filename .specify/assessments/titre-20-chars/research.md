# Idea Research: Préfixe de 20 caractères pour la sortie JSON

- **Slug**: titre-20-chars
- **Created**: 2026-10-27
- **Evidence confidence (overall)**: high

Périmètre : recherche interne au dépôt uniquement, à la demande de
l'utilisateur ; aucune source externe n'a été consultée.

## Users & Demand

- Unique demandeur identifié : le propriétaire du dépôt, dans le intake
  (`intake.md`, idée citée). Aucun autre signal d'usage (tickets, interviews)
  n'existe. — [source: .specify/assessments/titre-20-chars/intake.md]
  (confidence: high)
- Le déclencheur précis reste inconnu (collisions vues ? lisibilité ?) ;
  le intake le marque `[NEEDS CLARIFICATION]`. — [source: intake.md,
  section Origin & Context] (confidence: low)
- Données réelles favorables : les 10 sorties du dépôt (`output/`) montrent des
  noms tronqués difficilement distinguables — `Cour_des-0037.json` (source
  `Cour_des_comptes_rapport.md`) et `Cour_de_-0039.json` (source
  `Cour_de_comptes_pagination.md`) ; de même `Ecalle_c-0033.json` /
  `Ecalle_o-0040.json`. À 20 caractères, ces paires deviennent
  distinctes (`Cour_des_comptes_rappo-…` / `Cour_de_comptes_pagin-…`).
  — [source: output/, Interne-Dev/Exemples/] (confidence: high)

## Prior Art

- FR-022 (spec actuelle) : « Le nom du fichier de sortie DOIT être : 8
  premiers caractères du titre du fichier d'entrée (espaces remplacées par
  `_`, accents simplifiés) + `-` + numéro d'occurrence à 4 chiffres + `.json` ».
  Le mot « titre » désigne ici le nom du fichier d'entrée, pas le champ
  `Titre` extrait par le LLM — l'implémentation suit cette lecture
  (`output_prefix` utilise `input_path.stem`). — [source:
  specs/001-txt-metadata-extraction/spec.md:364-366, src/txt_metadata/
  output.py:26-32] (confidence: high)
- Aucune tentative antérieure de changement de longueur dans le dépôt (spec,
  tasks, historique des branches 001–003) ; la valeur 8 est en place depuis la
  première implémentation. — [source: specs/, git log] (confidence: high)
- L'ambiguïté de préfixe court est déjà anticipée par le code d'appariement :
  deux entrées de même préfixe face à un JSON ne sont PAS liées
  (`test_appariement_ambigu_non_lie`). Le numéro d'occurrence empêche déjà
  toute collision de nom de fichier ; la longueur du préfixe n'affecte que la
  lisibilité et l'appariement. — [source: src/txt_metadata/inputs.py:70-82,
  tests/unit/test_pairing.py] (confidence: high)

## Market & Context

- Sans changement, l'alternative actuelle de l'utilisateur est de deviner la
  source d'un JSON par son préfixe de 8 caractères, ce que les 10 sorties
  réelles montrent peu fiable pour les noms longs et proches. —
  [source: output/] (confidence: medium)
- Coût du changement : 5 assertions de tests à mettre à jour, 4 documents
  (README, spec FR-022, contrat de sortie, docstrings) et 1 constante, car
  nommage et appariement partagent `_PREFIX_LENGTH` — [source: voir
  Data & Constraints] (confidence: high)

## Data & Constraints

- Architecture : une seule constante `_PREFIX_LENGTH = 8`
  (src/txt_metadata/output.py:17). Le nommage
  (`build_output_name`, output.py:36-39) et l'appariement d'amendement
  (`pair_documents`, src/txt_metadata/inputs.py:76, qui réutilise
  `output_prefix`) dérivent de la même fonction : changer la constante change
  les DEUX comportements simultanément. — [source: code] (confidence: high)
- Règle d'appariement : `j.stem.startswith(prefix)` ; repli par paire unique
  si un seul document et un seul JSON dans le dossier (inputs.py:78-81).
  Un JSON nommé avec l'ancien préfixe de 8 ne satisfait plus un préfixe de
  20 → il ne serait plus apparié par préfixe (seul le repli « paire unique »
  peut encore le rattraper). — [source: inputs.py:70-82] (confidence: high)
- Compatibilité descendante asymétrique : un préfixe d'appariement gardé à 8
  reconnaît les noms de 20 caractères (startswith), donc les JSON existants
  (8) et nouveaux (20) restent appariables. La réciproque est fausse.
  — [source: logique de startswith sur inputs.py:77] (confidence: high)
- FR-031 : un JSON amendé conserve son nom d'origine ; la cohabitation de
  noms courts (anciens) et longs (nouveaux) est donc prévue par la spec.
  — [source: spec.md:392-395] (confidence: high)
- Tests impactés par un passage à 20 : `test_prefix_limite_huit_caracteres`
  (`Rapport_` → échouerait), `test_nom_de_sortie`
  (`Rapport_-0007.json` → `Rapport_info-0007.json`), `test_pairing.py`
  (`Rapport_-0001.json` ne matche plus le préfixe 20 `Rapport_info`),
  `test_multi.py:74` (`Troisiem-0003.json` → `Troisieme-0003.json`).
  Non impactés : `bon-` (stem plus court que 8) et l'amendement
  `Rapport-0005.json` (apparié via le repli paire unique, pas par préfixe).
  — [source: tests/unit/test_output.py:22-33, tests/unit/test_pairing.py:16,
  tests/integration/test_multi.py:74,107,132] (confidence: high)
- Les 10 JSON existants dans `output/` ne sont pas concernés par
  l'appariement (ils ne sont pas dans les dossiers d'entrée) ; aucune
  migration de contenu n'est nécessaire pour eux. — [source: output/,
  inputs.py:70-82] (confidence: high)
- Longueur de chemin : +12 caractères max par nom de fichier ; sans effet
  notable sur la limite Windows (260) pour des arborescences raisonnables.
  — ASSUMPTION (confidence: medium)

## Evidence Against the Idea

- Aucune donnée d'usage observée (collision, erreur d'identification) ne
  motive le changement : la demande est un souhait déclaré, le déclencheur
  reste à clarifier. — [source: intake.md] (confidence: medium)
- Si l'appariement passe aussi à 20 (effet induit par la constante partagée),
  les JSON existants placés dans des dossiers d'entrée avec des noms à 8
  caractères ne sont plus appariés par préfixe — risque de régression de
  l'amendement (FR-026) sur des corpus déjà traités. — [source:
  inputs.py:76-77] (confidence: high)
- Churn de tests et de documentation : 5 assertions, 4 documents de référence
  décrivent explicitement « 8 premiers caractères » (README.md:58,
  FR-022, contracts/output-schema.md:41, docstrings output.py et
  inputs.py). — [source: dépôt] (confidence: high)
- Gain limité aux noms de fichiers de plus de 8 caractères (les stems courts
  comme `IFRI` ou `bon` ne changent pas) ; noms de sortie plus longs et
  moins lisibles dans un explorateur étroit. — [source: output.py:26-32]
  (confidence: medium)

## Gaps & Open Questions

- [NEEDS CLARIFICATION: « titre de l'entrée » = nom du fichier d'entrée
  (lecture de FR-022 et de l'implémentation actuelle, la plus probable) ou
  champ `Titre` extrait par le LLM ? Le wording de FR-022 penche pour la
  première, mais la demande dit « sans changer le reste des critères » ce qui
  la rend très probable — à confirmer.]
- [NEEDS CLARIFICATION: l'appariement doit-il suivre à 20 (constante
  partagée) ou rester à 8 pour préserver l'amendement des JSON existants ?
  Les deux options sont viables, avec des effets différents documentés
  ci-dessus.]
- [NEEDS CLARIFICATION: faut-il renommer ou laisser cohabiter les JSON déjà
  produits (les 10 fichiers de `output/`) ? FR-031 suggère que la cohabitation
  est acceptable.]

## Sources

- Aucune source web consultée (recherche interne au dépôt, demande
  explicite de l'utilisateur). Sources internes citées inline :
  `src/txt_metadata/output.py`, `src/txt_metadata/inputs.py`,
  `tests/unit/test_output.py`, `tests/unit/test_pairing.py`,
  `tests/integration/test_multi.py`,
  `specs/001-txt-metadata-extraction/spec.md` (FR-022, FR-026, FR-027,
  FR-031), `specs/001-txt-metadata-extraction/contracts/output-schema.md`,
  `README.md`, `output/` (10 JSON réels), `Interne-Dev/Exemples/`,
  `.specify/assessments/titre-20-chars/intake.md`.
