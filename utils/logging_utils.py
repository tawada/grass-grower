""" Logging utilities for the project. """
import logging
from functools import wraps
from logging import getLogger


def setup_logging():
    """Setup logging for the project."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(process)d - %(threadName)s - %(message)s",
        handlers=[
            logging.FileHandler("debug.log"),  # Log to a file
            logging.StreamHandler(),  # Log to standard output
        ],
    )


def log(message, level="info", **kwargs):
    """Log a message to the logger."""
    logger = getLogger(__name__)

    extra_info = " ".join(f"{key}={value}" for key, value in kwargs.items())
    full_message = f"{message} {extra_info}".strip()

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(full_message)


def exception_handler(func):
    """Decorator to handle exceptions in a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log(f"An error occurred in {func.__name__}: {e}", level="error")
            # More sophisticated error handling can be added here

    return wrapper
