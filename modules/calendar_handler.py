"""Calendar handler for Google Calendar API integration."""

from __future__ import annotations

import pickle
from datetime import datetime as dt, timedelta
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import settings
from modules.logger import get_logger

logger = get_logger(__name__)

# Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def authenticate_calendar() -> Any:
    """
    Authenticate with Google Calendar API using OAuth2 credentials.

    Returns:
        A Google Calendar API service object.

    Raises:
        RuntimeError: If credentials file is missing or authentication fails.
    """
    credentials_path = settings.CALENDAR_CREDENTIALS_PATH

    if not credentials_path:
        raise RuntimeError(
            "Missing CALENDAR_CREDENTIALS_PATH. Set it in the .env file."
        )

    credentials_file = Path(credentials_path)

    if not credentials_file.exists():
        raise RuntimeError(
            f"Calendar credentials file not found at {credentials_path}. "
            "Download OAuth2 credentials from Google Cloud Console."
        )

    creds = None
    token_path = Path(credentials_path).parent / "calendar_token.pickle"

    # Load existing token if available
    if token_path.exists():
        with open(token_path, "rb") as token_file:
            creds = pickle.load(token_file)

    # Refresh or create new credentials
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES
        )
        creds = flow.run_local_server(port=0)

        # Save token for next time
        with open(token_path, "wb") as token_file:
            pickle.dump(creds, token_file)

    service = build("calendar", "v3", credentials=creds)
    logger.info("Successfully authenticated with Google Calendar API")
    return service


def create_event(
    title: str,
    start_time: dt,
    end_time: dt,
    description: str = "",
    calendar_id: str = "primary",
) -> str:
    """
    Create a new event on Google Calendar.

    Args:
        title: Event title.
        start_time: Event start datetime.
        end_time: Event end datetime.
        description: Optional event description.
        calendar_id: Calendar ID (defaults to 'primary' for main calendar).

    Returns:
        Event ID of the created event.

    Raises:
        ValueError: If start_time >= end_time or invalid datetime format.
        RuntimeError: If Calendar API call fails or quota limit exceeded.
    """
    # Validate datetime inputs
    if not isinstance(start_time, dt):
        raise ValueError(f"start_time must be datetime object, got {type(start_time)}")
    if not isinstance(end_time, dt):
        raise ValueError(f"end_time must be datetime object, got {type(end_time)}")
    if start_time >= end_time:
        raise ValueError("start_time must be before end_time")

    try:
        service = authenticate_calendar()

        # Create event object
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
        }

        # Insert event into calendar
        result = service.events().insert(
            calendarId=calendar_id, body=event
        ).execute()

        event_id = result.get("id")
        logger.info(f"Created event '{title}' with ID: {event_id}")
        return event_id

    except ValueError as exc:
        logger.error(f"Invalid event data: {exc}")
        raise
    except HttpError as exc:
        error_content = exc.resp.status
        if error_content == 403:
            logger.error("Quota limit exceeded for Google Calendar API")
            raise RuntimeError("Calendar API quota limit exceeded") from exc
        logger.error(f"Calendar API error: {exc}")
        raise RuntimeError(f"Calendar API error: {exc}") from exc
    except Exception as exc:
        logger.error(f"Unexpected error creating event: {exc}")
        raise RuntimeError(f"Unexpected error creating event: {exc}") from exc


def get_upcoming_events(
    days: int = 7, calendar_id: str = "primary", max_results: int = 10
) -> list[dict[str, Any]]:
    """
    Fetch upcoming events from Google Calendar.

    Args:
        days: Number of days to look ahead (default: 7).
        calendar_id: Calendar ID (defaults to 'primary' for main calendar).
        max_results: Maximum number of events to return.

    Returns:
        A list of event dicts with 'id', 'summary', 'start', 'end' keys.

    Raises:
        RuntimeError: If Calendar API call fails or invalid datetime format.
    """
    if days < 0:
        raise ValueError("days must be non-negative")
    if max_results < 1:
        raise ValueError("max_results must be at least 1")

    try:
        service = authenticate_calendar()

        now = dt.utcnow().isoformat() + "Z"
        future = (dt.utcnow() + timedelta(days=days)).isoformat() + "Z"

        # Fetch events within the specified date range
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            timeMax=future,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        if not events:
            logger.info(f"No upcoming events found in the next {days} day(s)")
            return []

        # Extract relevant event info
        upcoming_events = []
        for event in events:
            upcoming_events.append(
                {
                    "id": event.get("id"),
                    "summary": event.get("summary", "(No Title)"),
                    "start": event.get("start", {}).get("dateTime", ""),
                    "end": event.get("end", {}).get("dateTime", ""),
                    "description": event.get("description", ""),
                }
            )

        logger.info(f"Retrieved {len(upcoming_events)} upcoming events")
        return upcoming_events

    except HttpError as exc:
        error_content = exc.resp.status
        if error_content == 403:
            logger.error("Quota limit exceeded for Google Calendar API")
            raise RuntimeError("Calendar API quota limit exceeded") from exc
        logger.error(f"Calendar API error: {exc}")
        raise RuntimeError(f"Calendar API error: {exc}") from exc
    except Exception as exc:
        logger.error(f"Unexpected error fetching events: {exc}")
        raise RuntimeError(f"Unexpected error fetching events: {exc}") from exc
