"""
Logging Module for AI Personal Assistant

This module provides a centralized logging system for all components of the assistant.
It supports file and console logging with configurable log levels.
"""

import logging
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Logger:
    """
    Centralized logging system for the AI Personal Assistant.
    
    This class implements a singleton pattern to ensure consistent logging
    across all modules.
    
    Attributes:
        _instance (Logger): Singleton instance of the Logger class
        _logger (logging.Logger): Internal logger instance
    """
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        """
        Create a singleton instance of the Logger class.
        
        Returns:
            Logger: The singleton Logger instance
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self) -> None:
        """
        Initialize the logging configuration.
        
        Sets up file and console handlers with appropriate formatting
        and log levels based on environment variables.
        """
        # Get configuration from environment
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_file = os.getenv('LOG_FILE', 'logs/assistant.log')
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self._logger = logging.getLogger('AIPersonalAssistant')
        self._logger.setLevel(getattr(logging, log_level))
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        Get the logger instance.
        
        Returns:
            logging.Logger: The configured logger instance
        """
        return self._logger
    
    def debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message (str): The message to log
        """
        self._logger.debug(message)
    
    def info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message (str): The message to log
        """
        self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message (str): The message to log
        """
        self._logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """
        Log an error message.
        
        Args:
            message (str): The message to log
            exc_info (bool): Include exception info if True
        """
        self._logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False) -> None:
        """
        Log a critical message.
        
        Args:
            message (str): The message to log
            exc_info (bool): Include exception info if True
        """
        self._logger.critical(message, exc_info=exc_info)


# Create a global logger instance
logger = Logger()


def get_logger() -> Logger:
    """
    Get the global logger instance.
    
    Returns:
        Logger: The global Logger instance
    """
    return logger
