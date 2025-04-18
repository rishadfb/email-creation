"""
Email assistant implementation.

This module provides the email assistant implementation that helps users
create personalized marketing emails.
"""
import asyncio
import json
import streamlit as st
from typing import Dict, Optional, List

from .base import Assistant
from ..orchestration.orchestrator import EmailOrchestrator
from ..core.state import add_message, get_contacts
from ..core.exceptions import EmailCreationError

class EmailAssistant(Assistant):
    """Email assistant for creating personalized marketing emails."""
    
    # Example prompts for quick testing
    EXAMPLE_PROMPTS = {
        "Welcome Email for New Customers": "Create a welcome email for new customers who just signed up for our software service, highlighting the key features and offering a quick start guide.",
        "Product Launch Announcement": "Create an email announcing our new product line of eco-friendly office supplies, emphasizing sustainability and modern design.",
        "Monthly Newsletter": "Create a monthly newsletter for our fitness app subscribers with workout tips, success stories, and upcoming features."
    }
    
    def __init__(self):
        """Initialize the email assistant."""
        super().__init__(
            name="AI Email Assistant",
            emoji="🧠",
            description="Create personalized marketing emails for your contacts"
        )
        self.orchestrator = EmailOrchestrator()
        
    def initialize_session_state(self) -> None:
        """Initialize email assistant session state variables."""
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {
                "current_step": "welcome",
                "campaign_details": {
                    'intent': '',
                    'preview_contact': None,
                    'template': None,
                    'content': None,
                    'html': None
                },
            }
    
    def render_sidebar(self) -> None:
        """Render the email assistant sidebar."""
        # Empty sidebar for now - we've moved contacts to the main area
        pass
    
    def render_welcome(self) -> None:
        """Render the email assistant welcome message and contacts upload."""
        with st.container():
            st.write("I'll help you create personalized marketing emails for your contacts using AI-powered content generation.")
            
            st.subheader("Getting Started:")
            st.markdown("1. **Upload your contacts.json** file below")
            st.markdown("2. **Describe your campaign** or select an example")
            st.markdown("3. **Preview and refine** your personalized email")
            
            st.write("Your emails will include AI-generated images and personalized content based on your contacts' information.")
            
            # Add contacts upload section
            st.subheader("Upload contacts to get started")
            
            # File upload section with instructions
            uploaded_file = st.file_uploader("Upload Contacts", type=['json'], key="contact_uploader")
            
            if uploaded_file:
                try:
                    contacts_data = json.load(uploaded_file)
                    if not isinstance(contacts_data, dict) or 'contacts' not in contacts_data:
                        st.error("⚠️ Invalid format. Expected {'contacts': [...]}")
                    else:
                        contact_count = len(contacts_data['contacts'])
                        st.success(f"✅ {contact_count} contacts loaded successfully")
                        st.session_state.contacts = contacts_data['contacts']
                        
                        # Show a sample of the first contact
                        if contact_count > 0:
                            with st.expander("View Sample Contact"):
                                st.json(contacts_data['contacts'][0])
                except Exception as e:
                    st.error(f"⚠️ Error loading contacts: {str(e)}")
            
            # Add help information
            with st.expander("📋 Contact Format Help"):
                st.markdown("""
                Your contacts.json file should have this structure:
                ```json
                {
                  "contacts": [
                    {
                      "first_name": "John",
                      "last_name": "Doe",
                      "job_title": "Software Engineer",
                      "company": "Tech Corp",
                      "industry": "Technology"
                    }
                  ]
                }
                ```
                """)
    
    def render_example_prompts(self) -> Optional[str]:
        """Render email assistant example prompts."""
        state = self.get_state()
        if state["current_step"] == 'welcome':
            # Check if contacts exist in session state
            contacts_exist = 'contacts' in st.session_state and st.session_state.contacts
            
            # Only show example prompts if contacts exist
            if contacts_exist:
                st.markdown("### Try one of these examples:")
                
                # Create a multi-column layout to control width - make columns narrower
                col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 2])
                
                # Only use the first 3 columns for buttons, leaving the rest empty
                # This makes each button column narrower
                button_cols = [col1, col2, col3]
                for i, (name, prompt) in enumerate(self.EXAMPLE_PROMPTS.items()):
                    with button_cols[i]:
                        # Add consistent styling to buttons
                        if st.button(f"📝 {name}", key=f"example_{i}", help=prompt, 
                                    use_container_width=True):
                            return prompt
        return None
    
    def render_result(self, result: Dict) -> None:
        """Render the email creation result with preview and download options."""
        # Display a header for the preview section
        st.subheader("📧 Email Preview")
        
        # Create tabs for preview and HTML code
        preview_tab, code_tab = st.tabs(["Preview", "HTML Code"])
        
        with preview_tab:
            # Render the HTML preview
            st.components.v1.html(result['html'], height=800, scrolling=True)
            
            # Add download button
            st.download_button(
                "📥 Download HTML",
                result['html'],
                file_name="email_preview.html",
                mime="text/html"
            )
        
        with code_tab:
            # Show the HTML code with syntax highlighting
            st.code(result['html'], language="html")
    
    async def process_prompt(self, prompt: str) -> None:
        """Process a user prompt and generate an email response."""
        contacts = get_contacts()
        if not contacts:
            self.add_message("assistant", "Please upload your contacts.json file first! I need it to create personalized emails.")
            return
        
        state = self.get_state()
        campaign_details = state["campaign_details"]
            
        if state["current_step"] == 'welcome':
            # Store campaign intent and preview contact
            campaign_details["intent"] = prompt
            campaign_details["preview_contact"] = contacts[0]
            
            # Setup status displays
            self.orchestrator.setup_status_displays()
            
            try:
                # Start the email creation process
                result = await self.orchestrator.create_email(
                    campaign_intent=prompt,
                    contact=contacts[0],
                    assistant=self
                )
                
                # Store results in campaign details
                campaign_details["template"] = result.get("template")
                campaign_details["content"] = result.get("content")
                campaign_details["html"] = result.get("html")
                
                # Display the result
                self.render_result(result)
                
                # Add to chat history
                self.add_message(
                    role="assistant",
                    content="✨ Here's your personalized email preview! Let me know if you'd like any changes.",
                    html=result['html']
                )
                
            except EmailCreationError as e:
                # Handle specific email creation errors
                st.error(f"Failed to create email: {str(e)}")
                self.add_message(
                    role="assistant",
                    content=f"I encountered an error while creating your email: {str(e)}\nPlease try again or modify your request."
                )
            except Exception as e:
                # Handle unexpected errors
                st.error(f"An unexpected error occurred: {str(e)}")
                self.add_message(
                    role="assistant",
                    content=f"I encountered an unexpected error: {str(e)}\nPlease try again later."
                )
            
            # Update the step
            self.update_state(current_step="feedback")
            
        elif state["current_step"] == 'feedback':
            # Handle feedback and make adjustments
            self.add_message(
                role="assistant",
                content="I'll help you refine the email. What specific aspects would you like to change?"
            )
            
        else:
            self.add_message(
                role="assistant",
                content="I'm here to help! What would you like to do with your email campaign?"
            )
