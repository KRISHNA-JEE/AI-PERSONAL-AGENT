"""Main CLI entry point for AI Personal Assistant."""

import sys
from datetime import datetime, timedelta

from core.assistant import get_assistant
from modules.logger import get_logger

logger = get_logger(__name__)


def display_menu() -> None:
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("AI Personal Assistant - Main Menu")
    print("=" * 60)
    print("1. Ask a question (ChatGPT)")
    print("2. Get email summary")
    print("3. Schedule email reminder")
    print("4. View upcoming calendar events")
    print("5. Create a calendar event")
    print("6. View scheduled tasks")
    print("7. Remove scheduled task")
    print("8. Get assistant status")
    print("9. Exit")
    print("=" * 60)


def ask_question() -> None:
    """Handle asking a question."""
    question = input("Enter your question: ").strip()
    if not question:
        print("Question cannot be empty!")
        return

    print("\nProcessing your question...")
    try:
        assistant = get_assistant()
        response = assistant.process_user_query(question)
        print(f"\nAssistant Response:\n{response}")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to process question: {exc}")


def get_email_summary() -> None:
    """Handle email summary request."""
    try:
        max_emails = input("Number of emails to summarize (default 10): ").strip()
        max_emails = int(max_emails) if max_emails else 10

        print("\nFetching and summarizing emails...")
        assistant = get_assistant()
        summary = assistant.get_email_summary(max_emails=max_emails)
        print(f"\nEmail Summary:\n{summary}")
    except ValueError as exc:
        print(f"Invalid input: {exc}")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to get email summary: {exc}")


def schedule_email_reminder() -> None:
    """Handle scheduling email reminder."""
    try:
        time_str = input("Enter reminder time (HH:MM, default 08:00): ").strip()
        time_str = time_str if time_str else "08:00"

        # Validate time format
        datetime.strptime(time_str, "%H:%M")

        assistant = get_assistant()
        assistant.schedule_email_reminder(time=time_str)
        print(f"Email reminder scheduled for {time_str} daily")
    except ValueError as exc:
        print(f"Invalid time format! Use HH:MM format (e.g., 14:30)")
        logger.error(f"Invalid time format: {exc}")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to schedule email reminder: {exc}")


def view_calendar_events() -> None:
    """Handle viewing calendar events."""
    try:
        days = input("Number of days to look ahead (default 7): ").strip()
        days = int(days) if days else 7

        print(f"\nFetching upcoming events for next {days} days...")
        assistant = get_assistant()
        events = assistant.get_upcoming_calendar_events(days=days)

        if not events:
            print("No upcoming events found.")
            return

        print(f"\nUpcoming Events ({len(events)} total):")
        print("-" * 60)
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.get('summary', '(No Title)')}")
            print(f"   Start: {event.get('start', 'N/A')}")
            print(f"   End: {event.get('end', 'N/A')}")
            if event.get('description'):
                print(f"   Description: {event['description']}")
            print()
    except ValueError as exc:
        print(f"Invalid input: {exc}")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to view calendar events: {exc}")


def create_calendar_event() -> None:
    """Handle creating a calendar event."""
    try:
        title = input("Event title: ").strip()
        if not title:
            print("Event title cannot be empty!")
            return

        start_str = input("Start date/time (YYYY-MM-DD HH:MM): ").strip()
        end_str = input("End date/time (YYYY-MM-DD HH:MM): ").strip()
        description = input("Event description (optional): ").strip()

        # Parse dates
        start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M")

        if start_time >= end_time:
            print("Start time must be before end time!")
            return

        print("\nCreating calendar event...")
        assistant = get_assistant()
        event_id = assistant.create_calendar_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
        )
        print(f"Event created successfully! Event ID: {event_id}")
    except ValueError as exc:
        print(
            f"Invalid date/time format! Use YYYY-MM-DD HH:MM (e.g., 2026-02-15 14:30)"
        )
        logger.error(f"Invalid date/time format: {exc}")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to create calendar event: {exc}")


def view_scheduled_tasks() -> None:
    """Handle viewing scheduled tasks."""
    try:
        assistant = get_assistant()
        tasks = assistant.get_pending_tasks()

        if not tasks:
            print("No scheduled tasks found.")
            return

        print(f"\nScheduled Tasks ({len(tasks)} total):")
        print("-" * 60)
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to view scheduled tasks: {exc}")


def remove_scheduled_task() -> None:
    """Handle removing a scheduled task."""
    try:
        task_name = input("Enter task name to remove: ").strip()
        if not task_name:
            print("Task name cannot be empty!")
            return

        assistant = get_assistant()
        removed = assistant.remove_scheduled_task(task_name)

        if removed:
            print(f"Task '{task_name}' removed successfully.")
        else:
            print(f"Task '{task_name}' not found.")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to remove task: {exc}")


def show_status() -> None:
    """Display assistant status."""
    try:
        assistant = get_assistant()
        status = assistant.status()

        print("\nAssistant Status:")
        print("-" * 60)
        print(f"Running: {status['running']}")
        print(f"Pending Tasks: {status['pending_tasks']}")
        if status['task_names']:
            print("Task List:")
            for task in status['task_names']:
                print(f"  - {task}")
    except Exception as exc:
        print(f"Error: {exc}")
        logger.error(f"Failed to get assistant status: {exc}")


def main() -> None:
    """Main CLI loop."""
    print("\nWelcome to AI Personal Assistant!")
    print("Starting assistant with background task scheduler...")

    assistant = get_assistant()
    try:
        assistant.start()
        print("✓ Assistant started successfully")

        while True:
            display_menu()
            choice = input("Select an option (1-9): ").strip()

            if choice == "1":
                ask_question()
            elif choice == "2":
                get_email_summary()
            elif choice == "3":
                schedule_email_reminder()
            elif choice == "4":
                view_calendar_events()
            elif choice == "5":
                create_calendar_event()
            elif choice == "6":
                view_scheduled_tasks()
            elif choice == "7":
                remove_scheduled_task()
            elif choice == "8":
                show_status()
            elif choice == "9":
                print("\nExiting AI Personal Assistant...")
                break
            else:
                print("Invalid option! Please select 1-9.")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as exc:
        print(f"Fatal error: {exc}")
        logger.error(f"Fatal error in main loop: {exc}")
    finally:
        print("Shutting down assistant...")
        assistant.stop()
        print("✓ Assistant stopped successfully")
        print("Goodbye!")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error(f"Fatal error: {exc}")
        sys.exit(1)
