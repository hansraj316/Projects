"""
Job Search page for InterviewAgent Streamlit app
"""

import streamlit as st

def show_job_search():
    """Display the job search page"""
    
    st.header("🔍 Job Search")
    st.info("Job search and discovery functionality will be implemented here.")
    
    # Placeholder content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Search Filters")
        keywords = st.text_input("Keywords", placeholder="e.g., software engineer")
        location = st.text_input("Location", placeholder="e.g., Remote, San Francisco")
        salary_min = st.number_input("Minimum Salary", value=0, step=10000)
    
    with col2:
        st.subheader("Job Sites")
        st.checkbox("LinkedIn", value=True)
        st.checkbox("Indeed", value=True)
        st.checkbox("Glassdoor", value=False)
    
    if st.button("Search Jobs"):
        st.success("Job search initiated!")
    
    st.subheader("Discovered Jobs")
    st.info("No jobs found. Configure job sites and run a search!")

if __name__ == "__main__":
    show_job_search()