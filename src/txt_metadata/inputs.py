"""Découverte des entrées et appariement texte/JSON (FR-001, FR-027).

Multi-entrées transparent : fichiers `.md`/`.txt`, dossiers parcourus
récursivement (sous-dossiers inclus), formats inattendus ignorés
silencieusement. Appariement : par préfixe reconnu dès 8 caractères
normalisés et départagé jusqu'à 20, ou paire unique dans un sous-dossier.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .output import load_existing, output_prefix, simplify_accents

SUPPORTED_EXTENSIONS = {".md", ".txt"}

_MATCH_MIN = 8
_MATCH_MAX = 20


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


def common_prefix_length(document: InputDocument, json_stem: str) -> int:
    """Préfixe commun le plus long entre le nom normalisé du document et
    le nom du JSON (normalisé : espaces remplacées par ``_``, accents
    simplifiés), plafonné à ``_MATCH_MAX`` caractères (FR-004)."""
    stem = simplify_accents(json_stem.replace(" ", "_"))
    name = output_prefix(document.path)
    length = 0
    for char_doc, char_json in zip(name, stem):
        if char_doc != char_json:
            break
        length += 1
        if length >= _MATCH_MAX:
            break
    return length


def pair_documents(documents: list[InputDocument]) -> None:
    """Apparie chaque document à un JSON de sortie existant (FR-027).

    Priorité : candidats reconnus dès 8 caractères normalisés, départagés
    par le préfixe commun le plus long (jusqu'à 20) ; sinon paire unique
    du sous-dossier ; sinon document traité seul.
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
            name = output_prefix(doc.path)
            threshold = min(_MATCH_MIN, len(name))
            candidates = [(common_prefix_length(doc, j.stem), j) for j in jsons]
            matches = [(length, j) for length, j in candidates if length >= threshold]
            if len(matches) == 1:
                doc.paired_json = matches[0][1]
            elif len(matches) > 1:
                # FR-004 : le candidat le plus proche est retenu ; en cas
                # d'égalité parfaite, le document est traité seul (FR-005)
                best = max(length for length, _ in matches)
                best_matches = [j for length, j in matches if length == best]
                if len(best_matches) == 1:
                    doc.paired_json = best_matches[0]
            elif len(docs) == 1 and len(jsons) == 1:
                doc.paired_json = jsons[0]


def read_text(path: Path) -> str:
    """Lit un document texte : UTF-8, repli latin-1 tolérant."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")
