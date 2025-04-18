"""UI components and rendering utilities for the Email Creation application.

This module provides functions for rendering different parts of the UI,
including the sidebar, chat messages, and email preview.
"""

from typing import Dict, List
import json
import streamlit as st


# Example prompts for quick testing
EXAMPLE_PROMPTS = {
    "Welcome Email for New Customers": "Create a welcome email for new customers who just signed up for our software service, highlighting the key features and offering a quick start guide.",
    "Product Launch Announcement": "Create an email announcing our new product line of eco-friendly office supplies, emphasizing sustainability and modern design.",
    "Monthly Newsletter": "Create a monthly newsletter for our fitness app subscribers with workout tips, success stories, and upcoming features."
}

def setup_page():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="AI Email Assistant",
        page_icon="🧠",
        layout="wide"
    )

def render_sidebar():
    """Render the sidebar with file upload, contact management, and tech stack info"""
    with st.sidebar:
        # Use custom CSS to reduce spacing
        st.markdown("""
        <style>
        [data-testid="stSidebarUserContent"] > div:first-child {margin-top: 1rem;}
        [data-testid="stFileUploader"] {margin-top: -1rem;}
        </style>
        """, unsafe_allow_html=True)
        
        st.header("📁 Contact Management")
        # File upload section with instructions
        uploaded_file = st.file_uploader("Upload Contacts", type=['json'], label_visibility="hidden")
        
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
                        st.subheader("Sample Contact")
                        st.json(contacts_data['contacts'][0], expanded=False)
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
        # Check if contacts exist in session state
        contacts_exist = 'contacts' in st.session_state and st.session_state.contacts
        
        # Add header with status indication
        if contacts_exist:
            st.markdown("### Try one of these examples:")
        else:
            st.markdown("### Upload contacts to enable examples")
        
        # Create a multi-column layout to control width - make columns narrower
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 2])
        
        # Only use the first 3 columns for buttons, leaving the rest empty
        # This makes each button column narrower
        button_cols = [col1, col2, col3]
        for i, (name, prompt) in enumerate(EXAMPLE_PROMPTS.items()):
            with button_cols[i]:
                # Add consistent styling to buttons but disable if no contacts
                if st.button(f"📝 {name}", key=f"example_{i}", help=prompt, 
                            use_container_width=True, disabled=not contacts_exist):
                    return prompt
    return None

def render_welcome_message():
    """Render the initial welcome message with instructions"""
    if not st.session_state.messages:
        # We don't add any initial message to the chat history
        # Instead, we just show the instructions directly in the UI
        with st.container():
            st.write("I'll help you create personalized marketing emails for your contacts using AI-powered content generation.")
            
            st.subheader("Getting Started:")
            st.markdown("1. **Upload your contacts.json** file in the sidebar")
            st.markdown("2. **Describe your campaign** or select an example below")
            st.markdown("3. **Preview and refine** your personalized email")
            
            st.write("Your emails will include AI-generated images and personalized content based on your contacts' information.")

def render_result(result: Dict):
    """Render the email creation result with preview and download options"""
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