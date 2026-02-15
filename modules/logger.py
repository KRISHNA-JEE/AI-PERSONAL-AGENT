"""Logging utility for AI Personal Assistant."""

import logging
import sys
from pathlib import Path

from config import settings


class UTF8Formatter(logging.Formatter):
    """Formatter that handles Unicode characters on Windows console."""
    
    def format(self, record):
        msg = super().format(record)
        if hasattr(sys.stderr, 'reconfigure'):
            try:
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass
        return msg


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with file and console handlers.

    Args:
        name: The logger name (typically __name__).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create formatters with UTF-8 support
    formatter = UTF8Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with UTF-8 encoding
    log_file = Path(settings.LOG_FILE_PATH)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler with UTF-8 support
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
