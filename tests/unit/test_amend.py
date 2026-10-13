"""Tests unitaires de la politique d'amendement (T029, FR-026).

Un JSON existant apparié est amendé sur place ; les champs vides sont
complétés en priorité ; un champ rempli n'est remplacé que si la
nouvelle valeur est vérifiée dans le texte source (haut degré
d'assurance).
"""

from txt_metadata.__main__ import _apply_amendment
from txt_metadata.models import MetadataOutput

SOURCE = (
    "Rapport d'information sur les moyens. "
    "Présenté par Anne Rapporteuse. Publié par l'Assemblée nationale "
    "le 30 septembre 2026, référence N° 3201."
)


def test_champs_vides_completes():
    existing = MetadataOutput(typologie="Rapport")
    new = MetadataOutput(typologie="Rapport", titre="Rapport d'information")
    merged = _apply_amendment(existing, new, source_text=SOURCE)
    assert merged.titre == "Rapport d'information"


def test_champ_remple_conserve_si_non_verifie():
    existing = MetadataOutput(typologie="Rapport", titre="Titre corrigé à la main")
    new = MetadataOutput(typologie="Rapport", titre="Titre halluciné par le modèle")
    merged = _apply_amendment(existing, new, source_text=SOURCE)
    assert merged.titre == "Titre corrigé à la main"


def test_champ_remple_remplace_si_verifie_dans_le_texte():
    existing = MetadataOutput(typologie="Rapport", editeur="Ancien éditeur")
    new = MetadataOutput(typologie="Rapport", editeur="Assemblée nationale")
    merged = _apply_amendment(existing, new, source_text=SOURCE)
    assert merged.editeur == "Assemblée nationale"


def test_typologie_autre_peut_etre_affinee():
    existing = MetadataOutput(typologie="Autre")
    new = MetadataOutput(typologie="Rapport")
    merged = _apply_amendment(existing, new, source_text=SOURCE)
    assert merged.typologie == "Rapport"


def test_typologie_remplee_conservee():
    existing = MetadataOutput(typologie="Cours")
    new = MetadataOutput(typologie="Rapport")
    merged = _apply_amendment(existing, new, source_text=SOURCE)
    assert merged.typologie == "Cours"
