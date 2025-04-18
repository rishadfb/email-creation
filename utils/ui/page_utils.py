"""
Page utilities for the application.

This module provides common page setup and configuration functions.
"""
import streamlit as st

def setup_page():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="AI Assistants",
        page_icon="🧠",
        layout="wide"
    )
