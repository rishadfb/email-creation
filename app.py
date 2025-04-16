import os
import json
import streamlit as st
from dotenv import load_dotenv
from utils.gemini import GeminiClient
from utils.html_utils import HTMLProcessor

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

def process_prompt(prompt: str):
    """Process a prompt and generate appropriate response"""
    if not hasattr(st.session_state, 'contacts'):
        with st.chat_message("assistant"):
            response = "Please upload your contacts.json file first! I need it to create personalized emails."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if st.session_state.current_step == 'welcome':
                    # Store campaign intent and select template
                    st.session_state.campaign_details['intent'] = prompt
                    template = clients['gemini'].select_template(
                        campaign_intent=prompt,
                        templates=["welcome_email.html"]
                    )
                    st.session_state.campaign_details['template'] = template
                    
                    # Select a preview contact
                    preview_contact = st.session_state.contacts[0]  # First contact for preview
                    st.session_state.campaign_details['preview_contact'] = preview_contact
                    
                    response = f"""
                    Great! I understand you want to create {prompt}
                    
                    I've selected a template that would work well for this campaign. Let me generate a preview using the contact:
                    **{preview_contact['first_name']} {preview_contact.get('last_name', '')}** from **{preview_contact['company']}**
                    
                    Would you like me to generate the email preview? Or would you prefer to use a different contact for the preview?
                    """
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.current_step = 'preview_confirmation'
                    
                elif st.session_state.current_step == 'preview_confirmation':
                    if 'yes' in prompt.lower() or 'generate' in prompt.lower() or 'preview' in prompt.lower():
                        # Generate content and preview
                        content = clients['gemini'].generate_email_content(
                            contact=st.session_state.campaign_details['preview_contact'],
                            template=st.session_state.campaign_details['template'],
                            campaign_purpose=st.session_state.campaign_details['intent']
                        )
                        
                        html = clients['html'].process_template(
                            template_path=f"templates/{st.session_state.campaign_details['template']}",
                            content=content
                        )
                        
                        response = "✨ Here's your personalized email preview! Let me know if you'd like any changes."
                        st.markdown(response)
                        st.components.v1.html(html, height=800, scrolling=True)
                        st.download_button(
                            "Download HTML",
                            html,
                            file_name="email_preview.html",
                            mime="text/html"
                        )
                        
                        message = {
                            "role": "assistant",
                            "content": response,
                            "html": html
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

# Page config
st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="🧠",
    layout="wide"
)

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

# Display chat messages
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

# Welcome message and example prompts
if not st.session_state.messages:
    with st.chat_message("assistant"):
        welcome_msg = """
        👋 Hi! I'm your AI Email Assistant. I'll help you create personalized email campaigns for your contacts.
        
        To get started, upload your contacts.json file in the sidebar, then tell me what kind of campaign you'd like to create!
        
        Try one of these examples:
        """
        st.markdown(welcome_msg)
        
        # Example prompt buttons
        cols = st.columns(len(EXAMPLE_PROMPTS))
        for i, (name, prompt) in enumerate(EXAMPLE_PROMPTS.items()):
            with cols[i]:
                if st.button(f"📝 {name}", key=f"example_{i}", help=prompt):
                    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.selected_prompt = prompt
                    st.rerun()

# Handle user input or process selected prompt
if st.session_state.selected_prompt:
    prompt = st.session_state.selected_prompt
    st.session_state.selected_prompt = None  # Clear the selection
    process_prompt(prompt)

# Always display the chat input field
if prompt := st.chat_input("Describe your campaign or ask me anything..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    process_prompt(prompt) 