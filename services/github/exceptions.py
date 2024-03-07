"""Exceptions for the package."""
import subprocess

exception_keywords = {
    "Could not resolve hostname github.com: Name or service not known":
    RuntimeError,
    "Repository not found.": ValueError,
}


def parse_exception(err: subprocess.CalledProcessError):
    """Parse exception from stderr"""
    for keyword, exception in exception_keywords.items():
        if err.stderr and keyword in err.stderr.decode():
            return exception, keyword
    return RuntimeError, str(err)
