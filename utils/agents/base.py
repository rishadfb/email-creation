"""
Base agent interfaces for the Email Creation application.

This module defines abstract base classes for each agent type to ensure
consistent implementation across the application.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any

class Agent(ABC):
    """Base class for all agents"""
    
    def __init__(self):
        """Initialize the agent"""
        self.status = "idle"
        self.progress = 0.0
        self._status_callback: Optional[Callable[[str, float], None]] = None
        
    def set_status_callback(self, callback: Callable[[str, float], None]):
        """Set the callback for status updates"""
        self._status_callback = callback
        
    def update_status(self, status: str, progress: float):
        """Update agent status and progress"""
        self.status = status
        self.progress = progress
        if self._status_callback:
            self._status_callback(status, progress)
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's primary function"""
        pass


class TemplateSelector(Agent):
    """Interface for template selection agents"""
    
    @abstractmethod
    async def select_template(self, campaign_intent: str, templates: List[str]) -> str:
        """
        Select the best template for a campaign
        
        Args:
            campaign_intent: Description of the campaign's purpose and goals
            templates: List of available template names
            
        Returns:
            Name of the selected template
        """
        pass


class ContentGenerator(Agent):
    """Interface for content generation agents"""
    
    @abstractmethod
    async def generate_content(self, contact: Dict, campaign_purpose: str) -> Dict[str, str]:
        """
        Generate personalized email content
        
        Args:
            contact: Dictionary containing contact information
            campaign_purpose: Description of the campaign purpose
            
        Returns:
            Dictionary containing generated content fields
        """
        pass


class HtmlCompiler(Agent):
    """Interface for HTML compilation agents"""
    
    @abstractmethod
    async def compile_html(self, template: str, content: Dict) -> str:
        """
        Compile the email HTML with content and images
        
        Args:
            template: Name of the template to use
            content: Dictionary containing content to inject
            
        Returns:
            Compiled HTML
        """
        pass
