import os
from typing import Dict
from bs4 import BeautifulSoup

class HTMLProcessor:
    """Utility for processing HTML email templates"""
    
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