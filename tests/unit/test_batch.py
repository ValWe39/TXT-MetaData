"""Tests unitaires du groupement par lots (T024, FR-020)."""

from txt_metadata.batch import run_batch


def test_taille_zero_sequentiel():
    order: list[int] = []

    def worker(value: int) -> int:
        order.append(value)
        return value * 2

    results = run_batch(list(range(5)), worker, batch_size=0)
    assert results == [0, 2, 4, 6, 8]
    assert order == [0, 1, 2, 3, 4]


def test_lots_parallels_ordre_preserve():
    def worker(value: int) -> int:
        return value + 1

    results = run_batch(list(range(10)), worker, batch_size=3)
    assert results == list(range(1, 11))


def _identity(value: int) -> int:
    """Worker trivial pour les tests."""
    return value


def test_lot_vide():
    assert run_batch([], _identity, batch_size=0) == []
    assert run_batch([], _identity, batch_size=25) == []
