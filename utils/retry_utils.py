"""
This file contains the retry_on_exception decorator
which can be used to retry a function in case of
a specific exception.
"""

import functools
import logging
from time import sleep


def retry_on_exception(exception_to_check,
                       tries=4,
                       delay=3,
                       backoff=2,
                       logger=None):
    """
    Decorator to retry a function in case of a specific exception.

    Args:
        exception_to_check: Exception to check.
        tries: Number of tries.
        delay: Initial delay in seconds.
        backoff: Backoff factor.
        logger: Logger to use.

    Returns:
        Decorator function.
    """

    def decorator_retry(func):

        @functools.wraps(func)
        def func_retry(*args, **kwargs):
            _logger = logger or logging.getLogger(__name__)
            mtries, mdelay = tries, delay

            while mtries > 0:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as err:
                    _logger.warning(
                        f"{str(err)}, retrying in {mdelay} seconds...")
                    sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)

        return func_retry

    return decorator_retry
