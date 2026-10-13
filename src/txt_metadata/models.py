"""Entités métier et validation des métadonnées (data-model.md).

``MetadataOutput`` porte les 7 clés exactes du schéma de sortie.
Validation : Typologie obligatoire parmi 9 valeurs ; Titre ≤ 150
caractères ; champs optionnels vides si absents (FR-006 à FR-009).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

TYPOLOGIES: tuple[str, ...] = (
    "Article",
    "Rapport",
    "Ouvrage",
    "Cours",
    "Bibliothèque",
    "Extrait",
    "Communiqué",
    "Compte-rendu",
    "Autre",
)

MAX_TITLE_LENGTH = 150

FIELD_ORDER: tuple[str, ...] = (
    "Typologie",
    "Auteur(s)",
    "Titre",
    "Editeur",
    "Date",
    "Référence",
    "Citation",
)

# Variantes acceptées en entrée (réponses LLM tolérantes)
_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    "Typologie": ("typologie", "type", "typology"),
    "Auteur(s)": ("auteur(s)", "auteurs", "auteur", "authors", "author(s)"),
    "Titre": ("titre", "title"),
    "Editeur": ("editeur", "éditeur", "publisher", "editor"),
    "Date": ("date", "date de parution", "date de publication"),
    "Référence": ("référence", "reference", "ref"),
    "Citation": ("citation", "comment citer", "how to cite"),
}


class MetadataValidationError(ValueError):
    """Valeur de métadonnée invalide."""


def _norm_key(key: str) -> str | None:
    folded = unicodedata.normalize("NFKD", key.strip().lower())
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    for canonical, aliases in _KEY_ALIASES.items():
        for alias in aliases:
            norm_alias = unicodedata.normalize("NFKD", alias)
            norm_alias = "".join(
                ch for ch in norm_alias if not unicodedata.combining(ch)
            )
            if folded == norm_alias:
                return canonical
    return None


@dataclass
class MetadataOutput:
    """Métadonnées d'un document, sérialisées en JSON de sortie."""

    typologie: str = "Autre"
    auteurs: list[str] = field(default_factory=list)
    titre: str = ""
    editeur: str = ""
    date: str = ""
    reference: str = ""
    citation: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> MetadataOutput:
        """Construit depuis une réponse LLM ou un JSON existant.

        Tolérant aux clés manquantes et aux variantes de nommage ;
        ``None`` devient valeur vide.
        """
        mapped: dict[str, object] = {}
        for key, value in data.items():
            canonical = _norm_key(key)
            if canonical is None:
                continue
            mapped[canonical] = value
        return cls(
            typologie=str(mapped.get("Typologie", "") or ""),
            auteurs=[str(a).strip() for a in (mapped.get("Auteur(s)") or []) if a],
            titre=str(mapped.get("Titre", "") or "").strip(),
            editeur=str(mapped.get("Editeur", "") or "").strip(),
            date=str(mapped.get("Date", "") or "").strip(),
            reference=str(mapped.get("Référence", "") or "").strip(),
            citation=str(mapped.get("Citation", "") or "").strip(),
        )

    def validate(self) -> None:
        """Vérifie les règles du schéma (lève MetadataValidationError)."""
        typologie = self.typologie.strip()
        canonical = next(
            (
                value
                for value in TYPOLOGIES
                if unicodedata.normalize("NFKC", value).lower()
                == unicodedata.normalize("NFKC", typologie).lower()
            ),
            None,
        )
        if canonical is None:
            allowed = ", ".join(TYPOLOGIES)
            msg = f"Typologie invalide : '{typologie}' (attendu : {allowed})"
            raise MetadataValidationError(msg)
        self.typologie = canonical
        if len(self.titre) > MAX_TITLE_LENGTH:
            self.titre = self.titre[:MAX_TITLE_LENGTH]
        self.auteurs = [a for a in self.auteurs if a]

    def is_empty(self, field_name: str) -> bool:
        """Vrai si le champ nommé (canonique) est vide."""
        values = {
            "Typologie": self.typologie,
            "Auteur(s)": self.auteurs,
            "Titre": self.titre,
            "Editeur": self.editeur,
            "Date": self.date,
            "Référence": self.reference,
            "Citation": self.citation,
        }
        value = values[field_name]
        return not value or value == []

    def to_dict(self) -> dict[str, object]:
        """Dictionnaire ordonné avec les 7 clés exactes du schéma."""
        return {
            "Typologie": self.typologie,
            "Auteur(s)": list(self.auteurs),
            "Titre": self.titre,
            "Editeur": self.editeur,
            "Date": self.date,
            "Référence": self.reference,
            "Citation": self.citation,
        }


@dataclass
class DocumentResult:
    """Statut d'un document traité dans un lot (RunReport, FR-032)."""

    source: str
    status: str  # "created" | "amended" | "failed"
    detail: str = ""
