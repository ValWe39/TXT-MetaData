"""Tests unitaires de la citation (T018, FR-011 à FR-013)."""

from txt_metadata.citation import (
    compose_citation,
    fix_citation_case,
    format_authors,
    normalize_date,
    resolve_citation,
    verify_in_text,
)
from txt_metadata.models import MetadataOutput


def test_normalisation_date_numerique_en_longue():
    assert normalize_date("28/07/2026") == "28 juillet 2026"
    assert normalize_date("06.09.2018") == "06 septembre 2018"
    assert normalize_date("1-12-2024") == "1 décembre 2024"


def test_normalisation_date_conserve_les_autres_formats():
    assert normalize_date("avril 2025") == "avril 2025"
    assert normalize_date("30 septembre 2026") == "30 septembre 2026"
    assert normalize_date("99/99/2026") == "99/99/2026"


def test_deux_auteurs_personnes_reliees_par_et():
    authors = ["Karim Ben Cheikh", "Sophie Mette"]
    assert format_authors(authors) == "Karim Ben Cheikh et Sophie Mette"


def test_plus_de_trois_auteurs_premier_et_al():
    authors = ["A. Premier", "B. Second", "C. Troisieme", "D. Quatrieme"]
    assert format_authors(authors) == "A. Premier et al."


def test_institutions_reliees_par_virgules():
    authors = ["XVIIe législature", "Session ordinaire de 2026-2027"]
    assert (
        format_authors(authors) == "XVIIe législature, Session ordinaire de 2026-2027"
    )


def test_composition_complete_avec_reference():
    citation = compose_citation(
        ["Laurent Bansept", "Élie Tenenbaum"],
        "Après Barkhane : repenser la posture stratégique",
        "Focus stratégique, n° 109",
        "Ifri",
        "mai 2022",
    )
    assert citation == (
        'Laurent Bansept et Élie Tenenbaum, "Après Barkhane : repenser '
        'la posture stratégique", Focus stratégique, n° 109, Ifri, mai 2022'
    )


def test_composition_reference_vide_omise():
    citation = compose_citation(
        ["Pernod Ricard"],
        "Communiqué établissant le bilan semestriel",
        "",
        "pernod-ricard.com",
        "28/07/2026",
    )
    assert citation == (
        'Pernod Ricard, "Communiqué établissant le bilan semestriel", '
        "pernod-ricard.com, 28 juillet 2026"
    )


def test_composition_champs_insuffisants_vide():
    assert compose_citation(["Un auteur"], "", "", "", "") == ""
    assert compose_citation([], "Un titre seulement", "", "", "") == ""
    assert compose_citation([], "", "", "", "") == ""


def test_casse_majuscules_longues_repassent_en_capitale():
    assert fix_citation_case("MÉCOMPTES PUBLICS") == "Mécomptes Publics"
    # acronyme court : casse conservée
    assert fix_citation_case("FIPECO") == "FIPECO"


def test_verify_in_text_normalise_les_espaces():
    source = "Ce rapport  doit être cité ainsi :\n\ndes espaces    variés."
    assert verify_in_text("être cité ainsi : des espaces variés", source)
    assert not verify_in_text("phrase absente du document", source)


def test_resolve_citation_paragraphe_exact_repris():
    source = (
        "Texte du document. Pour citer ce rapport : Dubois, « Titre », "
        "Revue, 2020. Suite du document."
    )
    metadata = MetadataOutput(
        typologie="Rapport",
        citation="Pour citer ce rapport : Dubois, « Titre », Revue, 2020",
    )
    resolved = resolve_citation(metadata, source_text=source)
    assert resolved == "Pour citer ce rapport : Dubois, « Titre », Revue, 2020"


def test_resolve_citation_hallucinee_remplacee_par_composition():
    source = "Texte du document sans paragraphe de citation."
    metadata = MetadataOutput(
        typologie="Rapport",
        auteurs=["Marie Curie"],
        titre="Titre du texte",
        editeur="Editeur",
        date="2020",
        citation="Citation inventée par le modèle",
    )
    resolved = resolve_citation(metadata, source_text=source)
    assert resolved == 'Marie Curie, "Titre du texte", Editeur, 2020'


def test_resolve_citation_vide_si_champs_insuffisants():
    metadata = MetadataOutput(typologie="Autre")
    assert resolve_citation(metadata, source_text="texte") == ""
