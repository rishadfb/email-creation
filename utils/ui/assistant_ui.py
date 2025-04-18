"""
Assistant UI components for the application.

This module provides UI components for rendering the assistant selection dropdown
and managing the active assistant's UI.
"""
import streamlit as st
from typing import Optional

from ..assistants.registry import registry

def render_assistant_selector() -> None:
    """
    Render the assistant selector dropdown in the sidebar.
    
    This allows users to switch between different assistants.
    """
    assistants = registry.get_all_assistants()
    
    # Create a list of display names for the dropdown
    assistant_options = [assistant.display_name for assistant in assistants]
    
    # Get the current assistant's display name
    current_assistant = registry.get_current_assistant()
    current_index = assistant_options.index(current_assistant.display_name)
    
    # Add a dropdown to select the assistant with custom styling
    st.sidebar.markdown("""
    <style>
    div[data-testid="stSelectbox"] > div > div > div {
        font-weight: bold;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    selected_index = st.sidebar.selectbox(
        "Select an assistant:",
        range(len(assistant_options)),
        format_func=lambda i: assistant_options[i],
        index=current_index,
        label_visibility="collapsed"
    )
    
    # If the selection changed, update the current assistant
    if selected_index != current_index:
        selected_assistant = assistants[selected_index]
        registry.set_current_assistant(selected_assistant.name)
        # Force a rerun to update the UI
        st.rerun()
    
    # Add a separator
    st.sidebar.markdown("---")

def render_assistant_ui() -> None:
    """
    Render the UI for the current assistant.
    
    This includes the main title, welcome message, and any assistant-specific UI.
    """
    # Get the current assistant
    assistant = registry.get_current_assistant()
    
    # Render the main title
    st.title(assistant.display_name)
    
    # Initialize the assistant's session state if needed
    assistant.initialize_session_state()
    
    # If there are no messages, show the welcome message
    if not st.session_state.messages:
        assistant.render_welcome()
    
    # Display chat messages
    render_chat_messages()
    
    # Show example prompts and get the selected one if any
    example_prompt = assistant.render_example_prompts()
    
    return example_prompt

def render_chat_messages() -> None:
    """Render all chat messages with their HTML content if available."""
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
