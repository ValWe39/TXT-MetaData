"""Tests unitaires du nommage et de l'écriture des sorties (FR-021,
FR-022, FR-026 ; quickstart : nommage et amendement)."""

import json
from pathlib import Path

import pytest

from txt_metadata.models import FIELD_ORDER, MetadataOutput
from txt_metadata.output import (
    amend_in_place,
    build_output_name,
    load_existing,
    merge_amendment,
    output_prefix,
    write_new,
)


def test_prefix_espaces_et_accents():
    path = Path("première séance du vendredi.md")
    assert output_prefix(path) == "premiere_seance_du_v"


def test_prefix_limite_vingt_caracteres():
    # l'underscore issu d'une espace compte comme un caractère
    assert output_prefix(Path("Rapport_information.md")) == "Rapport_information"
    assert output_prefix(Path("IFRI.md")) == "IFRI"


def test_nom_de_sortie():
    name = build_output_name(Path("Mon dossier/Rapport info.md"), "0007")
    assert name == "Rapport_info-0007.json"


def test_ecriture_nouvelle_sortie(tmp_path):
    metadata = MetadataOutput(
        typologie="Rapport",
        auteurs=["Sophie Mette"],
        titre="Titre du rapport",
        editeur="Assemblée nationale",
        date="30 septembre 2026",
        reference="N° 3201",
        citation='Sophie Mette, "Titre du rapport", N° 3201, '
        "Assemblée nationale, 30 septembre 2026",
    )
    target = write_new(
        metadata,
        output_dir=tmp_path / "output",
        input_path=Path("rapport.md"),
        occurrence="0001",
    )
    assert target.exists()
    data = json.loads(target.read_text(encoding="utf-8"))
    assert list(data.keys()) == list(FIELD_ORDER)
    assert data["Typologie"] == "Rapport"
    assert target.name == "rapport-0001.json"


def test_ecriture_dossier_cree_automatiquement(tmp_path):
    metadata = MetadataOutput(typologie="Autre")
    target = write_new(
        metadata,
        output_dir=tmp_path / "a" / "b" / "c",
        input_path=Path("x.md"),
        occurrence="0001",
    )
    assert target.exists()


def test_load_existing_format_valide(tmp_path):
    path = tmp_path / "rapport-0001.json"
    path.write_text(
        json.dumps({"Typologie": "Rapport", "Titre": "Un titre"}, ensure_ascii=False),
        encoding="utf-8",
    )
    loaded = load_existing(path)
    assert loaded is not None
    assert loaded.typologie == "Rapport"
    assert loaded.titre == "Un titre"


def test_load_existing_format_invalide(tmp_path):
    path = tmp_path / "autre.json"
    path.write_text(json.dumps({"nimportequoi": 1}), encoding="utf-8")
    assert load_existing(path) is None
    broken = tmp_path / "broken.json"
    broken.write_text("{pas du json", encoding="utf-8")
    assert load_existing(broken) is None


def test_merge_complete_les_champs_vides():
    existing = MetadataOutput(typologie="Rapport", titre="Titre conservé")
    new = MetadataOutput(
        typologie="Autre", titre="Titre différent", editeur="Ifri", date="mai 2022"
    )
    merged = merge_amendment(existing, new, high_confidence=False)
    assert merged.titre == "Titre conservé"  # rempli : non challengé
    assert merged.editeur == "Ifri"  # vide : complété
    assert merged.date == "mai 2022"


def test_merge_haut_degre_assurance_remplace():
    existing = MetadataOutput(typologie="Rapport", titre="Ancien titre")
    new = MetadataOutput(typologie="Autre", titre="Nouveau titre vérifié")
    merged = merge_amendment(existing, new, high_confidence=True)
    assert merged.titre == "Nouveau titre vérifié"


def test_amend_sur_place(tmp_path):
    path = tmp_path / "rapport-0001.json"
    merged = MetadataOutput(typologie="Rapport", editeur="Ifri")
    amend_in_place(path, merged)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["Editeur"] == "Ifri"


def test_titre_tronque_a_150():
    metadata = MetadataOutput(typologie="Autre", titre="x" * 200)
    metadata.validate()
    assert len(metadata.titre) == 150
    with pytest.raises(ValueError):
        MetadataOutput(typologie="Inconnu").validate()
