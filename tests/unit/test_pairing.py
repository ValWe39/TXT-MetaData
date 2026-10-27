"""Tests unitaires de l'appariement texte/JSON (T028, FR-027)."""

import json
from pathlib import Path

from txt_metadata.inputs import discover, pair_documents


def _write_json(path: Path, typologie: str = "Rapport") -> None:
    path.write_text(
        json.dumps({"Typologie": typologie}, ensure_ascii=False), encoding="utf-8"
    )


def test_appariement_par_prefixe(tmp_path):
    (tmp_path / "Rapport info.md").write_text("texte", encoding="utf-8")
    # ancien nommage (préfixe 8 caractères) : reconnu car 8 caractères
    # partagés avec le préfixe « Rapport_info » (FR-003)
    _write_json(tmp_path / "Rapport_-0001.json")
    (tmp_path / "Autre doc.md").write_text("texte", encoding="utf-8")
    docs = {d.path.name: d for d in discover([tmp_path])}
    pair_documents(list(docs.values()))
    assert docs["Rapport info.md"].paired_json is not None
    assert docs["Rapport info.md"].paired_json.name == "Rapport_-0001.json"
    assert docs["Autre doc.md"].paired_json is None


def test_paire_unique_dans_un_sous_dossier(tmp_path):
    (tmp_path / "Texte unique.md").write_text("texte", encoding="utf-8")
    _write_json(tmp_path / "Prefixe-0009.json")
    docs = discover([tmp_path])
    pair_documents(docs)
    assert docs[0].paired_json is not None


def test_appariement_ambigu_non_lie(tmp_path):
    (tmp_path / "Rapport A.md").write_text("texte", encoding="utf-8")
    (tmp_path / "Rapport B.md").write_text("texte", encoding="utf-8")
    _write_json(tmp_path / "Rapport-0001.json")
    docs = discover([tmp_path])
    pair_documents(docs)
    assert all(d.paired_json is None for d in docs)


def test_json_hors_format_non_apparie(tmp_path):
    (tmp_path / "Rapport info.md").write_text("texte", encoding="utf-8")
    (tmp_path / "Rapport-0002.json").write_text(
        json.dumps({"cle": "inconnue"}), encoding="utf-8"
    )
    docs = discover([tmp_path])
    pair_documents(docs)
    assert docs[0].paired_json is None


def test_departage_ancien_et_nouveau(tmp_path):
    # FR-004 : entre un ancien nommage (8 caractères partagés) et le
    # nouveau (12), le candidat le plus proche est retenu
    (tmp_path / "Rapport info.md").write_text("texte", encoding="utf-8")
    _write_json(tmp_path / "Rapport_-0001.json")
    _write_json(tmp_path / "Rapport_info-0007.json")
    docs = discover([tmp_path])
    pair_documents(docs)
    assert docs[0].paired_json is not None
    assert docs[0].paired_json.name == "Rapport_info-0007.json"


def test_appariement_nom_accentue(tmp_path):
    # le nom du JSON est normalisé (espaces → ``_``, accents simplifiés)
    # avant comparaison : ici 12 caractères partagés une fois normalisé
    (tmp_path / "Rapport info.md").write_text("texte", encoding="utf-8")
    _write_json(tmp_path / "Rapport infó-0002.json")
    docs = discover([tmp_path])
    pair_documents(docs)
    assert docs[0].paired_json is not None
    assert docs[0].paired_json.name == "Rapport infó-0002.json"


def test_egalite_parfaite_non_lie(tmp_path):
    # FR-005 : deux candidats partageant exactement autant de caractères
    # ne départagent pas : le document est traité seul
    (tmp_path / "Rapport info.md").write_text("texte", encoding="utf-8")
    _write_json(tmp_path / "Rapport_-0001.json")
    _write_json(tmp_path / "Rapport_-0002.json")
    docs = discover([tmp_path])
    pair_documents(docs)
    assert docs[0].paired_json is None
