"""
Main CLI interface for AI Personal Assistant

This module provides the command-line interface for interacting with all
assistant features.
"""

import click
import sys
from typing import Optional

from ai_assistant.modules.logging_module import get_logger
from ai_assistant.modules.ai_query import AIQuery
from ai_assistant.modules.email import EmailManager
from ai_assistant.modules.calendar import CalendarManager
from ai_assistant.modules.reminders import RemindersManager

logger = get_logger()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    AI Personal Assistant - Your intelligent command-line companion.
    
    Integrates ChatGPT, Gmail, Google Calendar, and task reminders.
    """
    logger.info("AI Personal Assistant started")


@cli.command()
@click.argument('query', nargs=-1, required=True)
@click.option('--model', default='gpt-3.5-turbo', help='GPT model to use')
def ask(query, model):
    """
    Ask ChatGPT a question.
    
    Example: assistant ask "What is the weather like today?"
    """
    try:
        query_text = ' '.join(query)
        logger.info(f"Processing AI query: {query_text[:50]}...")
        
        ai = AIQuery(model=model)
        response = ai.query(query_text, use_history=False)
        
        click.echo("\n" + "="*60)
        click.echo("ChatGPT Response:")
        click.echo("="*60)
        click.echo(response)
        click.echo("="*60 + "\n")
        
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
        click.echo("Please set OPENAI_API_KEY in your .env file", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error in ask command: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--max-results', default=10, help='Maximum number of emails to fetch')
@click.option('--days-back', default=7, help='Number of days to look back')
def email(max_results, days_back):
    """
    Fetch and summarize recent emails from Gmail.
    
    Example: assistant email --max-results 5 --days-back 3
    """
    try:
        logger.info(f"Fetching emails: max={max_results}, days={days_back}")
        
        manager = EmailManager()
        
        click.echo("Authenticating with Gmail...")
        manager.authenticate()
        
        click.echo(f"Fetching last {max_results} emails from past {days_back} days...\n")
        emails = manager.get_recent_emails(max_results, days_back)
        
        summary = manager.summarize_emails(emails)
        
        click.echo("="*60)
        click.echo("Email Summary:")
        click.echo("="*60)
        click.echo(summary)
        click.echo("="*60 + "\n")
        
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}", err=True)
        click.echo("\nTo set up Gmail integration:", err=True)
        click.echo("1. Go to Google Cloud Console", err=True)
        click.echo("2. Enable Gmail API", err=True)
        click.echo("3. Download credentials.json", err=True)
        click.echo("4. Place it in the project root", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error in email command: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--max-results', default=10, help='Maximum number of events to fetch')
@click.option('--days-ahead', default=7, help='Number of days to look ahead')
def calendar(max_results, days_ahead):
    """
    Show upcoming events from Google Calendar.
    
    Example: assistant calendar --max-results 5 --days-ahead 3
    """
    try:
        logger.info(f"Fetching calendar events: max={max_results}, days={days_ahead}")
        
        manager = CalendarManager()
        
        click.echo("Authenticating with Google Calendar...")
        manager.authenticate()
        
        click.echo(f"Fetching next {max_results} events for the next {days_ahead} days...\n")
        events = manager.get_upcoming_events(max_results, days_ahead)
        
        formatted = manager.format_events(events)
        
        click.echo("="*60)
        click.echo("Calendar Events:")
        click.echo("="*60)
        click.echo(formatted)
        click.echo("="*60 + "\n")
        
    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}", err=True)
        click.echo("\nTo set up Calendar integration:", err=True)
        click.echo("1. Go to Google Cloud Console", err=True)
        click.echo("2. Enable Google Calendar API", err=True)
        click.echo("3. Download credentials.json", err=True)
        click.echo("4. Place it in the project root", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error in calendar command: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.group()
def reminder():
    """
    Manage task reminders.
    """
    pass


@reminder.command('add')
@click.argument('title')
@click.option('--description', '-d', default='', help='Reminder description')
@click.option('--due-date', help='Due date (YYYY-MM-DD)')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high']), 
              default='medium', help='Priority level')
def reminder_add(title, description, due_date, priority):
    """
    Add a new reminder.
    
    Example: assistant reminder add "Buy groceries" -d "Milk, eggs, bread" --priority high
    """
    try:
        logger.info(f"Adding reminder: {title}")
        
        manager = RemindersManager()
        reminder = manager.add_reminder(title, description, due_date, priority)
        
        click.echo(f"\n✓ Reminder added successfully!")
        click.echo(f"  Title: {reminder['title']}")
        click.echo(f"  ID: {reminder['id']}")
        click.echo(f"  Priority: {reminder['priority']}\n")
        
    except Exception as e:
        logger.error(f"Error adding reminder: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@reminder.command('list')
@click.option('--all', '-a', 'show_all', is_flag=True, help='Show completed reminders')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high']), 
              help='Filter by priority')
def reminder_list(show_all, priority):
    """
    List all reminders.
    
    Example: assistant reminder list --all
    """
    try:
        logger.info("Listing reminders")
        
        manager = RemindersManager()
        reminders = manager.get_reminders(show_completed=show_all, priority=priority)
        formatted = manager.format_reminders(reminders)
        
        click.echo("\n" + "="*60)
        click.echo("Reminders:")
        click.echo("="*60)
        click.echo(formatted)
        click.echo("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error listing reminders: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@reminder.command('complete')
@click.argument('reminder_id', type=int)
def reminder_complete(reminder_id):
    """
    Mark a reminder as completed.
    
    Example: assistant reminder complete 1
    """
    try:
        logger.info(f"Completing reminder: {reminder_id}")
        
        manager = RemindersManager()
        success = manager.complete_reminder(reminder_id)
        
        if success:
            click.echo(f"\n✓ Reminder {reminder_id} marked as completed!\n")
        else:
            click.echo(f"\n✗ Reminder {reminder_id} not found.\n", err=True)
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error completing reminder: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@reminder.command('delete')
@click.argument('reminder_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this reminder?')
def reminder_delete(reminder_id):
    """
    Delete a reminder.
    
    Example: assistant reminder delete 1
    """
    try:
        logger.info(f"Deleting reminder: {reminder_id}")
        
        manager = RemindersManager()
        success = manager.delete_reminder(reminder_id)
        
        if success:
            click.echo(f"\n✓ Reminder {reminder_id} deleted!\n")
        else:
            click.echo(f"\n✗ Reminder {reminder_id} not found.\n", err=True)
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error deleting reminder: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """
    Show a comprehensive status overview.
    
    Displays reminders, recent emails, and upcoming calendar events.
    """
    try:
        logger.info("Generating status overview")
        
        click.echo("\n" + "="*60)
        click.echo("AI PERSONAL ASSISTANT - STATUS OVERVIEW")
        click.echo("="*60 + "\n")
        
        # Show reminders
        click.echo("📋 REMINDERS:")
        click.echo("-" * 60)
        manager = RemindersManager()
        reminders = manager.get_reminders(show_completed=False)
        click.echo(manager.format_reminders(reminders))
        
        click.echo("\n" + "="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error in status command: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        click.echo(f"\nUnexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
