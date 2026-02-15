"""
Tests for the reminders module.
"""

import pytest
import json
from pathlib import Path
from ai_assistant.modules.reminders import RemindersManager, add_reminder, list_reminders


def test_reminders_manager_initialization(mock_reminders_file):
    """Test RemindersManager initialization."""
    manager = RemindersManager()
    assert manager.reminders == []
    assert Path(manager.reminders_file).exists()


def test_add_reminder(mock_reminders_file):
    """Test adding a new reminder."""
    manager = RemindersManager()
    
    reminder = manager.add_reminder(
        title="Test Task",
        description="Test description",
        priority="high"
    )
    
    assert reminder["id"] == 1
    assert reminder["title"] == "Test Task"
    assert reminder["priority"] == "high"
    assert reminder["completed"] is False
    assert len(manager.reminders) == 1


def test_generate_id(mock_reminders_file):
    """Test ID generation."""
    manager = RemindersManager()
    
    # First reminder should get ID 1
    r1 = manager.add_reminder("Task 1")
    assert r1["id"] == 1
    
    # Second reminder should get ID 2
    r2 = manager.add_reminder("Task 2")
    assert r2["id"] == 2


def test_get_reminders_filter_completed(mock_reminders_file, sample_reminders):
    """Test filtering reminders by completion status."""
    manager = RemindersManager()
    manager.reminders = sample_reminders
    
    # Get only active reminders
    active = manager.get_reminders(show_completed=False)
    assert len(active) == 1
    assert active[0]["completed"] is False
    
    # Get all reminders
    all_reminders = manager.get_reminders(show_completed=True)
    assert len(all_reminders) == 2


def test_get_reminders_filter_priority(mock_reminders_file, sample_reminders):
    """Test filtering reminders by priority."""
    manager = RemindersManager()
    manager.reminders = sample_reminders
    
    high_priority = manager.get_reminders(priority="high")
    assert len(high_priority) == 1
    assert high_priority[0]["priority"] == "high"


def test_complete_reminder(mock_reminders_file):
    """Test completing a reminder."""
    manager = RemindersManager()
    reminder = manager.add_reminder("Test Task")
    
    success = manager.complete_reminder(reminder["id"])
    assert success is True
    
    # Check that reminder is marked as completed
    updated = manager.get_reminders(show_completed=True)[0]
    assert updated["completed"] is True
    assert updated["completed_at"] is not None


def test_complete_nonexistent_reminder(mock_reminders_file):
    """Test completing a reminder that doesn't exist."""
    manager = RemindersManager()
    
    success = manager.complete_reminder(999)
    assert success is False


def test_delete_reminder(mock_reminders_file):
    """Test deleting a reminder."""
    manager = RemindersManager()
    reminder = manager.add_reminder("Test Task")
    
    success = manager.delete_reminder(reminder["id"])
    assert success is True
    assert len(manager.reminders) == 0


def test_delete_nonexistent_reminder(mock_reminders_file):
    """Test deleting a reminder that doesn't exist."""
    manager = RemindersManager()
    
    success = manager.delete_reminder(999)
    assert success is False


def test_format_reminders(mock_reminders_file):
    """Test formatting reminders for display."""
    manager = RemindersManager()
    manager.add_reminder("Task 1", priority="high")
    manager.add_reminder("Task 2", priority="low")
    
    formatted = manager.format_reminders()
    assert "Task 1" in formatted
    assert "Task 2" in formatted
    assert "!!!" in formatted  # High priority symbol
    assert "!" in formatted  # Low priority symbol


def test_format_empty_reminders(mock_reminders_file):
    """Test formatting when no reminders exist."""
    manager = RemindersManager()
    
    formatted = manager.format_reminders()
    assert "No active reminders" in formatted


def test_persistence(mock_reminders_file):
    """Test that reminders are persisted to file."""
    # Create and save a reminder
    manager1 = RemindersManager()
    manager1.add_reminder("Persistent Task")
    
    # Create new instance and verify data is loaded
    manager2 = RemindersManager()
    assert len(manager2.reminders) == 1
    assert manager2.reminders[0]["title"] == "Persistent Task"


def test_convenience_functions(mock_reminders_file):
    """Test convenience functions."""
    result = add_reminder("Test Task", priority="high")
    assert "Reminder added" in result
    
    listing = list_reminders()
    assert "Test Task" in listing
