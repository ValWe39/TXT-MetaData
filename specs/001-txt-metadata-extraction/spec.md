# Feature Specification: TXT-MetaData — Extraction de métadonnées de documents texte

**Feature Branch**: `001-initialisation`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Outil TXT-MetaData : extraire une liste de
métadonnées d'un texte d'entrée (.md ou .txt) à l'aide d'un LLM Mistral AI par
appel API ; sortie JSON nommée à partir du titre du fichier avec compteur
d'occurrence persistant ; gestion des multi-entrées (fichiers, dossiers,
sous-dossiers), amendement de fichiers sortie existants, options CLI (modèle,
batch, retry, température, dossier de sortie)."

## Clarifications

### Session 2026-10-13

- Q: En cas d'échec définitif sur l'un des documents (après épuisement des
  retries) pendant un traitement multi-entrées, que doit faire l'outil ? → A:
  Continuer : l'échec d'un document ne bloque pas le lot ; l'outil journalise
  l'erreur, passe au document suivant et présente un bilan final.
- Q: Quand un JSON de sortie existant est amendé, où la version amendée
  doit-elle être écrite ? → A: Sur place : le JSON existant est modifié à son
  emplacement d'origine (dossier d'entrée) ; aucune copie n'est écrite dans le
  dossier de sortie.
- Q: Quel objectif de temps de traitement l'outil doit-il viser, mesurable pour
  les tests ? → A: 10 documents traités en moins de 15 minutes (objectif par
  lot, sans seuil par document).
- Q: Quel style de guillemets la citation composée doit-elle utiliser autour du
  titre ? → A: Guillemets droits (") autour du titre, quel que soit le document
  source.
- Précision utilisateur : par défaut, l'outil crée le dossier `output` (à la
  racine du projet) s'il n'existe pas et y insère les sorties ; interprétation
  retenue : création automatique sans demande de confirmation (outil CLI en
  traitement par lot), sauf override par `--output-folder`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Métadonnées d'un fichier texte unique (Priority: P1)

L'utilisateur fournit un fichier texte (.md ou .txt) à l'outil. L'outil
sélectionne automatiquement un échantillon du début et de la fin du document,
interroge un modèle de langage Mistral AI pour identifier les métadonnées du
document (typologie, auteurs, titre, éditeur, date, référence, citation), et
produit un fichier JSON dans le dossier de sortie. L'utilisateur n'a aucune
commande complémentaire à saisir pour ce cas standard.

**Why this priority**: C'est le cœur de la valeur de l'outil ; sans ce parcours,
rien ne fonctionne.

**Independent Test**: Fournir un des fichiers d'exemple (ex.
`Interne-Dev/Exemples/IFRI/IFRI.md`) et vérifier que le JSON produit correspond
à la sortie manuelle attendue.

**Acceptance Scenarios**:

1. **Given** un fichier `MonRapport.md` de 50 000 caractères, **When**
   l'utilisateur lance la commande standard sur ce fichier, **Then** l'outil
   produit un JSON contenant au minimum `Typologie` (valeur valide parmi les 8
   catégories) et, quand ils sont identifiables, les champs optionnels.
2. **Given** un fichier de moins de 36 000 caractères, **When** il est traité,
   **Then** l'intégralité du texte est envoyée à l'analyse (aucune troncature,
   aucun séparateur artificiel).
3. **Given** le fichier de compteur est absent à la racine de l'outil, **When**
   le premier JSON est produit, **Then** il porte le numéro d'occurrence `0001`.
4. **Given** le fichier de compteur contient `0012`, **When** un document est
   produit, **Then** il porte le numéro `0013` et le compteur est mis à jour
   immédiatement après écriture du JSON.
5. **Given** le fichier de compteur est présent mais illisible ou corrompu,
   **When** l'outil est lancé, **Then** il échoue rapidement avec un message
   explicite, sans produire aucune sortie et sans écraser le compteur.
6. **Given** aucun dossier `output` n'existe à la racine du projet, **When**
   l'utilisateur lance la commande standard sans option, **Then** l'outil crée
   automatiquement le dossier `output` et y écrit le JSON de sortie, sans
   demander de confirmation.

