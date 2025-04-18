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
            content: Dictionary containing content to inject
            
        Returns:
            Compiled HTML
        """
        try:
            self.update_status("Generating images", 0.3)
            
            # Generate images based on content
            images = await self._generate_email_images(content)
            
            # Add images to content
            content_with_images = {**content, **images}
            
            self.update_status("Processing template", 0.6)
            html = self.template_service.render_template(
                template_name=template,
                content=content_with_images
            )
            
            if not html:
                raise EmailCompilationError("Failed to generate HTML")
            
            self.update_status("Compiling final email", 0.9)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            # Basic HTML validation
            if not html.strip().startswith('<') or not html.strip().endswith('>'):
                raise EmailCompilationError("Generated HTML appears to be invalid")
            
            self.update_status("Email ready", 1.0)
            return html
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise EmailCompilationError(f"Email compilation failed: {str(e)}")
    
    async def _generate_email_images(self, content: Dict) -> Dict[str, str]:
        """
        Generate all images needed for the email template based on content
        
        Args:
            content: Dictionary containing email content fields
            
        Returns:
            Dictionary of image placeholders and their generated image URLs
        """
        images = {}
        
        # Generate hero image based on welcome message and company
        hero_prompt = f"""
        Create a professional and modern hero banner image for {content['company_name']}.
        The image should reflect this message: {content['welcome_message']}
        Make it suitable for an email header with clean, corporate aesthetics.
        Ensure it's well-lit, professional, and engaging.
        The style should be photorealistic and high-quality.
        Include subtle branding elements and avoid text in the image.
        """
        images['HERO_IMAGE'] = self.ai_service.generate_image(hero_prompt)
        
        # Generate feature images based on feature content
        feature1_prompt = f"""
        Create a professional illustration representing: {content['feature1_title']}
        The illustration should convey: {content['feature1_text']}
        Make it modern, clean, and iconic.
        Use a style suitable for business communication.
        Avoid text in the image.
        Focus on simple, clear visual metaphors.
        """
        images['FEATURE1_IMAGE'] = self.ai_service.generate_image(feature1_prompt)
        
        feature2_prompt = f"""
        Create a professional illustration representing: {content['feature2_title']}
        The illustration should convey: {content['feature2_text']}
        Make it modern, clean, and iconic.
        Match the style of the first feature image.
        Avoid text in the image.
        Focus on simple, clear visual metaphors.
        """
        images['FEATURE2_IMAGE'] = self.ai_service.generate_image(feature2_prompt)
        
        # Generate highlight section image
        highlight_prompt = f"""
        Create an impactful image for: {content['highlight_title']}
        The image should represent: {content['highlight_text']}
        Make it bold and attention-grabbing while maintaining professionalism.
        Use a style that complements the other images.
        Focus on a clean, modern aesthetic.
        Avoid text in the image.
        """
        images['HIGHLIGHT_IMAGE'] = self.ai_service.generate_image(highlight_prompt)
        
        return images
