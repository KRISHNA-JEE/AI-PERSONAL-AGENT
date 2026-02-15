"""
Email Module for AI Personal Assistant

This module integrates with Gmail API to fetch and summarize emails.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
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

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class EmailManager:
    """
    Email manager for Gmail integration.
    
    This class handles authentication and email retrieval from Gmail API,
    providing functionality to fetch and summarize recent emails.
    
    Attributes:
        credentials_file (str): Path to Gmail credentials JSON file
        token_file (str): Path to store OAuth token
        service: Gmail API service instance
    """
    
    def __init__(self):
        """
        Initialize the Email Manager.
        
        Raises:
            FileNotFoundError: If credentials file is not found
        """
        self.credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
        self.service = None
        
        logger.info("Email Manager initialized")
    
    def authenticate(self) -> None:
        """
        Authenticate with Gmail API using OAuth2.
        
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
                        f"Gmail credentials file '{self.credentials_file}' not found. "
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
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service initialized successfully")
        except Exception as e:
            logger.error(f"Error building Gmail service: {str(e)}", exc_info=True)
            raise
    
    def get_recent_emails(self, max_results: int = 10, days_back: int = 7) -> List[Dict]:
        """
        Fetch recent emails from Gmail.
        
        Args:
            max_results (int): Maximum number of emails to fetch
            days_back (int): Number of days to look back
            
        Returns:
            List[Dict]: List of email summaries with sender, subject, and snippet
            
        Raises:
            Exception: If not authenticated or API request fails
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            # Calculate date for query
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{after_date}'
            
            logger.debug(f"Fetching emails with query: {query}")
            
            # Call Gmail API
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No messages found")
                return []
            
            email_list = []
            for msg in messages:
                try:
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']
                    ).execute()
                    
                    headers = message.get('payload', {}).get('headers', [])
                    email_data = {
                        'id': message['id'],
                        'snippet': message.get('snippet', ''),
                        'from': '',
                        'subject': '',
                        'date': ''
                    }
                    
                    for header in headers:
                        name = header['name'].lower()
                        if name == 'from':
                            email_data['from'] = header['value']
                        elif name == 'subject':
                            email_data['subject'] = header['value']
                        elif name == 'date':
                            email_data['date'] = header['value']
                    
                    email_list.append(email_data)
                    
                except Exception as e:
                    logger.warning(f"Error fetching message {msg['id']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully fetched {len(email_list)} emails")
            return email_list
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
            raise
    
    def summarize_emails(self, emails: List[Dict]) -> str:
        """
        Create a text summary of emails.
        
        Args:
            emails (List[Dict]): List of email data
            
        Returns:
            str: Formatted summary of emails
        """
        if not emails:
            return "No emails to summarize."
        
        summary = f"Summary of {len(emails)} recent emails:\n\n"
        
        for i, email in enumerate(emails, 1):
            summary += f"{i}. From: {email['from']}\n"
            summary += f"   Subject: {email['subject']}\n"
            summary += f"   Preview: {email['snippet'][:100]}...\n"
            summary += f"   Date: {email['date']}\n\n"
        
        logger.info("Email summary generated")
        return summary


def get_email_summary(max_results: int = 10, days_back: int = 7) -> str:
    """
    Convenience function to get email summary.
    
    Args:
        max_results (int): Maximum number of emails to fetch
        days_back (int): Number of days to look back
        
    Returns:
        str: Formatted email summary
    """
    manager = EmailManager()
    manager.authenticate()
    emails = manager.get_recent_emails(max_results, days_back)
    return manager.summarize_emails(emails)
