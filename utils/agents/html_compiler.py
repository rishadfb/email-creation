"""
HTML compilation agent for the Email Creation application.

This module implements the HTML compilation agent, which is responsible
for compiling the final HTML email with content and images.
"""
import asyncio
from typing import Dict
from .base import HtmlCompiler
from ..services.ai_service import GeminiService
from ..services.template_service import TemplateService
from ..core.exceptions import EmailCompilationError

class GeminiHtmlCompiler(HtmlCompiler):
    """HTML compilation agent using Gemini AI for image generation"""
    
    def __init__(self):
        """Initialize the HTML compilation agent"""
        super().__init__()
        self.ai_service = GeminiService()
        self.template_service = TemplateService()
        
    async def execute(self, *args, **kwargs) -> str:
        """Execute the agent's primary function"""
        return await self.compile_html(
            template=kwargs.get('template', ''),
            content=kwargs.get('content', {})
        )
        
    async def compile_html(self, template: str, content: Dict) -> str:
        """
        Compile the email HTML with content and images
        
        Args:
            template: Name of the template to use
            content: Dictionary containing content and image URLs to inject
            
        Returns:
            Compiled HTML
        """
        try:
            self.update_status("Processing template", 0.3)
            
            # Render the template with the content (which now includes images)
            html = self.template_service.render_template(
                template_name=template,
                content=content
            )
            
            if not html:
                raise EmailCompilationError("Failed to generate HTML")
            
            self.update_status("Validating HTML", 0.7)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            # Basic HTML validation
            if not html.strip().startswith('<') or not html.strip().endswith('>'):
                raise EmailCompilationError("Generated HTML appears to be invalid")
            
            self.update_status("Email ready", 1.0)
            return html
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise EmailCompilationError(f"Email compilation failed: {str(e)}")
    