---

### User Story 2 - Échantillonnage du texte pour l'analyse (Priority: P2)

Pour les documents longs, l'outil n'envoie pas l'intégralité du texte au modèle
: il construit un extrait composé du début et de la fin du document (environ 20
000 premiers et 16 000 derniers caractères, bornes indicatives maximales). La
coupure respecte une hiérarchie de préservation : sous-partie > paragraphe >
phrase > mot, avec ajout de "..." si une phrase est coupée. Un dispositif clair
distingue les deux segments pour que le modèle ne confonde pas la fin du
document avec la suite hiérarchique du début.

**Why this priority**: Détermine la qualité et le coût de l'extraction sur les
documents longs ; pilote directement la justesse des métadonnées.

**Independent Test**: Traiter un document long (ex.
`Cour_des_comptes_rapport.md`) et vérifier que les métadonnées de couverture (en
début) et de colophon (en fin) sont toutes deux détectées.

**Acceptance Scenarios**:

1. **Given** un document de plus de 36 000 caractères, **When** l'extrait est
   construit, **Then** il contient une partie du début et une partie de la fin,
   séparées par un dispositif identifiable (ex. mention explicite de fin de
   première partie / début de dernière partie).
2. **Given** un point de coupure qui tombe au milieu d'une sous-partie, **When**
   la coupure est calculée, **Then** elle est reculée pour préserver la
   sous-partie ; à défaut, le paragraphe ; à défaut, la phrase ; à défaut, aucun
   mot n'est coupé.
3. **Given** une coupure qui sépare une phrase, **When** l'extrait est
   constitué, **Then** "..." est inséré à l'endroit de la coupure.

---

### User Story 3 - Identification des métadonnées par appel LLM (Priority: P2)

L'outil interroge un modèle de langage Mistral AI avec un prompt clair et
robuste, conçu pour limiter l'hallucination : le modèle ne doit renseigner un
champ que s'il est réellement présent dans l'extrait. La typologie est
obligatoire (Article, Rapport, Ouvrage, Cours, Bibliothèque, Extrait,
Communiqué, Compte-rendu, Autre). Les autres champs sont renseignés uniquement
si l'outil les trouve. Le champ "Citation" est construit soit en reprenant
exactement un paragraphe de citation explicite présent dans le texte, soit par
composition déterministe à partir des autres champs (auteurs dans l'ordre
d'apparition, maximum 3 auteurs puis "et al.", majuscules aux noms propres,
acronymes et débuts de phrase uniquement).

**Why this priority**: C'est la fonctionnalité de valeur vue par l'utilisateur ;
la qualité du prompt et de la logique de citation conditionne la conformité des
sorties.

**Independent Test**: Comparer les sorties produites sur les 10 exemples fournis
avec les sorties manuelles de référence.

**Acceptance Scenarios**:

1. **Given** un document qui contient un paragraphe "Comment citer ce rapport :
   ...", **When** les métadonnées sont extraites, **Then** le champ "Citation"
   reprend exactement le contenu et le format de ce paragraphe, et seulement
   celui-ci.
2. **Given** un document sans paragraphe de citation mais avec auteur, titre,
   éditeur et date identifiés, **When** la sortie est produite, **Then** la
   citation est composée au format `<auteur>, <titre>, <référence>, <éditeur>,
   <date>` (la référence étant omise si vide).
3. **Given** un document avec 5 auteurs, **When** la citation est composée,
   **Then** seul le premier auteur est cité, suivi de "et al.".
4. **Given** un rapport parlementaire sans auteur explicite, **When** les
   auteurs sont recherchés, **Then** les rapporteurs/co-rapporteurs
   (parlementaires présentant le rapport) sont retenus comme auteurs.
5. **Given** un document dont les métadonnées ne figurent nulle part dans
   l'extrait, **When** la sortie est produite, **Then** les champs non trouvés
   restent vides (pas de valeur inventée).
6. **Given** plusieurs candidats pour un même champ, **When** la sortie est
   produite, **Then** l'outil retient le plus probable.

---

### User Story 4 - Traitement multi-entrées transparent (Priority: P3)

