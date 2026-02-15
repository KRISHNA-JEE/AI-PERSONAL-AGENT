"""
Tests for the AI query module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ai_assistant.modules.ai_query import AIQuery, query_ai


def test_ai_query_initialization_without_api_key(monkeypatch):
    """Test that AIQuery raises error without API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="OPENAI_API_KEY must be set"):
        AIQuery()


def test_ai_query_initialization_with_api_key(temp_env_file):
    """Test successful AIQuery initialization."""
    ai = AIQuery()
    assert ai.model == "gpt-3.5-turbo"
    assert ai.conversation_history == []


def test_ai_query_with_mock_response(temp_env_file):
    """Test querying AI with mocked response."""
    with patch('ai_assistant.modules.ai_query.OpenAI') as mock_openai:
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        ai = AIQuery()
        response = ai.query("Test prompt")
        
        assert response == "Test response"
        assert len(ai.conversation_history) == 2


def test_clear_history(temp_env_file):
    """Test clearing conversation history."""
    with patch('ai_assistant.modules.ai_query.OpenAI'):
        ai = AIQuery()
        ai.conversation_history = [{"role": "user", "content": "test"}]
        
        ai.clear_history()
        assert ai.conversation_history == []


def test_get_history(temp_env_file):
    """Test getting conversation history."""
    with patch('ai_assistant.modules.ai_query.OpenAI'):
        ai = AIQuery()
        test_history = [{"role": "user", "content": "test"}]
        ai.conversation_history = test_history
        
        history = ai.get_history()
        assert history == test_history
        assert history is not ai.conversation_history  # Should be a copy


def test_set_system_prompt(temp_env_file):
    """Test setting system prompt."""
    with patch('ai_assistant.modules.ai_query.OpenAI'):
        ai = AIQuery()
        
        ai.set_system_prompt("You are a helpful assistant")
        assert len(ai.conversation_history) == 1
        assert ai.conversation_history[0]["role"] == "system"


def test_query_without_history(temp_env_file):
    """Test query without using conversation history."""
    with patch('ai_assistant.modules.ai_query.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        ai = AIQuery()
        response = ai.query("Test", use_history=False)
        
        assert response == "Response"
        assert len(ai.conversation_history) == 0
