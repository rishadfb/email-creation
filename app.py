import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required API keys
if not os.getenv("APOLLO_API_KEY") or not os.getenv("GEMINI_API_KEY"):
    st.error("⚠️ Missing API keys. Please ensure APOLLO_API_KEY and GEMINI_API_KEY are set in your .env file.")
    st.stop()

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
    st.header("Add a contacts.json file")
    uploaded_file = st.file_uploader("", type=['json'])

# Main content area
if not uploaded_file:
    st.info("Please upload a contacts JSON file to begin")
else:
    st.success("Contacts file uploaded successfully!")
    # TODO: Add contact processing logic here 