""" Logging utilities for the project. """
from loguru import logger


def setup_logging():
    """Setup logging for the project."""
    logger.remove()  # Remove default handler
    logger.add(
        # Log file path
        "debug.log",
        # New file is created each time the log file reaches 100 MB
        rotation="100 MB",
        # Logs older than 10 days are deleted
        retention="10 days",
        level="INFO")
    # You can also add stdout logging with custom format
    logger.add(sink=lambda msg: print(msg, flush=True),
               format="{time} - {level} - {message}",
               level="INFO")


def log(message, level="info", **kwargs):
    """Log a message to the logger."""
    extra_info = " ".join(f"{key}={value}" for key, value in kwargs.items())
    full_message = f"{message} {extra_info}".strip()

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(full_message)
