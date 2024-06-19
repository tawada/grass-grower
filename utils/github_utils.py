"""Utilities for working with GitHub repositories."""
import os
import subprocess

from config import config
from services.github import exceptions
from utils.logging_utils import log

DEFAULT_PATH = config["repository_path"]


def exec_git_command(
        repo: str,
        command: list[str],
        capture_output: bool = False) -> subprocess.CompletedProcess:
    """
    Execute a shell command within the specified git repository path.
    If capture_output is True, the function returns a subprocess.CompletedProcess object.
    Otherwise, it returns a boolean indicating success.

    Returns:
        Union[bool, subprocess.CompletedProcess]: The result of the subprocess run or success flag.
    """
    repo_path = os.path.join(DEFAULT_PATH, repo)
    try:
        complete_process = subprocess.run(
            command,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            cwd=repo_path,
            check=True,
        )
        return complete_process
    except subprocess.CalledProcessError as err:
        shorted_commands = " ".join(command)[:50]
        log(
            f"Command {shorted_commands} failed with error ({err.returncode}): {err}",
            level="exception",
        )
        exception, error_message = exceptions.parse_exception(err)
        raise exception(error_message) from err


def exec_git_command_and_response_bool(repo: str,
                                       command: list[str],
                                       capture_output: bool = False) -> bool:
    """This function executes a shell command within the specified git repository path."""
    return bool(exec_git_command(repo, command, capture_output))


def exists_repo(base_path: str, repo: str) -> bool:
    """Check if the repository exists."""
    path = os.path.join(base_path, repo)
    return os.path.exists(path)


def make_owner_dir(base_path: str, repo: str):
    """Create a directory for the repository owner."""
    owner = repo[:repo.index("/")]
    path = os.path.join(base_path, owner)
    os.makedirs(path, exist_ok=True)
