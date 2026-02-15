"""Task scheduler for managing reminders and recurring tasks."""

from __future__ import annotations

import atexit
import schedule
import threading
import time
from typing import Callable, Any

from modules.logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """Manages scheduled tasks and reminders."""

    def __init__(self):
        """Initialize the task scheduler."""
        self.scheduler = schedule.Scheduler()
        self.scheduler_thread = None
        self.is_running = False

    def schedule_reminder(
        self,
        task_name: str,
        trigger_time: str,
        task: Callable | None = None,
        unit: str = "days",
    ) -> schedule.Job:
        """
        Schedule a reminder task to run at a specific time.

        Args:
            task_name: Name/description of the task.
            trigger_time: Time in HH:MM format (24-hour) or interval for unit (e.g., "10:30", "2").
            task: Callable function to execute. If None, logs the reminder.
            unit: Time unit for scheduling ('days', 'hours', 'minutes', 'seconds'). Default: 'days'.

        Returns:
            The scheduled job object.

        Raises:
            ValueError: If trigger_time format is invalid or task_name is empty.
            TypeError: If task is not callable.
        """
        if not task_name or not isinstance(task_name, str):
            raise ValueError("task_name must be a non-empty string")

        if not trigger_time or not isinstance(trigger_time, str):
            raise ValueError("trigger_time must be a non-empty string")

        if unit not in ["days", "hours", "minutes", "seconds"]:
            raise ValueError(
                f"unit must be one of ['days', 'hours', 'minutes', 'seconds'], got '{unit}'"
            )

        # Default task logs the reminder if not provided
        if task is None:
            task = lambda: logger.info(f"Reminder: {task_name}")
        elif not callable(task):
            raise TypeError(f"task must be callable, got {type(task)}")

        try:
            # Schedule based on unit
            if unit == "days":
                # For daily tasks, interpret trigger_time as HH:MM format
                job = self.scheduler.every().day.at(trigger_time).do(task)
            elif unit == "hours":
                # For hourly tasks, trigger_time is an interval
                interval = int(trigger_time)
                job = self.scheduler.every(interval).hours.do(task)
            elif unit == "minutes":
                # For minute-based tasks
                interval = int(trigger_time)
                job = self.scheduler.every(interval).minutes.do(task)
            elif unit == "seconds":
                # For second-based tasks
                interval = int(trigger_time)
                job = self.scheduler.every(interval).seconds.do(task)

            job.tag(task_name)
            logger.info(f"Scheduled task '{task_name}' to run at {trigger_time} {unit}")
            return job

        except ValueError as exc:
            logger.error(f"Invalid time format for task '{task_name}': {exc}")
            raise ValueError(
                f"Invalid time format '{trigger_time}' for unit '{unit}': {exc}"
            ) from exc
        except Exception as exc:
            logger.error(f"Error scheduling task '{task_name}': {exc}")
            raise RuntimeError(f"Error scheduling task '{task_name}': {exc}") from exc

    def schedule_email_summary(self, trigger_time: str = "08:00") -> schedule.Job:
        """
        Schedule a daily email summary task.

        Args:
            trigger_time: Time to run summary in HH:MM format (default: "08:00").

        Returns:
            The scheduled job object.
        """
        def email_summary_task():
            # Import here to avoid circular imports
            from modules.email_handler import summarize_emails

            try:
                summary = summarize_emails()
                logger.info("Daily email summary completed")
                return summary
            except Exception as exc:
                logger.error(f"Failed to generate email summary: {exc}")

        return self.schedule_reminder(
            "Daily Email Summary", trigger_time, task=email_summary_task, unit="days"
        )

    def run(self, background: bool = True, interval: int = 60) -> None:
        """
        Run the scheduler loop.

        Args:
            background: If True, run in a background thread. If False, run blocking.
            interval: Polling interval in seconds (default: 60).

        Raises:
            RuntimeError: If scheduler is already running.
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        self.is_running = True
        logger.info("Starting task scheduler...")

        if background:
            # Run in background thread
            self.scheduler_thread = threading.Thread(
                target=self._run_loop, args=(interval,), daemon=True
            )
            self.scheduler_thread.start()
            logger.info("Task scheduler running in background thread")
        else:
            # Run blocking
            self._run_loop(interval)

        # Register cleanup on exit
        atexit.register(self.stop)

    def _run_loop(self, interval: int) -> None:
        """
        Internal scheduler loop.

        Args:
            interval: Polling interval in seconds.
        """
        try:
            while self.is_running:
                self.scheduler.run_pending()
                time.sleep(interval)
        except Exception as exc:
            logger.error(f"Error in scheduler loop: {exc}")
            self.is_running = False

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.is_running:
            return

        self.is_running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        logger.info("Task scheduler stopped")

    def get_pending_tasks(self) -> list[str]:
        """
        Get list of pending tasks.

        Returns:
            List of task names (tags) currently scheduled.
        """
        return [job.tags for job in self.scheduler.jobs]

    def remove_task(self, task_name: str) -> bool:
        """
        Remove a scheduled task by name.

        Args:
            task_name: Name of the task to remove.

        Returns:
            True if task was removed, False if not found.
        """
        initial_count = len(self.scheduler.jobs)
        self.scheduler.clear(task_name)
        removed = len(self.scheduler.jobs) < initial_count
        if removed:
            logger.info(f"Removed task '{task_name}'")
        else:
            logger.warning(f"Task '{task_name}' not found")
        return removed

    def clear_all(self) -> None:
        """Clear all scheduled tasks."""
        count = len(self.scheduler.jobs)
        self.scheduler.clear()
        logger.info(f"Cleared {count} scheduled tasks")


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> TaskScheduler:
    """
    Get the global scheduler instance (singleton).

    Returns:
        The TaskScheduler instance.
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TaskScheduler()
    return _scheduler_instance
