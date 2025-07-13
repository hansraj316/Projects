"""
Applications page for InterviewAgent Streamlit app
"""

import streamlit as st

def show_applications():
    """Display the applications tracking page"""
    
    st.header("📝 Applications")
    st.info("Application tracking functionality will be implemented here.")
    
    # Placeholder content
    st.subheader("Application Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", 0)
    with col2:
        st.metric("Pending", 0)
    with col3:
        st.metric("Submitted", 0)
    with col4:
        st.metric("Responses", 0)
    
    st.subheader("Recent Applications")
    st.info("No applications found. Start the automation workflow to begin applying!")

if __name__ == "__main__":
    show_applications()