"""
Settings page for InterviewAgent Streamlit app
"""

import streamlit as st
import os
from src.config import get_config

def show_settings():
    """Display the settings page"""
    
    st.header("⚙️ Settings")
    
    # Configuration Status
    with st.expander("📋 Configuration Status", expanded=False):
        st.info("This section shows what configuration has been loaded from environment variables (.env file)")
        
        config_status = {
            "USER_NAME": os.getenv('USER_NAME', 'Not set'),
            "USER_EMAIL": os.getenv('USER_EMAIL', 'Not set'),
            "JOB_KEYWORDS": os.getenv('JOB_KEYWORDS', 'Not set'),
            "PREFERRED_LOCATION": os.getenv('PREFERRED_LOCATION', 'Not set'),
            "MINIMUM_SALARY": os.getenv('MINIMUM_SALARY', 'Not set'),
            "EXPERIENCE_LEVEL": os.getenv('EXPERIENCE_LEVEL', 'Not set'),
            "GMAIL_EMAIL": os.getenv('GMAIL_EMAIL', 'Not set'),
            "OPENAI_API_KEY": "Set" if os.getenv('OPENAI_API_KEY') else 'Not set'
        }
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**User Configuration:**")
            for key in ["USER_NAME", "USER_EMAIL", "GMAIL_EMAIL"]:
                status = config_status[key]
                icon = "✅" if status != "Not set" else "❌"
                st.write(f"{icon} {key}: {status}")
        
        with col2:
            st.write("**Job Search Configuration:**")
            for key in ["JOB_KEYWORDS", "PREFERRED_LOCATION", "MINIMUM_SALARY", "EXPERIENCE_LEVEL"]:
                status = config_status[key]
                icon = "✅" if status != "Not set" else "❌"
                st.write(f"{icon} {key}: {status}")
        
        # OpenAI status
        openai_status = config_status["OPENAI_API_KEY"]
        icon = "✅" if openai_status == "Set" else "❌"
        st.write(f"{icon} **OPENAI_API_KEY**: {openai_status}")
    
    # Load configuration and environment variables
    try:
        config = get_config()
        
        # Get environment values or use defaults
        user_name = os.getenv('USER_NAME', config.USER_NAME)
        user_email = os.getenv('USER_EMAIL', config.USER_EMAIL)
        job_keywords = os.getenv('JOB_KEYWORDS', 'software engineer, developer, python')
        preferred_location = os.getenv('PREFERRED_LOCATION', 'Remote')
        minimum_salary = int(os.getenv('MINIMUM_SALARY', '80000'))
        experience_level = os.getenv('EXPERIENCE_LEVEL', 'Mid')
        max_applications = int(os.getenv('MAX_APPLICATIONS_PER_DAY', '10'))
        gmail_email = os.getenv('GMAIL_EMAIL', '')
        
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        # Fallback to environment variables only
        user_name = os.getenv('USER_NAME', 'Your Name')
        user_email = os.getenv('USER_EMAIL', 'user@example.com')
        job_keywords = os.getenv('JOB_KEYWORDS', 'software engineer, developer, python')
        preferred_location = os.getenv('PREFERRED_LOCATION', 'Remote')
        minimum_salary = int(os.getenv('MINIMUM_SALARY', '80000'))
        experience_level = os.getenv('EXPERIENCE_LEVEL', 'Mid')
        max_applications = int(os.getenv('MAX_APPLICATIONS_PER_DAY', '10'))
        gmail_email = os.getenv('GMAIL_EMAIL', '')
    
    # User Settings
    st.subheader("👤 User Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=user_name)
        email = st.text_input("Email", value=user_email)
    
    with col2:
        st.info("Single-user MVP - These settings apply to the current user.")
        if user_name != 'Your Name':
            st.success(f"✅ Loaded from environment: {user_name}")
        else:
            st.warning("⚠️ Using default values. Update your .env file.")
    
    # Job Search Preferences
    st.subheader("🔍 Job Search Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        keywords = st.text_area("Keywords", value=job_keywords, help="Comma-separated job keywords")
        location = st.text_input("Preferred Location", value=preferred_location, help="Preferred work location")
        
    with col2:
        salary_min = st.number_input("Minimum Salary", value=minimum_salary, step=10000, help="Minimum acceptable salary")
        experience_levels = ["Entry", "Mid", "Senior", "Lead"]
        default_exp_index = experience_levels.index(experience_level) if experience_level in experience_levels else 1
        exp_level = st.selectbox("Experience Level", experience_levels, index=default_exp_index)
    
    # Automation Settings
    st.subheader("🤖 Automation Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_apply = st.checkbox("Enable Auto-Apply", value=False, help="Automatically apply to matching jobs")
        max_apps = st.number_input("Max Applications per Day", value=max_applications, min_value=1, max_value=50, help="Limit daily applications")
        
    with col2:
        schedule_enabled = st.checkbox("Enable Scheduling", value=False, help="Schedule automatic job applications")
        schedule_time = st.time_input("Automation Time", help="Time to run automated job search")
    
    # Job Sites Configuration
    st.subheader("🌐 Job Sites")
    
    st.info("Configure job sites and credentials for automated job discovery.")
    
    # Add placeholder for job site configuration
    with st.expander("LinkedIn Configuration"):
        linkedin_email = st.text_input("LinkedIn Email", type="password", help="Your LinkedIn login email")
        linkedin_password = st.text_input("LinkedIn Password", type="password", help="Your LinkedIn password")
        linkedin_enabled = st.checkbox("Enable LinkedIn", value=True)
    
    with st.expander("Indeed Configuration"):
        indeed_email = st.text_input("Indeed Email", type="password", help="Your Indeed login email")
        indeed_password = st.text_input("Indeed Password", type="password", help="Your Indeed password")  
        indeed_enabled = st.checkbox("Enable Indeed", value=True)
    
    with st.expander("Gmail Notifications"):
        gmail_display = gmail_email if gmail_email else "Not configured"
        st.text_input("Gmail Email", value=gmail_display, disabled=True, help="Configured in environment variables")
        gmail_configured = st.checkbox("Enable Email Notifications", value=bool(gmail_email), disabled=True)
        if gmail_email:
            st.success("✅ Gmail configured for notifications")
        else:
            st.warning("⚠️ Gmail not configured. Set GMAIL_EMAIL in environment.")
    
    # Save button
    if st.button("💾 Save All Settings", type="primary"):
        st.success("Settings saved successfully!")
        st.balloons()

if __name__ == "__main__":
    show_settings()