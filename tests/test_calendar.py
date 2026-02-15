"""
Tests for the calendar module.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from ai_assistant.modules.calendar import CalendarManager, get_calendar_events


def test_calendar_manager_initialization():
    """Test CalendarManager initialization."""
    manager = CalendarManager()
    assert manager.service is None
    assert manager.credentials_file is not None


def test_authenticate_without_credentials_file(tmp_path, monkeypatch):
    """Test authentication fails without credentials file."""
    monkeypatch.setenv("CALENDAR_CREDENTIALS_FILE", str(tmp_path / "nonexistent.json"))
    
    manager = CalendarManager()
    
    with pytest.raises(FileNotFoundError, match="Calendar credentials file"):
        manager.authenticate()


def test_get_upcoming_events_not_authenticated():
    """Test getting events without authentication."""
    manager = CalendarManager()
    
    with pytest.raises(Exception, match="Not authenticated"):
        manager.get_upcoming_events()


@patch('ai_assistant.modules.calendar.build')
@patch('ai_assistant.modules.calendar.Credentials')
def test_get_upcoming_events_success(mock_creds, mock_build):
    """Test successfully fetching upcoming events."""
    # Setup mock service
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    # Mock events list response
    now = datetime.utcnow()
    event_time = (now + timedelta(days=1)).isoformat() + 'Z'
    
    mock_service.events().list().execute.return_value = {
        'items': [
            {
                'id': '123',
                'summary': 'Test Event 1',
                'start': {'dateTime': event_time},
                'end': {'dateTime': event_time},
                'location': 'Test Location',
                'description': 'Test Description',
                'status': 'confirmed'
            },
            {
                'id': '456',
                'summary': 'Test Event 2',
                'start': {'dateTime': event_time},
                'end': {'dateTime': event_time},
                'location': '',
                'description': '',
                'status': 'confirmed'
            }
        ]
    }
    
    manager = CalendarManager()
    manager.service = mock_service
    
    events = manager.get_upcoming_events(max_results=10, days_ahead=7)
    
    assert len(events) == 2
    assert events[0]['summary'] == 'Test Event 1'
    assert events[0]['location'] == 'Test Location'


@patch('ai_assistant.modules.calendar.build')
@patch('ai_assistant.modules.calendar.Credentials')
def test_get_upcoming_events_empty(mock_creds, mock_build):
    """Test fetching events when none exist."""
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    mock_service.events().list().execute.return_value = {'items': []}
    
    manager = CalendarManager()
    manager.service = mock_service
    
    events = manager.get_upcoming_events()
    assert events == []


def test_format_events_empty():
    """Test formatting empty events list."""
    manager = CalendarManager()
    formatted = manager.format_events([])
    assert "No upcoming events" in formatted


def test_format_events():
    """Test formatting events."""
    manager = CalendarManager()
    
    now = datetime.utcnow()
    event_time = (now + timedelta(days=1)).isoformat()
    
    events = [
        {
            'summary': 'Meeting',
            'start': event_time,
            'end': event_time,
            'location': 'Office',
            'description': 'Important meeting'
        },
        {
            'summary': 'Lunch',
            'start': event_time,
            'end': event_time,
            'location': '',
            'description': ''
        }
    ]
    
    formatted = manager.format_events(events)
    
    assert "2 upcoming event" in formatted
    assert "Meeting" in formatted
    assert "Office" in formatted
    assert "Lunch" in formatted