L'utilisateur peut fournir un fichier, un dossier, ou plusieurs dossiers (y
compris avec des sous-dossiers). L'outil détecte seul le mode et traite chaque
fichier texte valide comme une entrée standard (une entrée = une sortie). Les
fichiers au format non attendu sont ignorés silencieusement. Chaque sortie
consomme un numéro d'occurrence dans l'ordre de production.

**Why this priority**: Étend la productivité de l'outil du cas unitaire au
traitement de masse sans commande supplémentaire.

**Independent Test**: Lancer l'outil sur `Interne-Dev/Exemples/` et vérifier
qu'un JSON est produit par fichier texte, dans tous les sous-dossiers.

**Acceptance Scenarios**:

1. **Given** un dossier contenant 3 `.txt` et 1 `.pdf`, **When** l'outil est
   lancé sur ce dossier, **Then** 3 JSON sont produits et le `.pdf` est ignoré.
2. **Given** un dossier contenant des sous-dossiers avec des `.md` et `.txt`,
   **When** l'outil est lancé sur le dossier racine, **Then** tous les fichiers
   texte de l'arborescence sont traités.
3. **Given** trois dossiers en entrée, **When** l'outil est lancé, **Then** les
   fichiers de tous les dossiers sont traités dans un processus unique.
4. **Given** un traitement multi-entrées, **When** les JSON sont créés, **Then**
   chaque JSON reçoit un numéro d'occurrence unique dans l'ordre de création,
   sans doublon au sein de l'exécution.

---

### User Story 5 - Amendement d'un fichier sortie existant (Priority: P3)

Lorsqu'un dossier d'entrée contient, en plus du fichier texte, un JSON au format
de sortie de l'outil, l'outil amende ce JSON existant au lieu d'en créer un
nouveau. Il complète en priorité les champs vides, et ne remplace un champ déjà
rempli que si le nouveau résultat présente un degré d'assurance élevé.

**Why this priority**: Évite d'écraser le travail de correction manuel de
l'utilisateur ; indispensable au workflow itératif.

**Independent Test**: Placer un JSON partiellement rempli à côté d'un texte
d'exemple, relancer l'outil, et vérifier que seuls les champs vides ont été
complétés.

**Acceptance Scenarios**:

1. **Given** un dossier contenant `Texte.md` et un JSON au format de sortie avec
   `Typologie` remplie et `Titre` vide, **When** l'outil est lancé, **Then** le
   JSON existant est amendé : `Titre` est complété, `Typologie` est conservée
   sauf assurance élevée du contraire.
2. **Given** un dossier contenant plusieurs `.md`/`.txt` et plusieurs JSON non
   appariables, **When** l'outil est lancé, **Then** seuls les fichiers texte
   pouvant être liés sans ambiguïté à un JSON (par le titre ou paire unique dans
   un sous-dossier) sont amendés ; les fichiers texte restants sont traités
   comme éléments seuls.
3. **Given** un JSON amendé, **When** le traitement se termine, **Then** aucun
   nouveau fichier de sortie ni numéro d'occurrence supplémentaire n'est créé
   pour ce document.

---

### User Story 6 - Configuration par ligne de commande (Priority: P4)

L'utilisateur peut ajuster le comportement via des options : choix du modèle
(large4, large, medium, small par défaut, 14b, 8b, 3b, zai), température du
modèle (0 par défaut), taille de batch (0 à 100, 25 par défaut), nombre de retry
(0 à 10, 3 par défaut), délai du premier retry (1 à 10 s, 3 par défaut), dossier
de sortie ("output" à la racine par défaut). Les retries suivent une progression
exponentielle (délai multiplié par 2 à chaque essai).

**Why this priority**: Confort et maîtrise avancée ; le comportement par défaut
doit être pertinent sans aucune option.

**Independent Test**: Lancer avec chaque option sur un fichier d'exemple et
vérifier la prise en compte (modèle appelé, délais de retry observés,
emplacement de sortie).

**Acceptance Scenarios**:

1. **Given** la commande `txt-metadata` sans option, **When** elle est exécutée,
   **Then** le modèle `mistral-small-latest` est utilisé avec température 0,
   batch 25, retry 3, délai 3 s, sortie dans `output/`.
