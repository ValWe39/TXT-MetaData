"""Appels LLM Mistral AI et extraction des métadonnées (FR-014 à FR-017).

Un appel principal en mode JSON strict (``response_format`` json_object)
avec un prompt anti-hallucination ; la réponse est validée contre le
schéma ; en cas d'invalidité, l'appel est rejoué dans la limite de
5 appels LLM par document. Chaque appel est protégé par le retry
exponentiel (FR-019).
"""

from __future__ import annotations

import json
import time
from typing import Any, Protocol

from .citation import compose_citation
from .models import TYPOLOGIES, MetadataOutput, MetadataValidationError
from .retry import with_retry
from .sampling import Extrait, render_extrait

MODELS: dict[str, str] = {
    "large4": "mistral-large-4",
    "large": "mistral-large-latest",
    "medium": "mistral-medium-latest",
    "small": "mistral-small-latest",
    "14b": "ministral-14b-latest",
    "8b": "ministral-8b-latest",
    "3b": "ministral-3b-latest",
    "zai": "zai-glm-5-3",
}

DEFAULT_MODEL_ALIAS = "small"
DEFAULT_TEMPERATURE = 0.0
MAX_LLM_CALLS_PER_DOCUMENT = 5


class ExtractionError(Exception):
    """Échec définitif de l'extraction pour un document."""


class ChatClient(Protocol):
    """Client compatible SDK Mistral (mockable en test)."""

    def chat_complete(self, *, model: str, messages: list[dict], **kwargs: Any):
        """Appel chat completions ; renvoie un objet avec .choices[0]
        .message.content (chaîne JSON)."""


class MistralChatClient:
    """Adapte le client SDK Mistral (``chat.complete``) à l'interface
    interne ``chat_complete`` (mockable en test)."""

    def __init__(self, sdk_client: Any) -> None:
        self._sdk = sdk_client

    def chat_complete(self, *, model: str, messages: list[dict], **kwargs: Any) -> Any:
        """Délègue au chat completions du SDK."""
        return self._sdk.chat.complete(model=model, messages=messages, **kwargs)


def create_client(api_key: str) -> Any:
    """Crée le client Mistral (import SDK retardé pour faciliter les
    tests)."""
    from mistralai.client import Mistral

    return MistralChatClient(Mistral(api_key=api_key))


PROMPT_TEMPLATE = """Tu es un bibliothécaire-documentaliste expert. Ton \
rôle : identifier les métadonnées du document dont voici un extrait.

RÈGLES IMPÉRATIVES (anti-hallucination) :
- Ne remplis un champ QUE si l'information figure explicitement dans \
l'extrait ci-dessous.
- Si une information est absente, laisse le champ vide : chaîne vide "" \
(ou liste vide [] pour les auteurs). N'invente JAMAIS une valeur.
- Si plusieurs candidats existent pour un champ, choisis le plus \
probable pour le document lui-même (ignore les bibliographies et les \
mentions d'autres documents).

TYPOLOGIE (obligatoire, exactement une de ces valeurs) :
- "Article" : article de journal, de revue, édito, entretien par un média. \
Une analyse ou une tribune publiée par un média ou une revue reste un \
"Article", même longue, détaillée et structurée.
- "Rapport" : rapport scientifique, d'étude, annuel, périodique, financier.
- "Ouvrage" : livre, recueil, ouvrage.
- "Cours" : cours, explications, mémo ; ton de l'explication, définitions. \
Inclut les fiches ou notes explicatives publiées par un institut ou un \
organisme de recherche (ex. une fiche FIPECO sur un concept).
- "Bibliothèque" : support dont l'objet est le référencement (liste \
d'ouvrages, d'articles, de rapports...).
- "Extrait" : partie seulement d'un ouvrage plus important (ex. un \
chapitre sans pages de présentation).
- "Communiqué" : communiqué de presse, flash info, format plutôt court.
- "Compte-rendu" : délibérations, débats, suite de prises de paroles, \
interview, séance d'assemblée.
- "Autre" : tout support non classable dans les catégories précédentes.

RÈGLES DES CHAMPS :
- "Auteur(s)" : liste, une chaîne par auteur dans l'ordre d'apparition. \
Rapport : les rapporteurs/co-rapporteurs. Rapport parlementaire : les \
parlementaires qui le présentent. Communiqué/article/cours sans auteur \
personne physique : la société ou la revue à l'origine du texte.
- "Titre" : titre du document, 150 caractères maximum.
- "Editeur" : sens élargi — revue pour un article, site internet ou \
domaine pour un support digital (ex. fipeco.fr, www.ccomptes.fr), \
institution (ex. Assemblée nationale), think tank ou éditeur.
- "Date" : date de parution, au format du document.
- "Référence" : référence du support (numéro d'étude, de rapport...).
- "Citation" : SI le document contient un paragraphe expliquant comment \
le citer, recopie-le EXACTEMENT (contenu et format) ; SINON laisse "" \
(ne compose rien toi-même).
- Casse des champs : pour "Titre", "Date" et "Référence", reproduis la \
casse du document. Pour "Auteur(s)" et "Editeur", utilise la casse \
usuelle de citation : noms de personnes en capitales initiales \
(François Ecalle, même si la couverture écrit FRANÇOIS ECALLE) ; \
sigles et acronymes conservés en majuscules (FIPECO, AN) ; sociétés \
et institutions avec leur casse usuelle, même si le document les \
écrit en majuscules (PERNOD RICARD → Pernod Ricard, ASSEMBLÉE \
NATIONALE → Assemblée nationale, Cour des comptes).

Réponds UNIQUEMENT avec un objet JSON ayant exactement ces clés :
"Typologie", "Auteur(s)", "Titre", "Editeur", "Date", "Référence", \
"Citation".

=== EXTRAIT DU DOCUMENT ===
{extrait}
=== FIN DE L'EXTRAIT ==="""


