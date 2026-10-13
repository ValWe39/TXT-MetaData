"""Tests d'intégration multi-entrées et amendement (T027, T030, T031 ;
quickstart V2/V3). Mock du client LLM, aucun appel réseau."""

import json

import pytest

import txt_metadata.__main__ as main_module


class FakeResponse:
    def __init__(self, content):
        class Message:
            pass

        class Choice:
            pass

        message = Message()
        message.content = content
        choice = Choice()
        choice.message = message
        self.choices = [choice]


class FakeClient:
    """Renvoie la même réponse pour tous les documents."""

    def __init__(self, content):
        self.content = content

    def chat_complete(self, **kwargs):
        return FakeResponse(self.content)


RESPONSE = (
    '{"Typologie": "Rapport", "Auteur(s)": ["Un Auteur"], '
    '"Titre": "Titre extrait", "Editeur": "Ifri", "Date": "mai 2022", '
    '"Référence": "", "Citation": ""}'
)


@pytest.fixture()
def isolated_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test-factice")
    monkeypatch.setattr(main_module, "COUNTER_FILENAME", tmp_path / "counter.txt")

    def run(argv: list[str], client) -> int:
        def factory(api_key: str):
            return client

        monkeypatch.setattr(main_module, "create_client", factory)
        return main_module.main(argv)

    return run, tmp_path


def test_multi_entrees_numerotation_sequentielle(isolated_run):
    run, tmp_path = isolated_run
    for name in ("Premier.md", "Deuxieme.md", "Troisieme.txt", "ignore.pdf"):
        (tmp_path / name).write_text("contenu avec Titre extrait.", encoding="utf-8")
    output_dir = tmp_path / "sortie"
    code = run(
        [
            str(tmp_path),
            "--output-folder",
            str(output_dir),
            "--retry-occurences",
            "0",
            "--taille-batch",
            "0",
        ],
        FakeClient(RESPONSE),
    )
    assert code == 0
    # ordre de traitement déterministe (tri) : Deuxieme, Premier, Troisieme
    outputs = sorted(p.name for p in output_dir.glob("*.json"))
    assert outputs == ["Deuxieme-0001.json", "Premier-0002.json", "Troisiem-0003.json"]
    counter = (tmp_path / "counter.txt").read_text(encoding="utf-8")
    assert counter == "0003"


def test_amendement_sur_place_sans_numero(isolated_run):
    run, tmp_path = isolated_run
    doc = tmp_path / "Rapport info.md"
    doc.write_text("Titre extrait dans le texte du document.", encoding="utf-8")
    existing = tmp_path / "Rapport-0005.json"
    existing.write_text(
        json.dumps({"Typologie": "Rapport", "Editeur": "Ancien"}, ensure_ascii=False),
        encoding="utf-8",
    )
    output_dir = tmp_path / "sortie"
    code = run(
        [str(tmp_path), "--output-folder", str(output_dir), "--retry-occurences", "0"],
        FakeClient(RESPONSE),
    )
    assert code == 0
    data = json.loads(existing.read_text(encoding="utf-8"))
    # champ vide complété
    assert data["Titre"] == "Titre extrait"
    # champ rempli non vérifié : conservé
    assert data["Editeur"] == "Ancien"
    # aucun numéro consommé, aucune sortie dans le dossier
    assert not output_dir.exists()
    assert not (tmp_path / "counter.txt").exists()
    assert existing.name == "Rapport-0005.json"


def test_echec_en_lot_le_lot_poursuit(isolated_run, capsys):
    run, tmp_path = isolated_run

    class HalfFailingClient:
        """Échoue pour le document « mauvais », réussit pour l'autre."""

        def chat_complete(self, **kwargs):
            prompt = kwargs.get("messages", [{}])[0].get("content", "")
            if "MAUVAIS" in prompt:
                raise RuntimeError("erreur simulée")
            return FakeResponse(RESPONSE)

    (tmp_path / "mauvais.md").write_text("Document MAUVAIS. ", encoding="utf-8")
    (tmp_path / "bon.md").write_text("Document avec Titre extrait. ", encoding="utf-8")
    output_dir = tmp_path / "sortie"
    code = run(
        [str(tmp_path), "--output-folder", str(output_dir), "--retry-occurences", "0"],
        HalfFailingClient(),
    )
    assert code == 1
    outputs = list(output_dir.glob("*.json"))
    assert len(outputs) == 1
    assert outputs[0].name.startswith("bon-")
    counter = (tmp_path / "counter.txt").read_text(encoding="utf-8")
    assert counter == "0001"
    captured = capsys.readouterr()
    assert "Bilan" in captured.out
    assert "1 en échec" in captured.out
