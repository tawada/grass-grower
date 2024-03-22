"""Utility functions for logic operations."""
import os

from config import config


def enumarate_file_paths(repo_path: str, target_extension: list[str]):
    """Enumerate file paths in the repository."""

    for root, dirs, files in os.walk(repo_path):
        # Limit the directories to explore
        dirs[:] = list(filter(is_target_dir, dirs))
        for file_name in files:
            if is_target_file(file_name, target_extension):
                yield os.path.join(root, file_name)


def is_target_dir(dir_name: str):
    """Check if the directory is not a target directory."""
    return dir_name not in config["exclude_dirs"] and not dir_name.startswith(
        ".")


def is_target_file(file_name: str, target_extension: list[str]):
    """Check if the file is a target file."""
    return file_name.endswith(tuple(target_extension))
