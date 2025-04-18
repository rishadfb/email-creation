"""UI components and rendering utilities"""
import streamlit as st
from typing import Dict, List
import json

# Example prompts for quick testing
EXAMPLE_PROMPTS = {
    "Roland Welcome Email to Parents": "Create a welcome email for parents who just enrolled their kids in piano lessons, highlighting the joy of learning music and our beginner-friendly digital pianos for practice at home."
}

def setup_page():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="AI Email Assistant",
        page_icon="🧠",
        layout="wide"
    )

def render_sidebar():
    """Render the sidebar with file upload and tech stack info"""
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

def render_chat_messages():
    """Render all chat messages with their HTML content if available"""
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

def render_example_prompts():
    """Render example prompt buttons if in welcome step"""
    if st.session_state.current_step == 'welcome':
        st.markdown("### Try one of these examples:")
        cols = st.columns(len(EXAMPLE_PROMPTS))
        for i, (name, prompt) in enumerate(EXAMPLE_PROMPTS.items()):
            with cols[i]:
                if st.button(f"📝 {name}", key=f"example_{i}", help=prompt):
                    return prompt
    return None

def render_welcome_message():
    """Render the initial welcome message"""
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": """
            👋 Hi! I'm your AI Email Assistant. I'll help you create personalized email campaigns for your contacts.
            
            To get started, upload your contacts.json file in the sidebar, then tell me what kind of campaign you'd like to create!
            """
        })

def render_result(result: Dict):
    """Render the email creation result"""
    st.components.v1.html(result['html'], height=800, scrolling=True)
    st.download_button(
        "Download HTML",
        result['html'],
        file_name="email_preview.html",
        mime="text/html"
    ) 