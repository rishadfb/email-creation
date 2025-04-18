from typing import Dict
import asyncio
import streamlit as st
from .agents import TemplateSelectionAgent, ContentGenerationAgent, EmailCompilationAgent

class EmailCreationOrchestrator:
    def __init__(self):
        self.template_agent = TemplateSelectionAgent()
        self.content_agent = ContentGenerationAgent()
        self.compilation_agent = EmailCompilationAgent()
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
    
    async def create_email(self, campaign_intent: str, contact: Dict) -> Dict:
        """
        Create an email by orchestrating the template selection, content generation,
        and compilation agents.
        """
        try:
            # Set up status callbacks for each agent
            self.template_agent.set_status_callback(
                lambda status, progress: self._update_status_display('template', status, progress)
            )
            self.content_agent.set_status_callback(
                lambda status, progress: self._update_status_display('content', status, progress)
            )
            self.compilation_agent.set_status_callback(
                lambda status, progress: self._update_status_display('compilation', status, progress)
            )
            
            # Start template selection and content generation in parallel
            template_task = asyncio.create_task(
                self._run_template_selection(campaign_intent)
            )
            content_task = asyncio.create_task(
                self._run_content_generation(contact, campaign_intent)
            )
            
            # Wait for both to complete
            template, content = await asyncio.gather(template_task, content_task)
            
            # Store results in session state
            st.session_state.campaign_details.update({
                'template': template,
                'content': content
            })
            
            # Once we have both, start compilation
            html = await self._run_compilation(template, content)
            
            # Store final HTML
            st.session_state.campaign_details['html'] = html
            
            return {
                'template': template,
                'content': content,
                'html': html
            }
            
        except Exception as e:
            st.error(f"Error creating email: {str(e)}")
            raise
    
    async def _run_template_selection(self, campaign_intent: str) -> str:
        """Run template selection with status updates"""
        try:
            return await self.template_agent.run(
                campaign_intent=campaign_intent,
                templates=["welcome_email.html"]
            )
        except Exception as e:
            self._update_status_display('template', f"Error: {str(e)}", 1.0)
            raise
    
    async def _run_content_generation(self, contact: Dict, campaign_purpose: str) -> Dict:
        """Run content generation with status updates"""
        try:
            return await self.content_agent.run(
                contact=contact,
                campaign_purpose=campaign_purpose
            )
        except Exception as e:
            self._update_status_display('content', f"Error: {str(e)}", 1.0)
            raise
    
    async def _run_compilation(self, template: str, content: Dict) -> str:
        """Run email compilation with status updates"""
        try:
            return await self.compilation_agent.run(
                template=template,
                content=content
            )
        except Exception as e:
            self._update_status_display('compilation', f"Error: {str(e)}", 1.0)
            raise 