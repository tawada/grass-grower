"""Utility functions for logic operations."""
import os

from config import config


def enumarate_file_paths(repo_path: str, target_extension: list[str]):
    """Enumerate file paths in the repository."""

    for root, dirs, files in os.walk(repo_path):
        # Limit the directories to explore
        dirs[:] = [
            d for d in dirs
            if d not in config["exclude_dirs"] and not d.startswith(".")
            if not d.startswith(".") and not d.startswith("_")
            and not d.startswith("venv")
        ]
        for file in files:
            if file.endswith(tuple(target_extension)):
                yield os.path.join(root, file)
