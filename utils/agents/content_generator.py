"""
Content generation agent for the Email Creation application.

This module implements the content generation agent, which is responsible
for generating personalized email content based on contact data and campaign purpose.
"""
import asyncio
from typing import Dict
from .base import ContentGenerator
from ..services.ai_service import GeminiService
from ..core.exceptions import ContentGenerationError

class GeminiContentGenerator(ContentGenerator):
    """Content generation agent using Gemini AI"""
    
    def __init__(self):
        """Initialize the content generation agent"""
        super().__init__()
        self.ai_service = GeminiService()
        
    async def execute(self, *args, **kwargs) -> Dict[str, str]:
        """Execute the agent's primary function"""
        return await self.generate_content(
            contact=kwargs.get('contact', {}),
            campaign_purpose=kwargs.get('campaign_purpose', '')
        )
        
    async def generate_content(self, contact: Dict, campaign_purpose: str) -> Dict[str, str]:
        """
        Generate personalized email content
        
        Args:
            contact: Dictionary containing contact information
            campaign_purpose: Description of the campaign purpose
            
        Returns:
            Dictionary containing generated content fields
        """
        try:
            self.update_status("Analyzing contact data", 0.2)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            self.update_status("Generating content", 0.5)
            content = self.ai_service.generate_email_content(
                contact=contact,
                template="welcome_email.html",  # Template name will be updated later
                campaign_purpose=campaign_purpose
            )
            
            if not content:
                raise ContentGenerationError("Failed to generate content")
            
            self.update_status("Refining personalization", 0.8)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            # Validate required content fields - updated to match what Gemini generates
            required_fields = {
                'subject', 'preheader', 'headline', 'subheadline', 'welcome_message',
                'company_name', 'feature1_title', 'feature1_text', 'feature2_title',
                'feature2_text', 'highlight_title', 'highlight_text', 'cta_headline',
                'cta_text'
            }
            missing_fields = required_fields - set(content.keys())
            if missing_fields:
                raise ContentGenerationError(f"Missing required content fields: {missing_fields}")
            
            self.update_status("Content ready", 1.0)
            return content
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise ContentGenerationError(f"Content generation failed: {str(e)}")
