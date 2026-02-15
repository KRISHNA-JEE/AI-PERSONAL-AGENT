"""AI handler for querying OpenAI ChatCompletion API."""

from __future__ import annotations

from typing import Any

from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError, OpenAIError

from config import settings


def _get_client() -> OpenAI:
    """Get OpenAI client with API key from settings."""
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in the .env file.")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def ask_chatgpt(question: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Ask a question to OpenAI ChatCompletion API.

    Args:
        question: The user prompt or question.
        model: The ChatCompletion model to use.

    Returns:
        The assistant response as a string.
    """
    if not question or not question.strip():
        raise ValueError("Question must be a non-empty string.")

    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
        )
        return response.choices[0].message.content.strip()
    except AuthenticationError as exc:
        raise RuntimeError("Invalid OpenAI API key.") from exc
    except RateLimitError as exc:
        raise RuntimeError("OpenAI API quota exceeded or rate limited.") from exc
    except APIConnectionError as exc:
        raise RuntimeError("Network error while contacting OpenAI API.") from exc
    except OpenAIError as exc:
        raise RuntimeError("OpenAI API error occurred.") from exc
