"""Tests unitaires de la découverte des entrées (T023, FR-001)."""

from txt_metadata.inputs import discover, read_text


def test_fichier_unique(tmp_path):
    doc = tmp_path / "exemple.md"
    doc.write_text("texte", encoding="utf-8")
    docs = discover([doc])
    assert len(docs) == 1
    assert docs[0].path.name == "exemple.md"


def test_dossier_recursif_avec_filtrage(tmp_path):
    (tmp_path / "a.md").write_text("texte", encoding="utf-8")
    (tmp_path / "sous").mkdir()
    (tmp_path / "sous" / "b.txt").write_text("texte", encoding="utf-8")
    (tmp_path / "sous" / "c.pdf").write_text("binaire", encoding="utf-8")
    (tmp_path / "sous" / "d.docx").write_text("binaire", encoding="utf-8")
    docs = discover([tmp_path])
    names = sorted(d.path.name for d in docs)
    assert names == ["a.md", "b.txt"]


def test_plusieurs_dossiers_et_doublons(tmp_path):
    other = tmp_path / "autre"
    other.mkdir()
    (tmp_path / "x.md").write_text("x", encoding="utf-8")
    (other / "y.md").write_text("y", encoding="utf-8")
    # le même fichier passé deux fois n'est traité qu'une fois
    docs = discover([tmp_path, other, tmp_path / "x.md"])
    paths = sorted(d.path.name for d in docs)
    assert paths == ["x.md", "y.md"]
    resolved = {d.path.resolve() for d in docs}
    assert len(resolved) == 2


def test_fichier_hors_format_ignore(tmp_path):
    (tmp_path / "z.pdf").write_text("x", encoding="utf-8")
    docs = discover([tmp_path])
    assert docs == []


def test_lecture_utf8_et_repli_latin1(tmp_path):
    utf8 = tmp_path / "utf8.md"
    utf8.write_text("Éàç texte", encoding="utf-8")
    assert read_text(utf8) == "Éàç texte"
    latin = tmp_path / "latin.md"
    latin.write_bytes("Éàç texte".encode("latin-1"))
    assert read_text(latin) == "Éàç texte"
