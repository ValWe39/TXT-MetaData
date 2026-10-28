# Feature Specification: Option --sous-dossiers — paires autonomes en sortie

**Feature Branch**: `004-option-sous-dossiers`

**Created**: 2026-10-28

**Status**: Draft

**Input**: Handoff de l'évaluation `option-sous-dossiers` (verdict go,
option B) — un flag optionnel de la CLI range chaque nouvelle sortie
dans une unité unique nommée d'après son numéro d'occurrence,
accompagnée d'une copie de son fichier source ; le comportement par
défaut reste strictement inchangé.

## Clarifications

### Session 2026-10-28

- Q: Forme exacte du nom de l'unité de rangement — numéro seul
  (`0068`), numéro + nom (`0068-IFRI`) ou nom + numéro (`IFRI-0068`) ?
  → A: Numéro + nom : `0068-IFRI` — le numéro d'occurrence en tête
  préserve le tri chronologique, le nom du document rend l'unité
  lisible sans l'ouvrir ; le segment nominal est le même préfixe
  normalisé que celui du nom du JSON.
- Q: Le dossier de sortie doit-il être exclu automatiquement de la
  découverte des entrées quand un chemin fourni le couvre, ou le
  risque de re-traitement des copies reste-t-il documenté comme une
  hypothèse d'usage ? → A: Oui — exclusion automatique : le dossier de
  sortie (chemin résolu) est exclu de la découverte quand un chemin
  d'entrée le couvre ; les copies présentes dans les unités ne sont
  jamais traitées comme des entrées.
- Q: À la création d'une sortie quand l'unité cible existe déjà
  (collision de nom), la copie de la source doit-elle écraser le
  fichier existant, le conserver ou bloquer la création ? → A:
  Écraser — la copie existante dans l'unité est remplacée, par
  cohérence avec l'écrasement d'un JSON de nom identique en mode plat.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Paire autonome à la création (Priority: P1)

L'utilisateur traite un document (ex. `IFRI.md`) avec l'option
`--sous-dossiers` active. À la création du JSON, l'outil range celui-ci
dans une unité unique nommée d'après le numéro d'occurrence du
document, accompagnée d'une copie exacte du fichier source portant son
nom d'origine. L'utilisateur dispose alors d'une paire autonome
« source + métadonnées » archivable ou partageable sans manipulation
manuelle.

