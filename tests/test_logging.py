"""
Tests for the logging module.
"""

import pytest
import logging
from pathlib import Path
from ai_assistant.modules.logging_module import Logger, get_logger


def test_logger_singleton():
    """Test that Logger implements singleton pattern."""
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2


def test_logger_initialization(tmp_path, monkeypatch):
    """Test logger initialization with custom settings."""
    log_file = tmp_path / "test.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # Reset singleton
    Logger._instance = None
    
    logger = Logger()
    assert logger._logger is not None
    assert logger._logger.name == "AIPersonalAssistant"


def test_logger_methods(tmp_path, monkeypatch):
    """Test various logging methods."""
    log_file = tmp_path / "test.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))
    
    # Reset singleton
    Logger._instance = None
    
    logger = Logger()
    
    # Test logging methods
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Verify log file was created
    assert log_file.exists()


def test_get_logger_function():
    """Test get_logger convenience function."""
    logger = get_logger()
    assert isinstance(logger, Logger)
    assert logger._logger is not None


def test_logger_log_levels(tmp_path, monkeypatch):
    """Test that log levels are properly set."""
    log_file = tmp_path / "test.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    
    # Reset singleton
    Logger._instance = None
    
    logger = Logger()
    assert logger._logger.level == logging.WARNING
