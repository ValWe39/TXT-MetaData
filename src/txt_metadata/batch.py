"""Groupement des requêtes par lots (FR-020, R1).

``--taille-batch`` : les appels LLM des documents d'un même lot sont
envoyés en parallèle par groupes de N (défaut 25) ; chaque requête
reste un appel chat/completions individuel. 0 = traitement séquentiel,
une requête à la fois.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def run_batch(
    items: list[T],
    worker: Callable[[T], R],
    *,
    batch_size: int,
) -> list[R]:
    """Exécute ``worker`` sur chaque élément, par lots de taille
    ``batch_size`` (0 = séquentiel). L'ordre des résultats suit l'ordre
    des éléments."""
    if batch_size <= 0:
        return [worker(item) for item in items]
    results: list[R | None] = [None] * len(items)
    for start in range(0, len(items), batch_size):
        chunk = items[start : start + batch_size]
        with ThreadPoolExecutor(max_workers=len(chunk)) as pool:
            for index, result in zip(
                range(start, start + len(chunk)),
                pool.map(worker, chunk),
            ):
                results[index] = result
    return [r for r in results if r is not None]
