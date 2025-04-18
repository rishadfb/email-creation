from typing import Dict, Any
import asyncio
import streamlit as st
from ..agents import EmailTemplateSelector, EmailContentGenerator, EmailHtmlCompiler
from ..core.exceptions import EmailCreationError
from ..assistants.base import Assistant

class EmailOrchestrator:
    def __init__(self):
        self.template_selector = EmailTemplateSelector()
        self.content_generator = EmailContentGenerator()
        self.html_compiler = EmailHtmlCompiler()
        self._status_containers: Dict[str, Dict] = {}
        
    def _update_status_display(self, agent_name: str, status: str, progress: float):
        """Update the status display for an agent"""
        if agent_name in self._status_containers:
            self._status_containers[agent_name]['status'].text(status)
            self._status_containers[agent_name]['progress'].progress(progress)
    
    def setup_status_displays(self):
        """Create and store status display containers"""
        # Create a container for all status displays
        status_container = st.container()
        
        with status_container:
            # Template Selection
            st.subheader("Template Selection")
            self._status_containers['template'] = {
                'status': st.empty(),
                'progress': st.progress(0.0)
            }
            
            # Add some spacing
            st.write("")
            
            # Content Generation
            st.subheader("Content Generation")
            self._status_containers['content'] = {
                'status': st.empty(),
                'progress': st.progress(0.0)
            }
            
            # Add some spacing
            st.write("")
            
            # Email Compilation
            st.subheader("Email Compilation")
            self._status_containers['compilation'] = {
                'status': st.empty(),
                'progress': st.progress(0.0)
            }
            
            # Add some spacing before the results
            st.write("")
            st.write("")
    
    async def create_email(self, campaign_intent: str, contact: Dict, assistant: Assistant) -> Dict:
        """
        Create an email by orchestrating the template selection, content generation,
        and compilation agents.
        
        Args:
            campaign_intent: The intent of the campaign
            contact: The contact to use for personalization
            assistant: The assistant instance for state management
        """
        try:
            # Set up status callbacks for each agent
            self.template_selector.set_status_callback(
                lambda status, progress: self._update_status_display('template', status, progress)
            )
            self.content_generator.set_status_callback(
                lambda status, progress: self._update_status_display('content', status, progress)
            )
            self.html_compiler.set_status_callback(
                lambda status, progress: self._update_status_display('compilation', status, progress)
            )
            
            # Get the assistant's state
            state = assistant.get_state()
            campaign_details = state.get("campaign_details", {})
            
            # Start template selection and content generation in parallel
            template_task = asyncio.create_task(
                self._select_template(campaign_intent)
            )
            content_task = asyncio.create_task(
                self._generate_content(contact, campaign_intent)
            )
            
            # Wait for both to complete
            template, content = await asyncio.gather(template_task, content_task)
            
            # Update campaign details in the assistant's state
            campaign_details.update({
                'template': template,
                'content': content
            })
            
            # Once we have both, start compilation
            html = await self._compile_html(template, content)
            
            # Store final HTML in the assistant's state
            campaign_details['html'] = html
            
            # Update the assistant's state
            assistant.update_state(campaign_details=campaign_details)
            
            return {
                'template': template,
                'content': content,
                'html': html
            }
            
        except Exception as e:
            st.error(f"Error creating email: {str(e)}")
            raise
    
    async def _select_template(self, campaign_intent: str) -> str:
        """Run template selection with status updates"""
        try:
            # Get available templates from the template service instead of hardcoding
            from ..services.template_service import TemplateService
            template_service = TemplateService()
            available_templates = template_service.get_available_templates()
            
            if not available_templates:
                raise EmailCreationError("No templates found in the templates directory")
                
            return await self.template_selector.execute(
                campaign_intent=campaign_intent,
                templates=available_templates
            )
        except Exception as e:
            self._update_status_display('template', f"Error: {str(e)}", 1.0)
            raise EmailCreationError(f"Template selection failed: {str(e)}")
    
    async def _generate_content(self, contact: Dict, campaign_purpose: str) -> Dict:
        """Run content generation with status updates"""
        try:
            return await self.content_generator.execute(
                contact=contact,
                campaign_purpose=campaign_purpose
            )
        except Exception as e:
            self._update_status_display('content', f"Error: {str(e)}", 1.0)
            raise EmailCreationError(f"Content generation failed: {str(e)}")
    
    async def _compile_html(self, template: str, content: Dict) -> str:
        """Run email compilation with status updates"""
        try:
            return await self.html_compiler.execute(
                template=template,
                content=content
            )
        except Exception as e:
            self._update_status_display('compilation', f"Error: {str(e)}", 1.0)
            raise EmailCreationError(f"HTML compilation failed: {str(e)}") 