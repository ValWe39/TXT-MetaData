"""Échantillonnage début/fin d'un document (FR-002 à FR-005).

Document long : extrait = ~20 000 premiers caractères + ~16 000 derniers,
coupés proprement (sous-partie, à défaut paragraphe, à défaut phrase, à
défaut mot ; « ... » si une phrase est séparée) et séparés par un
dispositif explicite pour que la fin du texte ne soit pas lue comme la
suite hiérarchique du début (FR-004). Document court : texte intégral.
"""

from __future__ import annotations

from dataclasses import dataclass

HEAD_LIMIT = 20_000
TAIL_LIMIT = 16_000

_SENTENCE_ENDS = ".!?"


@dataclass
class Extrait:
    """Extrait soumis au LLM (data-model.md)."""

    head: str
    tail: str
    is_full_text: bool


def _is_word_break(text: str, pos: int) -> bool:
    """Vrai si couper en ``pos`` préserve les mots (fin de mot/ligne)."""
    if pos <= 0 or pos >= len(text):
        return False
    return text[pos - 1] in " \t\n"


def _is_paragraph_break(text: str, pos: int) -> bool:
    """Vrai si ``pos`` démarre un nouveau paragraphe ou une sous-partie."""
    if pos <= 0 or pos >= len(text):
        return False
    if text[pos] == "#":
        return True
    return text[pos - 1] == "\n" and text[pos - 2 : pos] == "\n"


def _is_sentence_break(text: str, pos: int) -> bool:
    """Vrai si ``pos`` suit une fin de phrase nette."""
    if pos <= 0 or pos >= len(text):
        return False
    if text[pos - 1] in _SENTENCE_ENDS and text[pos] in " \t\n":
        return True
    return text[pos - 1] == "\n" and text[pos] == "\n"


def _cut_head(text: str, limit: int) -> tuple[str, bool]:
    """Coupe le segment de début au plus près de ``limit``.

    Retourne (segment, phrase_coupee). Priorité : sous-partie/paragraphe,
    phrase, mot ; à défaut coupure dure au caractère.
    """
    if len(text) <= limit:
        return text, False
    best_para = 0
    best_sentence = 0
    best_word = 0
    for pos in range(limit, max(limit // 2, 1), -1):
        if _is_paragraph_break(text, pos):
            best_para = pos
            break
    if not best_para:
        for pos in range(limit, max(limit // 2, 1), -1):
            if _is_sentence_break(text, pos):
                best_sentence = pos
                break
    if not best_para and not best_sentence:
        for pos in range(limit, max(limit // 2, 1), -1):
            if _is_word_break(text, pos):
                best_word = pos
                break
    cut = best_para or best_sentence or best_word or limit
    phrase_cut = not (best_para or best_sentence)
    return text[:cut].rstrip(), phrase_cut


def _cut_tail(text: str, offset: int, limit: int) -> tuple[str, bool]:
    """Coupe le segment de fin au plus tôt dans les ``limit`` derniers
    caractères. ``offset`` = indice du premier caractère du segment brut.
    Retourne (segment, phrase_coupee)."""
    raw = text[offset:]
    if offset <= 0:
        return raw, False
    max_scan = min(len(raw), max(len(raw) // 2, 1))
    best_para = 0
    best_sentence = 0
    best_word = 0
    for pos in range(max_scan):
        if _is_paragraph_break(raw, pos):
            best_para = pos
            break
    if not best_para:
        for pos in range(max_scan):
            if _is_sentence_break(raw, pos):
                best_sentence = pos
                break
    if not best_para and not best_sentence:
        for pos in range(max_scan):
            if _is_word_break(raw, pos):
                best_word = pos
                break
    cut = best_para or best_sentence or best_word
    if cut:
        return raw[cut:].lstrip(), not (best_para or best_sentence)
    return raw.lstrip(), True


def build_extrait(text: str) -> Extrait:
    """Construit l'extrait d'un document (FR-002, FR-005)."""
    if len(text) <= HEAD_LIMIT + TAIL_LIMIT:
        return Extrait(head=text, tail="", is_full_text=True)
    head, head_cut = _cut_head(text, HEAD_LIMIT)
    tail_offset = len(text) - TAIL_LIMIT
    tail, tail_cut = _cut_tail(text, tail_offset, TAIL_LIMIT)
    if head_cut:
        head += " ..."
    if tail_cut:
        tail = "... " + tail.lstrip()
    return Extrait(head=head, tail=tail, is_full_text=False)


def render_extrait(extrait: Extrait) -> str:
    """Rend l'extrait avec le dispositif de séparation (FR-004).

    Le LLM doit comprendre que la fin du document n'est PAS la suite
    hiérarchique du début.
    """
    if extrait.is_full_text:
        return extrait.head
    return (
        "=== DÉBUT DU DOCUMENT (première partie de l'extrait) ===\n"
        f"{extrait.head}\n"
        "=== FIN DE LA PREMIÈRE PARTIE — "
        "le milieu du document est omis, la suite n'est PAS la suite logique "
        "du début ===\n"
        "=== DERNIÈRE PARTIE DE L'EXTRAIT (fin du document) ===\n"
        f"{extrait.tail}\n"
        "=== FIN DU DOCUMENT ==="
    )
