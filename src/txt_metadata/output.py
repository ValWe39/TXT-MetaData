"""Nommage, écriture et amendement des sorties JSON (FR-021, FR-022,
FR-026).

Nouveau fichier : ``<20 premiers caractères normalisés du nom d'entrée>-
<numéro>.json`` dans le dossier de sortie (créé automatiquement).
Amendement : fusion sur place, sans nouveau numéro ni copie.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from .models import FIELD_ORDER, MetadataOutput, MetadataValidationError

_NAME_PREFIX_LENGTH = 20


def simplify_accents(text: str) -> str:
    """Remplace les caractères accentués par leur équivalent ASCII."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def output_prefix(input_path: Path) -> str:
    """20 premiers caractères du nom du fichier (sans extension) :
    espaces remplacées par ``_``, accents simplifiés (FR-022) ; nom
    complet si plus court."""
    base = input_path.stem
    base = base.replace(" ", "_")
    base = simplify_accents(base)
    return base[:_NAME_PREFIX_LENGTH]


def build_output_name(input_path: Path, occurrence: str) -> str:
    """Nom du fichier de sortie : ``<préfixe>-<NNNN>.json``."""
    return f"{output_prefix(input_path)}-{occurrence}.json"


def write_new(
    metadata: MetadataOutput,
    *,
    output_dir: Path,
    input_path: Path,
    occurrence: str,
) -> Path:
    """Écrit un nouveau JSON dans le dossier de sortie (créé si absent)."""
    metadata.validate()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / build_output_name(input_path, occurrence)
    target.write_text(
        json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target


def load_existing(path: Path) -> MetadataOutput | None:
    """Charge un JSON existant ; ``None`` si le format n'est pas reconnu."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    keys = {str(k) for k in data}
    if not keys.issubset(set(FIELD_ORDER)):
        return None
    if "Typologie" not in keys:
        return None
    metadata = MetadataOutput.from_dict(data)
    try:
        metadata.validate()
    except MetadataValidationError:
        return None
    return metadata


def merge_amendment(
    existing: MetadataOutput,
    new: MetadataOutput,
    *,
    high_confidence: bool,
) -> MetadataOutput:
    """Fusionne les métadonnées pour un amendement (FR-026).

    Champs vides de l'existant complétés en priorité par les nouvelles
    valeurs ; champs déjà remplis remplacés uniquement si le nouveau
    résultat est à haut degré d'assurance.
    """
    merged = MetadataOutput(
        typologie=existing.typologie,
        auteurs=list(existing.auteurs),
        titre=existing.titre,
        editeur=existing.editeur,
        date=existing.date,
        reference=existing.reference,
        citation=existing.citation,
    )
    # la typologie « Autre » est le repli : elle peut toujours être
    # affinée par une extraction valide
    if existing.typologie == "Autre" and new.typologie != "Autre":
        merged.typologie = new.typologie
    candidates: list[tuple[str, object]] = [
        ("Auteur(s)", new.auteurs),
        ("Titre", new.titre),
        ("Editeur", new.editeur),
        ("Date", new.date),
        ("Référence", new.reference),
        ("Citation", new.citation),
    ]
    for name, value in candidates:
        if existing.is_empty(name) and value or high_confidence and value:
            setattr(
                merged,
                {
                    "Auteur(s)": "auteurs",
                    "Titre": "titre",
                    "Editeur": "editeur",
                    "Date": "date",
                    "Référence": "reference",
                    "Citation": "citation",
                }[name],
                list(value) if isinstance(value, list) else value,
            )
    merged.validate()
    return merged


def amend_in_place(path: Path, merged: MetadataOutput) -> None:
    """Réécrit le JSON existant à son emplacement d'origine (FR-026)."""
    path.write_text(
        json.dumps(merged.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
