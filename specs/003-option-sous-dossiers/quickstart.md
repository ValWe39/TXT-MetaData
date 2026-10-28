# Quickstart — Valider l'option --sous-dossiers

**Feature**: specs/003-option-sous-dossiers | **Date**: 2026-10-28

Guide de validation de bout en bout. Le rangement est déterministe : les
scénarios 1 et 5 ne consomment pas d'API LLM (tests simulés) ; seuls les
scénarios 2 à 4 (exemples réels) utilisent la clé. Périmètre des exemples
réels imposé : `Interne-Dev/Exemples/IFRI` et
`Interne-Dev/Exemples/Ecalle_cours`.

## Prérequis

- Python 3.11+ ; `pip install -e .` dans le dépôt.
- Tests : `pip install pytest` (déjà requis par le projet).
- Scénarios 2 à 4 uniquement : variable d'environnement `MISTRAL_API_KEY`
  chargée depuis le `.env` local (jamais committé).
- Compteur à 0067 au moment de la rédaction : les numéros 0068/0069/0070
  ci-dessous sont indicatifs.

## Scénario 1 — Rangement en unité (déterministe)

```bash
python -m pytest tests/unit/test_output.py tests/unit/test_cli.py \
  tests/unit/test_inputs.py -q
```

Attendu : avec l'option active, une création produit
`output/00NN-<prefixe>/<prefixe>-00NN.json` + copie du source au nom
d'origine, contenu identique ; l'option est inactive par défaut ; le
dossier de sortie est exclu de la découverte quand un chemin d'entrée
le couvre.

## Scénario 2 — Exemple réel : création d'une unité IFRI

Le dossier `Interne-Dev/Exemples/IFRI/` contient déjà `IFRI-0042.json` :
pointer l'outil dessus déclencherait l'amendement, pas la création. On
passe donc par une copie temporaire du `.md` dans un dossier vide.

```bash
mkdir tmp-ifri && cp "Interne-Dev/Exemples/IFRI/IFRI.md" tmp-ifri/
txt-metadata tmp-ifri/IFRI.md --sous-dossiers --output-folder output
```

Attendu :

1. Une unité `output/0068-IFRI/` est créée.
2. Elle contient `IFRI-0068.json` (nom inchangé, FR-004) et `IFRI.md`,
   copie identique octet pour octet (`diff tmp-ifri/IFRI.md
   output/0068-IFRI/IFRI.md` : aucune différence).
3. Le bilan affiche le chemin complet du JSON, unité comprise.

## Scénario 3 — Exemple réel : création d'une unité Ecalle_cours

```bash
mkdir tmp-ecalle && cp "Interne-Dev/Exemples/Ecalle_cours/Ecalle_cours.md" tmp-ecalle/
txt-metadata tmp-ecalle/Ecalle_cours.md --sous-dossiers --output-folder output
```

Attendu : une unité `output/0069-Ecalle_cours/` contenant
`Ecalle_cours-0069.json` et la copie `Ecalle_cours.md`. Le préfixe
`Ecalle_cours` (12 caractères) reste distinct de `Ecalle_ouvrage`
(`Ecalle_o`) : les deux familles ne se confondent pas, même rangées en
unités.

## Scénario 4 — Amendement d'une paire rangée (IFRI)

```bash
txt-metadata output/0068-IFRI --sous-dossiers --output-folder output
```

Attendu (contrat §4) :

1. Le JSON `output/0068-IFRI/IFRI-0068.json` est amendé sur place, par
   le repli « paire unique du sous-dossier » (la copie `IFRI.md` joue
   le rôle de document, le JSON celui de candidat).
2. Nom et numéro conservés ; **aucun numéro consommé**.
3. La copie `IFRI.md` est inchangée (checksum identique avant/après).

## Scénario 5 — Régression du mode par défaut (Ecalle_cours)

```bash
mkdir tmp-ecalle2 && cp "Interne-Dev/Exemples/Ecalle_cours/Ecalle_cours.md" tmp-ecalle2/
txt-metadata tmp-ecalle2/Ecalle_cours.md --output-folder output
```

Attendu : sans l'option, la sortie est écrite **à plat** —
`output/Ecalle_cours-0070.json`, sans unité ni copie ; les unités et
JSON existants de `output/` sont inchangés.

## Critères de succès vérifiés

- **SC-001** : scénarios 2-3 — chaque paire réelle (IFRI, Ecalle_cours)
  est retrouvée sans manipulation manuelle, dans une unité unique.
- **SC-002** : scénarios 1 et 5 — sans l'option, layout identique à
  aujourd'hui ; tests existants du mode par défaut au vert, non modifiés.
- **SC-003** : scénarios 2-5 — les 10 JSON existants de `output/` restent
  à plat et inchangés.
- **SC-004** : README, contrat CLI (spec 001) et spec 001 (FR-026
  amendé) décrivent l'option sans divergence avec le comportement réel.
