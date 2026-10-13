# Research — TXT-MetaData

Date : 2026-10-13 | Spec : [spec.md](./spec.md)

Sources : documentation Mistral AI fournie dans `Interne-Dev/Ressources/Mistral
AI/` (octobre 2026) — api-nettoye.md, batch-processing-nettoye.md,
json_mode-nettoye.md, first-api-request-nettoye.md ; constitution du projet ;
sorties manuelles de référence des 10 exemples.

## R1 — Sémantique de `--taille-batch` (FR-020)

- **Décision** : le « batch » désigne le groupement des requêtes LLM par lots de
  taille N (défaut 25), exécutés en parallèle, chaque requête restant un appel
  `chat/completions` individuel. Avec `--taille-batch 0`, chaque requête est
  envoyée séquentiellement, une par une.
- **Rationale** : le Batch API Mistral est asynchrone et orienté gros volumes
  (fichier JSONL de jusqu'à 1 M requêtes, création d'un job, polling, fenêtre
  d'achèvement de 24 h, remise de 50 %). Il est incompatible avec l'objectif de
  10 documents en moins de 15 minutes (SC-009) et avec un usage interactif local
  : exécution en un seul process, résultat immédiat.
- **Alternatives considérées** : Batch API Mistral (rejeté : asynchrone, job +
  polling + téléchargement de résultats, complexité supérieure à la valeur
  ajoutée pour des lots de 1 à quelques centaines de documents) ; embedding
  batching (rejeté : aucun embedding dans le pipeline, arbitré en clarification
  du 2026-10-13).

## R2 — Mode JSON et robustesse de la réponse (FR-015)

- **Décision** : chaque appel LLM utilise `response_format={"type":
  "json_object"}` (JSON mode Mistral), combiné à un prompt qui impose
  explicitement le schéma JSON attendu et interdit d'inventer des valeurs. La
  réponse est validée côté client contre le schéma de sortie ; toute valeur
  invalide (typologie hors liste) est rejetée et l'appel peut être rejoué dans
  la limite des 5 appels (FR-017).
- **Rationale** : la doc Mistral confirme que le JSON mode garantit un JSON
  valide mais recommande d'expliciter le format demandé dans le prompt ; la
  validation post-appel protège des champs vides ou faux.
- **Alternatives considérées** : parsing libre de la réponse (rejeté : fragile),
  sortie structurée sans validation (rejeté : risque d'hallucination non
  détectée).

## R3 — Retry exponentiel (FR-019)

- **Décision** : backoff exponentiel local : délai initial `--retry-time`
  (défaut 3 s), multiplié par 2 à chaque essai (3, 6, 12 s), jusqu'à
  `--retry-occurences` essais (défaut 3), par appel LLM.
- **Rationale** : la doc Mistral recommande explicitement le « wait and retry
  with exponential backoff » sur `429 Too Many Requests` ; le cahier des charges
  fixe les valeurs par défaut (3, 6, 12).
- **Alternatives considérées** : retry linéaire (rejeté : moins adapté aux
  limites de débit), abandon au premier échec (rejeté : non conforme).

## R4 — Extraction hybride de la citation (FR-011, FR-016)

- **Décision** : un seul appel LLM principal demande toutes les métadonnées, y
  compris la détection d'un éventuel paragraphe « comment citer ». La citation
  est ensuite construite de façon déterministe : (a) si un paragraphe de
  citation a été signalé par le LLM, il est repris exactement du texte source
  par recherche locale ; (b) sinon, composition `<auteur>, <titre>, <référence>,
  <éditeur>, <date>` avec les règles de casse et d'« et al. ». Le pipeline reste
  à 1 appel en nominal, la marge des 5 appels n'étant consommée que si la
  validation détectre un problème.
- **Rationale** : la citation est un champ à format contraint ; la partie
  déterministe élimine l'hallucination de mise en forme (guillemets, casse,
  ordre des auteurs, « et al. »). La reprise exacte du paragraphe source évite
  que le LLM paraphrase une citation officielle.
- **Alternatives considérées** : citation entièrement générée par le LLM (rejeté
  : format non contrôlable) ; appels multiples systématiques (rejeté : coût et
  latence inutiles).

## R5 — Échantillonnage (FR-002 à FR-005)

