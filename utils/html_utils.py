import os
from typing import Dict, Optional
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
from bs4 import BeautifulSoup

class HTMLProcessor:
    """Process HTML templates with content and generated images"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Gemini API key for image generation"""
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        self.client = genai.Client(api_key=api_key)
    
    def generate_image(self, prompt: str) -> str:
        """
        Generate an image using Imagen 3.0
        
        Args:
            prompt: Description of the image to generate
            
        Returns:
            Base64 encoded image data ready for HTML embedding
        """
        try:
            response = self.client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                )
            )
            
            # Get the first generated image
            image_bytes = response.generated_images[0].image.image_bytes
            
            # Convert to base64 for HTML embedding
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
            
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            # Return a placeholder image URL
            return "https://via.placeholder.com/500x300"
    
    def generate_email_images(self, content: Dict[str, str]) -> Dict[str, str]:
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
        images['HERO_IMAGE'] = self.generate_image(hero_prompt)
        
        # Generate feature images based on feature content
        feature1_prompt = f"""
        Create a professional illustration representing: {content['feature1_title']}
        The illustration should convey: {content['feature1_text']}
        Make it modern, clean, and iconic.
        Use a style suitable for business communication.
        Avoid text in the image.
        Focus on simple, clear visual metaphors.
        """
        images['FEATURE1_IMAGE'] = self.generate_image(feature1_prompt)
        
        feature2_prompt = f"""
        Create a professional illustration representing: {content['feature2_title']}
        The illustration should convey: {content['feature2_text']}
        Make it modern, clean, and iconic.
        Match the style of the first feature image.
        Avoid text in the image.
        Focus on simple, clear visual metaphors.
        """
        images['FEATURE2_IMAGE'] = self.generate_image(feature2_prompt)
        
        # Generate highlight section image
        highlight_prompt = f"""
        Create an impactful image for: {content['highlight_title']}
        The image should represent: {content['highlight_text']}
        Make it bold and attention-grabbing while maintaining professionalism.
        Use a style that stands out but matches the email's aesthetic.
        Avoid text in the image.
        Focus on creating visual impact.
        """
        images['HIGHLIGHT_IMAGE'] = self.generate_image(highlight_prompt)
        
        return images
    
    def process_template(self, template_path: str, content: Dict[str, str]) -> str:
        """
        Process an HTML template with content and generated images
        
        Args:
            template_path: Path to the HTML template file
            content: Dictionary containing content to inject
            
        Returns:
            Processed HTML with content and images
        """
        # Read template
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Generate images based on content
        images = self.generate_email_images(content)
        
        # Combine content and images
        replacements = {**content, **images}
        
        # Process template
        soup = BeautifulSoup(template, 'html.parser')
        
        # Replace all placeholders
        html = template
        for key, value in replacements.items():
            placeholder = f"<!-- {key} -->"
            html = html.replace(placeholder, str(value))
        
        return html
    
    @staticmethod
    def load_template(template_path: str) -> str:
        """
        Load an HTML template from file
        
        Args:
            template_path: Path to the HTML template file
            
        Returns:
            Template content as string
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        with open(template_path, 'r') as f:
            return f.read()
    
    @staticmethod
    def inject_content(template: str, content: Dict[str, str]) -> str:
        """
        Inject generated content into HTML template
        
        Args:
            template: HTML template string
            content: Dictionary containing content to inject:
                    - subject
                    - preheader
                    - headline
                    - body
                    - cta_text
                    
        Returns:
            Processed HTML with content injected
        """
        soup = BeautifulSoup(template, 'lxml')
        
        # Replace title/subject
        title_tag = soup.find('title')
        if title_tag:
            title_tag.string = content.get('subject', '')
        
        # Replace content in HTML comments
        html = str(soup)
        replacements = {
            '<!-- SUBJECT -->': content.get('subject', ''),
            '<!-- HEADLINE -->': content.get('headline', ''),
            '<!-- BODY -->': content.get('body', ''),
            '<!-- CTA_TEXT -->': content.get('cta_text', ''),
            '<!-- CTA_LINK -->': '#', # Default link
            '<!-- UNSUBSCRIBE_LINK -->': '#', # Default unsubscribe
            '<!-- HEADER_IMAGE -->': '', # No image by default
        }
        
        for old, new in replacements.items():
            html = html.replace(old, new)
        
        return html
    
    @staticmethod
    def get_available_templates(templates_dir: str) -> list:
        """
        Get list of available template names in the templates directory
        
        Args:
            templates_dir: Path to templates directory
            
        Returns:
            List of template names (without .html extension)
        """
        if not os.path.exists(templates_dir):
            return []
            
        templates = []
        for file in os.listdir(templates_dir):
            if file.endswith('.html'):
                templates.append(file[:-5])  # Remove .html extension
        return templates 