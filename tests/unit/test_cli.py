"""Tests unitaires de la validation des options CLI (T032, FR-029,
FR-030)."""

from pathlib import Path

import pytest

from txt_metadata.cli import CliError, parse_args


def test_valeurs_par_defaut(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("x", encoding="utf-8")
    options = parse_args([str(doc)])
    assert options.model_alias == "small"
    assert options.batch_size == 25
    assert options.retries == 3
    assert options.retry_time == 3
    assert options.output_folder == Path("output")
    assert options.temperature == 0.0


@pytest.mark.parametrize(
    ("alias",),
    [
        ("large4",),
        ("large",),
        ("medium",),
        ("small",),
        ("14b",),
        ("8b",),
        ("3b",),
        ("zai",),
    ],
)
def test_alias_modeles_valides(tmp_path, alias):
    doc = tmp_path / "a.md"
    doc.write_text("x", encoding="utf-8")
    options = parse_args([str(doc), "--choix", alias])
    assert options.model_alias == alias


def test_alias_inconnu_rejete(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("x", encoding="utf-8")
    with pytest.raises(CliError, match="modèle inconnu"):
        parse_args([str(doc), "--choix", "gpt"])


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--taille-batch", "101"),
        ("--taille-batch", "-1"),
        ("--retry-occurences", "11"),
        ("--retry-time", "0"),
        ("--temperature-llm", "1.5"),
        ("--temperature-llm", "-0.1"),
    ],
)
def test_valeurs_hors_bornes_rejetees(tmp_path, option, value):
    doc = tmp_path / "a.md"
    doc.write_text("x", encoding="utf-8")
    with pytest.raises(CliError, match="hors bornes"):
        parse_args([str(doc), option, value])


def test_valeurs_aux_bornes_valides(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("x", encoding="utf-8")
    options = parse_args(
        [
            str(doc),
            "--taille-batch",
            "0",
            "--retry-occurences",
            "10",
            "--retry-time",
            "10",
            "--temperature-llm",
            "1",
        ]
    )
    assert options.batch_size == 0
    assert options.retries == 10
    assert options.retry_time == 10
    assert options.temperature == 1.0


def test_chemin_inexistant_rejete(tmp_path):
    with pytest.raises(CliError, match="introuvable"):
        parse_args([str(tmp_path / "absent.md")])