- **Décision** : cible de 20 000 premiers / 16 000 derniers caractères (bornes
  indicatives maximales). Les coupures sont reculées vers l'unité structurante
  la plus large disponible sous la borne : sous-partie (titre markdown `#`/`##`…
  le plus proche), puis paragraphe (double saut de ligne), puis phrase
  (ponctuation finale), puis mot. Si une phrase est coupée, « ... » est inséré.
  Les deux segments sont séparés par un marqueur explicite du type « [DÉBUT DU
  DOCUMENT (extrait)] » / « [FIN DU DOCUMENT (extrait) — la suite du document
  est tronquée] » afin que le modèle ne lise pas la fin comme la suite du début
  (FR-004). Document plus court que la somme des bornes : texte intégral
  (FR-005).
- **Rationale** : les métadonnées (auteurs, éditeur, citation officielle,
  colophon) se concentrent en tête et en queue de document ; le marqueur évite
  la confusion hiérarchique signalée dans le cahier des charges.
- **Alternatives considérées** : texte intégral (rejeté : coût et limites de
  contexte), échantillon aléatoire (rejeté : perd les pages de titre et
  colophon).

## R6 — Compteur d'occurrence (FR-023 à FR-025)

- **Décision** : fichier `counter.txt` à la racine du projet, contenant
  uniquement le numéro à 4 chiffres (ex. `0013`). Écriture atomique (écriture
  dans un fichier temporaire puis remplacement) immédiatement après chaque
  document produit, avant le document suivant. Absent → redémarre à 0001 ;
  illisible/corrompu → échec rapide sans écriture. Cycle : 0001…9999 puis 0000,
  puis nouveau cycle.
- **Rationale** : exigence du cahier des charges ; l'écriture atomique « après
  chaque document » garantit qu'un numéro consommé n'est jamais réutilisé même
  en cas d'interruption (SC-004).
- **Alternatives considérées** : compteur en mémoire flushé en fin d'exécution
  (rejeté : perte en cas d'interruption), base locale (rejeté : YAGNI).

## R7 — Appariement texte/JSON pour l'amendement (FR-026 à FR-027)

- **Décision** : appariement par titre de fichier : un `.txt`/`.md` de nom
  `<base>.<ext>` est lié au JSON dont le nom commence par les 8 premiers
  caractères normalisés de `<base>` (espaces → `_`, accents simplifiés).
  Ambiguïté impossible à lever → le texte est traité seul ; paire unique dans un
  sous-dossier → appariement accepté même si le préfixe diffère. Amendement :
  remplir les champs vides ; ne remplacer un champ rempli que si la confiance du
  pipeline est élevée (typologie obligatoire validée + accord des champs
  adjacents) ; écriture sur place, sans nouveau numéro (arbitrage du
  2026-10-13).
- **Rationale** : le préfixe de 8 caractères normalisés du nom de sortie dérive
  du nom du fichier d'entrée : le lien est donc reconstructible sans metadata.
- **Alternatives considérées** : appariement par horodatage (rejeté : non
  demandé), amender sans condition (rejeté : détruirait la correction manuelle
  de l'utilisateur).

## R8 — Dépendances et empaquetage

- **Décision** : SDK officiel `mistralai` (MIT) pour les appels API (conforme au
  principe III, éditeur français) ; `python-dotenv` (MIT) pour `.env` ; argparse
  (stdlib) pour le CLI ; point d'entrée console `txt-metadata` déclaré dans
  `pyproject.toml` ; tests avec pytest (MIT).
- **Rationale** : le SDK gère l'authentification, les timeouts et suit la
  documentation officielle fournie ; minimisation des dépendances (YAGNI,
  principe IV).
- **Alternatives considérées** : appels HTTP directs sans SDK (rejeté :
  réinvention de l'authentification et des erreurs), click/typer (rejeté :
  argparse suffit pour 6 options).

## R9 — Échec en lot et bilan (FR-032)

- **Décision** : échec d'un document → journalisation locale (stderr), poursuite
  du lot, bilan final (documents réussis/échoués) sur stdout. Codes retour : 0 =
  tout réussi ; 1 = au moins un échec ; 2 = erreur fatale avant traitement
  (options invalides, clé absente, compteur corrompu).
- **Rationale** : arbitrage utilisateur du 2026-10-13 ; un code retour distinct
  par classe d'échec permet l'automatisation.
- **Alternatives considérées** : arrêt au premier échec (rejeté : arbitrage
  contraire), codes retour uniformes (rejeté : non scriptable).