**Why this priority**: c'est la raison d'être de la fonctionnalité —
les JSON produits vivent à plat dans le dossier de sortie tandis que
leurs sources vivent ailleurs ; reconstituer la paire exige aujourd'hui
une copie manuelle (problem.md de l'évaluation).

**Independent Test**: exécutable sur l'exemple réel `IFRI.md` en
vérifiant que l'unité créée contient le JSON et une copie identique de
la source, sans aucune manipulation manuelle.

**Acceptance Scenarios**:

1. **Given** l'option active et un document `IFRI.md` à traiter,
   **When** l'outil crée sa sortie (occurrence 0068), **Then** le JSON
   est placé dans une unité `0068-IFRI/` du dossier de sortie (numéro
   d'occurrence + `-` + préfixe normalisé du nom d'entrée), et une
   copie exacte de `IFRI.md` sous son nom d'origine l'accompagne dans
   la même unité.
2. **Given** l'option active et une entrée `.txt` (ex. `notes.txt`),
   **When** la sortie est créée, **Then** l'unité contient le JSON et
   la copie `notes.txt`, la copie visant le fichier source quelle que
   soit son extension.
3. **Given** l'option active et un document dont le nom d'entrée compte
   moins de 20 caractères, **When** la sortie est créée, **Then** le
   nom du JSON reste régi par la règle de nommage en vigueur
   (préfixe-00NN.json, spécification 001 FR-022) — seule son unité de
   rangement change.

---

### User Story 2 - Comportement par défaut inchangé (Priority: P2)

Sans l'option, l'utilisateur retrouve exactement le comportement
actuel : les nouvelles sorties sont écrites à plat dans le dossier de
sortie, aucun fichier existant n'est renommé, recréé ou déplacé, et
l'amendement comme la numérotation fonctionnent à l'identique.
L'installation de l'option ne change rien aux usages existants.

**Why this priority**: garantie de non-régression portée par la
décision d'évaluation — la métrique « sans l'option, layout
strictement identique » doit être structurellement satisfaite.

**Independent Test**: exécutable sans l'option sur le corpus des 10
exemples du projet : le contenu du dossier de sortie est identique à
celui d'aujourd'hui, et les tests existants du mode par défaut restent
au vert sans modification de leurs assertions.

**Acceptance Scenarios**:

1. **Given** l'option absente de la ligne de commande, **When** un
   document est traité, **Then** le JSON est écrit à plat dans le
   dossier de sortie comme avant, sans unité ni copie.
2. **Given** un dossier de sortie contenant 10 JSON existants à plat,
   **When** l'option est utilisée pour de nouveaux documents, **Then**
   aucun des 10 JSON existants n'est déplacé, renommé ou modifié.
3. **Given** l'option absente, **When** un dossier d'entrée contient un
   document et un JSON au format de sortie, **Then** l'amendement sur
   place se produit exactement comme avant (spécification 001
   FR-026/FR-027), sans unité ni copie.

---

### User Story 3 - Amendement d'une paire rangée (Priority: P3)

L'utilisateur possède une unité contenant une copie de la source et son
JSON (produite par l'option). Il relance l'outil sur cette unité : le
JSON doit être amendé sur place par le repli existant « paire unique du
sous-dossier » (spécification 001 FR-027), sans consommer de nouveau
numéro ; la copie n'est jamais modifiée ni recréée par un amendement.
En revanche, relancer l'outil sur la source d'origine (hors unité)
crée une nouvelle paire — cette asymétrie est assumée par la décision
d'évaluation (option B).

**Why this priority**: cas d'usage d'itération documenté par
l'évaluation ; il fixe la frontière du périmètre B pour éviter tout
glissement vers l'appariement étendu (option C, hors périmètre).

**Independent Test**: exécutable sur une unité contenant `IFRI.md`
(copie) et son JSON : la relance amende le JSON sur place, la copie et
le compteur restent intacts.

**Acceptance Scenarios**:

1. **Given** une unité contenant une copie `IFRI.md` et son JSON au
   format de sortie, **When** l'outil traite cette unité (option
   active ou absente), **Then** le JSON est amendé sur place via le
   repli « paire unique du sous-dossier », sans nouveau numéro.
2. **Given** une unité amendée, **When** l'amendement se termine,
   **Then** la copie de la source est inchangée (octet pour octet).
3. **Given** la source d'origine hors de toute unité, **When**
   l'utilisateur la re-traite, **Then** une nouvelle paire est créée
   avec un nouveau numéro (asymétrie assumée, hors périmètre :
   retrouver la paire depuis la source).

---

### Edge Cases

- Document en échec définitif (après retries) : aucune unité créée,
  aucune copie écrite, aucun numéro consommé (spécification 001 FR-023
  et FR-032, inchangées).
- Amendement d'un JSON apparié dans le dossier d'entrée alors que
  l'option est active : l'amendement se produit sur place à
  l'emplacement d'origine ; aucune unité ni copie n'est créée pour un
  amendement (l'option ne s'applique qu'aux créations).
- Unité dont le nom existerait déjà (collision après un cycle complet
  du compteur, > 10 000 sorties au même endroit) : le comportement
  suit la sémantique actuelle des noms de fichiers, qui se répètent
  aussi après un cycle ; le JSON est écrit dans l'unité existante, et
  la copie de la source écrase celle éventuellement présente dans
  l'unité.
- Fichier source illisible au moment de la copie : le document est
  traité comme en échec (aucune unité, aucun numéro consommé) — une
  paire incomplète ne doit jamais être laissée sur disque.
- L'option combinée à `--output-folder` : les unités sont créées sous
  le dossier de sortie configuré, créé automatiquement s'il est absent
  (spécification 001 FR-021, inchangée).
- Un chemin d'entrée couvrant le dossier de sortie (ou un de ses
  parents) : le dossier de sortie, chemin résolu, est exclu de la
  découverte des documents ; les copies présentes dans les unités ne
  sont jamais candidates au re-traitement.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La commande DOIT exposer une option `--sous-dossiers`,
  booléenne et sans valeur, inactive par défaut ; son absence produit
  un comportement strictement identique à l'actuel.
- **FR-002**: À la création d'un nouveau JSON avec l'option active,
  l'outil DOIT placer le JSON dans une unité de rangement unique du
  dossier de sortie, nommée : numéro d'occurrence à 4 chiffres, suivi
  d'un tiret puis du préfixe normalisé du nom du fichier d'entrée (le
  même que celui du nom du JSON, spécification 001 FR-022 — espaces
  remplacées par `_`, accents simplifiés), sans extension (ex.
  `0068-IFRI`, `0071-Cour_des_comptes_rappo`).
- **FR-003**: L'unité DOIT contenir une copie exacte du fichier source
  (contenu identique), portant le nom d'origine du fichier d'entrée,
  créée en même temps que le JSON, quelle que soit l'extension du
  fichier source (`.md` ou `.txt`). Si une copie de même nom existe
  déjà dans l'unité, elle est écrasée (cohérence avec l'écrasement
  d'un JSON de nom identique en mode plat).
- **FR-004**: Le nom du JSON dans l'unité DOIT rester régi par la règle
  de nommage en vigueur (spécification 001 FR-022, contrat 002) : seul
  son rangement change, pas son nom.
- **FR-005**: Sans l'option, aucune unité ni copie NE DOIT être créée ;
  les sorties sont écrites à plat dans le dossier de sortie, et aucun
  fichier existant NE DOIT être renommé, recréé ou déplacé, option
  active ou non.
- **FR-006**: L'option NE DOIT modifier ni la numérotation des
  occurrences (spécification 001 FR-023 à FR-025), ni l'appariement,
  ni la fusion d'amendement : un JSON apparié est amendé sur place à
  son emplacement d'origine, sans unité, copie ni numéro consommé.
- **FR-007**: Un document en échec NE DOIT laisser aucune trace
  partielle : ni unité, ni copie, ni numéro consommé.
- **FR-008**: Le re-traitement d'une unité existante DOIT amender le
  JSON sur place par le repli « paire unique du sous-dossier »
  (spécification 001 FR-027) ; la copie de la source NE DOIT jamais
  être modifiée, recréée ni supprimée par un amendement.
- **FR-009**: Les unités DOIVENT être créées sous le dossier de sortie
  configuré par `--output-folder` (défaut `output/`), créé
  automatiquement s'il est absent.
- **FR-010**: La documentation utilisateur (README, contrat CLI) et la
  spécification 001 DOIVENT décrire l'option et son comportement réel
  sans divergence ; le point « aucune copie n'est écrite dans le
  dossier de sortie » de la spécification 001 (FR-026, session
  2026-10-13) DOIT être amendé explicitement : une copie de la source
  est écrite dans le dossier de sortie, uniquement à la création et
  uniquement quand l'option est active.
- **FR-011**: Quand un chemin d'entrée couvre le dossier de sortie,
  celui-ci (chemin résolu) DOIT être exclu de la découverte des
  documents ; les copies de source présentes dans les unités NE DOIVENT
  jamais être traitées comme des entrées.

### Key Entities

- **Unité de rangement**: sous-dossier du dossier de sortie, unique
  par document créé, nommé `NNNN-<préfixe normalisé>` (numéro
  d'occurrence en tête, préfixe identique à celui du JSON) ; contient
  exactement le JSON de sortie et la copie de la source.
- **Copie de source**: réplique exacte du fichier d'entrée (contenu
  identique, nom d'origine conservé), figée à la création ; jamais
  mise à jour ni supprimée par la suite.
- **Option de rangement**: flag CLI booléen `--sous-dossiers`,
  inactive par défaut ; n'active le rangement en unités que pour les
  créations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur l'exemple réel `IFRI.md`, la paire « source + JSON »
  est retrouvée sans aucune manipulation manuelle dans une unité unique
  (baseline : JSON seul à plat dans `output/`, source séparée).
- **SC-002**: Sans l'option, l'exécution sur le corpus des 10 exemples
  du projet produit un dossier de sortie identique à celui d'aujourd'hui
  ; les tests existants du mode par défaut restent au vert sans
  modification de leurs assertions de layout (baseline : 96 tests
  verts).
- **SC-003**: Après installation de l'option, les 10 JSON existants
  du dossier de sortie restent à plat, inchangés, quel que soit l'usage
  de l'option (baseline : 10 JSON à plat).
- **SC-004**: Les documents de référence (README, contrat CLI,
  spécification 001 amendée) décrivent l'option et la copie sans
  divergence avec le comportement réel.

## Assumptions

- La copie de la source est figée à la création : aucune synchronisation
  ultérieure entre la source et sa copie (hors périmètre de la décision
  d'évaluation, option B).
- L'asymétrie d'amendement est assumée : re-traiter la source d'origine
  crée une nouvelle paire ; retrouver la paire depuis la source
  (appariement étendu, option C) est un incrément ultérieur éventuel,
  hors périmètre.
- La collision des noms d'unités après un cycle complet du compteur
  (> 10 000 sorties au même endroit) suit la sémantique existante des
  noms de fichiers, qui se répètent aussi après un cycle ; aucun
  mécanisme de prévention dédié n'est ajouté (constitution : YAGNI).
- L'option n'accepte aucune valeur ni paramètre : présence = active,
  absence = inactive.
