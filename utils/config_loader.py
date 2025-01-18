"""Module for loading configuration from a JSON file."""

import json
import os
from typing import Any, Dict

from utils.logging_utils import log


def load_config(file_path: str = "") -> Dict[str, Any]:
    """Load configuration from a JSON file.

    Args:
        file_path (str): Path to the configuration file.

    Returns:
        dict: Configuration as a dictionary.
    """
    if file_path == "":
        file_path = os.getenv('CONFIG_PATH', 'config.json')
    try:
        with open(file_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        log(
            f"Configuration file {file_path} not found. Loading default configuration.",
            level="warning",
        )
        return get_default_config()
    except json.JSONDecodeError as err:
        log(
            (f"Error decoding JSON from {file_path}. "
             f"Details: {err.msg} at line {err.lineno}, column {err.colno}"),
            level="error",
        )
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Provide a default configuration as a fallback."""
    repository_path = os.getenv('REPOSITORY_PATH', 'downloads')
    return {
        "repository_path": repository_path,
        "exclude_dirs": ["__pycache__", ".git", repository_path],
        "openai_model_name": os.getenv('OPENAI_MODEL_NAME', 'gpt-4'),
    }
