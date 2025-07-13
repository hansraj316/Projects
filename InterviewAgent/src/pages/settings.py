"""
Settings page for InterviewAgent Streamlit app
"""

import streamlit as st

def show_settings():
    """Display the settings page"""
    
    st.header("⚙️ Settings")
    
    # User Settings
    st.subheader("👤 User Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="Your Name")
        email = st.text_input("Email", placeholder="your-email@example.com")
    
    with col2:
        st.info("Single-user MVP - These settings apply to the current user.")
    
    # Job Search Preferences
    st.subheader("🔍 Job Search Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        keywords = st.text_area("Keywords", placeholder="software engineer, developer, python")
        location = st.text_input("Preferred Location", placeholder="Remote, San Francisco, New York")
        
    with col2:
        salary_min = st.number_input("Minimum Salary", value=80000, step=10000)
        experience_level = st.selectbox("Experience Level", ["Entry", "Mid", "Senior", "Lead"])
    
    # Automation Settings
    st.subheader("🤖 Automation Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_apply = st.checkbox("Enable Auto-Apply", value=False)
        max_applications = st.number_input("Max Applications per Day", value=10, min_value=1, max_value=50)
        
    with col2:
        schedule_enabled = st.checkbox("Enable Scheduling", value=False)
        schedule_time = st.time_input("Automation Time")
    
    # Job Sites Configuration
    st.subheader("🌐 Job Sites")
    
    st.info("Configure job sites and credentials for automated job discovery.")
    
    # Add placeholder for job site configuration
    with st.expander("LinkedIn Configuration"):
        st.text_input("LinkedIn Email", type="password")
        st.text_input("LinkedIn Password", type="password")
        st.checkbox("Enable LinkedIn", value=True)
    
    with st.expander("Indeed Configuration"):
        st.text_input("Indeed Email", type="password")
        st.text_input("Indeed Password", type="password")  
        st.checkbox("Enable Indeed", value=True)
    
    # Save button
    if st.button("💾 Save All Settings", type="primary"):
        st.success("Settings saved successfully!")
        st.balloons()

if __name__ == "__main__":
    show_settings()