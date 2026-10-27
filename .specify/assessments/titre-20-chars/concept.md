# Concept: Préfixe de sortie lisible et rattachable à la source

- **Slug**: titre-20-chars
- **Created**: 2026-10-27
- **Recommended option**: B — Préfixe de nommage à 20, appariement conservé à 8

## Options

### Option A — Constante partagée passée à 20

- **Sketch**: le nommage des nouvelles sorties prend les 20 premiers
  caractères normalisés du nom d'entrée ; l'appariement d'amendement suit
  automatiquement puisqu'il réutilise la même constante et la même fonction
  (`output_prefix`). Une seule valeur à changer dans l'outil.
- **Appetite**: small
- **Trade-offs**: gagne — modification minimale, noms de sortie
  distinguables sur le corpus réel, appariement plus discriminant sur les
  nouveaux corpus. Sacrifie — l'amendement des JSON existants nommés sur
  8 caractères : ils ne sont plus appariés par préfixe, seul le repli
  « paire unique » (un document, un JSON) peut encore les rattraper ;
  dans un dossier contenant plusieurs documents, un ancien JSON ne serait
  plus amendé (régression FR-026 sur les corpus déjà traités).
- **Rabbit holes**: renommage ou migration des JSON existants pour restaurer
  l'appariement — ouvre un chantier de migration hors de l'appétit annoncé ;
  option CLI `--longueur-prefixe` qui glisse vers un nommage configurable.

### Option B — Nommage à 20, appariement conservé à 8

- **Sketch**: les nouvelles sorties sont nommées sur 20 caractères
  normalisés ; l'appariement d'amendement continue de matcher sur le
  préfixe de 8 caractères, qui reconnaît à la fois les anciens noms
  (8 caractères) et les nouveaux (20 caractères, dont les 8 premiers
  coïncident). L'utilisateur voit des noms complets ; l'amendement des
  corpus existants fonctionne inchangé.
- **Appetite**: small
- **Trade-offs**: gagne — les trois objectifs du problème sont tenus
  (rattachement visuel, critères de nommage inchangés hormis la longueur,
  amendement préservé) ; la compatibilité descendante est démontrée par
  la logique `startswith` (research.md, Data & Constraints). Sacrifie —
  deux longueurs coexistent dans le code et la documentation, à expliquer
  et à tester ; cas limite : un même document dont un ancien JSON
  (8 caractères) et un nouveau (20) coexistent produit deux candidats à
  l'appariement, donc aucun appariement (comportement sûr actuel, mais à
  documenter).
- **Rabbit holes**: sur-ingénierie de l'appariement (matching flou,
  comparaison de tous les préfixes candidats) au lieu du simple test
  d'égalité de longueur ; renommage des anciens JSON pour « uniformiser »,
  explicitement exclu par FR-031.

### Option C — Ne rien faire

- **Sketch**: l'outil reste à 8 caractères ; l'utilisateur compense en
  ouvrant les JSON ou en maintenant une correspondance mentale fichier ↔
  source, voire en renommant ses fichiers d'entrée pour qu'ils divergent
  dès les 8 premiers caractères.
- **Appetite**: small (nul)
- **Trade-offs**: gagne — zéro travail, zéro risque. Sacrifie — le
  problème persiste et s'aggrave à mesure que le corpus grossit (2 paires
  indiscernables déjà observées sur 10 sorties réelles) ; impose une
  discipline de nommage aux fichiers d'entrée, qui contredit l'usage
  observé (noms longs et descriptifs dans Interne-Dev/Exemples).
- **Rabbit holes**: aucun technique ; risque d'usure (erreurs
  d'identification silencieuses) non mesuré à ce jour.

## Recommendation

Option B. Elle est la seule qui satisfait les trois buts du problème à la
fois : rattachement visuel (métrique : 0 paire indiscernable sur le corpus
des 10 exemples, contre 2 aujourd'hui), critères de nommage inchangés hors
la longueur, et amendement des corpus déjà traités préservé — l'option A
casserait le troisième but, que la recherche identifie comme le risque
principal. L'appétit reste small : une constante dédoublée, environ 5
assertions de tests et 4 documents à mettre à jour (research.md, Data &
Constraints). L'option C est écartée : le coût est nul mais le problème
constaté sur données réelles n'est pas résolu.

## Out of Scope (for the recommended option)

- Renommage ou migration des JSON déjà produits (FR-031 : un JSON conserve
  son nom d'origine).
- Toute option CLI de longueur de préfixe configurable.
- Changement des critères de normalisation (espaces → `_`, accents),
  du format `<préfixe>-<NNNN>.json`, de la numérotation et du compteur.
- Appariement tolérant aux ambiguïtés : un appariement ambigu reste non
  lié (comportement actuel conservé).
- Extraction, prompts, modèles LLM, batch, interface CLI.

## Assumptions to Validate

- « Titre de l'entrée » = nom du fichier d'entrée sans extension (lecture
  de FR-022 et de l'implémentation), pas le champ `Titre` extrait par le
  LLM.
- Les noms des fichiers d'entrée du corpus divergent dans leurs 20 premiers
  caractères normalisés (vérifié sur les 10 exemples du dépôt, à confirmer
  sur les corpus futurs).
- Les corpus déjà traités à amender contiennent majoritairement un document
  par dossier (repli « paire unique » opérationnel de toute façon en
  option B).
- 20 caractères restent sous les limites de longueur de chemin des
  arborescences visées (Windows, 260 caractères par défaut).
