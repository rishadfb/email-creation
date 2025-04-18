import os
import json
import asyncio
from typing import Dict, List, Optional
import streamlit as st
from dotenv import load_dotenv
from utils.gemini import GeminiClient
from utils.html_utils import HTMLProcessor
from utils.agents import TemplateSelectionAgent, ContentGenerationAgent, EmailCompilationAgent

# Page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="🧠",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Check for required API keys
if not os.getenv("APOLLO_API_KEY") or not os.getenv("GEMINI_API_KEY"):
    st.error("⚠️ Missing API keys. Please ensure APOLLO_API_KEY and GEMINI_API_KEY are set in your .env file.")
    st.stop()

# Initialize clients
@st.cache_resource
def init_clients():
    return {
        'gemini': GeminiClient(),
        'html': HTMLProcessor()
    }

clients = init_clients()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'welcome'
if 'campaign_details' not in st.session_state:
    st.session_state.campaign_details = {
        'intent': '',
        'preview_contact': None,
        'template': None,
        'content': None,
        'html': None
    }
if 'selected_prompt' not in st.session_state:
    st.session_state.selected_prompt = None

# Example prompts
EXAMPLE_PROMPTS = {
    "Roland Welcome Email to Parents": "Create a welcome email for parents who just enrolled their kids in piano lessons, highlighting the joy of learning music and our beginner-friendly digital pianos for practice at home."
}

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
            def status_callback(status: str, progress: float):
                self._update_status_display('template', status, progress)
            
            self.template_agent.set_status_callback(status_callback)
            template = await self.template_agent.run(
                campaign_intent=campaign_intent,
                templates=["welcome_email.html"]
            )
            return template
            
        except Exception as e:
            self._update_status_display('template', f"Error: {str(e)}", 1.0)
            raise
    
    async def _run_content_generation(self, contact: Dict, campaign_purpose: str) -> Dict:
        """Run content generation with status updates"""
        try:
            def status_callback(status: str, progress: float):
                self._update_status_display('content', status, progress)
            
            self.content_agent.set_status_callback(status_callback)
            content = await self.content_agent.run(
                contact=contact,
                campaign_purpose=campaign_purpose
            )
            return content
            
        except Exception as e:
            self._update_status_display('content', f"Error: {str(e)}", 1.0)
            raise
    
    async def _run_compilation(self, template: str, content: Dict) -> str:
        """Run email compilation with status updates"""
        try:
            def status_callback(status: str, progress: float):
                self._update_status_display('compilation', status, progress)
            
            self.compilation_agent.set_status_callback(status_callback)
            html = await self.compilation_agent.run(
                template=template,
                content=content
            )
            return html
            
        except Exception as e:
            self._update_status_display('compilation', f"Error: {str(e)}", 1.0)
            raise

# Initialize orchestrator
@st.cache_resource
def init_orchestrator():
    return EmailCreationOrchestrator()

orchestrator = init_orchestrator()

def process_prompt(prompt: str):
    """Process a prompt and generate appropriate response"""
    if not hasattr(st.session_state, 'contacts'):
        with st.chat_message("assistant"):
            response = "Please upload your contacts.json file first! I need it to create personalized emails."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        with st.chat_message("assistant"):
            if st.session_state.current_step == 'welcome':
                # Store campaign intent
                st.session_state.campaign_details['intent'] = prompt
                preview_contact = st.session_state.contacts[0]
                st.session_state.campaign_details['preview_contact'] = preview_contact
                
                # Setup status displays
                orchestrator.setup_status_displays()
                
                try:
                    # Start the email creation process
                    result = asyncio.run(orchestrator.create_email(
                        campaign_intent=prompt,
                        contact=preview_contact
                    ))
                    
                    # Display the result
                    st.components.v1.html(result['html'], height=800, scrolling=True)
                    st.download_button(
                        "Download HTML",
                        result['html'],
                        file_name="email_preview.html",
                        mime="text/html"
                    )
                    
                    # Add to chat history
                    message = {
                        "role": "assistant",
                        "content": "✨ Here's your personalized email preview! Let me know if you'd like any changes.",
                        "html": result['html']
                    }
                    st.session_state.messages.append(message)
                    
                except Exception as e:
                    st.error(f"Failed to create email: {str(e)}")
                    message = {
                        "role": "assistant",
                        "content": f"I encountered an error while creating your email: {str(e)}\nPlease try again or modify your request."
                    }
                    st.session_state.messages.append(message)
                
                st.session_state.current_step = 'feedback'
                
            elif st.session_state.current_step == 'feedback':
                # Handle feedback and make adjustments
                response = "I'll help you refine the email. What specific aspects would you like to change?"
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            else:
                response = "I'm here to help! What would you like to do with your email campaign?"
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar for contacts upload
with st.sidebar:
    st.header("Add a contacts.json file")
    uploaded_file = st.file_uploader("", type=['json'])
    
    if uploaded_file:
        try:
            contacts_data = json.load(uploaded_file)
            if not isinstance(contacts_data, dict) or 'contacts' not in contacts_data:
                st.error("Invalid contacts format. Expected {'contacts': [...]}")
            else:
                st.success(f"✅ {len(contacts_data['contacts'])} contacts loaded")
                st.session_state.contacts = contacts_data['contacts']
        except Exception as e:
            st.error(f"Error loading contacts: {str(e)}")
    
    # Subtle tech stack footer
    st.markdown("---")
    st.markdown(
        "<div style='position: fixed; bottom: 20px; font-size: 0.8em; color: #666;'>"
        "Powered by Apollo · Gemini · Imagen 3.0"
        "</div>",
        unsafe_allow_html=True
    )

# Main chat interface
st.title("🧠 AI Email Assistant")

# Welcome message on first load
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": """
        👋 Hi! I'm your AI Email Assistant. I'll help you create personalized email campaigns for your contacts.
        
        To get started, upload your contacts.json file in the sidebar, then tell me what kind of campaign you'd like to create!
        """
    })

# Display all chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "html" in message:
            st.components.v1.html(message["html"], height=800, scrolling=True)
            st.download_button(
                "Download HTML",
                message["html"],
                file_name="email_preview.html",
                mime="text/html"
            )

# Always show example prompts if no campaign has started
if st.session_state.current_step == 'welcome':
    st.markdown("### Try one of these examples:")
    cols = st.columns(len(EXAMPLE_PROMPTS))
    for i, (name, prompt) in enumerate(EXAMPLE_PROMPTS.items()):
        with cols[i]:
            if st.button(f"📝 {name}", key=f"example_{i}", help=prompt):
                st.session_state.messages.append({"role": "user", "content": prompt})
                process_prompt(prompt)
                st.rerun()

# Handle user input
if prompt := st.chat_input("Describe your campaign or ask me anything..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    process_prompt(prompt) 