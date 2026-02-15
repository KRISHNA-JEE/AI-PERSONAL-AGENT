"""
Pytest configuration and fixtures for AI Personal Assistant tests.
"""

import pytest
import os
import json
from pathlib import Path


@pytest.fixture
def temp_env_file(tmp_path, monkeypatch):
    """
    Create a temporary .env file for testing.
    
    Args:
        tmp_path: Pytest temporary directory fixture
        monkeypatch: Pytest monkeypatch fixture
        
    Returns:
        Path to temporary .env file
    """
    env_file = tmp_path / ".env"
    env_content = """
OPENAI_API_KEY=test_api_key
LOG_LEVEL=DEBUG
LOG_FILE=logs/test.log
REMINDERS_FILE=data/test_reminders.json
"""
    env_file.write_text(env_content)
    
    # Set environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "test.log"))
    monkeypatch.setenv("REMINDERS_FILE", str(tmp_path / "test_reminders.json"))
    
    return env_file


@pytest.fixture
def mock_reminders_file(tmp_path, monkeypatch):
    """
    Create a temporary reminders file for testing.
    
    Args:
        tmp_path: Pytest temporary directory fixture
        monkeypatch: Pytest monkeypatch fixture
        
    Returns:
        Path to temporary reminders file
    """
    reminders_file = tmp_path / "reminders.json"
    monkeypatch.setenv("REMINDERS_FILE", str(reminders_file))
    return reminders_file


@pytest.fixture
def sample_reminders():
    """
    Sample reminder data for testing.
    
    Returns:
        List of sample reminder dictionaries
    """
    return [
        {
            "id": 1,
            "title": "Test Reminder 1",
            "description": "Test description",
            "due_date": "2026-12-31",
            "priority": "high",
            "completed": False,
            "created_at": "2026-01-01T00:00:00",
            "completed_at": None
        },
        {
            "id": 2,
            "title": "Test Reminder 2",
            "description": "",
            "due_date": None,
            "priority": "medium",
            "completed": True,
            "created_at": "2026-01-01T00:00:00",
            "completed_at": "2026-01-02T00:00:00"
        }
    ]
