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
        Create a professional, minimalist hero banner image for {content['company_name']}.
        Concept: {content['welcome_message']}
        
        STYLE REQUIREMENTS:
        - Clean, modern aesthetic with subtle color palette
        - Minimalist composition with plenty of negative space
        - High-end corporate/professional look
        - Photorealistic, not illustrated or cartoon-like
        - Subtle lighting effects and shadows for depth
        
        IMPORTANT RESTRICTIONS:
        - NO TEXT whatsoever in the image
        - NO logos or explicit branding elements
        - NO busy patterns or distracting elements
        - NO people with recognizable faces
        - Image should be abstract enough to work in any industry
        """
        images['HERO_IMAGE'] = self.ai_service.generate_image(hero_prompt)
        
        # Generate feature images based on feature content
        feature1_prompt = f"""
        Create a professional image representing the concept: {content['feature1_title']}
        Core idea to convey: {content['feature1_text']}
        
        STYLE REQUIREMENTS:
        - Elegant, minimalist design with a single clear focal point
        - Soft, professional color palette that complements corporate branding
        - Clean lines and simple geometry
        - High-quality photorealistic rendering
        - Subtle shadows and lighting for dimension
        
        IMPORTANT RESTRICTIONS:
        - NO TEXT or typography elements whatsoever
        - NO cluttered compositions or busy backgrounds
        - NO cartoon-style illustrations
        - NO literal interpretations that look like stock photos
        - Image should use abstract visual metaphors rather than literal representations
        """
        images['FEATURE1_IMAGE'] = self.ai_service.generate_image(feature1_prompt)
        
        feature2_prompt = f"""
        Create a professional image representing the concept: {content['feature2_title']}
        Core idea to convey: {content['feature2_text']}
        
        STYLE REQUIREMENTS:
        - Elegant, minimalist design with a single clear focal point
        - Soft, professional color palette matching the first feature image
        - Clean lines and simple geometry
        - High-quality photorealistic rendering
        - Subtle shadows and lighting for dimension
        
        IMPORTANT RESTRICTIONS:
        - NO TEXT or typography elements whatsoever
        - NO cluttered compositions or busy backgrounds
        - NO cartoon-style illustrations
        - NO literal interpretations that look like stock photos
        - Image should use abstract visual metaphors rather than literal representations
        - MUST visually complement the first feature image in style and tone
        """
        images['FEATURE2_IMAGE'] = self.ai_service.generate_image(feature2_prompt)
        
        # Generate highlight section image
        highlight_prompt = f"""
        Create a premium, eye-catching image for the key highlight: {content['highlight_title']}
        Core message to convey: {content['highlight_text']}
        
        STYLE REQUIREMENTS:
        - Bold, sophisticated design with strong visual impact
        - Rich, premium color palette that stands out while complementing the other images
        - Elegant composition with a clear focal point
        - High-end photorealistic rendering with depth and dimension
        - Professional lighting effects that create visual interest
        
        IMPORTANT RESTRICTIONS:
        - ABSOLUTELY NO TEXT or typography elements
        - NO generic stock photo look or clichéd business imagery
        - NO cluttered or busy compositions
        - NO cartoon-style illustrations
        - Image should use sophisticated visual metaphors that feel premium and exclusive
        - Must harmonize with the other images while being slightly more impactful
        """
        images['HIGHLIGHT_IMAGE'] = self.ai_service.generate_image(highlight_prompt)
        
        return images