def build_prompt(extrait: Extrait) -> str:
    """Construit le prompt complet à partir de l'extrait."""
    return PROMPT_TEMPLATE.format(extrait=render_extrait(extrait))


def parse_response_content(content: str) -> dict:
    """Parse la réponse JSON du modèle (tolérante au bruit d'escapement)."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            msg = "Réponse LLM sans objet JSON"
            raise ValueError(msg)
        data = json.loads(content[start : end + 1])
    if not isinstance(data, dict):
        msg = "Réponse LLM : JSON attendu, reçu autre chose"
        raise TypeError(msg)
    return data


def _call_model(
    client: Any,
    *,
    prompt: str,
    model: str,
    temperature: float,
    retries: int,
    retry_delay: float,
    sleep,
) -> dict:
    """Un appel chat completions protégé par le retry exponentiel ;
    renvoie le dictionnaire JSON parsé."""

    def invoke() -> Any:
        return client.chat_complete(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            response_format={"type": "json_object"},
        )

    response = with_retry(
        invoke, retries=retries, initial_delay=retry_delay, sleep=sleep
    )
    content = response.choices[0].message.content
    if not isinstance(content, str):
        msg = "Réponse LLM sans contenu"
        raise TypeError(msg)
    return parse_response_content(content)


def extract_metadata(
    client: Any,
    extrait: Extrait,
    *,
    model_alias: str = DEFAULT_MODEL_ALIAS,
    temperature: float = DEFAULT_TEMPERATURE,
    retries: int = 3,
    retry_delay: float = 3.0,
    sleep=time.sleep,
) -> MetadataOutput:
    """Extrait les métadonnées : jusqu'à 5 appels LLM par document
    (FR-017), chaque appel protégé par le retry exponentiel (FR-019)."""
    model = MODELS[model_alias]
    prompt = build_prompt(extrait)
    last_error: Exception | None = None
    for _ in range(MAX_LLM_CALLS_PER_DOCUMENT):
        try:
            data = _call_model(
                client,
                prompt=prompt,
                model=model,
                temperature=temperature,
                retries=retries,
                retry_delay=retry_delay,
                sleep=sleep,
            )
            metadata = MetadataOutput.from_dict(data)
            metadata.validate()
            return metadata
        except (TypeError, ValueError, MetadataValidationError) as exc:
            last_error = exc
            continue
    msg = (
        f"Extraction en échec après {MAX_LLM_CALLS_PER_DOCUMENT} appels : {last_error}"
    )
    raise ExtractionError(msg)


def compose_fallback_citation(metadata: MetadataOutput) -> str:
    """Citation composée déterministe (utilisée par la phase US1)."""
    return compose_citation(
        metadata.auteurs,
        metadata.titre,
        metadata.reference,
        metadata.editeur,
        metadata.date,
    )


def typologies() -> tuple[str, ...]:
    """Liste canonique des typologies (exposée pour les tests)."""
    return TYPOLOGIES
