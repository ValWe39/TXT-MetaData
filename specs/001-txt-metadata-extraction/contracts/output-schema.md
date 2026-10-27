# Schéma de sortie JSON — TXT-MetaData

Date : 2026-10-13 | Spec : [spec.md](../spec.md) (FR-006 à FR-013, FR-021 à
FR-027) | Modèle de données : [data-model.md](../data-model.md)

## Format

Un fichier JSON par document traité, encodage UTF-8, clés dans l'ordre
ci-dessous, toutes présentes (valeurs vides : chaîne vide ou liste vide).

```json
{
  "Typologie": "Rapport",
  "Auteur(s)": ["Karim Ben Cheikh", "Sophie Mette"],
  "Titre": "RAPPORT D'INFORMATION sur les moyens consacrés au volet ...",
  "Editeur": "ASSEMBLÉE NATIONALE",
  "Date": "30 septembre 2026",
  "Référence": "N° 3201",
  "Citation": "Karim Ben Cheikh et Sophie Mette, \"Rapport ...\", 2026"
}
```

## Champs

- `Typologie` (obligatoire) : exactement l'une des 9 valeurs : Article, Rapport,
  Ouvrage, Cours, Bibliothèque, Extrait, Communiqué, Compte-rendu, Autre.
- `Auteur(s)` : liste de chaînes, une par auteur/co-auteur ; liste vide si aucun
  trouvé. Ordre d'apparition dans le document.
- `Titre` : chaîne ≤ 150 caractères (tronquée au-delà) ; vide si absent.
- `Editeur` : chaîne, sens élargi ; vide si absent.
- `Date` : chaîne au format trouvé dans le document ; vide si absente.
- `Référence` : chaîne ; vide si absente.
- `Citation` : chaîne construite selon la spec (reprise exacte du paragraphe «
  comment citer » ou composition `<auteur>, <titre>, <référence>, <éditeur>,
  <date>` — référence omise si vide) ; vide si aucun paragraphe de citation et
  champs insuffisants.

## Nommage du fichier de sortie (FR-022)

```text
<20 premiers caractères du nom du fichier d'entrée, sans extension>
  → espaces remplacées par "_", accents simplifiés (é→e)
+ "-" + numéro d'occurrence à 4 chiffres + ".json"
```

Exemple : `Rapport information.md` → `Rapport_information-0001.json`.

## Numérotation (FR-023 à FR-025)

- Numéros attribués séquentiellement, 0001 au premier usage, +1 par nouveau
  fichier créé, cycle 0001…9999 → 0000.
- Dernier numéro persisté dans `counter.txt` à la racine du projet (contenu
  unique : le numéro à 4 chiffres), mis à jour après chaque document produit.
- Un JSON amendé ne consomme pas de numéro et conserve son nom d'origine.
