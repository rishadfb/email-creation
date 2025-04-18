"""
Assistant registry for the application.

This module provides a registry for all available assistants in the application.
"""
from typing import Dict, List, Type
import streamlit as st

from .base import Assistant
from .email_assistant import EmailAssistant

class AssistantRegistry:
    """Registry for all available assistants in the application."""
    
    def __init__(self):
        """Initialize the assistant registry."""
        self._assistants: Dict[str, Assistant] = {}
        self._register_default_assistants()
    
    def _register_default_assistants(self) -> None:
        """Register the default assistants."""
        self.register(EmailAssistant())
        # Register additional assistants here as they are implemented
    
    def register(self, assistant: Assistant) -> None:
        """
        Register a new assistant.
        
        Args:
            assistant: The assistant instance to register
        """
        self._assistants[assistant.name] = assistant
    
    def get_assistant(self, name: str) -> Assistant:
        """
        Get an assistant by name.
        
        Args:
            name: The name of the assistant to get
            
        Returns:
            The assistant instance
            
        Raises:
            KeyError: If no assistant with the given name exists
        """
        return self._assistants[name]
    
    def get_all_assistants(self) -> List[Assistant]:
        """
        Get all registered assistants.
        
        Returns:
            A list of all registered assistant instances
        """
        return list(self._assistants.values())
    
    def get_current_assistant(self) -> Assistant:
        """
        Get the currently selected assistant.
        
        Returns:
            The currently selected assistant instance
        """
        # Initialize session state if needed
        if "current_assistant_name" not in st.session_state:
            # Default to the first assistant
            assistants = self.get_all_assistants()
            if assistants:
                st.session_state.current_assistant_name = assistants[0].name
            else:
                raise ValueError("No assistants registered")
        
        # Get the current assistant
        return self.get_assistant(st.session_state.current_assistant_name)
    
    def set_current_assistant(self, name: str) -> None:
        """
        Set the currently selected assistant.
        
        Args:
            name: The name of the assistant to select
            
        Raises:
            KeyError: If no assistant with the given name exists
        """
        # Verify the assistant exists
        self.get_assistant(name)
        
        # Set the current assistant
        st.session_state.current_assistant_name = name

# Create a singleton instance
registry = AssistantRegistry()
