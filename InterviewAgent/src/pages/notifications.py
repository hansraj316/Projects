"""
Notifications page for InterviewAgent Streamlit app
"""

import streamlit as st

def show_notifications():
    """Display the notifications page"""
    
    st.header("📧 Notifications")
    st.info("Notification management functionality will be implemented here.")
    
    # Placeholder content
    st.subheader("Email Settings")
    
    email = st.text_input("Notification Email", placeholder="your-email@example.com")
    
    st.checkbox("Application Status Updates", value=True)
    st.checkbox("Daily Summary Reports", value=True)
    st.checkbox("Error Notifications", value=True)
    
    if st.button("Save Settings"):
        st.success("Notification settings saved!")
    
    st.subheader("Recent Notifications")
    st.info("No notifications yet.")

if __name__ == "__main__":
    show_notifications()