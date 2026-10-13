"""Compteur d'occurrence persistant (FR-023 à FR-025).

``counter.txt`` à la racine de l'outil contient uniquement le dernier
numéro utilisé (4 chiffres). Écriture atomique après chaque document
produit : un numéro consommé n'est jamais réutilisé, même en cas
d'interruption. Cycle : 0001…9999 puis 0000, puis nouveau cycle.
"""

from __future__ import annotations

import os
import re
import threading
from pathlib import Path

_COUNTER_RE = re.compile(r"^\d{1,4}$")
_CYCLE = 10_000
_LOCK = threading.Lock()


class CounterError(Exception):
    """Fichier de compteur illisible ou corrompu (erreur fatale, code 2)."""


def _parse(content: str) -> int:
    text = content.strip()
    if not _COUNTER_RE.match(text):
        msg = f"Fichier de compteur corrompu ou illisible : '{content[:50]}'"
        raise CounterError(msg)
    return int(text)


def load(path: Path) -> int:
    """Retourne le dernier numéro utilisé (0 si le fichier est absent)."""
    if not path.exists():
        return 0
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"Fichier de compteur illisible : {exc}"
        raise CounterError(msg) from exc
    return _parse(content)


def next_occurrence(path: Path) -> str:
    """Incrémente le compteur et retourne le nouveau numéro à 4 chiffres.

    Absent → 0001 (premier usage) ; après 9999 → 0000. L'écriture est
    atomique (fichier temporaire + remplacement) et immédiate. L'appel
    est protégé par un verrou : en batch parallèle, chaque numéro est
    attribué à l'instant exact de la création d'un JSON, sans doublon
    (FR-023) ; un document en échec n'en consomme jamais.
    """
    with _LOCK:
        current = load(path)
        value = (current + 1) % _CYCLE
        token = f"{value:04d}"
        tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
        tmp.write_text(token, encoding="utf-8")
        os.replace(tmp, path)
        return token
