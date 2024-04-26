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
