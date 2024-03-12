"""Utilities for working with GitHub repositories."""
import os


def exists_repo(base_path: str, repo: str) -> bool:
    """Check if the repository exists."""
    path = os.path.join(base_path, repo)
    return os.path.exists(path)


def make_owner_dir(base_path: str, repo: str):
    """Create a directory for the repository owner."""
    owner = repo[:repo.index("/")]
    path = os.path.join(base_path, owner)
    os.makedirs(path, exist_ok=True)
