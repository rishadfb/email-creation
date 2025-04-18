import asyncio
import streamlit as st
from utils.core.state import initialize_session_state, add_message
from utils.ui.page_utils import setup_page
from utils.ui.assistant_ui import render_assistant_selector, render_assistant_ui
from utils.assistants.registry import registry
from utils.core.config import is_config_valid, get_missing_keys
from utils.core.exceptions import ConfigurationError

# Check for required API keys
if not is_config_valid():
    missing_keys = get_missing_keys()
    st.error(f"⚠️ Missing API keys: {', '.join(missing_keys)}. Please ensure these are set in your .env file.")
    st.stop()

# Setup the page
setup_page()

# Initialize session state
initialize_session_state()

async def process_user_input(prompt: str):
    """Process user input with the current assistant"""
    # Get the current assistant
    assistant = registry.get_current_assistant()
    
    # Process the prompt with the current assistant
    await assistant.process_prompt(prompt)

# Render the assistant selector in the sidebar
render_assistant_selector()

# Render the current assistant's sidebar
current_assistant = registry.get_current_assistant()
current_assistant.render_sidebar()

# Render the assistant UI and get any selected example prompt
example_prompt = render_assistant_ui()

# Process example prompt if one was selected
if example_prompt:
    current_assistant.add_message("user", example_prompt)
    asyncio.run(process_user_input(example_prompt))
    st.rerun()

# Check if contacts exist
contacts_exist = 'contacts' in st.session_state and st.session_state.contacts

# Handle user input - only enable if contacts exist
if contacts_exist:
    if prompt := st.chat_input("Describe your campaign or ask me anything..."):
        current_assistant.add_message("user", prompt)
        asyncio.run(process_user_input(prompt))
else:
    # Disabled chat input with explanation
    st.chat_input("Please upload contacts first...", disabled=True)