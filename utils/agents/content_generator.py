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
        Generate personalized email content including text and images
        
        Args:
            contact: Dictionary containing contact information
            campaign_purpose: Description of the campaign purpose
            
        Returns:
            Dictionary containing generated content fields and image URLs
        """
        try:
            self.update_status("Analyzing contact data", 0.1)
            await asyncio.sleep(0.1)  # Allow UI to update
            
            self.update_status("Generating text content", 0.3)
            content = self.ai_service.generate_email_content(
                contact=contact,
                template="welcome_email.html",  # Template name will be updated later
                campaign_purpose=campaign_purpose
            )
            
            if not content:
                raise ContentGenerationError("Failed to generate content")
            
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
            
            # Generate images based on the content
            self.update_status("Generating images", 0.5)
            images = await self._generate_email_images(content)
            
            # Combine text content with image URLs
            content_with_images = {**content, **images}
            
            self.update_status("Content ready", 1.0)
            return content_with_images
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", 1.0)
            raise ContentGenerationError(f"Content generation failed: {str(e)}")
            
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
