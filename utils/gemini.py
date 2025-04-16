import os
import json
from typing import Dict, List, Optional
from google import genai
from google.genai import types

class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client with an API key"""
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        self.client = genai.Client(api_key=api_key)
    
    def select_template(self, campaign_intent: str, templates: List[str]) -> str:
        """
        Select the best template for an email campaign based on its intent
        
        Args:
            campaign_intent: Description of the campaign's purpose and goals
                           (e.g., "Welcome email for new software users",
                                 "Monthly newsletter for existing customers",
                                 "Product launch announcement")
            templates: List of available template names
            
        Returns:
            Name of the selected template
        """
        prompt = f"""
        Select the most appropriate email template for the following campaign:
        
        Campaign Intent:
        {campaign_intent}
        
        Available Templates:
        {', '.join(templates)}
        
        Consider the following factors:
        - The primary goal of the campaign
        - The type of content needed (promotional, informational, onboarding, etc.)
        - The expected engagement level
        - The complexity of the message
        
        Return only the template name that would be most effective.
        """
        
        # Simple approach without temperature or other settings
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",  # Using the faster model for template selection
            contents=prompt
        )
        return response.text.strip()
    
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
            Dictionary containing generated content fields:
            - subject
            - preheader
            - headline
            - body
            - cta_text
            - company_name (for template)
            - feature1_title
            - feature1_text
            - feature2_title
            - feature2_text
            - highlight_title
            - highlight_text
            - cta_headline
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
        
        Generate a JSON object with the following fields:
        - subject: Compelling, personalized subject line
        - preheader: Preview text that appears in email clients
        - headline: Main email heading
        - subheadline: Supporting text under headline
        - welcome_message: Personalized welcome paragraph
        - company_name: Company name for branding
        - feature1_title: First feature heading
        - feature1_text: First feature description
        - feature2_title: Second feature heading
        - feature2_text: Second feature description
        - highlight_title: Special highlight section heading
        - highlight_text: Special highlight description
        - cta_headline: Call to action section heading
        - cta_text: Action-oriented button text
        
        Make the content professional, engaging, and personalized to the contact's role and industry.
        Format the response as a valid JSON object.
        """
        
        # Simple approach without temperature or other settings
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",  # Switch to the pro model for content generation
            contents=prompt
        )
        
        try:
            # Safely parse JSON response
            content = json.loads(response.text)
            
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
            print(f"Error parsing Gemini response: {str(e)}")
            print(f"Raw response: {response.text}")
            
            # Return default content structure
            return {
                'subject': 'Welcome to Our Service',
                'preheader': 'Get started with your new account',
                'headline': 'Welcome Aboard',
                'subheadline': 'We are excited to have you join us',
                'welcome_message': 'Thank you for choosing our service',
                'company_name': contact.get('company', 'Our Company'),
                'feature1_title': 'Feature 1',
                'feature1_text': 'Description of our first key feature',
                'feature2_title': 'Feature 2',
                'feature2_text': 'Description of our second key feature',
                'highlight_title': 'Special Offer',
                'highlight_text': 'Learn more about our special welcome offer',
                'cta_headline': 'Get Started Today',
                'cta_text': 'Activate Your Account'
            } 