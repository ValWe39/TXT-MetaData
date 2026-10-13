"""Construction de la citation (FR-011 à FR-013).

Deux cas exclusifs :
1. un paragraphe « comment citer » existe dans le texte → reprise
   exacte (vérifiée dans le texte source) ;
2. sinon, composition déterministe : ``<auteur>, <titre>, <référence>,
   <éditeur>, <date>`` (référence omise si vide).

Règles de composition : guillemets droits autour du titre ; auteurs dans
l'ordre d'apparition, dernier relié par « et » pour des noms propres ;
plus de trois auteurs → premier auteur + « et al. » ; casse de citation
(minuscules sauf noms propres, acronymes, initiales de phrase).
"""

from __future__ import annotations

import re

from .models import MetadataOutput

MAX_AUTHORS = 3

_MONTHS_FR = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)
_NUMERIC_DATE_RE = re.compile(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$")


def normalize_date(date: str) -> str:
    """Normalise une date numérique en date longue française pour la
    citation : 28/07/2026 → 28 juillet 2026 ; 06.09.2018 → 06 septembre
    2018. Les autres formats sont conservés tels quels."""
    match = _NUMERIC_DATE_RE.match(date.strip())
    if not match:
        return date
    day, month, year = match.groups()
    index = int(month)
    if 1 <= index <= 12:
        return f"{day} {_MONTHS_FR[index - 1]} {year}"
    return date


_PERSON_STOPWORDS = {"de", "du", "des", "la", "le", "les", "d", "l"}


def _looks_like_person(name: str) -> bool:
    """Heuristique : un auteur est une personne physique si son nom est
    court et entièrement en capitales initiales (sinon institution,
    reliée par des virgules)."""
    tokens = name.split()
    if not 1 <= len(tokens) <= 4:
        return False
    for token in tokens:
        cleaned = re.sub(r"[^\wàâçéèêëîïôûüÿœæ-]", "", token, flags=re.IGNORECASE)
        if not cleaned:
            continue
        if cleaned.lower() in _PERSON_STOPWORDS:
            return False
        if not cleaned[0].isupper():
            return False
    return True


def format_authors(authors: list[str]) -> str:
    """Formate la liste des auteurs selon FR-012."""
    if not authors:
        return ""
    if len(authors) > MAX_AUTHORS:
        return f"{authors[0]} et al."
    if len(authors) == 1:
        return authors[0]
    if all(_looks_like_person(a) for a in authors):
        return ", ".join(authors[:-1]) + " et " + authors[-1]
    return ", ".join(authors)


def fix_citation_case(text: str) -> str:
    """Filet de sécurité : les mots tout en majuscules de plus de
    6 lettres repassent en Capitale initiale (MÉCOMPTES → Mécomptes).
    Les acronymes courts (FIPECO, AN…) et les noms propres gardent
    leur casse, fournie par l'extraction."""
    words = text.split(" ")
    fixed = []
    for word in words:
        stripped = word.strip(".,;:!?\"'«»()")
        if (
            stripped.isupper()
            and len(stripped) > 6
            and any(ch.isalpha() for ch in stripped)
        ):
            word = word.replace(stripped, stripped.capitalize())
        fixed.append(word)
    return " ".join(fixed)


def compose_citation(
    authors: list[str],
    titre: str,
    reference: str,
    editeur: str,
    date: str,
) -> str:
    """Compose la citation à partir des champs extraits (FR-011 cas 2).

    Retourne une chaîne vide si les champs disponibles sont
    insuffisants (FR-013).
    """
    parts: list[str] = []
    authors_part = format_authors(authors)
    if authors_part:
        parts.append(authors_part)
    if titre:
        parts.append(f'"{titre}"')
    if reference:
        parts.append(reference)
    if editeur:
        parts.append(editeur)
    if date:
        parts.append(normalize_date(date))
    if len(parts) <= 1:
        return ""
    citation = ", ".join(parts)
    return fix_citation_case(citation)


def verify_in_text(citation: str, source_text: str) -> bool:
    """Vrai si la citation est trouvée (espaces normalisés) dans le
    texte source : reprise exacte garantie, pas une hallucination."""
    if not citation:
        return False

    def norm(value: str) -> str:
        return " ".join(value.split()).lower()

    return norm(citation) in norm(source_text)


def resolve_citation(
    metadata: MetadataOutput,
    *,
    source_text: str,
) -> str:
    """Résout le champ Citation (cas 1 exact, sinon cas 2 composé).

    La citation renvoyée par le LLM n'est gardée telle quelle que si
    elle est vérifiée mot à mot dans le texte source ; sinon la
    citation est composée de façon déterministe.
    """
    if metadata.citation and verify_in_text(metadata.citation, source_text):
        return metadata.citation.strip()
    return compose_citation(
        metadata.auteurs,
        metadata.titre,
        metadata.reference,
        metadata.editeur,
        metadata.date,
    )
