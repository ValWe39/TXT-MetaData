"""Découverte des entrées et appariement texte/JSON (FR-001, FR-027).

Multi-entrées transparent : fichiers `.md`/`.txt`, dossiers parcourus
récursivement (sous-dossiers inclus), formats inattendus ignorés
silencieusement. Appariement : par préfixe de 8 caractères normalisés,
ou paire unique dans un sous-dossier.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .output import load_existing, output_prefix

SUPPORTED_EXTENSIONS = {".md", ".txt"}


@dataclass
class InputDocument:
    """Document texte d'entrée (data-model.md)."""

    path: Path
    paired_json: Path | None = None


def _sort_key(path: Path) -> str:
    """Clé de tri déterministe des documents (insensible à la casse)."""
    return str(path).lower()


def _iter_supported(paths: list[Path]) -> list[Path]:
    """Liste triée, dédupliquée, des fichiers texte supportés."""
    found: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                found.append(path)
        elif path.is_dir():
            for candidate in sorted(path.rglob("*")):
                if (
                    candidate.is_file()
                    and candidate.suffix.lower() in SUPPORTED_EXTENSIONS
                ):
                    resolved = candidate.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        found.append(candidate)
    return sorted(found, key=_sort_key)


def discover(paths: list[Path]) -> list[InputDocument]:
    """Découvre les documents d'entrée (fichiers ou dossiers, FR-001)."""
    return [InputDocument(path=p) for p in _iter_supported(paths)]


def pair_documents(documents: list[InputDocument]) -> None:
    """Apparie chaque document à un JSON de sortie existant (FR-027).

    Priorité : préfixe de 8 caractères normalisés unique ; sinon paire
    unique du sous-dossier ; sinon document traité seul.
    """
    by_dir: dict[Path, list[InputDocument]] = {}
    for doc in documents:
        by_dir.setdefault(doc.path.parent, []).append(doc)
    for directory, docs in by_dir.items():
        jsons = [
            candidate
            for candidate in sorted(directory.glob("*.json"))
            if load_existing(candidate) is not None
        ]
        for doc in docs:
            prefix = output_prefix(doc.path)
            matches = [j for j in jsons if j.stem.startswith(prefix)]
            if len(matches) == 1:
                doc.paired_json = matches[0]
            elif len(docs) == 1 and len(jsons) == 1:
                doc.paired_json = jsons[0]


def read_text(path: Path) -> str:
    """Lit un document texte : UTF-8, repli latin-1 tolérant."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")
