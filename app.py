import os
import asyncio
from dotenv import load_dotenv
import streamlit as st
from utils.orchestrator import EmailCreationOrchestrator
from utils.state import (
    initialize_session_state, add_message, get_contacts,
    update_campaign_details
)
from utils.ui import (
    setup_page, render_sidebar, render_chat_messages,
    render_example_prompts, render_welcome_message,
    render_result
)

# Load environment variables
load_dotenv()

# Check for required API keys
if not os.getenv("APOLLO_API_KEY") or not os.getenv("GEMINI_API_KEY"):
    st.error("⚠️ Missing API keys. Please ensure APOLLO_API_KEY and GEMINI_API_KEY are set in your .env file.")
    st.stop()

# Initialize orchestrator
@st.cache_resource
def init_orchestrator():
    return EmailCreationOrchestrator()

# Setup the page
setup_page()

# Initialize session state
initialize_session_state()

# Initialize orchestrator
orchestrator = init_orchestrator()

async def process_prompt(prompt: str):
    """Process a prompt and generate appropriate response"""
    contacts = get_contacts()
    if not contacts:
        add_message("assistant", "Please upload your contacts.json file first! I need it to create personalized emails.")
        return
        
    if st.session_state.current_step == 'welcome':
        # Store campaign intent and preview contact
        update_campaign_details(
            intent=prompt,
            preview_contact=contacts[0]
        )
        
        # Setup status displays
        orchestrator.setup_status_displays()
        
        try:
            # Start the email creation process
            result = await orchestrator.create_email(
                campaign_intent=prompt,
                contact=contacts[0]
            )
            
            # Display the result
            render_result(result)
            
            # Add to chat history
            add_message(
                role="assistant",
                content="✨ Here's your personalized email preview! Let me know if you'd like any changes.",
                html=result['html']
            )
            
        except Exception as e:
            st.error(f"Failed to create email: {str(e)}")
            add_message(
                role="assistant",
                content=f"I encountered an error while creating your email: {str(e)}\nPlease try again or modify your request."
            )
        
        st.session_state.current_step = 'feedback'
        
    elif st.session_state.current_step == 'feedback':
        # Handle feedback and make adjustments
        add_message(
            role="assistant",
            content="I'll help you refine the email. What specific aspects would you like to change?"
        )
        
    else:
        add_message(
            role="assistant",
            content="I'm here to help! What would you like to do with your email campaign?"
        )

# Render the sidebar
render_sidebar()

# Main chat interface
st.title("🧠 AI Email Assistant")

# Welcome message
render_welcome_message()

# Display chat messages
render_chat_messages()

# Show example prompts
if example_prompt := render_example_prompts():
    add_message("user", example_prompt)
    asyncio.run(process_prompt(example_prompt))
    st.rerun()

# Handle user input
if prompt := st.chat_input("Describe your campaign or ask me anything..."):
    add_message("user", prompt)
    asyncio.run(process_prompt(prompt)) 