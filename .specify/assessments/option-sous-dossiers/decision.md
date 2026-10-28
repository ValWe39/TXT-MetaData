# Decision: Paires autonomes source + métadonnées en sortie

- **Slug**: option-sous-dossiers
- **Decided**: 2026-10-28
- **Verdict**: go
- **Artifacts reviewed**: intake.md | research.md | problem.md | concept.md

## Scorecard

| Criterion | Rating | Justification |
| --- | --- | --- |
| Problem validity | adequate | Paires non autonomes, 3e demande |
| Evidence strength | strong | Interne sourcé, confiance high |
| Value vs. inaction | strong | Copies manuelles vs correctif small |
| Feasibility / appetite | strong | Repli FR-027 réutilisé, appétit small |
| Strategic fit | adequate | Tension FR-026 à trancher |
| Risk posture | adequate | Risques bornés, hypothèses ouvertes |

Justifications détaillées :

- **Problem validity (adequate)** : problème réel pour l'unique
  demandeur — paires source/JSON non autonomes, 3e demande consécutive
  sur le rangement des sorties (research.md, Users & Demand) ;
  motivation précise encore non renseignée.
- **Evidence strength (strong)** : recherche interne exhaustive, chaque
  affirmation citée (code, spec 001/002, données réelles output/ et
  compteur) ; confiance globale high (research.md).
- **Value vs. inaction (strong)** : le coût de l'inaction est documenté
  et récurrent — copie manuelle à chaque besoin, JSON orphelins si la
  source bouge (problem.md, Cost of Inaction).
- **Feasibility / appetite (strong)** : option B en appétit small,
  réutilise le repli « paire unique du sous-dossier » déjà implémenté
  (FR-027), aucune refonte du mode par défaut (concept.md).
- **Strategic fit (adequate)** : cohérent avec l'outil CLI batch et le
  principe d'optionnalité ; tension avec la décision enregistrée
  FR-026 (« aucune copie dans le dossier de sortie ») à trancher
  explicitement en spécification.
- **Risk posture (adequate)** : risques identifiés et bornés (asymétrie
  d'amendement assumée, divergence copie/source exclue du périmètre,
  boucle de rétroaction, cycle du compteur) ; mitigations reposant sur
  des hypothèses d'usage à valider (concept.md, Assumptions).

## Verdict & Rationale

**Go.** Le problème est réel pour le demandeur et le coût de l'inaction
est récurrent ; l'évidence est solide et entièrement sourcée en interne ;
l'option B tient dans un appétit small sans toucher au mode par défaut ni
déplacer aucun fichier existant, ce qui satisfait structurellement la
métrique « layout inchangé sans l'option » (problem.md, Success Metrics).
Les risques résiduels (asymétrie d'amendement, copies figées) sont assumés
et bornés par le hors-périmètre du concept ; l'extension de l'appariement
(option C) reste disponible comme incrément ultérieur si l'usage la rend
nécessaire. Le seul point de gouvernance — la contradiction avec
l'intention FR-026 de la spec 001 — est un arbitrage de spécification,
pas un bloqueur d'évidence : il est explicitement reporté au handoff.

## If go — Handoff to `/speckit-specify`

- **Problem** : les JSON produits vivent à plat dans le dossier de sortie
  tandis que leurs sources `.md`/`.txt` vivent ailleurs ; la paire
  « source + métadonnées » n'est pas autonome et doit être reconstituée à
  la main (archivage, partage).
- **Chosen approach** : Option B — flag optionnel `--sous-dossiers` ;
  à la création d'un JSON, placement dans une unité de rangement unique
  nommée d'après le numéro d'occurrence, accompagnée d'une copie du
  fichier source à son nom d'origine ; amendement par les mécanismes
  existants (relance sur l'unité → repli « paire unique » FR-027).
- **In scope / out of scope** : en scope — nouvelles créations uniquement,
  unités sous le dossier configuré (`--output-folder`), comportement par
  défaut strictement inchangé. Hors scope — migration des 10 JSON
  existants, extension de l'appariement (retrouver la paire depuis la
  source d'origine : option C, incrément ultérieur), synchronisation
  copie/source (copie figée à la création), toute configuration du
  rangement au-delà du flag.
- **Success metrics** : chaque nouvelle paire retrouvée sans étape
  manuelle (démonstration sur l'exemple réel IFRI) ; sans l'option,
  layout identique à aujourd'hui, 96 tests verts sans modification des
  assertions de layout par défaut ; `output/` inchangé hors nouvelles
  sorties.
- **Carried-forward open questions** :
  - [NEEDS CLARIFICATION: nom exact de l'unité de rangement — numéro
    seul (`0036`) ou lisible (`IFRI-0036`) ; décision de spécification.]
  - [NEEDS CLARIFICATION: sort de la décision FR-026 « aucune copie dans
    le dossier de sortie » (spec 001, session 2026-10-13) — assumée
    dépassée pour les créations ou contournée ; à trancher et documenter.]
  - [NEEDS CLARIFICATION: collision des noms d'unités après un cycle
    complet du compteur (> 10 000 sorties au même endroit) — acceptable
    ou à prévenir (research.md, Data & Constraints).]
  - [NEEDS CLARIFICATION: motivation précise du demandeur (archivage,
    navigation, pipeline aval ?) — non renseignée dans le intake.]