2. **Given** l'option de choix de modèle avec `medium`, **When** la commande est
   exécutée, **Then** le modèle `mistral-medium-latest` est utilisé.
3. **Given** un appel API qui échoue, **When** les retries s'enchaînent,
   **Then** les tentatives ont lieu après 3 s, puis 6 s, puis 12 s (limité au
   nombre de retry configuré), puis l'outil signale l'échec.
4. **Given** une option hors bornes (ex. température 5), **When** la commande
   est exécutée, **Then** l'outil rejette la valeur avec un message explicite
   avant tout traitement.

---

### Edge Cases

- **Document court** (moins de la somme des deux bornes d'échantillonnage) :
  l'intégralité du texte est analysée, sans séparateur.
- **Document dont le titre de fichier contient des accents/espaces** : le nom de
  sortie remplace les espaces par `_` et simplifie les accents, puis ajoute
  `-NNNN`.
- **Compteur à 9999** : le document suivant porte `0000` (retour à 0000 après
  9999, cycle recommencé), puis `0001`.
- **Interruption brutale de l'exécution** : un numéro consommé n'est jamais
  réutilisé (persistance après chaque document).
- **Fichier texte vide ou quasi vide** : l'outil produit une sortie avec
  `Typologie` = "Autre" et champs optionnels vides, sans échouer.
- **Texte contenant de faux candidats** (mentions d'autres documents,
  bibliographies) : le choix se porte sur le candidat le plus probable pour le
  document lui-même.
- **Titre de document de plus de 150 caractères** : tronqué à 150 caractères
  dans le champ `Titre` (la citation utilise la valeur tronquée).
- **Fichiers de formats inattendus** (pdf, docx, images) : ignorés sans erreur
  bloquante.
- **Plusieurs LLM candidats pour un même champ** : si des appels multiples
  (jusqu'à 5) sont jugés pertinents, notamment pour la citation, leurs résultats
  sont consolidés sans dépasser 5 appels par document.
- **Dossier de sortie inexistant** : créé automatiquement.
- **Fichier `.env` absent ou clé API manquante** : échec rapide avec message
  explicite avant tout appel ; la clé n'est jamais copiée, loguée ou persistée
  ailleurs que dans la variable d'environnement.

## Requirements *(mandatory)*

### Functional Requirements

#### Entrées et échantillonnage

- **FR-001**: L'outil DOIT accepter en entrée un fichier texte (.md ou .txt), un
  dossier, ou plusieurs dossiers, et détecter seul le mode sans commande
  complémentaire.
- **FR-002**: Pour les documents longs, l'outil DOIT construire un extrait
  composé d'une partie du début (environ 20 000 premiers caractères, borne
  indicative maximale) et d'une partie de la fin (environ 16 000 derniers
  caractères, borne indicative maximale).
- **FR-003**: Les points de coupure DOIVENT respecter la hiérarchie de
  préservation : sous-partie si possible, sinon paragraphe, sinon phrase, sinon
  mot ; "..." DOIT être inséré lorsqu'une phrase est séparée.
- **FR-004**: L'extrait DOIT comporter un dispositif permettant au modèle
  d'identifier que les deux segments sont distincts (la fin du texte n'est pas
  la suite hiérarchique du début).
- **FR-005**: Pour un document plus court que la somme des bornes, l'outil DOIT
  envoyer l'intégralité du texte.

#### Métadonnées

- **FR-006**: Le champ `Typologie` est OBLIGATOIRE et DOIT valoir exactement
  l'une des valeurs : Article, Rapport, Ouvrage, Cours, Bibliothèque, Extrait,
  Communiqué, Compte-rendu, Autre (définitions de la section 2 du cahier des
  charges).
- **FR-007**: Les champs `Auteur(s)`, `Titre`, `Editeur`, `Date`, `Référence`,
  `Citation` sont OPTIONNELS : ils ne DOIVENT être remplis que si l'information
  est trouvée dans l'extrait ; en cas de candidats multiples, le plus probable
  est retenu.
