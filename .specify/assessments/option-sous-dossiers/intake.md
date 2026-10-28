# Idea Intake: Option --sous-dossiers (JSON + copie .md dans un sous-dossier numéroté)

- **Slug**: option-sous-dossiers
- **Created**: 2026-10-28
- **Source**: pasted text (repo : TXT-MetaData, branche `003-titre-20-car`)
- **Type**: improvement

## Idea (as captured)

> Je souhaiterais ajouter la commande optionelle suivante "--sous-dossiers"
> permettant, en sortie, de placer le .json de sortie avec son .md d'entrée
> (une copie) dans un sous-dossier unique au numéro d'occurence.
>
> Pour l'exemple réel, tu peux refaire avec l'exemple IFRI.

## Restated

Une nouvelle option CLI optionnelle `--sous-dossiers` ferait que chaque
sortie n'écrase plus le JSON directement dans le dossier de sortie : le
JSON produit serait accompagné d'une copie du fichier d'entrée (.md) et
l'ensemble serait placé dans un sous-dossier unique nommé d'après le
numéro d'occurrence attribué au document. Sans l'option, le comportement
actuel resterait inchangé.

## Exemple réel (IFRI, illustratif)

Aujourd'hui, avec `Interne-Dev/Exemples/IFRI/IFRI.md`, l'occurrence 0036
est attribuée et la sortie est :

```text
output/
└── IFRI-0036.json
```

Avec `--sous-dossiers`, l'idée produirait un layout du type :

```text
output/
└── <sous-dossier nommé d'après 0036>/
    ├── IFRI-0036.json
    └── IFRI.md   (copie du fichier d'entrée)
```

La forme exacte du nom du sous-dossier (ex. `0036`, `36`,
`occurrence-0036`) reste à définir.

## Origin & Context

- **Raised by**: l'utilisateur (propriétaire du dépôt), via la commande
  `/speckit-assess-intake`
- **Trigger**: [NEEDS CLARIFICATION: motivation — regrouper le JSON et sa
  source .md pour archivage/navigation ? éviter les collisions de noms ?
  préparation d'un pipeline aval ?]

Contexte code (lecture seule, pour situer l'idée) :

- `src/txt_metadata/cli.py` : le parseur argparse n'a aujourd'hui aucune
  option de sous-dossiers ; les options existantes sont `--choix`,
  `--taille-batch`, `--retry-occurences`, `--retry-time`,
  `--output-folder`, `--temperature-llm` (FR-028 à FR-030), avec
  validation en bornes et échec rapide code 2.
- `src/txt_metadata/output.py` : `write_new()` écrit
  `<20 premiers caractères normalisés>-<NNNN>.json` à plat dans le
  dossier de sortie (créé si absent) ; l'amendement fusionne sur place,
  sans nouveau numéro ni copie (FR-026).
- `src/txt_metadata/counter.py` : `next_occurrence()` attribue le numéro
  à 4 chiffres (cycle 0001…9999 puis 0000) de façon atomique et
  verrouillée, à l'instant exact de la création du JSON ; un document en
  échec n'en consomme jamais (FR-023 à FR-025).
- `src/txt_metadata/batch.py` : traitement par lots parallèles — le
  numéro d'occurrence et le placement des fichiers doivent rester
  cohérents en parallèle.
- Entrée `.txt` : l'option parle de « .md d'entrée » ; l'outil accepte
  aussi les `.txt`, la copie devrait vraisemblablement viser le fichier
  d'entrée quelle que soit son extension.

## First-Glance Unknowns

- [NEEDS CLARIFICATION: nom exact du sous-dossier — `0036` seul,
  préfixe lisible (ex. `IFRI-0036`), ou autre format ? L'utilisateur dit
  « unique au numéro d'occurrence », à préciser.]
- [NEEDS CLARIFICATION: le JSON dans le sous-dossier conserve-t-il son
  nom complet `<préfixe>-<NNNN>.json` (ex. `IFRI-0036.json`) ou un nom
  simplifié ?]
- [NEEDS CLARIFICATION: la copie du fichier d'entrée garde-t-elle son
  nom d'origine (`IFRI.md`) ou un nom dérivé ? La copie est-elle une
  copie exacte (contenu identique) ?]
- [NEEDS CLARIFICATION: que devient l'amendement d'un JSON existant
  (FR-026, fusion sur place) — l'appariement doit-il aussi chercher dans
  les sous-dossiers ? La copie .md est-elle mise à jour lors d'un
  amendement ?]
- [NEEDS CLARIFICATION: l'option s'applique-t-elle uniquement aux
  nouveaux fichiers, ou faut-il prévoir quoi que ce soit pour les JSON
  existants déjà à plat dans `output/` ?]
- [NEEDS CLARIFICATION: cycle du compteur (0000 après 9999) — deux
  occurrences d'un même cycle de 10 000 peuvent-elles entrer en
  collision dans le nom du sous-dossier, ou l'unicité est-elle garantie
  par le cycle lui-même ?]
- [NEEDS CLARIFICATION: interaction avec `--output-folder` — les
  sous-dossiers sont-ils créés dans le dossier de sortie configuré
  (défaut `output/`) ?]
- [NEEDS CLARIFICATION: bornes/validation de l'option (flag booléen
  simple sans valeur ?) et mise à jour documentaire attendue (README,
  FR-028 à FR-030, contrat de sortie, tests).]
