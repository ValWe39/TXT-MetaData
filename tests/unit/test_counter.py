"""Tests unitaires du compteur d'occurrence (FR-023 à FR-025)."""

import pytest

from txt_metadata import counter


def test_fichier_absent_premiere_occurrence_0001(tmp_path):
    path = tmp_path / "counter.txt"
    assert counter.load(path) == 0
    assert counter.next_occurrence(path) == "0001"
    assert path.read_text(encoding="utf-8") == "0001"


def test_incrementation_et_persistance(tmp_path):
    path = tmp_path / "counter.txt"
    path.write_text("0012", encoding="utf-8")
    assert counter.next_occurrence(path) == "0013"
    assert path.read_text(encoding="utf-8") == "0013"


def test_cycle_apres_9999(tmp_path):
    path = tmp_path / "counter.txt"
    path.write_text("9999", encoding="utf-8")
    assert counter.next_occurrence(path) == "0000"
    assert counter.next_occurrence(path) == "0001"


def test_fichier_corrompu_echec_rapide(tmp_path):
    path = tmp_path / "counter.txt"
    path.write_text("abc", encoding="utf-8")
    with pytest.raises(counter.CounterError):
        counter.next_occurrence(path)
    assert path.read_text(encoding="utf-8") == "abc"


def test_valeur_hors_plage_refusee(tmp_path):
    path = tmp_path / "counter.txt"
    path.write_text("12345", encoding="utf-8")
    with pytest.raises(counter.CounterError):
        counter.load(path)


def test_espaces_toleres(tmp_path):
    path = tmp_path / "counter.txt"
    path.write_text("0042\n", encoding="utf-8")
    assert counter.load(path) == 42
