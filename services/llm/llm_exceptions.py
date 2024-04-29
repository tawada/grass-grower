"""Exceptions for the package."""
import functools


class LLMException(Exception):
    """Base exception raised for errors in the LLM package."""

    message = ""

    def __init__(self, message: str = None):
        if message is None:
            message = self.message
        super().__init__(message)


class UnknownLLMException(LLMException):
    """Exception raised for unknown errors in the LLM package."""


class NotFoundAPIKeyException(LLMException):
    """Exception raised for errors in the LLM package."""

    message = "API key must"


def retry_handler(retry_or_func=0):
    """Decorator to retry a function call."""

    if callable(retry_or_func):
        func = retry_or_func
        return retry_handler()(func)
    retry = retry_or_func

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(retry + 1):
                try:
                    return func(*args, **kwargs)
                except LLMException as err:
                    original_err = err
            raise original_err

        return wrapper

    return decorator
