# Feature Specification: Préfixe de 20 caractères pour les sorties JSON

**Feature Branch**: `003-titre-20-car`

**Created**: 2026-10-27

**Status**: Draft

**Input**: Handoff de l'évaluation `titre-20-chars` (verdict go) — nommage
des nouvelles sorties sur les 20 premiers caractères normalisés du nom
d'entrée ; appariement d'amendement reconnaissant un JSON à partir de 8
caractères et prolongeant l'analyse jusqu'à 20.

## Clarifications

### Session 2026-10-27

- Q: Le nom du fichier JSON candidat doit-il être comparé tel quel ou
  normalisé avant la comparaison d'appariement ? → A: Normalisé (le nom du
  JSON candidat est normalisé — espaces remplacées par `_`, accents
  simplifiés — avant la comparaison avec le nom du document ; les JSON
  renommés manuellement avec accents ou espaces sont ainsi reconnus).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sorties identifiables par leur seul nom (Priority: P1)

L'utilisateur traite un lot de documents aux noms longs et proches (ex.
`Cour_des_comptes_rapport.md` et `Cour_de_comptes_pagination.md`). Une fois
l'outil exécuté, chaque JSON produit dans le dossier de sortie porte un nom
assez long pour que l'utilisateur le rattache au bon document source sans
l'ouvrir : les 20 premiers caractères normalisés du nom d'entrée.

**Why this priority**: c'est la raison d'être de la fonctionnalité — le
corpus réel du projet compte déjà 2 paires de sorties quasi indiscernables
sur 10 ; sans ce changement, le problème persiste et s'aggrave.

**Independent Test**: exécutable sur les 10 exemples de `Interne-Dev/` en
vérifiant que chaque sortie est rattachable à sa source par son seul nom de
fichier.

**Acceptance Scenarios**:

1. **Given** un document nommé `Cour_des_comptes_rapport.md`, **When** il est
   traité, **Then** la sortie est nommée à partir des 20 premiers caractères
   normalisés de son nom (`Cour_des_comptes_rappo-000X.json`).
2. **Given** deux documents dont les noms divergent dans les 20 premiers
   caractères normalisés, **When** ils sont traités, **Then** leurs sorties
   sont distinguables par leur seul préfixe.
3. **Given** un document dont le nom compte moins de 20 caractères
   normalisés, **When** il est traité, **Then** la sortie utilise le nom
   complet normalisé, sans padding.

---

### User Story 2 - Amendement des corpus déjà traités préservé (Priority: P2)

L'utilisateur possède des dossiers d'entrée contenant déjà des JSON au
format de l'outil, nommés sur 8 caractères par les versions précédentes. En
réexécutant l'outil sur ces dossiers, ces JSON existants doivent toujours
être reconnus et amendés sur place, exactement comme avant le changement.

**Why this priority**: garantir qu'un changement cosmétique de nommage ne
casse pas la promesse d'amendement des versions précédentes ; c'est le
risque principal identifié par l'évaluation.

**Independent Test**: exécutable sur un dossier contenant un document et un
JSON existant au nom court (8 caractères) : le JSON doit être amendé, sans
nouvelle sortie ni numéro consommé.

**Acceptance Scenarios**:

1. **Given** un dossier avec `Rapport info.md` et un JSON existant nommé
   `Rapport_-0001.json`, **When** l'outil traite le dossier, **Then** le JSON
   existant est amendé sur place et conserve son nom et son numéro.
2. **Given** un dossier avec un seul document et un seul JSON hors préfixe
   commun, **When** l'outil traite le dossier, **Then** le repli « paire
   unique du sous-dossier » s'applique comme avant.

---

### User Story 3 - Départage ancien/nouveau nommage (Priority: P3)

Dans un dossier, un ancien JSON (nom sur 8 caractères) et un nouveau (nom
sur 20) peuvent coexister pour un même document. L'appariement doit
reconnaître les deux comme candidats, prolonger l'analyse jusqu'à 20
caractères et retenir le candidat qui partage le plus de caractères avec le
nom du document ; en cas d'égalité parfaite, aucun n'est retenu et le
document est traité seul (comportement sûr actuel).

**Why this priority**: cas limite documenté par l'évaluation ; rare mais
doit être défini pour éviter un amendement silencieux du mauvais JSON.

**Independent Test**: exécutable sur un dossier contenant un document, un
JSON ancien et un JSON nouveau du même document : seul le candidat le plus
proche est amendé.

**Acceptance Scenarios**:

1. **Given** un dossier avec `Rapport info.md`, un ancien `Rapport_-0001.json`
   et un nouveau `Rapport_info-0007.json`, **When** l'outil traite le dossier,
   **Then** seul le JSON dont le nom partage le plus de caractères avec le
   nom du document est amendé.
2. **Given** deux candidats partageant exactement le même nombre de
   caractères avec le nom du document, **When** l'appariement est évalué,
   **Then** aucun candidat n'est retenu et le document est traité seul.

---

### Edge Cases

