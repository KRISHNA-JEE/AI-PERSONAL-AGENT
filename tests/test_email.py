"""
Tests for the email module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ai_assistant.modules.email import EmailManager, get_email_summary


def test_email_manager_initialization():
    """Test EmailManager initialization."""
    manager = EmailManager()
    assert manager.service is None
    assert manager.credentials_file is not None


def test_authenticate_without_credentials_file(tmp_path, monkeypatch):
    """Test authentication fails without credentials file."""
    monkeypatch.setenv("GMAIL_CREDENTIALS_FILE", str(tmp_path / "nonexistent.json"))
    
    manager = EmailManager()
    
    with pytest.raises(FileNotFoundError, match="Gmail credentials file"):
        manager.authenticate()


def test_get_recent_emails_not_authenticated():
    """Test getting emails without authentication."""
    manager = EmailManager()
    
    with pytest.raises(Exception, match="Not authenticated"):
        manager.get_recent_emails()


@patch('ai_assistant.modules.email.build')
@patch('ai_assistant.modules.email.Credentials')
def test_get_recent_emails_success(mock_creds, mock_build):
    """Test successfully fetching recent emails."""
    # Setup mock service
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    # Mock email list response
    mock_service.users().messages().list().execute.return_value = {
        'messages': [{'id': '123'}, {'id': '456'}]
    }
    
    # Mock individual message responses
    def mock_get_message(*args, **kwargs):
        message_id = kwargs.get('id')
        return Mock(execute=lambda: {
            'id': message_id,
            'snippet': 'Test snippet',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Thu, 1 Jan 2026 00:00:00'}
                ]
            }
        })
    
    mock_service.users().messages().get = mock_get_message
    
    manager = EmailManager()
    manager.service = mock_service
    
    emails = manager.get_recent_emails(max_results=2, days_back=7)
    
    assert len(emails) == 2
    assert emails[0]['from'] == 'test@example.com'
    assert emails[0]['subject'] == 'Test Subject'


def test_summarize_emails_empty():
    """Test summarizing empty email list."""
    manager = EmailManager()
    summary = manager.summarize_emails([])
    assert "No emails to summarize" in summary


def test_summarize_emails():
    """Test summarizing emails."""
    manager = EmailManager()
    
    emails = [
        {
            'from': 'sender1@example.com',
            'subject': 'Subject 1',
            'snippet': 'Email content preview',
            'date': 'Thu, 1 Jan 2026 00:00:00'
        },
        {
            'from': 'sender2@example.com',
            'subject': 'Subject 2',
            'snippet': 'Another email preview',
            'date': 'Fri, 2 Jan 2026 00:00:00'
        }
    ]
    
    summary = manager.summarize_emails(emails)
    
    assert "2 recent emails" in summary
    assert "sender1@example.com" in summary
    assert "Subject 1" in summary
    assert "sender2@example.com" in summary
