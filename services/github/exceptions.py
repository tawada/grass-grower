"""Exceptions for the package."""
import subprocess


class CommandExecutionException(Exception):
    """Base exception raised for errors in the command execution."""
    message = ""

    def __init__(self, message: str = None):
        if message is None:
            message = self.message
        super().__init__(message)


class UnknownCommandException(CommandExecutionException):
    """Exception raised for unknown commands."""


class GitException(CommandExecutionException):
    """Base exception raised for errors in the Git API."""


class GitHubException(CommandExecutionException):
    """Base exception raised for errors in the GitHub API."""


class GitHubConnectionException(GitHubException):
    """Exception raised for errors in the GitHub API connection."""
    message = "Could not resolve hostname github.com: Name or service not known"


class GitHubRepoNotFoundException(GitHubException):
    """Exception raised for errors in the GitHub API connection."""
    message = "Repository not found."


exception_keywords: dict[str, type[CommandExecutionException]] = {}
_src: list[type[CommandExecutionException]] = [
    GitHubConnectionException, GitHubRepoNotFoundException
]
for _exception in _src:
    exception_keywords[_exception.message] = _exception


def parse_exception(err: subprocess.CalledProcessError):
    """Parse exception from stderr"""
    for keyword, exception in exception_keywords.items():
        if err.stderr and keyword in err.stderr.decode():
            return exception, keyword
    return UnknownCommandException, str(err)
