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


class LLMJSONParseException(LLMException):
    """Exception raised for errors in the LLM package."""

    message = "Failed to parse JSON response."


def retry_wrapper(func, retry: int, args, kwargs):
    """Retry a function call."""

    for _ in range(retry + 1):
        try:
            return func(*args, **kwargs)
        except LLMException as err:
            original_err = err
    raise original_err


def get_retry_decorator(retry: int):
    """Get a retry decorator with a specified number of retries."""

    def retry_decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry_wrapper(func, retry, args, kwargs)

        return wrapper

    return retry_decorator


def retry_handler(retry_or_func=0):
    """Decorator to retry a function call."""

    if callable(retry_or_func):
        func = retry_or_func
        return retry_handler()(func)
    retry = retry_or_func
    return get_retry_decorator(retry)
