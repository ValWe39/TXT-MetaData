"""Chargement de la configuration : clé API Mistral (constitution, principe I).

La clé n'est jamais loguée, persistée ni copiée ailleurs que dans la
variable d'environnement ``MISTRAL_API_KEY``.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Erreur fatale de configuration (code retour 2)."""


def load_api_key(env_file: Path | None = None) -> str:
    """Charge la clé API Mistral depuis le .env puis l'environnement.

    Le ``.env`` est résolu depuis le répertoire courant uniquement
    (aucune remontée arborescente). Échoue rapidement avec un message
    explicite si la clé est absente (FR-018) : aucun appel réseau n'est
    tenté.
    """
    if env_file is None:
        env_file = Path(".env")
    load_dotenv(dotenv_path=env_file)
    api_key = os.environ.get("MISTRAL_API_KEY", "").strip()
    if not api_key:
        msg = (
            "MISTRAL_API_KEY absente : définissez-la dans le fichier .env "
            "à la racine du projet (voir .env.example)."
        )
        raise ConfigurationError(msg)
    return api_key
