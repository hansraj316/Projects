"""
Resume Manager page for InterviewAgent Streamlit app
"""

import streamlit as st

def show_resume_manager():
    """Display the resume manager page"""
    
    st.header("📄 Resume Manager")
    st.info("Resume management functionality will be implemented here.")
    
    # Placeholder content
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        st.success("Resume uploaded successfully!")
    
    st.subheader("Existing Resumes")
    st.info("No resumes found. Upload your first resume above!")

if __name__ == "__main__":
    show_resume_manager()