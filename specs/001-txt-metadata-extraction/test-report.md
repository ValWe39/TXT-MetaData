# Rapport de test et calibration — TXT-MetaData

Date : 2026-10-13 | Modèle : mistral-small-latest (défaut), température 0 | Spec
: [spec.md](./spec.md) (SC-001, SC-004) | Quickstart : V1 à V5

## Synthèse

- **Typologies** : 9/9 exactes sur les 9 exemples dotés d'une référence manuelle
  (Corsen_ai n'a pas de référence) — objectif SC-001 (≥ 8/10) atteint.
- **Tests automatisés** : 92 tests verts (unitaires + intégration, LLM simulé —
  aucune consommation d'API en CI).
- **Validation réelle** : 4 passages complets sur les 10 exemples avec l'API
  Mistral (runs du 2026-10-13, sorties 0001 à 0041).
- **Champs** : sur les documents à référence, la grande majorité des champs non
  vides attendus sont retrouvés ; divergences résiduelles détaillées ci-dessous.

## Parcours de calibration (4 itérations de prompt)

- **Run 1** : 8/9 typologies (Grand_Continent classé Rapport). Divergences :
  dates numériques non normalisées dans les citations composées ; éditeurs
  digitaux (`pernod-ricard.com`, `www.ccomptes.fr`) non détectés.
- **Run 2** (après indice prompt « éditeur = site/domaine pour un support
  digital » et « une analyse de média reste un Article ») : 9/9 typologies ;
  éditeurs digitaux corrects ; normalisation des dates implémentée (28/07/2026 →
  28 juillet 2026 dans la citation, conforme aux références Communique et
  Ecalle_cours). Régression : le modèle a minusculisé des noms propres (« karim
  ben cheikh »).
- **Run 3** (instruction de casse précise : Prénom Nom, sigles conservés,
  institutions en casse usuelle) : casse des personnes rétablie ; bascule
  ponctuelle d'Ecalle_cours vers « Article » (variabilité du modèle).
- **Run 4** (indice « fiche d'organisme de recherche = Cours ») : 9/9
  typologies, ordre des auteurs Grand_Continent conforme.

## Conformité attendue vs sorties (divergences documentées)

Règle générale de la spec : la règle prévaut sur l'exemple ; l'outil reste
généraliste.

- **Grand_Continent_article** : la citation produite est « Tristan
  Claret-Trentelivres et al., ... » conformément à la règle arbitrée (plus de
  trois auteurs → premier + « et al. »), alors que la référence manuelle liste
  les quatre auteurs. Divergence attendue et voulue.
- **IFRI** : la citation est le paragraphe « comment citer » du document, repris
  exactement avec ses guillemets « » (FR-011 cas 1, prioritaire sur la règle des
  guillemets droits qui ne s'applique qu'aux citations composées). Conforme.
- **Communique** : l'auteur ressort parfois en majuscules (« PERNOD RICARD »)
  selon les runs (variabilité du modèle malgré l'instruction de casse) ; la
  référence attend « Pernod Ricard ». L'éditeur varie entre « Pernod Ricard », «
  pernod-ricard.com » et « `www.pernod-ricard.com` » selon les runs ; la
  référence attend « `pernod-ricard.com` ».
- **Cour_de_comptes_pagination** : l'éditeur varie entre « Cour des comptes » et
  « `www.ccomptes.fr` » selon les runs (référence : `www.ccomptes.fr`). Le titre
  est rempli (« Publications des rapports... ») alors que la référence le laisse
  vide ; en conséquence la citation est composée alors que la référence la
  laisse vide.
- **Cour_des_comptes_rapport** : auteur « Cour des comptes » au lieu de «
  TROISIEME CHAMBRE » ; date remplie (9 juillet 2026) et citation composée alors
  que la référence laisse les deux vides. L'outil applique la règle de
  composition dès que les champs sont non vides ; la référence manuelle a fait
  un choix plus conservateur.
- **Ecalle_cours** : selon les runs, l'auteur est « FIPECO » (conforme à la
  référence) ou « François Ecalle » (l'auteur personne physique du mémo) ;
  l'éditeur « FIPECO » au lieu de « `fipeco.fr` ».
- **Ecalle_ouvrage** : le titre complet du document est repris (« Mécomptes
  publics : Conception et contrôle... ») au lieu du seul « Mécomptes Publics »
  de la référence ; l'ISBN est saisi comme référence, donc inséré dans la
  citation, alors que la référence laisse le champ vide.
- **AN_Rapport** : le titre contient « n° 3201 » (référence : sans) ; éditeur en
  casse usuelle (« Assemblée nationale » vs « ASSEMBLÉE NATIONALE »), la
  référence de citation utilisant « Assemblée Nationale ». Contenu équivalent.
- **AN_deliberation** : auteurs « Assemblée nationale » au lieu de « XVIIe
  législature » / « Session ordinaire de 2026-2027 » ; titre préfixé par «
  Compte rendu de » (référence : sans). Contenu proche.
- **Corsen_ai** : pas de sortie manuelle de référence fournie. Sortie produite :
  Cours, auteur Corsen AI, titre « Le Chat et MCP — Automatisez vos Workflows »,
  29 juillet 2026 — à valider à la main.

## Variabilité du modèle

À température 0, les sorties restent légèrement variables d'un run à l'autre
(casse d'un auteur, choix de l'éditeur digital, ordre prénom/nom). Les sorties
0032 à 0041 constituent l'état final de la calibration. Pour durcir un usage
particulier, relancer l'outil amende sur place les JSON existants (FR-026) : les
champs vides se complètent, les champs remplis ne sont challengés que si la
nouvelle valeur est vérifiée mot à mot dans le texte source.

## Scénarios quickstart

- **V1** (fichier unique) : validé en réel — JSON créé, compteur 0001, code
  retour 0.
- **V2** (amendement) : validé par tests d'intégration (mock) — amendement sur
  place, sans numéro consommé.
- **V3** (échec en lot) : validé par tests d'intégration (mock) — lot poursuivi,
  code retour 1, aucun numéro consommé pour l'échec.
- **V4** (compteur) : validé par tests unitaires — absent → 0001 ; corrompu →
  code 2 ; incrément persistant.
- **V5** (calibration) : validé — présent rapport (9/9 typologies).