- **FR-008**: Le champ `Auteur(s)` DOIT contenir une chaîne par auteur ou
  co-auteur, avec les règles métier suivantes : rapporteurs/co-rapporteurs pour
  un rapport ; parlementaires présentant le rapport pour un rapport
  parlementaire ; société ou revue d'origine pour un communiqué, article ou
  cours sans auteur personne physique.
- **FR-009**: Le champ `Titre` DOIT être limité à 150 caractères, tronqué
  au-delà.
- **FR-010**: Le champ `Editeur` DOIT être compris au sens élargi (revue, site
  internet, institution, think tank, éditeur d'ouvrage).
- **FR-011**: Le champ `Citation` DOIT être rempli selon deux cas exclusifs :
  (a) un paragraphe explicitant comment citer le document existe dans le texte —
  reprise exacte de son contenu et format ; (b) sinon, composition à partir des
  autres champs au format `<auteur>, <titre>, <référence>, <éditeur>, <date>`
  (référence omise si vide).
- **FR-012**: La citation composée DOIT respecter : minuscules partout sauf noms
  propres, acronymes et initiales de phrase ; auteurs dans l'ordre d'apparition,
  séparés par des virgules, le dernier relié par "et" s'il s'agit de noms
  propres ; s'il y a plus de trois auteurs, seul le premier est cité, suivi de
  "et al." (jusqu'à trois auteurs inclus, tous sont cités) ; le titre est
  entouré de guillemets droits (").
- **FR-013**: Le champ `Citation` NE DOIT PAS être rempli si aucun paragraphe de
  citation n'existe et que les champs nécessaires à la composition sont
  insuffisants.

#### Modèle et appels API

- **FR-014**: L'analyse DOIT être réalisée par appel API à un modèle de langage
  de l'environnement Mistral AI, parmi : mistral-large-4, mistral-large-latest,
  mistral-medium-latest, mistral-small-latest (défaut), ministral-14b-latest,
  ministral-8b-latest, ministral-3b-latest, zai-glm-5-3.
- **FR-015**: Le prompt DOIT être clair, robuste et conçu pour éviter les
  hallucinations (aucune valeur inventée ; champs vides si information absente).
- **FR-016**: Pour les champs à réponse précise (notamment `Citation`), une
  solution hybride LLM/déterministe ou plusieurs appels LLM (maximum 5 par
  document) PEUVENT être utilisés, seulement si jugé pertinent.
- **FR-017**: Le nombre d'appels LLM par document NE DOIT PAS dépasser 5.
- **FR-018**: La clé d'API Mistral DOIT être chargée depuis la variable
  d'environnement `MISTRAL_API_KEY` (fichier .env local, non commité) ; il est
  INTERDIT de la copier, loguer ou persister ailleurs. Elle ne sert qu'aux
  appels API des modèles.
- **FR-019**: En cas d'échec d'appel, l'outil DOIT appliquer des retries à
  intervalle exponentiel (3 s, 6 s, 12 s par défaut), dans la limite configurée,
  avant de signaler l'échec.
- **FR-020**: Les appels LLM sur les entrées multiples DOIVENT pouvoir être
  groupés par lots de taille configurable (option `--taille-batch`, 0 à 100,
  défaut 25) ; une valeur de 0 signifie que chaque requête est traitée
  individuellement, sans lot. L'outil N'utilise PAS d'embedding : la clé API ne
  sert qu'aux appels LLM.

#### Sortie

- **FR-021**: La sortie DOIT être un JSON contenant les métadonnées, écrite par
  défaut dans un dossier `output` à la racine du projet : ce dossier DOIT être
  créé automatiquement par l'outil s'il n'existe pas, sans demande de
  confirmation, et recevoir toutes les nouvelles sorties (sauf override par
  `--output-folder`).
- **FR-022**: Le nom du fichier de sortie DOIT être : 20 premiers caractères du
  titre du fichier d'entrée (espaces remplacés par `_`, accents simplifiés) +
  `-` + numéro d'occurrence à 4 chiffres + `.json`.
- **FR-023**: Le numéro d'occurrence DOIT être attribué séquentiellement à
  chaque document produit (0001 au premier usage, +1 par document, retour à 0000
  après 9999), sans doublon au sein d'une exécution.
- **FR-024**: Le dernier numéro utilisé DOIT être mémorisé dans un fichier texte
  à la racine de l'outil contenant uniquement ce numéro, persisté après chaque
  document produit ; un numéro consommé n'est jamais réutilisé, même en cas
  d'interruption.
- **FR-025**: Si le fichier de compteur est absent, l'outil DOIT repartir à 0001
  ; s'il est présent mais illisible/corrompu, l'outil DOIT échouer rapidement
  avec un message explicite, sans écrire de sortie.
- **FR-026**: Un fichier JSON existant au format de sortie trouvé dans le
  dossier d'entrée DOIT être amendé plutôt que recréé : compléter en priorité
  les champs vides ; ne challenger les champs remplis que pour des résultats à
  haut degré d'assurance. L'amendement DOIT être écrit sur place, à
  l'emplacement d'origine du JSON, sans créer de copie dans le dossier de
  sortie.
- **FR-027**: L'appariement texte/JSON DOIT se faire par le titre de fichier
  (reconnaissance dès 8 caractères partagés, analyse prolongée jusqu'à 20,
  candidat le plus proche retenu, égalité parfaite non liée) ou par unicité
  de la paire dans un sous-dossier ; les textes non appariables sont
  traités comme éléments seuls.

#### Interface

- **FR-028**: La commande générale DOIT être `txt-metadata`.
- **FR-029**: Les options DOIVENT inclure : `--choix modèle-llm` (large4, large,
  medium, small défaut, 14b, 8b, 3b, zai), `--taille-batch` (0–100, défaut 25 ;
  0 = pas de batch), `--retry-occurences` (0–10, défaut 3), `--retry-time` (1–10
  s, défaut 3), `--output-folder` (défaut "output"), `--temperature-llm` (0–1,
  défaut 0).
- **FR-030**: Les valeurs d'options hors bornes DOIVENT être rejetées avec un
  message explicite avant tout traitement.
- **FR-031**: Un JSON amendé NE consomme PAS de numéro d'occurrence : il
  conserve son nom (et donc son numéro) d'origine ; seuls les nouveaux fichiers
  de sortie créés consomment un numéro.
- **FR-032**: En cas d'échec définitif d'un document (après épuisement des
  retries) dans un traitement multi-entrées, l'outil DOIT journaliser l'erreur,
  poursuivre avec les documents restants et présenter un bilan final (succès et
  échecs) ; un document en échec ne produit pas de sortie et ne consomme pas de
  numéro d'occurrence.

### Key Entities *(include if feature involves data)*

- **Document entrée (Texte1)**: fichier .md ou .txt fourni par l'utilisateur ;
  source de l'analyse.
- **Extrait (Extrait1)**: échantillon dérivé de Texte1 (début + fin), soumis à
  l'analyse ; porte un dispositif de séparation des deux segments.
- **Métadonnées**: ensemble des champs extraits (Typologie obligatoire ;
  Auteur(s), Titre, Editeur, Date, Référence, Citation optionnels).
- **Sortie JSON**: document produit, nommé `<20 premiers caractères du
  titre>-<numéro d'occurrence 4 chiffres>.json`, stocké dans le dossier de
  sortie ; peut préexister et être amendée.
- **Compteur d'occurrence**: fichier texte à la racine de l'outil contenant
  uniquement le dernier numéro utilisé ; persisté après chaque production ;
  source de vérité de la numérotation.
- **Paire texte/JSON**: association entre un document d'entrée et une sortie
  existante à amender.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur les 10 exemples fournis (`Interne-Dev/Exemples/`), les sorties
  produites correspondent aux sorties manuelles de référence : au minimum 8
  typologies exactes sur 10, et pour chaque document, au moins 80 % des champs
  non vides de la référence correctement remplis (toute divergence est
  documentée dans un rapport de test).
- **SC-002**: Aucune valeur hallucinée n'apparaît dans les sorties : tout champ
  rempli est justifiable par un élément présent dans l'extrait (vérifiable par
  revue manuelle sur l'échantillon de test).
- **SC-003**: Un document unique est traité de bout en bout (fichier → JSON)
  sans intervention utilisateur autre que la commande initiale.
- **SC-004**: Le compteur d'occurrence est fiable : après 5 exécutions
  interrompues ou non, aucun numéro n'est réutilisé et le compteur reflète
  toujours le dernier document produit.
- **SC-005**: Un dossier de 10 fichiers texte hétérogènes est traité en une
  seule commande, produisant exactement 10 sorties numérotées séquentiellement.
- **SC-006**: Un JSON partiellement rempli placé à côté de son texte voit ses
  champs vides complétés sans que les champs déjà remplis ne soient dégradés
  (sauf assurance élevée).
- **SC-007**: Aucune clé API n'apparaît jamais dans le code source, la
  configuration committée, les logs ou les sorties (conformité constitution du
  projet).
- **SC-008**: En cas d'indisponibilité du service d'analyse, l'outil applique
  les retries configurés ; en traitement multi-entrées, le document en échec est
  journalisé et le lot se poursuit ; aucun document en échec n'écrit de sortie
  partielle ni ne consomme de numéro d'occurrence, et un bilan final distingue
  succès et échecs.
- **SC-009**: Un lot de 10 documents est traité en moins de 15 minutes dans des
  conditions réseau normales (objectif indicatif par lot, sans seuil par
  document individuel).

## Assumptions

- La clé API est fournie par l'utilisateur via `.env` (`MISTRAL_API_KEY=...`) ;
  le fichier `.env` est exclu du versioning (conforme à la constitution du
  projet, principe I).
- Les documents en entrée sont en français (les exemples le sont) ; le prompt et
  les sorties sont en français, mais l'outil ne doit pas échouer sur un texte
  dans une autre langue.
- L'exemple `Corsen_ai` est fourni sans sortie manuelle de référence (absente de
  la liste du cahier des charges) : il sera utilisé pour la prise de
  connaissance des formats d'entrée et le test, et toute divergence sera
  signalée dans le rapport de test sans référence à comparer. De même, la sortie
  de `Cour_des_comptes_rapport` comporte une citation vide bien que des champs
  soient disponibles : ce cas (citation non exigée) est traité comme un exemple
  du champ optionnel non rempli.
- La sortie manuelle de référence `Grand_Continent_article` liste 4 auteurs dans
  la citation, ce qui ne respecte pas la règle retenue (plus de trois auteurs :
  premier auteur + "et al.", arbitrage utilisateur du 2026-10-13) ; cette
  divergence attendue sera documentée dans les rapports de test, la règle
  prévalant sur l'exemple.
- La sortie manuelle de référence `IFRI` utilise des guillemets français (« »)
  dans la citation, alors que le style retenu est le guillemet droit (") ; cette
  divergence attendue (unique parmi les références) sera documentée dans les
  rapports de test, la règle prévalant sur l'exemple.
- Le dossier `output` est créé automatiquement s'il n'existe pas ; l'utilisateur
  garde le contrôle de la rétention en supprimant ses fichiers (constitution,
  Data Retention).
- Le champ `Date` conserve le format trouvé dans le document (ex. "28/07/2026",
  "avril 2025") ; la citation composée utilise en revanche la date en toutes
  lettres selon les exemples de référence (ex. "28 juillet 2026", "mai 2022").
- Un "degré d'assurance élevé" pour l'amendement d'un champ déjà rempli
  correspond à une confiance marquée du pipeline d'extraction (score/confiance
  explicite) ; la barre est plus haute que pour remplir un champ vide.
- Les numéros 0000 à 9999 couvrent le cycle complet ; après 9999, le document
  suivant reçoit 0000 puis le cycle reprend à 0001.
- Les 11 ressources documentaires Mistral AI (API, batching, retry, JSON mode)
  fournies dans `Interne-Dev/Ressources/Mistral AI` font foi pour le
  comportement des appels ; elles sont datées d'octobre 2026.
- L'outil est généraliste : les exemples servent au calibrage et au test, pas au
  durcissement sur mesure ; les écarts constatés sur les exemples seront
  documentés dans les rapports de test.
