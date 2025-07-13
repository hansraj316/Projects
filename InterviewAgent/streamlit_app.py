"""
InterviewAgent - AI-Powered Job Application Automation
Main Streamlit Application Entry Point
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config import load_config
from database.connection import init_database
from utils.logging_utils import setup_logging

# Page Configuration
st.set_page_config(
    page_title="InterviewAgent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/interview-agent',
        'Report a bug': 'https://github.com/your-repo/interview-agent/issues',
        'About': "# InterviewAgent\nAI-Powered Job Application Automation System"
    }
)

def main():
    """Main application entry point"""
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(config.get('LOG_LEVEL', 'INFO'))
    
    # Initialize database connection
    if 'db_initialized' not in st.session_state:
        try:
            init_database()
            st.session_state.db_initialized = True
        except Exception as e:
            st.warning(f"Database initialization issue: {str(e)}. Running in mock mode.")
            st.session_state.db_initialized = True  # Continue anyway in mock mode
    
    # Application Header
    st.title("🤖 InterviewAgent")
    st.markdown("*AI-Powered Job Application Automation System*")
    
    # Sidebar Navigation
    with st.sidebar:
        st.header("Navigation")
        
        # Main navigation
        page = st.selectbox(
            "Choose a page:",
            [
                "🏠 Dashboard",
                "🤖 AI Agents",
                "📄 Resume Manager", 
                "🔍 Job Search",
                "📝 Applications",
                "📧 Notifications",
                "⚙️ Settings"
            ]
        )
        
        # Quick stats
        st.markdown("---")
        st.subheader("Quick Stats")
        
        # Initialize session state for stats
        if 'stats' not in st.session_state:
            st.session_state.stats = {
                'resumes': 0,
                'jobs_discovered': 0,
                'applications_submitted': 0,
                'applications_successful': 0
            }
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Resumes", st.session_state.stats['resumes'])
            st.metric("Applications", st.session_state.stats['applications_submitted'])
        with col2:
            st.metric("Jobs Found", st.session_state.stats['jobs_discovered'])
            st.metric("Success Rate", 
                     f"{st.session_state.stats['applications_successful']}/{st.session_state.stats['applications_submitted']}" 
                     if st.session_state.stats['applications_submitted'] > 0 else "0/0")
    
    # Route to appropriate page
    if page == "🏠 Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif page == "🤖 AI Agents":
        from pages.ai_agents import show_ai_agents
        show_ai_agents()
    elif page == "📄 Resume Manager":
        from pages.resume_manager import show_resume_manager
        show_resume_manager()
    elif page == "🔍 Job Search":
        from pages.job_search import show_job_search
        show_job_search()
    elif page == "📝 Applications":
        from pages.applications import show_applications
        show_applications()
    elif page == "📧 Notifications":
        from pages.notifications import show_notifications
        show_notifications()
    elif page == "⚙️ Settings":
        from pages.settings import show_settings
        show_settings()

if __name__ == "__main__":
    main()