# Quickstart — Valider le préfixe de 20 caractères

**Feature**: specs/002-titre-20-chars | **Date**: 2026-10-27

Guide de validation de bout en bout. Le nommage et l'appariement sont
déterministes : les scénarios 1 et 2 ne consomment pas d'API LLM (tests
simulés) ; seul le scénario 3 (exemple réel) utilise la clé.

## Prérequis

- Python 3.11+ ; `pip install -e .` dans le dépôt.
- Tests : `pip install pytest` (déjà requis par le projet).
- Scénario 3 uniquement : variable d'environnement `MISTRAL_API_KEY`
  chargée depuis le `.env` local (jamais committé).

## Scénario 1 — Nommage à 20 caractères (déterministe)

```bash
python -m pytest tests/unit/test_output.py -q
```

Attendu : les assertions de préfixe valident la troncature à 20 (ex.
`Rapport_information.md` → `Rapport_information`, `IFRI.md` → `IFRI` sans
padding) et le format `<préfixe>-<NNNN>.json`.

## Scénario 2 — Appariement progressif 8 → 20 (déterministe)

```bash
python -m pytest tests/unit/test_pairing.py tests/integration -q
```

Attendu, conformément au
[contrat](./contracts/naming-and-pairing.md) :

- ancien JSON (nom 8 caractères) reconnu et amendé sur place ;
- départage ancien/nouveau par le préfixe commun le plus long ;
- nom accentué normalisé avant comparaison ;
- égalité parfaite → document traité seul ;
- intégration : noms de sortie à 20 caractères de bout en bout
  (LLM simulé).

## Scénario 3 — Exemple réel : IFRI uniquement

Périmètre imposé : l'exemple réel se limite au dossier
`Interne-Dev/Exemples/IFRI`. Le nom « IFRI » (4 caractères) illustre la
voie « nom plus court que 20 » : le nom de sortie ne change pas.

```bash
txt-metadata "Interne-Dev/Exemples/IFRI/IFRI.md" --output-folder output
```

Attendu :

1. Une sortie `output/IFRI-00XX.json` est créée (nom identique à
   l'ancienne règle — FR-002, aucun padding).
2. Le JSON est au format de sortie habituel (Typologie, Auteur(s), …).
3. Réexécution avec le JSON déplacé dans le dossier d'entrée : il est
   amendé sur place, nom et numéro conservés, aucun numéro consommé.

L'effet propre des 20 caractères (SC-001) est démontré par les scénarios
déterministes ci-dessus avec des noms longs (ex.
`Cour_des_comptes_rappo-00XX.json`) ; il n'apparaît pas sur IFRI, nom trop
court — c'est attendu.

## Critères de succès vérifiés

- **SC-001** : scénarios 1-2 — zéro paire indiscernable sur les noms longs
  du corpus (vérifié par tests).
- **SC-002** : scénarios 2-3 — l'amendement des JSON existants (y compris
  anciens noms 8 caractères) fonctionne sans régression.
- **SC-003** : README, FR-022 de la spécification 001 et contrat de sortie
  décrivent le nommage à 20 sans divergence.
