"""Tests d'intégration du parcours fichier unique (T009, quickstart V1).

Mock du client LLM : aucun appel réseau, aucune consommation d'API.
"""

import json

import pytest

import txt_metadata.__main__ as main_module


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
    """Renvoie une réponse LLM fixe (JSON valide)."""

    def __init__(self, content):
        self.content = content

    def chat_complete(self, **kwargs):
        return FakeResponse(self.content)


VALID_RESPONSE = (
    '{"Typologie": "Rapport", "Auteur(s)": ["Anne Rapporteuse"], '
    '"Titre": "Rapport d\'information sur les moyens", '
    '"Editeur": "Assemblée nationale", "Date": "30 septembre 2026", '
    '"Référence": "N° 3201", "Citation": ""}'
)


@pytest.fixture()
def isolated_run(tmp_path, monkeypatch):
    """Isole compteur, cwd et clé API dans tmp_path ; injecte un faux
    client LLM à la place du SDK (aucun appel réseau)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test-factice")
    monkeypatch.setattr(main_module, "COUNTER_FILENAME", tmp_path / "counter.txt")

    def run(argv: list[str], client) -> int:
        def factory(api_key: str):
            return client

        monkeypatch.setattr(main_module, "create_client", factory)
        return main_module.main(argv)

    return run, tmp_path


def test_fichier_unique_v1(isolated_run):
    run, workdir = isolated_run
    tmp_path = workdir
    doc = tmp_path / "Rapport exemple.md"
    doc.write_text(
        "Rapport d'information sur les moyens.\nPrésenté par Anne "
        "Rapporteuse, Assemblée nationale, 30 septembre 2026, N° 3201.\n"
        + "Contenu du rapport. "
        * 20,
        encoding="utf-8",
    )
    output_dir = tmp_path / "sortie"
    code = run(
        [str(doc), "--output-folder", str(output_dir), "--retry-occurences", "0"],
        FakeClient(VALID_RESPONSE),
    )
    assert code == 0
    counter_file = tmp_path / "counter.txt"
    assert counter_file.read_text(encoding="utf-8") == "0001"
    outputs = list(output_dir.glob("*.json"))
    assert len(outputs) == 1
    assert outputs[0].name == "Rapport_-0001.json"
    data = json.loads(outputs[0].read_text(encoding="utf-8"))
    assert data["Typologie"] == "Rapport"
    assert data["Auteur(s)"] == ["Anne Rapporteuse"]
    # citation composée de façon déterministe (paragraphe absent)
    assert data["Citation"] == (
        'Anne Rapporteuse, "Rapport d\'information sur les moyens", '
        "N° 3201, Assemblée nationale, 30 septembre 2026"
    )


def test_compteur_corrompu_code_2(isolated_run, capsys):
    run, workdir = isolated_run
    (workdir / "counter.txt").write_text("corrompu", encoding="utf-8")
    doc = workdir / "a.md"
    doc.write_text("texte", encoding="utf-8")
    code = run([str(doc)], FakeClient(VALID_RESPONSE))
    assert code == 2
    assert "corrompu" in capsys.readouterr().err


def test_cle_absente_code_2(isolated_run, monkeypatch, capsys):
    run, workdir = isolated_run
    doc = workdir / "a.md"
    doc.write_text("texte", encoding="utf-8")
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    code = run([str(doc), "--retry-occurences", "0"], FakeClient(VALID_RESPONSE))
    assert code == 2
    assert "MISTRAL_API_KEY" in capsys.readouterr().err


def test_document_vide_sortie_minimale(isolated_run):
    run, workdir = isolated_run
    doc = workdir / "vide.md"
    doc.write_text("", encoding="utf-8")
    empty_response = (
        '{"Typologie": "Autre", "Auteur(s)": [], "Titre": "", '
        '"Editeur": "", "Date": "", "Référence": "", "Citation": ""}'
    )
    output_dir = workdir / "sortie"
    code = run(
        [str(doc), "--output-folder", str(output_dir), "--retry-occurences", "0"],
        FakeClient(empty_response),
    )
    assert code == 0
    data = json.loads((output_dir / "vide-0001.json").read_text(encoding="utf-8"))
    assert data["Typologie"] == "Autre"


def test_extraction_en_echec_document_ignore(isolated_run, capsys):
    run, workdir = isolated_run

    class FailingClient:
        def chat_complete(self, **kwargs):
            raise RuntimeError("service indisponible")

    doc = workdir / "echec.md"
    doc.write_text("texte", encoding="utf-8")
    output_dir = workdir / "sortie"
    code = run(
        [str(doc), "--output-folder", str(output_dir), "--retry-occurences", "0"],
        FailingClient(),
    )
    assert code == 1
    outputs = list(output_dir.glob("*.json")) if output_dir.exists() else []
    assert outputs == []
    assert not (workdir / "counter.txt").exists()
    captured = capsys.readouterr()
    assert "ÉCHEC" in captured.err
