""" Logging utilities for the project. """

from loguru import logger


def log(message, level="info", **kwargs):
    """Log a message to the logger."""
    extra_info = " ".join(f"{key}={value}" for key, value in kwargs.items())
    full_message = f"{message} {extra_info}".strip()

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(full_message)
