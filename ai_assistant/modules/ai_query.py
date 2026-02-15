"""
AI Query Module for AI Personal Assistant

This module integrates with OpenAI's ChatGPT API to handle natural language queries
and provide intelligent responses.
"""

import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
from openai import OpenAI

from .logging_module import get_logger

# Load environment variables
load_dotenv()

logger = get_logger()


class AIQuery:
    """
    AI Query handler using OpenAI's ChatGPT API.
    
    This class manages interactions with the ChatGPT API for processing
    user queries and generating intelligent responses.
    
    Attributes:
        client (OpenAI): OpenAI client instance
        model (str): The GPT model to use (default: gpt-3.5-turbo)
        conversation_history (List[Dict]): Chat history for context
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the AI Query module.
        
        Args:
            model (str): The GPT model to use
            
        Raises:
            ValueError: If OPENAI_API_KEY is not set in environment
        """
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY must be set in .env file")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info(f"AI Query module initialized with model: {model}")
    
    def query(self, prompt: str, use_history: bool = True) -> str:
        """
        Send a query to ChatGPT and get a response.
        
        Args:
            prompt (str): The user's query
            use_history (bool): Whether to include conversation history
            
        Returns:
            str: The AI's response
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.debug(f"Sending query to ChatGPT: {prompt[:50]}...")
            
            # Prepare messages
            messages = []
            if use_history and self.conversation_history:
                messages = self.conversation_history.copy()
            
            messages.append({"role": "user", "content": prompt})
            
            # Make API request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            if use_history:
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                # Keep only last 10 messages to avoid token limits
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
            
            logger.info("Query processed successfully")
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error processing AI query: {str(e)}", exc_info=True)
            raise
    
    def clear_history(self) -> None:
        """
        Clear the conversation history.
        """
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List[Dict[str, str]]: The conversation history
        """
        return self.conversation_history.copy()
    
    def set_system_prompt(self, system_prompt: str) -> None:
        """
        Set a system prompt to guide the AI's behavior.
        
        Args:
            system_prompt (str): The system prompt to use
        """
        # Insert system prompt at the beginning
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0] = {"role": "system", "content": system_prompt}
        else:
            self.conversation_history.insert(0, {"role": "system", "content": system_prompt})
        
        logger.info("System prompt set")


def query_ai(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Convenience function to query AI without managing instance.
    
    Args:
        prompt (str): The user's query
        model (str): The GPT model to use
        
    Returns:
        str: The AI's response
    """
    ai = AIQuery(model=model)
    return ai.query(prompt, use_history=False)
