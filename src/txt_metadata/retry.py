"""Retry exponentiel pour les appels API (FR-019).

Délai initial multiplié par 2 à chaque essai (3, 6, 12 s par défaut),
dans la limite du nombre de retries configuré. Les erreurs client
définitives (4xx hors 408/429) ne sont pas rejouées.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def _is_retryable(exc: Exception) -> bool:
    """Vrai si l'erreur mérite un retry (transitoire ou inconnue)."""
    status = getattr(exc, "status_code", None)
    return not (
        isinstance(status, int) and 400 <= status < 500 and status not in (408, 429)
    )


def with_retry(
    func: Callable[[], T],
    *,
    retries: int = 3,
    initial_delay: float = 3.0,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Exécute ``func`` avec backoff exponentiel.

    ``retries`` = nombre de nouveaux essais après l'échec initial
    (3 par défaut : 4 tentatives au total, délais 3, 6 puis 12 s).
    ``retries = 0`` = aucune replays.
    """
    attempt = 0
    while True:
        try:
            return func()
        except Exception as exc:
            if attempt >= retries or not _is_retryable(exc):
                raise
            if sleep is not None:
                sleep(initial_delay * (2**attempt))
            attempt += 1
