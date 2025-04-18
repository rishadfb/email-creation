"""
Template Service for the Email Creation application.

This module provides functionality for managing email templates,
including discovery, validation, and metadata extraction.
"""
import os
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from datetime import datetime
from ..core.exceptions import TemplateNotFoundError, TemplateError

class TemplateService:
    """Service for managing email templates"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template service
        
        Args:
            templates_dir: Path to the templates directory
        """
        self.templates_dir = templates_dir
        # Use a FileSystemLoader that includes both the templates directory and all subdirectories
        self.env = Environment(loader=FileSystemLoader([templates_dir, 
                                                       os.path.join(templates_dir, "welcome"),
                                                       os.path.join(templates_dir, "announcements"),
                                                       os.path.join(templates_dir, "newsletters")]))
        
    def get_available_templates(self) -> List[str]:
        """
        Get list of available template names in the templates directory
        
        Returns:
            List of template names (without .html extension)
        """
        if not os.path.exists(self.templates_dir):
            return []
            
        templates = []
        for file in os.listdir(self.templates_dir):
            if file.endswith('.html'):
                templates.append(file)
        
        # Also check subdirectories
        for subdir in os.listdir(self.templates_dir):
            subdir_path = os.path.join(self.templates_dir, subdir)
            if os.path.isdir(subdir_path):
                for file in os.listdir(subdir_path):
                    if file.endswith('.html'):
                        templates.append(f"{subdir}/{file}")
        
        return templates
    
    def get_template_metadata(self, template_name: str) -> Dict:
        """
        Extract metadata from a template
        
        Args:
            template_name: Name of the template (with .html extension)
            
        Returns:
            Dictionary containing template metadata
        """
        template_path = self._get_template_path(template_name)
        
        try:
            with open(template_path, 'r') as f:
                content = f.read()
                
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract metadata from HTML comments or meta tags
            metadata = {
                'name': template_name,
                'title': soup.title.string if soup.title else template_name,
                'description': self._extract_meta_description(soup),
                'category': self._determine_category(template_name),
                'required_fields': self._extract_required_fields(content),
            }
            
            return metadata
            
        except Exception as e:
            raise TemplateError(f"Error extracting metadata from template {template_name}: {str(e)}")
    
    def render_template(self, template_name: str, content: Dict) -> str:
        """
        Render a template with content
        
        Args:
            template_name: Name of the template (with .html extension)
            content: Dictionary containing content to inject
            
        Returns:
            Rendered HTML
        """
        try:
            # Get the template
            template = self.env.get_template(template_name)
            
            # Prepare template variables
            template_vars = {
                # Email metadata
                'subject': content.get('subject', ''),
                'preheader': content.get('preheader', ''),
                
                # Main content
                'headline': content.get('headline', ''),
                'subheadline': content.get('subheadline', ''),
                'welcome_message': content.get('welcome_message', ''),
                
                # Company info
                'company_name': content.get('company_name', ''),
                'company_address': content.get('company_address', ''),
                'logo_url': content.get('logo_url', ''),
                
                # Features
                'feature1_title': content.get('feature1_title', ''),
                'feature1_text': content.get('feature1_text', ''),
                'feature2_title': content.get('feature2_title', ''),
                'feature2_text': content.get('feature2_text', ''),
                
                # Highlight section
                'highlight_title': content.get('highlight_title', ''),
                'highlight_text': content.get('highlight_text', ''),
                
                # CTA section
                'cta_headline': content.get('cta_headline', ''),
                'cta_text': content.get('cta_text', ''),
                'cta_button': bool(content.get('cta_text')),
                'cta_url': content.get('cta_url', '#'),
                
                # Footer links
                'privacy_link': content.get('privacy_link', '#'),
                'terms_link': content.get('terms_link', '#'),
                'unsubscribe_link': content.get('unsubscribe_link', '#'),
                
                # Metadata
                'year': datetime.now().year,
            }
            
            # Add images if they exist in content
            for key, value in content.items():
                if key.endswith('_IMAGE'):
                    template_vars[key] = value
            
            # Render the template
            return template.render(**template_vars)
            
        except Exception as e:
            raise TemplateError(f"Error rendering template {template_name}: {str(e)}")
    
    def _get_template_path(self, template_name: str) -> str:
        """
        Get the full path to a template
        
        Args:
            template_name: Name of the template (with .html extension)
            
        Returns:
            Full path to the template
        """
        # Check if template includes a subdirectory
        if '/' in template_name:
            template_path = os.path.join(self.templates_dir, template_name)
        else:
            template_path = os.path.join(self.templates_dir, template_name)
            
        if not os.path.exists(template_path):
            raise TemplateNotFoundError(f"Template not found: {template_path}")
            
        return template_path
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract description from meta tags"""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta.get('content')
        return ""
    
    def _determine_category(self, template_name: str) -> str:
        """Determine template category from its path"""
        if '/' in template_name:
            return template_name.split('/')[0]
        return "general"
    
    def _extract_required_fields(self, content: str) -> List[str]:
        """Extract required fields from template content"""
        required_fields = []
        
        # Simple extraction based on Jinja2 variables
        # This is a basic implementation and could be improved
        import re
        matches = re.findall(r'\{\{\s*(\w+)\s*\}\}', content)
        for match in matches:
            if match not in required_fields and not match.startswith('_'):
                required_fields.append(match)
                
        return required_fields
