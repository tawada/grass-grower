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


class GitBranchAlreadyExistsException(GitException):
    """Exception raised for errors in the Git API."""

    # fatal: a branch named '<branch_name>' already exists
    message = "already exists"


class GitNothingToCommitException(GitException):
    """Exception raised for errors in the Git API."""

    message = "nothing to commit, working tree clean"


class GitNoRefFetchedException(GitException):
    """
    Exception raised for errors in the Git API.

    Your configuration specifies to merge with the ref 'refs/heads/
    <branch-name>' from the remote, but no such ref was fetched.
    """

    message = "no such ref was fetched"


class GitNoRemoteException(GitException):
    """Exception raised for errors in the Git API."""

    message = "No remote"


class GitNoUpstreamException(GitException):
    """Exception raised for errors in the Git API."""

    message = "No upstream"


class GitNoBranchException(GitException):
    """Exception raised for errors in the Git API."""

    message = "No branch"


class GitHubException(CommandExecutionException):
    """Base exception raised for errors in the GitHub API."""


class GitHubConnectionException(GitHubException):
    """Exception raised for errors in the GitHub API connection."""

    message = "Could not resolve hostname github.com"


class GitHubRepoNotFoundException(GitHubException):
    """Exception raised for errors in the GitHub API connection."""

    message = "Repository not found."


class GitHubNoChangesException(GitHubException):
    """Exception raised for errors in the GitHub API connection."""

    message = "No changes"


class GitHubNoPullRequestException(GitHubException):
    """Exception raised for errors in the GitHub API connection."""

    message = "No pull request found"


class GitHubNoIssuesException(GitHubException):
    """Exception raised for errors in the GitHub API connection."""

    message = "No issues found"


exception_keywords: dict[str, type[CommandExecutionException]] = {}
_src: list[type[CommandExecutionException]] = [
    GitBranchAlreadyExistsException,
    GitNothingToCommitException,
    GitNoRefFetchedException,
    GitHubConnectionException,
    GitHubRepoNotFoundException,
]
for _exception in _src:
    exception_keywords[_exception.message] = _exception


def parse_exception(err: subprocess.CalledProcessError):
    """Parse exception from stderr"""
    for keyword, exception in exception_keywords.items():
        if err.stderr and keyword in err.stderr.decode():
            return exception, keyword
    return UnknownCommandException, str(err)
