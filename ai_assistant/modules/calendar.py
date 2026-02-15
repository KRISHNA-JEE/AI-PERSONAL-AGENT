"""
Calendar Module for AI Personal Assistant

This module integrates with Google Calendar API to manage events and scheduling.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .logging_module import get_logger

# Load environment variables
load_dotenv()

logger = get_logger()

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarManager:
    """
    Calendar manager for Google Calendar integration.
    
    This class handles authentication and event management with Google Calendar API,
    providing functionality to fetch and display upcoming events.
    
    Attributes:
        credentials_file (str): Path to Calendar credentials JSON file
        token_file (str): Path to store OAuth token
        service: Google Calendar API service instance
    """
    
    def __init__(self):
        """
        Initialize the Calendar Manager.
        
        Raises:
            FileNotFoundError: If credentials file is not found
        """
        self.credentials_file = os.getenv('CALENDAR_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('CALENDAR_TOKEN_FILE', 'calendar_token.json')
        self.service = None
        
        logger.info("Calendar Manager initialized")
    
    def authenticate(self) -> None:
        """
        Authenticate with Google Calendar API using OAuth2.
        
        This method handles the OAuth2 flow and stores the token for future use.
        
        Raises:
            FileNotFoundError: If credentials file is not found
            Exception: If authentication fails
        """
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
                logger.debug("Loaded existing credentials from token file")
            except Exception as e:
                logger.warning(f"Error loading credentials: {str(e)}")
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed expired credentials")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {str(e)}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    raise FileNotFoundError(
                        f"Calendar credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("New credentials obtained")
                except Exception as e:
                    logger.error(f"Authentication failed: {str(e)}", exc_info=True)
                    raise
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
                logger.debug("Credentials saved to token file")
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Calendar service initialized successfully")
        except Exception as e:
            logger.error(f"Error building Calendar service: {str(e)}", exc_info=True)
            raise
    
    def get_upcoming_events(self, max_results: int = 10, days_ahead: int = 7) -> List[Dict]:
        """
        Fetch upcoming events from Google Calendar.
        
        Args:
            max_results (int): Maximum number of events to fetch
            days_ahead (int): Number of days to look ahead
            
        Returns:
            List[Dict]: List of upcoming events with details
            
        Raises:
            Exception: If not authenticated or API request fails
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            # Calculate time range
            now = datetime.now(timezone.utc)
            time_min = now.isoformat().replace('+00:00', 'Z')
            time_max = (now + timedelta(days=days_ahead)).isoformat().replace('+00:00', 'Z')
            
            logger.debug(f"Fetching events from {time_min} to {time_max}")
            
            # Call Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                logger.info("No upcoming events found")
                return []
            
            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                event_data = {
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                    'status': event.get('status', '')
                }
                
                event_list.append(event_data)
            
            logger.info(f"Successfully fetched {len(event_list)} events")
            return event_list
            
        except HttpError as error:
            logger.error(f"Calendar API error: {error}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}", exc_info=True)
            raise
    
    def format_events(self, events: List[Dict]) -> str:
        """
        Format events into a readable string.
        
        Args:
            events (List[Dict]): List of event data
            
        Returns:
            str: Formatted string of events
        """
        if not events:
            return "No upcoming events scheduled."
        
        formatted = f"You have {len(events)} upcoming event(s):\n\n"
        
        for i, event in enumerate(events, 1):
            formatted += f"{i}. {event['summary']}\n"
            
            # Format start time
            try:
                start_dt = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                formatted += f"   When: {start_dt.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
            except Exception:
                formatted += f"   When: {event['start']}\n"
            
            if event['location']:
                formatted += f"   Where: {event['location']}\n"
            
            if event['description']:
                desc = event['description'][:100]
                formatted += f"   Details: {desc}...\n"
            
            formatted += "\n"
        
        logger.info("Events formatted successfully")
        return formatted


def get_calendar_events(max_results: int = 10, days_ahead: int = 7) -> str:
    """
    Convenience function to get upcoming calendar events.
    
    Args:
        max_results (int): Maximum number of events to fetch
        days_ahead (int): Number of days to look ahead
        
    Returns:
        str: Formatted string of upcoming events
    """
    manager = CalendarManager()
    manager.authenticate()
    events = manager.get_upcoming_events(max_results, days_ahead)
    return manager.format_events(events)
