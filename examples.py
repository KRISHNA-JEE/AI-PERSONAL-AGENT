#!/usr/bin/env python3
"""
Example usage script for AI Personal Assistant

This script demonstrates how to use the AI Personal Assistant modules
programmatically rather than through the CLI.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Example 1: Using the AI Query module
print("=" * 60)
print("Example 1: AI Query")
print("=" * 60)

try:
    from ai_assistant.modules.ai_query import AIQuery
    
    # Check if API key is set
    if os.getenv('OPENAI_API_KEY'):
        ai = AIQuery()
        
        # Set a system prompt for specialized behavior
        ai.set_system_prompt("You are a helpful assistant that provides concise answers.")
        
        # Ask a question
        response = ai.query("What is Python used for?")
        print(f"Question: What is Python used for?")
        print(f"Answer: {response}\n")
        
        # Ask a follow-up question using conversation history
        response = ai.query("Can you give me 3 popular Python frameworks?")
        print(f"Question: Can you give me 3 popular Python frameworks?")
        print(f"Answer: {response}\n")
    else:
        print("Skipped: OPENAI_API_KEY not set in .env file\n")
except Exception as e:
    print(f"Error: {str(e)}\n")


# Example 2: Using the Reminders module
print("=" * 60)
print("Example 2: Task Reminders")
print("=" * 60)

try:
    from ai_assistant.modules.reminders import RemindersManager
    
    manager = RemindersManager()
    
    # Add some reminders
    reminder1 = manager.add_reminder(
        title="Complete project documentation",
        description="Write API docs and user guide",
        due_date="2026-03-15",
        priority="high"
    )
    print(f"Added: {reminder1['title']} (ID: {reminder1['id']})")
    
    reminder2 = manager.add_reminder(
        title="Team meeting",
        description="Weekly sync-up",
        priority="medium"
    )
    print(f"Added: {reminder2['title']} (ID: {reminder2['id']})")
    
    # List all reminders
    print("\nActive reminders:")
    reminders = manager.get_reminders(show_completed=False)
    for r in reminders:
        print(f"  - [{r['priority'].upper()}] {r['title']} (ID: {r['id']})")
    
    # Complete a reminder
    manager.complete_reminder(reminder2['id'])
    print(f"\nCompleted: {reminder2['title']}")
    
    # Show only active reminders
    print("\nRemaining active reminders:")
    active = manager.get_reminders(show_completed=False)
    for r in active:
        print(f"  - [{r['priority'].upper()}] {r['title']} (ID: {r['id']})")
    
    # Clean up - delete the test reminders
    manager.delete_reminder(reminder1['id'])
    manager.delete_reminder(reminder2['id'])
    print("\nTest reminders cleaned up.\n")
    
except Exception as e:
    print(f"Error: {str(e)}\n")


# Example 3: Using the Logging module
print("=" * 60)
print("Example 3: Logging")
print("=" * 60)

try:
    from ai_assistant.modules.logging_module import get_logger
    
    logger = get_logger()
    
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("Logged messages to file. Check logs/assistant.log\n")
    
except Exception as e:
    print(f"Error: {str(e)}\n")


# Example 4: Email module (requires Gmail credentials)
print("=" * 60)
print("Example 4: Email (requires credentials)")
print("=" * 60)

try:
    from ai_assistant.modules.email import EmailManager
    
    # Note: This will only work if you have set up Gmail API credentials
    if os.path.exists('credentials.json'):
        manager = EmailManager()
        manager.authenticate()
        
        # Fetch recent emails
        emails = manager.get_recent_emails(max_results=5, days_back=7)
        print(f"Found {len(emails)} recent emails")
        
        # Get summary
        summary = manager.summarize_emails(emails)
        print(summary)
    else:
        print("Skipped: credentials.json not found")
        print("Set up Gmail API credentials to use this feature\n")
        
except Exception as e:
    print(f"Note: {str(e)}\n")


# Example 5: Calendar module (requires Google Calendar credentials)
print("=" * 60)
print("Example 5: Calendar (requires credentials)")
print("=" * 60)

try:
    from ai_assistant.modules.calendar import CalendarManager
    
    # Note: This will only work if you have set up Google Calendar API credentials
    if os.path.exists('credentials.json'):
        manager = CalendarManager()
        manager.authenticate()
        
        # Fetch upcoming events
        events = manager.get_upcoming_events(max_results=5, days_ahead=7)
        print(f"Found {len(events)} upcoming events")
        
        # Format events
        formatted = manager.format_events(events)
        print(formatted)
    else:
        print("Skipped: credentials.json not found")
        print("Set up Google Calendar API credentials to use this feature\n")
        
except Exception as e:
    print(f"Note: {str(e)}\n")


print("=" * 60)
print("Examples completed!")
print("=" * 60)
