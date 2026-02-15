"""Email handler for Gmail API integration."""

from __future__ import annotations

import base64
import pickle
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import settings
from modules.ai_handler import ask_chatgpt
from modules.logger import get_logger

logger = get_logger(__name__)

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail() -> Any:
    """
    Authenticate with Gmail API using OAuth2 credentials.

    Returns:
        A Gmail API service object.

    Raises:
        RuntimeError: If credentials file is missing or authentication fails.
    """
    credentials_path = settings.GMAIL_CREDENTIALS_PATH

    if not credentials_path:
        raise RuntimeError(
            "Missing GMAIL_CREDENTIALS_PATH. Set it in the .env file."
        )

    credentials_file = Path(credentials_path)

    if not credentials_file.exists():
        raise RuntimeError(
            f"Gmail credentials file not found at {credentials_path}. "
            "Download OAuth2 credentials from Google Cloud Console."
        )

    try:
        # Try to load existing credentials
        creds = None
        token_path = credentials_file.parent / "gmail_token.pickle"

        if token_path.exists():
            with open(token_path, "rb") as token_file:
                creds = pickle.load(token_file)

        # Refresh or create new credentials
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_path, "wb") as token_file:
                pickle.dump(creds, token_file)

        service = build("gmail", "v1", credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
        return service

    except Exception as exc:
        logger.error(f"Gmail authentication failed: {exc}")
        raise RuntimeError(f"Gmail authentication failed: {exc}") from exc


def _decode_email_body(message: dict[str, Any]) -> str:
    """
    Decode email body from MIME-encoded message.

    Args:
        message: A Gmail API message dict.

    Returns:
        The decoded email body as a string.

    Raises:
        ValueError: If email body cannot be decoded.
    """
    try:
        # Get parts of the message
        if "parts" in message["payload"]:
            # Multi-part message (with attachments, HTML, etc.)
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part.get("body", {}).get("data")
                    if data:
                        return base64.urlsafe_b64decode(data).decode("utf-8")
            # If no plain text, try HTML
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "text/html":
                    data = part.get("body", {}).get("data")
                    if data:
                        return base64.urlsafe_b64decode(data).decode("utf-8")
        else:
            # Single-part message
            data = message["payload"].get("body", {}).get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8")

        # If no body found, return empty string
        return ""

    except Exception as exc:
        logger.warning(f"Failed to decode email body: {exc}")
        raise ValueError(f"Could not decode email body: {exc}") from exc


def get_unread_emails(max_results: int = 10) -> list[dict[str, Any]]:
    """
    Fetch latest unread emails from Gmail inbox.

    Args:
        max_results: Maximum number of unread emails to fetch (default: 10).

    Returns:
        A list of email dicts with 'id', 'subject', 'sender', 'body' keys.

    Raises:
        RuntimeError: If Gmail API call fails.
    """
    try:
        service = authenticate_gmail()

        # Get list of unread message IDs
        results = service.users().messages().list(
            userId="me",
            q="is:unread",
            maxResults=max_results,
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            logger.info("No unread emails found")
            return []

        emails = []

        for message in messages:
            try:
                msg = service.users().messages().get(
                    userId="me", id=message["id"], format="full"
                ).execute()

                headers = msg["payload"]["headers"]
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "(No Subject)",
                )
                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"),
                    "Unknown",
                )

                body = _decode_email_body(msg)

                emails.append(
                    {
                        "id": message["id"],
                        "subject": subject,
                        "sender": sender,
                        "body": body,
                    }
                )

            except ValueError as exc:
                logger.warning(
                    f"Could not process email {message['id']}: {exc}"
                )
                continue

        logger.info(f"Retrieved {len(emails)} unread emails")
        return emails

    except HttpError as exc:
        logger.error(f"Gmail API error: {exc}")
        raise RuntimeError(f"Gmail API error: {exc}") from exc
    except Exception as exc:
        logger.error(f"Unexpected error fetching emails: {exc}")
        raise RuntimeError(f"Unexpected error fetching emails: {exc}") from exc


def summarize_emails(max_results: int = 10) -> str:
    """
    Fetch unread emails and summarize them using ChatGPT.

    Args:
        max_results: Maximum number of unread emails to summarize.

    Returns:
        A string containing summaries of all unread emails.

    Raises:
        RuntimeError: If email fetching or ChatGPT call fails.
    """
    try:
        emails = get_unread_emails(max_results=max_results)

        if not emails:
            logger.info("No emails to summarize")
            return "No unread emails found."

        summaries = []

        for email in emails:
            try:
                prompt = (
                    f"Please summarize this email in 2-3 sentences:\n\n"
                    f"Subject: {email['subject']}\n"
                    f"From: {email['sender']}\n\n"
                    f"Body:\n{email['body'][:500]}"  # Limit body to 500 chars
                )

                summary = ask_chatgpt(prompt)
                summaries.append(
                    f"**{email['subject']}** (from {email['sender']})\n{summary}\n"
                )

                logger.info(f"Summarized email: {email['subject']}")

            except RuntimeError as exc:
                logger.error(f"Failed to summarize email {email['subject']}: {exc}")
                summaries.append(
                    f"**{email['subject']}** - Failed to summarize: {exc}\n"
                )

        result = "\n".join(summaries)
        logger.info("Email summarization complete")
        return result

    except RuntimeError as exc:
        logger.error(f"Error during email summarization: {exc}")
        raise
    except Exception as exc:
        logger.error(f"Unexpected error during email summarization: {exc}")
        raise RuntimeError(
            f"Unexpected error during email summarization: {exc}"
        ) from exc
