"""
Reminders Module for AI Personal Assistant

This module manages task reminders with persistence using JSON storage.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from .logging_module import get_logger

# Load environment variables
load_dotenv()

logger = get_logger()


class RemindersManager:
    """
    Reminders manager for task tracking.
    
    This class provides functionality to create, list, complete, and delete
    reminders with persistent JSON storage.
    
    Attributes:
        reminders_file (str): Path to reminders JSON file
        reminders (List[Dict]): List of reminder objects
    """
    
    def __init__(self):
        """
        Initialize the Reminders Manager.
        
        Loads existing reminders from file or creates a new file.
        """
        self.reminders_file = os.getenv('REMINDERS_FILE', 'data/reminders.json')
        self.reminders: List[Dict] = []
        
        # Ensure data directory exists
        Path(self.reminders_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing reminders
        self._load_reminders()
        
        logger.info("Reminders Manager initialized")
    
    def _load_reminders(self) -> None:
        """
        Load reminders from JSON file.
        
        Creates an empty file if it doesn't exist.
        """
        try:
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r') as f:
                    self.reminders = json.load(f)
                logger.debug(f"Loaded {len(self.reminders)} reminders from file")
            else:
                self.reminders = []
                self._save_reminders()
                logger.debug("Created new reminders file")
        except json.JSONDecodeError:
            logger.error("Invalid JSON in reminders file, creating new file")
            self.reminders = []
            self._save_reminders()
        except Exception as e:
            logger.error(f"Error loading reminders: {str(e)}", exc_info=True)
            self.reminders = []
    
    def _save_reminders(self) -> None:
        """
        Save reminders to JSON file.
        
        Raises:
            Exception: If save operation fails
        """
        try:
            with open(self.reminders_file, 'w') as f:
                json.dump(self.reminders, f, indent=2)
            logger.debug("Reminders saved to file")
        except Exception as e:
            logger.error(f"Error saving reminders: {str(e)}", exc_info=True)
            raise
    
    def add_reminder(self, title: str, description: str = "", 
                     due_date: Optional[str] = None, priority: str = "medium") -> Dict:
        """
        Add a new reminder.
        
        Args:
            title (str): Reminder title
            description (str): Optional description
            due_date (str): Optional due date in ISO format (YYYY-MM-DD)
            priority (str): Priority level (low, medium, high)
            
        Returns:
            Dict: The created reminder object
        """
        reminder = {
            'id': self._generate_id(),
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority,
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        self.reminders.append(reminder)
        self._save_reminders()
        
        logger.info(f"Added reminder: {title}")
        return reminder
    
    def _generate_id(self) -> int:
        """
        Generate a unique ID for a new reminder.
        
        Returns:
            int: Unique reminder ID
        """
        if not self.reminders:
            return 1
        return max(r['id'] for r in self.reminders) + 1
    
    def get_reminders(self, show_completed: bool = False, 
                      priority: Optional[str] = None) -> List[Dict]:
        """
        Get all reminders with optional filtering.
        
        Args:
            show_completed (bool): Include completed reminders
            priority (str): Filter by priority level
            
        Returns:
            List[Dict]: Filtered list of reminders
        """
        filtered = self.reminders
        
        if not show_completed:
            filtered = [r for r in filtered if not r['completed']]
        
        if priority:
            filtered = [r for r in filtered if r['priority'] == priority]
        
        logger.debug(f"Retrieved {len(filtered)} reminders")
        return filtered
    
    def complete_reminder(self, reminder_id: int) -> bool:
        """
        Mark a reminder as completed.
        
        Args:
            reminder_id (int): ID of the reminder to complete
            
        Returns:
            bool: True if successful, False if reminder not found
        """
        for reminder in self.reminders:
            if reminder['id'] == reminder_id:
                reminder['completed'] = True
                reminder['completed_at'] = datetime.now().isoformat()
                self._save_reminders()
                logger.info(f"Completed reminder: {reminder['title']}")
                return True
        
        logger.warning(f"Reminder {reminder_id} not found")
        return False
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """
        Delete a reminder.
        
        Args:
            reminder_id (int): ID of the reminder to delete
            
        Returns:
            bool: True if successful, False if reminder not found
        """
        for i, reminder in enumerate(self.reminders):
            if reminder['id'] == reminder_id:
                deleted = self.reminders.pop(i)
                self._save_reminders()
                logger.info(f"Deleted reminder: {deleted['title']}")
                return True
        
        logger.warning(f"Reminder {reminder_id} not found")
        return False
    
    def format_reminders(self, reminders: Optional[List[Dict]] = None) -> str:
        """
        Format reminders into a readable string.
        
        Args:
            reminders (List[Dict]): List of reminders to format (uses all if None)
            
        Returns:
            str: Formatted string of reminders
        """
        if reminders is None:
            reminders = self.get_reminders()
        
        if not reminders:
            return "No active reminders."
        
        formatted = f"You have {len(reminders)} reminder(s):\n\n"
        
        for reminder in reminders:
            status = "✓" if reminder['completed'] else "○"
            priority_symbol = {
                'high': '!!!',
                'medium': '!!',
                'low': '!'
            }.get(reminder['priority'], '!!')
            
            formatted += f"{status} [{priority_symbol}] {reminder['title']}\n"
            
            if reminder['description']:
                formatted += f"   Description: {reminder['description']}\n"
            
            if reminder['due_date']:
                formatted += f"   Due: {reminder['due_date']}\n"
            
            formatted += f"   ID: {reminder['id']}\n\n"
        
        logger.debug("Reminders formatted successfully")
        return formatted


def add_reminder(title: str, description: str = "", 
                due_date: Optional[str] = None, priority: str = "medium") -> str:
    """
    Convenience function to add a reminder.
    
    Args:
        title (str): Reminder title
        description (str): Optional description
        due_date (str): Optional due date
        priority (str): Priority level
        
    Returns:
        str: Confirmation message
    """
    manager = RemindersManager()
    reminder = manager.add_reminder(title, description, due_date, priority)
    return f"Reminder added: {reminder['title']} (ID: {reminder['id']})"


def list_reminders(show_completed: bool = False) -> str:
    """
    Convenience function to list reminders.
    
    Args:
        show_completed (bool): Include completed reminders
        
    Returns:
        str: Formatted list of reminders
    """
    manager = RemindersManager()
    reminders = manager.get_reminders(show_completed)
    return manager.format_reminders(reminders)
