"""
Template selection agent for the Email Creation application.

This module implements the template selection agent, which is responsible
for selecting the most appropriate email template based on campaign intent.
"""
import asyncio
from typing import List
from .base import TemplateSelector
from ..services.ai_service import GeminiService
from ..services.template_service import TemplateService
from ..core.exceptions import TemplateSelectionError

class GeminiTemplateSelector(TemplateSelector):
    """Template selection agent using Gemini AI"""
    
    def __init__(self):
        """Initialize the template selection agent"""
        super().__init__()
        self.ai_service = GeminiService()
        self.template_service = TemplateService()
        
    async def execute(self, *args, **kwargs) -> str:
        """Execute the agent's primary function"""
        return await self.select_template(
            campaign_intent=kwargs.get('campaign_intent', ''),
            templates=kwargs.get('templates', [])
        )
        
    async def select_template(self, campaign_intent: str, templates: List[str]) -> str:
        """
        Select the best template for a campaign
        
        Args:
            campaign_intent: Description of the campaign's purpose and goals
            templates: List of available template names
            
        Returns:
            Name of the selected template
        """
        try:
            self.update_status("Analyzing campaign intent", 0.3)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            # If no templates are provided, get all available templates
            if not templates:
                templates = self.template_service.get_available_templates()
                
            if not templates:
                raise TemplateSelectionError("No templates available")
            
            self.update_status("Evaluating templates", 0.6)
            template = self.ai_service.select_template(
                campaign_intent=campaign_intent,
                templates=templates
            )
            
            if not template:
                raise TemplateSelectionError("No suitable template found")
            
            # Map common campaign types to specific templates if AI didn't select a specific one
            template_mapping = {
                'welcome': 'welcome/welcome_email.html',
                'onboarding': 'welcome/welcome_email.html',
                'product launch': 'announcements/product_launch.html',
                'announcement': 'announcements/product_launch.html',
                'newsletter': 'newsletters/monthly_newsletter.html',
                'monthly': 'newsletters/monthly_newsletter.html'
            }
            
            # Check if the template exists directly
            if template not in templates:
                # Try to find a template based on keywords in the campaign intent
                for keyword, mapped_template in template_mapping.items():
                    if keyword.lower() in campaign_intent.lower():
                        if mapped_template in templates:
                            template = mapped_template
                            break
                else:
                    # Try to find a close match by name
                    for t in templates:
                        if template.lower() in t.lower():
                            template = t
                            break
                    else:
                        # If no match is found, use the first template
                        template = templates[0]
            
            self.update_status("Template selected", 1.0)
            return template
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise TemplateSelectionError(f"Template selection failed: {str(e)}")
