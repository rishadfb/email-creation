"""
AI Service for the Email Creation application.

This module provides a unified interface for AI-related functionality,
abstracting away the details of specific AI providers.
"""
import json
from typing import Dict, List, Optional
from google import genai
from google.genai import types
import base64
from ..core.config import get_api_key, get_app_setting
from ..core.exceptions import AIServiceError, ContentGenerationError

class AIService:
    """Base class for AI services"""
    
    def __init__(self, service_name: str):
        """Initialize the AI service"""
        self.service_name = service_name


class GeminiService(AIService):
    """Service for interacting with Google's Gemini AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini service with an API key"""
        super().__init__("Gemini")
        
        api_key = api_key or get_api_key("GEMINI_API_KEY")
        if not api_key:
            raise AIServiceError("API key is required", self.service_name)
        
        self.client = genai.Client(api_key=api_key)
    
    def select_template(self, campaign_intent: str, templates: List[str]) -> str:
        """
        Select the best template for an email campaign based on its intent
        
        Args:
            campaign_intent: Description of the campaign's purpose and goals
            templates: List of available template names
            
        Returns:
            Name of the selected template
        """
        # Create a mapping of template types to descriptions for better selection
        template_descriptions = {
            'welcome/welcome_email.html': 'Welcome email for new customers or users, focused on onboarding and introduction to services/products',
            'announcements/product_launch.html': 'Product announcement email for launching new products or services, highlighting features and benefits',
            'newsletters/monthly_newsletter.html': 'Monthly newsletter format with multiple sections for updates, articles, and regular communications'
        }
        
        # Create descriptions for any templates not in our mapping
        for template in templates:
            if template not in template_descriptions:
                # Extract basic info from the template name
                parts = template.replace('.html', '').split('/')
                if len(parts) > 1:
                    category = parts[0]
                    name = parts[1]
                else:
                    category = 'general'
                    name = parts[0]
                template_descriptions[template] = f"{name.replace('_', ' ').title()} email in the {category} category"
        
        # Build a more informative prompt with template descriptions
        prompt = f"""
        Select the most appropriate email template for the following campaign:
        
        Campaign Intent:
        {campaign_intent}
        
        Available Templates:
        {', '.join([f"{t} - {desc}" for t, desc in template_descriptions.items() if t in templates])}
        
        Consider the following factors:
        - The primary goal of the campaign (welcome, announcement, newsletter, etc.)
        - The type of content needed (promotional, informational, onboarding, etc.)
        - The expected engagement level
        - The complexity of the message
        
        Return only the exact template name (including folder path) that would be most effective.
        """
        
        # Get model from configuration
        model = get_app_setting("models.template_selection")
        
        try:
            # Generate content using configured model
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            raise AIServiceError(f"Template selection failed: {str(e)}", self.service_name)
    
    def generate_email_content(
        self,
        contact: Dict,
        template: str,
        campaign_purpose: str
    ) -> Dict[str, str]:
        """
        Generate personalized email content for a contact
        
        Args:
            contact: Dictionary containing contact information
            template: Name of the selected template
            campaign_purpose: Description of the campaign purpose
            
        Returns:
            Dictionary containing generated content fields
        """
        prompt = f"""
        Generate personalized email content for the following contact and campaign:
        
        Contact:
        - Name: {contact.get('first_name', '')}
        - Job Title: {contact.get('job_title', '')}
        - Company: {contact.get('company', '')}
        - Industry: {contact.get('industry', '')}
        
        Template: {template}
        Campaign Purpose: {campaign_purpose}
        
        IMPORTANT: Do NOT use placeholders like [Your Company Name] or [Your Software Name] in your response. 
        Instead, use specific, relevant names based on the campaign purpose. For example, if it's a software product, 
        give it a specific name like "Streamline Pro" or "TaskMaster". If it's for a company, use the actual company 
        name from the contact information or create a specific, realistic company name.
        
        Generate a JSON object with the following fields:
        - subject: Compelling, personalized subject line with the contact's name and without placeholders
        - preheader: Preview text that appears in email clients, without placeholders
        - headline: Main email heading that includes the contact's name and company, without placeholders
        - subheadline: Supporting text under headline, without placeholders
        - welcome_message: Personalized welcome paragraph that mentions the contact's name, job title, and company, without placeholders
        - company_name: Use the sender's company name based on the campaign purpose (not the contact's company), without placeholders
        - feature1_title: First feature heading, without placeholders
        - feature1_text: First feature description, without placeholders
        - feature2_title: Second feature heading, without placeholders
        - feature2_text: Second feature description, without placeholders
        - highlight_title: Special highlight section heading, without placeholders
        - highlight_text: Special highlight description, without placeholders
        - cta_headline: Call to action section heading, without placeholders
        - cta_text: Action-oriented button text, without placeholders
        
        Make the content professional, engaging, and personalized to the contact's role and industry.
        Return ONLY the JSON object with no additional text or formatting.
        """
        
        # Get model from configuration
        model = get_app_setting("models.content_generation")
        
        try:
            # Generate content using configured model
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            
            # Clean up the response text to handle markdown code blocks
            text = response.text.strip()
            if text.startswith('```'):
                # Remove the first line (```json or similar)
                text = text.split('\n', 1)[1]
            if text.endswith('```'):
                # Remove the last line (```)
                text = text.rsplit('\n', 1)[0]
            
            # Parse the cleaned JSON
            content = json.loads(text)
            
            required_keys = {
                'subject', 'preheader', 'headline', 'subheadline', 'welcome_message',
                'company_name', 'feature1_title', 'feature1_text', 'feature2_title',
                'feature2_text', 'highlight_title', 'highlight_text', 'cta_headline',
                'cta_text'
            }
            
            if not all(key in content for key in required_keys):
                missing_keys = required_keys - set(content.keys())
                raise ValueError(f"Missing required content fields: {missing_keys}")
                
            return content
            
        except (json.JSONDecodeError, ValueError) as e:
            # Raise a more specific exception with context
            raise ContentGenerationError(f"Error parsing Gemini response: {str(e)}. Raw response: {response.text}")
        except Exception as e:
            raise AIServiceError(f"Content generation failed: {str(e)}", self.service_name)
    
    def generate_image(self, prompt: str) -> str:
        """
        Generate an image using Imagen
        
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
            # Log the error but use a fallback image to avoid breaking the email
            error_msg = f"Error generating image: {str(e)}"
            # We could raise an exception here, but it's better to degrade gracefully
            # raise AIServiceError(error_msg, f"{self.service_name} Image Generation")
            # Return a placeholder image URL
            return "https://via.placeholder.com/500x300"
