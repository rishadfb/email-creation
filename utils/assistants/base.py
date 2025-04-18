"""
Base assistant class for the application.

This module provides the base assistant class that all assistants will inherit from.
"""
from abc import ABC, abstractmethod
import streamlit as st
from typing import Dict, Optional, List, Any, Callable

class Assistant(ABC):
    """Base class for all assistants in the application."""
    
    def __init__(self, name: str, emoji: str, description: str):
        """
        Initialize the assistant with basic information.
        
        Args:
            name: The name of the assistant
            emoji: The emoji to display next to the assistant name
            description: A short description of what the assistant does
        """
        self.name = name
        self.emoji = emoji
        self.description = description
        
    @property
    def display_name(self) -> str:
        """Return the formatted display name with emoji."""
        return f"{self.emoji} {self.name}"
    
    @abstractmethod
    def render_sidebar(self) -> None:
        """Render the assistant-specific sidebar content."""
        pass
    
    @abstractmethod
    def render_welcome(self) -> None:
        """Render the assistant-specific welcome message."""
        pass
    
    @abstractmethod
    def render_example_prompts(self) -> Optional[str]:
        """
        Render the assistant-specific example prompts.
        
        Returns:
            The selected example prompt if one was clicked, None otherwise
        """
        pass
    
    @abstractmethod
    async def process_prompt(self, prompt: str) -> None:
        """
        Process a user prompt and generate a response.
        
        Args:
            prompt: The user's prompt text
        """
        pass
    
    @abstractmethod
    def initialize_session_state(self) -> None:
        """Initialize any assistant-specific session state variables."""
        pass
