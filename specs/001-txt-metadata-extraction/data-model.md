# Data Model — TXT-MetaData

Date : 2026-10-13 | Spec : [spec.md](./spec.md) | Contrat de sortie :
[contracts/output-schema.md](./contracts/output-schema.md)

## Entités

### InputDocument (Texte1)

Document texte fourni en entrée, sur disque.

- **Champs** : chemin absolu (`path`) ; extension (`.md` ou `.txt`) ; contenu
  texte décodé en UTF-8 (avec repli sur l'encodage détecté) ; titre de fichier
  sans extension (`base_name`) ; booléen `paired_json` (JSON de sortie existant
  apparié, cf. ExistingOutput).
- **Validation** : extension `.md` ou `.txt` ; tout autre format est ignoré
  silencieusement (FR-001). Fichier vide ou quasi vide : accepté, produit une
  sortie minimale (Typologie = Autre, champs optionnels vides).
- **Relations** : 0..1 ExistingOutput ; 1 Extrait ; 1 MetadataOutput.

### Extrait (Extrait1)

Échantillon dérivé du document, soumis au LLM.

- **Champs** : `head` (segment de début, cible ≤ 20 000 caractères) ; `tail`
  (segment de fin, cible ≤ 16 000 caractères) ; `marker` (marqueur de séparation
  début/fin) ; `is_full_text` (booléen : document plus court que la somme des
  bornes → texte intégral, sans marqueur).
- **Validation / règles de coupure** (FR-003) : reculer la coupure vers l'unité
  la plus large sous la borne : sous-partie, à défaut paragraphe, à défaut
  phrase, à défaut mot ; « ... » inséré si une phrase est coupée ; jamais de mot
  coupé.
- **Cycle de vie** : construit à partir de InputDocument, consommé par l'appel
  LLM, jamais persisté (aucune copie cachée, constitution).

### MetadataOutput

Métadonnées extraites, sérialisées en JSON de sortie.

- **Champs** (noms exacts du schéma de sortie) :
- `Typologie` (obligatoire) : enum de 9 valeurs — Article, Rapport, Ouvrage,
  Cours, Bibliothèque, Extrait, Communiqué, Compte-rendu, Autre.
- `Auteur(s)` (optionnel) : liste de chaînes, une par auteur/co-auteur ; liste
  vide si aucun. Rapporteurs pour un rapport, parlementaires pour un rapport
  parlementaire, société/revue pour un communiqué ou cours sans auteur personne
  (FR-008).
- `Titre` (optionnel) : chaîne ≤ 150 caractères, tronquée au-delà (FR-009).
- `Editeur` (optionnel) : chaîne, sens élargi (revue, site, institution, think
  tank, éditeur) (FR-010).
- `Date` (optionnel) : chaîne au format trouvé dans le document.
- `Référence` (optionnel) : chaîne (numéro d'étude, etc.).
- `Citation` (optionnel) : chaîne construite selon FR-011/FR-012 (reprise exacte
  du paragraphe de citation, ou composition déterministe ; guillemets droits ;
  max 3 auteurs puis « et al. » ; vide si critères insuffisants).
- **Validation** : les 7 clés sont toujours présentes dans le JSON (valeurs
  vides : chaîne vide ou liste vide) ; `Typologie` doit appartenir à l'enum ;
  rejet de toute valeur non justifiable par l'extrait (anti-hallucination,
  FR-007, FR-015).
- **Cycle de vie** : produite par le pipeline → validée → soit écrite dans un
  nouveau fichier de sortie (nouveau numéro d'occurrence), soit fusionnée dans
  un ExistingOutput (amendement, sans nouveau numéro).

### ExistingOutput

JSON de sortie préexistant dans le dossier d'entrée, apparié à un InputDocument
(FR-026, FR-027).

- **Champs** : chemin ; contenu MetadataOutput existant.
- **Appariement** : par préfixe de 8 caractères normalisés du titre du fichier
  texte (espaces → `_`, accents simplifiés), ou par unicité de la paire dans un
  sous-dossier. Non appariable → le texte est traité seul.
- **Règles d'amendement** : compléter en priorité les champs vides ; ne
  remplacer un champ rempli que si le nouveau résultat est à haut degré
  d'assurance ; écriture sur place ; ne consomme pas de numéro d'occurrence.

### OccurrenceCounter

Compteur global persistant de la numérotation des sorties.

- **Stockage** : `counter.txt` à la racine du projet, contenu unique : numéro à
  4 chiffres (ex. `0013`).
- **Règles** : premier usage 0001 ; +1 par nouveau fichier créé ; cycle
  0001…9999 → 0000 → nouveau cycle ; persisté par écriture atomique après chaque
  document produit ; numéro consommé jamais réutilisé, même après interruption ;
  fichier absent → reprise à 0001 ; illisible/corrompu → échec rapide, aucune
  sortie (FR-023 à FR-025).
- **Relations** : consulté/mis à jour par le pipeline d'écriture des nouvelles
  sorties uniquement (les amendements n'y touchent pas).

### RunReport

Bilan d'une exécution (FR-032, SC-008).

- **Champs** : liste des documents traités avec statut (succès créé / succès
  amendé / échec) et message d'erreur éventuel ; compteur de départ et
  d'arrivée.
- **Validation** : aucun numéro consommé pour un document en échec.
- **Rendu** : bilan final sur stdout ; code retour 0 (tout réussi), 1 (au moins
  un échec), 2 (erreur fatale avant traitement).

## Diagramme de relations

```text
InputDocument 1───0..1 ExistingOutput (appariement FR-027)
InputDocument 1───1 Extrait (échantillonnage FR-002 à FR-005)
Extrait 1───1 MetadataOutput (appel LLM + validation + citation)
MetadataOutput ──> nouveau fichier output/ (consomme OccurrenceCounter)
MetadataOutput ──> ExistingOutput amendé (sur place, sans numéro)
RunReport agrège le statut de chaque InputDocument traité
```
