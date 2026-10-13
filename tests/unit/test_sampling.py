"""Tests unitaires de l'échantillonnage (T014, FR-002 à FR-005)."""

from txt_metadata.sampling import (
    HEAD_LIMIT,
    TAIL_LIMIT,
    _cut_head,
    _cut_tail,
    build_extrait,
    render_extrait,
)


def test_document_court_texte_integral():
    text = "Un document court, sans coupure nécessaire."
    extrait = build_extrait(text)
    assert extrait.is_full_text is True
    assert render_extrait(extrait) == text


def test_document_long_deux_segments_marques():
    text = "Phrase initiale. " + "Contenu long et répétitif du milieu. " * 3000
    text += " Conclusion finale du document."
    extrait = build_extrait(text)
    assert extrait.is_full_text is False
    rendered = render_extrait(extrait)
    assert rendered.startswith("=== DÉBUT DU DOCUMENT")
    assert "le milieu du document est omis" in rendered
    assert "=== DERNIÈRE PARTIE DE L'EXTRAIT" in rendered
    assert rendered.endswith("=== FIN DU DOCUMENT ===")
    assert "Conclusion finale" in extrait.tail
    assert len(extrait.head) <= HEAD_LIMIT + 4  # marge : " ..."


def test_coupure_sur_fin_de_phrase():
    text = "Bonjour tout le monde. Deuxième phrase un peu plus longue ici."
    segment, phrase_cut = _cut_head(text, 25)
    assert segment == "Bonjour tout le monde."
    assert phrase_cut is False


def test_coupure_sur_paragraphe():
    text = "Un.\n\nDeux mots suivis dans un second paragraphe ici."
    segment, phrase_cut = _cut_head(text, 7)
    assert segment == "Un."
    assert phrase_cut is False


def test_coupure_sur_mot_marque_phrase_coupee():
    text = "Une phrase tres longue sans point final du tout"
    segment, phrase_cut = _cut_head(text, 12)
    assert segment == "Une phrase"  # aucun mot coupé
    assert phrase_cut is True


def test_ellipse_ajoutee_aux_deux_segments_si_phrase_coupee():
    text = "mot " * 12000  # une seule « phrase » sans ponctuation
    extrait = build_extrait(text)
    assert extrait.is_full_text is False
    assert extrait.head.endswith("...")
    assert extrait.tail.startswith("...")


def test_pas_d_ellipse_si_coupure_propre():
    text = "Une phrase. " * 4000  # coupures nettes sur fin de phrase
    extrait = build_extrait(text)
    assert extrait.head.endswith(".")
    assert not extrait.head.endswith("... ")
    assert not extrait.tail.startswith("... ")


def test_coupure_fin_sur_debut_de_phrase():
    text = "Milieu coupé brutalement. Début propre de la fin du doc ici."
    # le segment brut commence juste après la fin de phrase
    offset = text.index("Début") - 2
    segment, phrase_cut = _cut_tail(text, offset, 60)
    assert segment.startswith("Début propre")
    assert phrase_cut is False


def test_coupure_fin_sur_mot_marque_phrase_coupee():
    text = "mot court " * 30
    offset = 5
    segment, phrase_cut = _cut_tail(text, offset, 300)
    assert phrase_cut is True
    # aucun mot coupé : le segment commence sur un mot complet
    assert segment.split()[0] == "mot"


def test_texte_integral_si_inferieur_aux_bornes():
    text = "a" * (HEAD_LIMIT + TAIL_LIMIT)
    extrait = build_extrait(text)
    assert extrait.is_full_text is True
    assert extrait.head == text
