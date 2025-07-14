#!/usr/bin/env python3
"""
Main application launcher for the Blockchain Protocol Upgrade Monitor.
"""

import streamlit as st
import asyncio
import logging
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.enhanced_timeline import render_enhanced_timeline
from src.ui.execution_guidance import render_execution_guidance
from src.ui.live_network_feed import render_live_network_feed, render_network_overview
from config.config import Config
from src.ui.theme import apply_theme, create_animated_title, create_theme_toggle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blockchain_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Blockchain Protocol Upgrade Monitor",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Validate configuration
    if not Config.validate_config():
        st.error("❌ Configuration validation failed. Please check your environment variables.")
        st.stop()

    # Apply theme and create title
    apply_theme()
    create_animated_title("Blockchain Protocol Upgrade Monitor", "Assessing risk and opportunities in real-time")
    create_theme_toggle()
    
    # Render live network feed in sidebar
    render_live_network_feed()
    
    # Create navigation
    st.sidebar.title("🔗 Protocol Monitor")
    page = st.sidebar.selectbox(
        "Navigation",
        ["📊 Upgrade Timeline", "📈 Risk Dashboard", "🎯 Execution Guidance", "⚙️ Settings"]
    )
    
    if page == "📊 Upgrade Timeline":
        # Create a three-column layout
        col1, col2, col3 = st.columns([2, 4, 2])
        
        with col1:
            st.header("📊 Network Status")
            render_network_overview()
        
        with col2:
            st.header("📋 Protocol Upgrades")
            asyncio.run(render_enhanced_timeline())
        
        with col3:
            st.header("🎯 Execution Guidance")
            # Mock risk score for demonstration
            example_risk_score = 68.5
            render_execution_guidance(example_risk_score)
    
    elif page == "📈 Risk Dashboard":
        st.title("📈 Risk Dashboard")
        render_network_overview()
        st.info("Advanced risk analytics coming soon...")
    
    elif page == "🎯 Execution Guidance":
        st.title("🎯 Execution Guidance")
        
        # Mock risk score input
        risk_score = st.slider("Adjust Risk Score", 0.0, 100.0, 50.0)
        render_execution_guidance(risk_score)
    
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")
        st.info("Settings page coming soon...")

if __name__ == "__main__":
    main()
