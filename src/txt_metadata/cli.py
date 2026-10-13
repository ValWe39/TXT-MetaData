"""Interface en ligne de commande (FR-028 à FR-030).

Commande générale : ``txt-metadata [OPTIONS] CHEMIN...``. Options :
``--choix`` (alias du modèle LLM), ``--taille-batch`` (0–100),
``--retry-occurences`` (0–10), ``--retry-time`` (1–10 s),
``--output-folder``, ``--temperature-llm`` (0–1). Toute valeur hors
bornes est rejetée avec un message explicite avant tout traitement.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from .extract import DEFAULT_MODEL_ALIAS, MODELS


class CliError(Exception):
    """Erreur d'options CLI : échec rapide, code retour 2."""


@dataclass
class Options:
    """Options validées d'une exécution."""

    paths: list[Path]
    model_alias: str
    batch_size: int
    retries: int
    retry_time: int
    output_folder: Path
    temperature: float


def _bounded_int(value: str, *, minimum: int, maximum: int, label: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        msg = f"{label} : valeur entière attendue, reçu '{value}'"
        raise CliError(msg) from exc
    if not minimum <= parsed <= maximum:
        msg = f"{label} : {parsed} hors bornes (attendu entre {minimum} et {maximum})"
        raise CliError(msg)
    return parsed


def _bounded_float(value: str, *, minimum: float, maximum: float, label: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        msg = f"{label} : valeur décimale attendue, reçu '{value}'"
        raise CliError(msg) from exc
    if not minimum <= parsed <= maximum:
        msg = f"{label} : {parsed} hors bornes (attendu entre {minimum} et {maximum})"
        raise CliError(msg)
    return parsed


def _model_alias(value: str) -> str:
    if value not in MODELS:
        allowed = ", ".join(sorted(MODELS))
        msg = f"--choix : modèle inconnu '{value}' (attendu parmi : {allowed})"
        raise CliError(msg)
    return value


def build_parser() -> argparse.ArgumentParser:
    """Construit le parseur d'arguments."""
    parser = argparse.ArgumentParser(
        prog="txt-metadata",
        description=(
            "Extraction de métadonnées de documents texte (.md/.txt) "
            "via l'API Mistral AI."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Fichier(s) .md/.txt ou dossier(s) à traiter.",
    )
    parser.add_argument(
        "--choix",
        default=DEFAULT_MODEL_ALIAS,
        help="Modèle LLM : large4, large, medium, small (défaut), 14b, 8b, 3b, zai.",
    )
    parser.add_argument(
        "--taille-batch",
        default="25",
        help="Taille des lots de requêtes, 0 à 100 (défaut 25 ; 0 = sans lot).",
    )
    parser.add_argument(
        "--retry-occurences",
        default="3",
        help="Nombre de retries par appel en échec, 0 à 10 (défaut 3).",
    )
    parser.add_argument(
        "--retry-time",
        default="3",
        help="Délai en secondes avant le premier retry, 1 à 10 (défaut 3).",
    )
    parser.add_argument(
        "--output-folder",
        default="output",
        help="Dossier de sortie (défaut : output à la racine du projet).",
    )
    parser.add_argument(
        "--temperature-llm",
        default="0",
        help="Température d'appel du LLM, 0 à 1 (défaut 0).",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> Options:
    """Parse et valide les arguments ; lève CliError si invalide."""
    args = build_parser().parse_args(argv)
    options = Options(
        paths=list(args.paths),
        model_alias=_model_alias(args.choix),
        batch_size=_bounded_int(
            args.taille_batch, minimum=0, maximum=100, label="--taille-batch"
        ),
        retries=_bounded_int(
            args.retry_occurences, minimum=0, maximum=10, label="--retry-occurences"
        ),
        retry_time=_bounded_int(
            args.retry_time, minimum=1, maximum=10, label="--retry-time"
        ),
        output_folder=Path(args.output_folder),
        temperature=_bounded_float(
            args.temperature_llm, minimum=0.0, maximum=1.0, label="--temperature-llm"
        ),
    )
    missing = [str(p) for p in options.paths if not p.exists()]
    if missing:
        msg = f"Chemin(s) introuvable(s) : {', '.join(missing)}"
        raise CliError(msg)
    return options
