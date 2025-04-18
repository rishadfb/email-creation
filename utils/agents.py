import asyncio
from typing import Dict, List, Optional, Callable
import streamlit as st
from .gemini import GeminiClient
from .html_utils import HTMLProcessor

class BaseAgent:
    def __init__(self):
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

class TemplateSelectionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.gemini = GeminiClient()
        
    async def run(self, campaign_intent: str, templates: List[str]) -> str:
        """Select the best template for the campaign"""
        try:
            self.update_status("Analyzing campaign intent", 0.3)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            self.update_status("Evaluating templates", 0.6)
            template = self.gemini.select_template(
                campaign_intent=campaign_intent,
                templates=templates
            )
            
            if not template:
                raise ValueError("No suitable template found")
            
            self.update_status("Template selected", 1.0)
            return template
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise

class ContentGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.gemini = GeminiClient()
        
    async def run(self, contact: Dict, campaign_purpose: str) -> Dict:
        """Generate personalized email content"""
        try:
            self.update_status("Analyzing contact data", 0.2)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            self.update_status("Generating content", 0.5)
            content = self.gemini.generate_email_content(
                contact=contact,
                template="welcome_email.html",  # Template name will be updated later
                campaign_purpose=campaign_purpose
            )
            
            if not content:
                raise ValueError("Failed to generate content")
            
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
                raise ValueError(f"Missing required content fields: {missing_fields}")
            
            self.update_status("Content ready", 1.0)
            return content
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise

class EmailCompilationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.html_processor = HTMLProcessor()
        
    async def run(self, template: str, content: Dict) -> str:
        """Compile the email HTML with content and images"""
        try:
            self.update_status("Generating images", 0.3)
            # Images are generated as part of process_template
            
            self.update_status("Processing template", 0.6)
            html = self.html_processor.process_template(
                template_path=f"templates/{template}",
                content=content
            )
            
            if not html:
                raise ValueError("Failed to generate HTML")
            
            self.update_status("Compiling final email", 0.9)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            # Basic HTML validation
            if not html.strip().startswith('<') or not html.strip().endswith('>'):
                raise ValueError("Generated HTML appears to be invalid")
            
            self.update_status("Email ready", 1.0)
            return html
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise 