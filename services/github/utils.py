"""Utility functions for the GitHub API."""
import os


def make_owner_dir(base_path: str, repo: str):
    """Create a directory for the repository owner."""
    owner = repo[:repo.index("/")]
    path = os.path.join(base_path, owner)
    os.makedirs(path, exist_ok=True)
