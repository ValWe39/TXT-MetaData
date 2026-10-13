"""Tests unitaires de l'extraction LLM : validation, mode JSON, plafond
d'appels, retry exponentiel (T017, FR-014 à FR-017, FR-019)."""

import pytest

from txt_metadata.extract import (
    MODELS,
    ExtractionError,
    extract_metadata,
    parse_response_content,
)
from txt_metadata.models import MetadataOutput, MetadataValidationError
from txt_metadata.retry import with_retry
from txt_metadata.sampling import build_extrait


def _no_sleep(seconds: float) -> None:
    """Sleep factice pour les tests (aucune attente)."""


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeClient:
    """Client de test : renvoie des réponses JSON successives."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def chat_complete(self, **kwargs):
        self.calls += 1
        content = self.responses.pop(0)
        if isinstance(content, Exception):
            raise content
        return FakeResponse(content)


VALID = (
    '{"Typologie": "Rapport", "Auteur(s)": ["A. Rapporteur"], '
    '"Titre": "Titre du rapport", "Editeur": "Ifri", '
    '"Date": "mai 2022", "Référence": "n° 109", "Citation": ""}'
)


def test_alias_modeles_complets():
    assert len(MODELS) == 8
    assert MODELS["small"] == "mistral-small-latest"
    assert MODELS["zai"] == "zai-glm-5-3"
    assert MODELS["14b"] == "ministral-14b-latest"


def test_parse_json_pur_et_encadre():
    assert parse_response_content('{"a": 1}') == {"a": 1}
    parsed = parse_response_content('Voici la réponse :\n{"b": 2}\nmerci.')
    assert parsed == {"b": 2}
    with pytest.raises(ValueError, match="JSON"):
        parse_response_content("aucun json ici")


def test_from_dict_tolerant_aux_variantes_de_cles():
    metadata = MetadataOutput.from_dict(
        {
            "typologie": "rapport",
            "auteurs": ["Un auteur"],
            "éditeur": "Editeur",
            "date": "2020",
            "reference": "X",
            "titre": "T",
            "citation": "C",
        }
    )
    metadata.validate()
    assert metadata.typologie == "Rapport"
    assert metadata.auteurs == ["Un auteur"]
    assert metadata.editeur == "Editeur"
    assert metadata.reference == "X"


def test_validate_rejette_typologie_inconnue():
    with pytest.raises(MetadataValidationError):
        MetadataOutput(typologie="Courrier").validate()


def test_extraction_nominal_un_appel():
    client = FakeClient([VALID])
    metadata = extract_metadata(
        client, build_extrait("Un court texte."), retries=0, sleep=_no_sleep
    )
    assert client.calls == 1
    assert metadata.typologie == "Rapport"
    assert metadata.auteurs == ["A. Rapporteur"]


def test_extraction_rejouee_jusqua_validite():
    client = FakeClient(["pas du json", '{"Typologie": "Invalide"}', VALID])
    metadata = extract_metadata(
        client, build_extrait("Texte."), retries=0, sleep=_no_sleep
    )
    assert client.calls == 3
    assert metadata.typologie == "Rapport"


def test_extraction_plafond_cinq_appels():
    client = FakeClient(["{invalide"] * 10)
    with pytest.raises(ExtractionError):
        extract_metadata(client, build_extrait("Texte."), retries=0, sleep=_no_sleep)
    assert client.calls == 5


def test_retry_exponentiel_delais_double():
    sleeps: list[float] = []
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 4:
            raise RuntimeError("échec transitoire")
        return "ok"

    def record(seconds: float) -> None:
        sleeps.append(seconds)

    result = with_retry(flaky, retries=3, initial_delay=3.0, sleep=record)
    assert result == "ok"
    assert sleeps == [3.0, 6.0, 12.0]


def test_retry_erreur_client_definitive_non_rejouee():
    class FatalError(Exception):
        status_code = 401

    attempts = {"n": 0}

    def always_fails():
        attempts["n"] += 1
        raise FatalError("clé refusée")

    with pytest.raises(FatalError):
        with_retry(always_fails, retries=3, initial_delay=3.0, sleep=None)
    assert attempts["n"] == 1
