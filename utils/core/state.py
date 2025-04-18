"""Session state management utilities for shared application state"""
import streamlit as st
from typing import Dict, List, Optional

def initialize_session_state():
    """Initialize shared session state variables"""
    # Initialize chat messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize contacts
    if 'contacts' not in st.session_state:
        st.session_state.contacts = None

def add_message(role: str, content: str, html: Optional[str] = None):
    """Add a message to the chat history (legacy method, assistants should use their own add_message)"""
    message = {"role": role, "content": content}
    if html:
        message["html"] = html
    st.session_state.messages.append(message)

def get_contacts() -> List[Dict]:
    """Get the loaded contacts or return None"""
    return st.session_state.contacts

def set_contacts(contacts: List[Dict]):
    """Set the contacts in session state"""
    st.session_state.contacts = contacts