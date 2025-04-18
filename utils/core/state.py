"""Session state management utilities"""
import streamlit as st
from typing import Dict, List, Optional

def initialize_session_state():
    """Initialize all required session state variables"""
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

def add_message(role: str, content: str, html: Optional[str] = None):
    """Add a message to the chat history"""
    message = {"role": role, "content": content}
    if html:
        message["html"] = html
    st.session_state.messages.append(message)

def get_contacts() -> List[Dict]:
    """Get the loaded contacts or return None"""
    return getattr(st.session_state, 'contacts', None)

def set_contacts(contacts: List[Dict]):
    """Set the contacts in session state"""
    st.session_state.contacts = contacts

def update_campaign_details(**kwargs):
    """Update campaign details with the provided key-value pairs"""
    st.session_state.campaign_details.update(kwargs) 