- Document dont le nom normalisé compte moins de 8 caractères
  (ex. `IFRI.md`) : la comparaison utilise le nom complet ; aucune
  exiguïté artificielle.
- Deux documents partageant leurs 20 premiers caractères normalisés :
  leurs sorties restent distinctes par le numéro d'occurrence, mais
  l'appariement ne peut pas les départager — chaque candidat ambigu reste
  non lié (comportement actuel conservé).
- Un JSON existant au format reconnu mais nommé sans rapport avec le
  document : non apparié par préfixe ; rattrapé uniquement par le repli
  « paire unique ».
- Un JSON existant au format reconnu dont le nom contient espaces ou
  accents (ex. `Rapport infó-0001.json`) : le nom est normalisé avant
  comparaison, il peut donc être reconnu comme candidat.
- Caractères accentués et espaces dans les 20 premiers caractères : la
  normalisation actuelle (espaces remplacées par `_`, accents simplifiés)
  s'applique inchangée, l'underscore compte pour un caractère.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le nom d'un nouveau fichier de sortie DOIT être composé des
  20 premiers caractères normalisés du nom du fichier d'entrée sans
  extension + `-` + numéro d'occurrence à 4 chiffres + `.json`. Les critères
  de normalisation existants (espaces remplacées par `_`, accents
  simplifiés) restent inchangés.
- **FR-002**: Si le nom normalisé du fichier d'entrée compte moins de 20
  caractères, le nom de sortie DOIT utiliser le nom complet, sans
  complément.
- **FR-003**: L'appariement texte/JSON DOIT reconnaître comme candidat tout
  JSON au format de sortie dont le nom, normalisé (espaces remplacées par
  `_`, accents simplifiés), partage au moins les 8 premiers caractères
  normalisés du document (ou le nom complet si plus court).
- **FR-004**: L'appariement DOIT prolonger l'analyse jusqu'à 20 caractères :
  parmi les candidats reconnus, celui dont le nom normalisé partage avec le
  nom normalisé du document le préfixe commun le plus long (au maximum 20
  caractères) DOIT être retenu.
- **FR-005**: En cas d'égalité parfaite entre plusieurs candidats, le
  document DOIT être traité seul (aucun appariement), sans erreur ni
  amendement arbitraire.
- **FR-006**: Aucun JSON existant NE DOIT être renommé, recréé ou déplacé à
  l'occasion d'un amendement ; il conserve son nom d'origine (comportement
  FR-031 de la spécification 001, inchangé).
- **FR-007**: La numérotation des occurrences (séquence, compteur,
  non-consommation par les amendements) DOIT rester inchangée.
- **FR-008**: La documentation utilisateur (README, contrat de sortie) et
  la spécification 001 (FR-022) DOIVENT décrire le comportement de nommage
  réel après le changement, sans divergence entre documents et outil.

### Key Entities

- **Préfixe de sortie**: les premiers caractères normalisés du nom du
  fichier d'entrée sans extension ; longueur effective entre 1 et 20
  caractères ; unique source du nom de sortie.
- **Paire texte/JSON**: association entre un document d'entrée et un JSON
  existant à amender ; reconnue par comparaison progressive du préfixe de 8
  à 20 caractères, départagée par la longueur de correspondance.
- **Candidat d'appariement**: JSON au format de sortie dont le nom partage
  au moins 8 caractères normalisés avec le document ; devient paire s'il
  est le candidat le plus proche.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur le corpus des 10 exemples du projet, zéro paire de
  sorties indiscernable par leur préfixe (baseline : 2 paires —
  `Cour_des`/`Cour_de_` et `Ecalle_c`/`Ecalle_o`).
- **SC-002**: Tous les comportements d'amendement vérifiés avant le
  changement restent vérifiés après : les corpus déjà traités continuent
  d'être amendés sans régression.
- **SC-003**: Les documents de référence du projet (README, contrat de
  sortie, spécification 001) décrivent sans divergence le nommage et
  l'appariement réels (baseline : 4 documents décrivant « 8 premiers
  caractères »).

## Assumptions

- « Titre de l'entrée » désigne le nom du fichier d'entrée sans extension
  (lecture de FR-022 de la spécification 001 et de l'implémentation
  actuelle), et non le champ `Titre` extrait par le LLM.
- La sémantique par défaut de l'appariement progressif est : reconnaissance
  à partir de 8 caractères partagés, sélection du candidat partageant le
  plus de caractères jusqu'à 20, non-liage en cas d'égalité parfaite
  (US-3, FR-003 à FR-005).
- Les JSON déjà produits dans les dossiers de sortie ne sont pas migrés ;
  la cohabitation de noms courts (anciens) et longs (nouveaux) est acceptée.
- Les noms des fichiers d'entrée du corpus divergent dans leurs 20 premiers
  caractères normalisés (vérifié sur les 10 exemples actuels).
- Le changement de nommage s'applique à toutes les nouvelles sorties,
  quelle que soit la longueur du nom d'entrée ; il n'existe pas d'option de
  configuration de la longueur.
