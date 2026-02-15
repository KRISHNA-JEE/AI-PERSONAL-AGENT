"""Main orchestrator for the AI Personal Assistant."""

from __future__ import annotations

from typing import Any, Optional

from modules.ai_handler import ask_chatgpt
from modules.calendar_handler import (
    authenticate_calendar,
    create_event,
    get_upcoming_events,
)
from modules.email_handler import (
    authenticate_gmail,
    get_unread_emails,
    summarize_emails,
)
from modules.logger import get_logger
from modules.task_scheduler import TaskScheduler, get_scheduler
from datetime import datetime

logger = get_logger(__name__)


class PersonalAssistant:
    """Main orchestrator for AI Personal Assistant features."""

    def __init__(self):
        """Initialize the Personal Assistant."""
        self.scheduler = get_scheduler()
        logger.info("Initializing AI Personal Assistant")

    def start(self) -> None:
        """Start the assistant with background task scheduler."""
        logger.info("Starting AI Personal Assistant")
        self.scheduler.run(background=True, interval=60)

    def stop(self) -> None:
        """Stop the assistant and all background tasks."""
        logger.info("Stopping AI Personal Assistant")
        self.scheduler.stop()

    def process_user_query(self, query: str) -> str:
        """
        Process a user query and return AI response.

        Args:
            query: User's natural language query.

        Returns:
            AI-generated response.

        Raises:
            RuntimeError: If ChatGPT API call fails.
            ValueError: If query is empty.
        """
        if not query or not isinstance(query, str):
            raise ValueError("query must be a non-empty string")

        logger.info(f"Processing user query: {query[:100]}...")
        try:
            response = ask_chatgpt(query)
            logger.info("Query processed successfully")
            return response
        except Exception as exc:
            logger.error(f"Error processing query: {exc}")
            raise RuntimeError(f"Failed to process query: {exc}") from exc

    def get_email_summary(self, max_emails: int = 10) -> str:
        """
        Get a summary of recent unread emails using AI.

        Args:
            max_emails: Maximum number of emails to summarize.

        Returns:
            AI-generated summary of emails.

        Raises:
            RuntimeError: If Gmail API or ChatGPT API fails.
        """
        logger.info(f"Fetching and summarizing up to {max_emails} emails")
        try:
            summary = summarize_emails(max_results=max_emails)
            logger.info("Email summary retrieved successfully")
            return summary
        except Exception as exc:
            logger.error(f"Error getting email summary: {exc}")
            raise RuntimeError(f"Failed to get email summary: {exc}") from exc

    def schedule_email_reminder(self, time: str = "08:00") -> None:
        """
        Schedule a daily email summary reminder.

        Args:
            time: Time to send reminder in HH:MM format (default: "08:00").

        Raises:
            RuntimeError: If scheduling fails.
        """
        logger.info(f"Scheduling daily email reminder at {time}")
        try:
            self.scheduler.schedule_email_summary(trigger_time=time)
            logger.info(f"Email reminder scheduled for {time}")
        except Exception as exc:
            logger.error(f"Error scheduling email reminder: {exc}")
            raise RuntimeError(f"Failed to schedule email reminder: {exc}") from exc

    def get_upcoming_calendar_events(self, days: int = 7) -> list[dict[str, Any]]:
        """
        Get upcoming calendar events.

        Args:
            days: Number of days to look ahead (default: 7).

        Returns:
            List of upcoming events with details.

        Raises:
            RuntimeError: If Calendar API fails.
            ValueError: If days is negative.
        """
        if days < 0:
            raise ValueError("days must be non-negative")

        logger.info(f"Fetching upcoming calendar events for next {days} days")
        try:
            events = get_upcoming_events(days=days)
            logger.info(f"Retrieved {len(events)} upcoming events")
            return events
        except Exception as exc:
            logger.error(f"Error fetching calendar events: {exc}")
            raise RuntimeError(f"Failed to fetch calendar events: {exc}") from exc

    def create_calendar_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
    ) -> str:
        """
        Create a new calendar event.

        Args:
            title: Event title.
            start_time: Event start datetime.
            end_time: Event end datetime.
            description: Optional event description.

        Returns:
            Created event ID.

        Raises:
            RuntimeError: If Calendar API fails.
            ValueError: If input validation fails.
        """
        logger.info(f"Creating calendar event: {title}")
        try:
            event_id = create_event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
            )
            logger.info(f"Calendar event created with ID: {event_id}")
            return event_id
        except Exception as exc:
            logger.error(f"Error creating calendar event: {exc}")
            raise RuntimeError(f"Failed to create calendar event: {exc}") from exc

    def schedule_custom_task(
        self,
        task_name: str,
        trigger_time: str,
        task: callable | None = None,
        unit: str = "days",
    ) -> None:
        """
        Schedule a custom task.

        Args:
            task_name: Name of the task.
            trigger_time: Time/interval to trigger the task.
            task: Optional callable to execute.
            unit: Time unit ('days', 'hours', 'minutes', 'seconds').

        Raises:
            RuntimeError: If scheduling fails.
        """
        logger.info(f"Scheduling custom task: {task_name}")
        try:
            self.scheduler.schedule_reminder(
                task_name=task_name,
                trigger_time=trigger_time,
                task=task,
                unit=unit,
            )
            logger.info(f"Custom task scheduled: {task_name}")
        except Exception as exc:
            logger.error(f"Error scheduling custom task: {exc}")
            raise RuntimeError(f"Failed to schedule custom task: {exc}") from exc

    def get_pending_tasks(self) -> list[str]:
        """
        Get list of pending scheduled tasks.

        Returns:
            List of task names.
        """
        tasks = self.scheduler.get_pending_tasks()
        logger.info(f"Retrieved {len(tasks)} pending tasks")
        return tasks

    def remove_scheduled_task(self, task_name: str) -> bool:
        """
        Remove a scheduled task.

        Args:
            task_name: Name of the task to remove.

        Returns:
            True if task was removed, False if not found.
        """
        removed = self.scheduler.remove_task(task_name)
        if removed:
            logger.info(f"Task removed: {task_name}")
        else:
            logger.warning(f"Task not found: {task_name}")
        return removed

    def voice_query(self, voice_query: str) -> str:
        """
        Process a voice query (currently uses text processing).

        Args:
            voice_query: Voice input converted to text.

        Returns:
            AI-generated response.

        Raises:
            RuntimeError: If ChatGPT API fails.
        """
        logger.info("Processing voice query")
        try:
            response = ask_chatgpt(voice_query)
            logger.info("Voice query processed successfully")
            return response
        except Exception as exc:
            logger.error(f"Error processing voice query: {exc}")
            raise RuntimeError(f"Failed to process voice query: {exc}") from exc

    def status(self) -> dict[str, Any]:
        """
        Get assistant status and pending tasks.

        Returns:
            Dictionary with status information.
        """
        return {
            "running": self.scheduler.is_running,
            "pending_tasks": len(self.scheduler.get_pending_tasks()),
            "task_names": self.scheduler.get_pending_tasks(),
        }


# Global assistant instance
_assistant_instance: Optional[PersonalAssistant] = None


def get_assistant() -> PersonalAssistant:
    """
    Get the global assistant instance (singleton).

    Returns:
        The PersonalAssistant instance.
    """
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = PersonalAssistant()
    return _assistant_instance
