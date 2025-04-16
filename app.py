import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="🧠",
    layout="wide"
)

# Title
st.title("🧠 AI Email Assistant")
st.markdown("""
A conversational AI-powered tool that generates personalized marketing emails using:
- Apollo API for contact enrichment
- Gemini for template selection and content generation
- Pre-defined HTML templates
""")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    # File uploader for contacts
    uploaded_file = st.file_uploader("Upload Contacts (JSON)", type=['json'])
    
    # API Keys input
    apollo_key = st.text_input("Apollo API Key", type="password", value=os.getenv("APOLLO_API_KEY", ""))
    gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))

# Main content area
if not uploaded_file:
    st.info("Please upload a contacts JSON file to begin")
else:
    st.success("Contacts file uploaded successfully!")
    # TODO: Add contact processing logic here 