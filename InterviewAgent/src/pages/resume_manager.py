"""
Resume Manager page for InterviewAgent Streamlit app
"""

import streamlit as st
import asyncio
import json
from typing import Dict, Any
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.resume_optimizer import ResumeOptimizerAgent
from agents.base_agent import AgentTask, AgentContext
from config import Config

def show_resume_manager():
    """Display the resume manager page with AI optimization"""
    
    st.header("📄 Resume Manager")
    
    # Initialize session state
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = {}
    if 'optimized_resume' not in st.session_state:
        st.session_state.optimized_resume = None
    if 'optimization_results' not in st.session_state:
        st.session_state.optimization_results = None
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📤 Upload Resume", "🎯 Optimize Resume", "📊 Results"])
    
    with tab1:
        _show_upload_section()
    
    with tab2:
        _show_optimization_section()
    
    with tab3:
        _show_results_section()


def _show_upload_section():
    """Show resume upload and parsing section"""
    st.subheader("Upload Your Resume")
    
    uploaded_file = st.file_uploader(
        "Choose a resume file", 
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume to get started with AI optimization"
    )
    
    if uploaded_file:
        st.success(f"Resume uploaded: {uploaded_file.name}")
        
        # Process the uploaded file
        file_content = uploaded_file.read()
        
        # For now, create a sample resume structure
        # In production, this would parse the actual file
        st.session_state.resume_data = {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1 (555) 123-4567",
            "professional_summary": "Experienced software engineer with expertise in Python, JavaScript, and cloud technologies.",
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "SQL"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Software Engineer",
                    "duration": "2020-Present",
                    "achievements": [
                        "Developed scalable web applications serving 100K+ users",
                        "Improved system performance by 40% through optimization",
                        "Led a team of 5 developers on critical projects"
                    ]
                },
                {
                    "company": "StartupXYZ",
                    "position": "Full Stack Developer",
                    "duration": "2018-2020",
                    "achievements": [
                        "Built responsive web applications using React and Node.js",
                        "Implemented CI/CD pipelines reducing deployment time by 60%",
                        "Collaborated with cross-functional teams to deliver features"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "school": "University of Technology",
                    "year": "2018"
                }
            ],
            "uploaded_file": uploaded_file.name,
            "upload_date": datetime.now().isoformat()
        }
        
        st.json(st.session_state.resume_data)
        
        # Manual resume entry option
        with st.expander("✏️ Edit Resume Details"):
            _show_resume_editor()


def _show_resume_editor():
    """Show form to manually edit resume details"""
    if not st.session_state.resume_data:
        st.info("Upload a resume first to edit details")
        return
    
    # Basic information
    st.subheader("Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name", value=st.session_state.resume_data.get("name", ""))
        email = st.text_input("Email", value=st.session_state.resume_data.get("email", ""))
    
    with col2:
        phone = st.text_input("Phone", value=st.session_state.resume_data.get("phone", ""))
    
    # Professional summary
    st.subheader("Professional Summary")
    summary = st.text_area(
        "Professional Summary", 
        value=st.session_state.resume_data.get("professional_summary", ""),
        height=100
    )
    
    # Skills
    st.subheader("Skills")
    skills_text = st.text_area(
        "Skills (comma-separated)", 
        value=", ".join(st.session_state.resume_data.get("skills", [])),
        height=80
    )
    
    # Update button
    if st.button("💾 Save Changes"):
        st.session_state.resume_data.update({
            "name": name,
            "email": email,
            "phone": phone,
            "professional_summary": summary,
            "skills": [skill.strip() for skill in skills_text.split(",") if skill.strip()]
        })
        st.success("Resume updated successfully!")
        st.rerun()


def _show_optimization_section():
    """Show AI resume optimization section"""
    st.subheader("🎯 AI Resume Optimization")
    
    if not st.session_state.resume_data:
        st.warning("Please upload a resume first in the Upload tab")
        return
    
    # Job description input
    st.write("### Job Description")
    job_description = st.text_area(
        "Paste the job description you want to optimize for:",
        height=200,
        placeholder="Paste the full job description here..."
    )
    
    # Job details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g., Google")
    
    with col2:
        job_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer")
    
    with col3:
        industry = st.text_input("Industry", placeholder="e.g., Technology")
    
    # Optimization options
    st.write("### Optimization Options")
    col1, col2 = st.columns(2)
    
    with col1:
        optimization_type = st.selectbox(
            "Optimization Type",
            ["Standard Optimization", "Research-Enhanced Optimization"],
            help="Research-enhanced uses web search for current industry trends"
        )
    
    with col2:
        optimization_approach = st.selectbox(
            "Optimization Approach",
            ["Balanced", "Conservative", "Aggressive", "Creative"],
            help="Different approaches to resume optimization"
        )
    
    # Optimize button
    if st.button("🚀 Optimize Resume", type="primary"):
        if not job_description:
            st.error("Please provide a job description")
            return
        
        if not company_name or not job_title:
            st.error("Please provide company name and job title")
            return
        
        # Show optimization progress
        with st.spinner("Optimizing your resume with AI..."):
            try:
                # Run async optimization
                result = asyncio.run(_optimize_resume(
                    job_description=job_description,
                    company_name=company_name,
                    job_title=job_title,
                    industry=industry,
                    optimization_type=optimization_type,
                    approach=optimization_approach
                ))
                
                if result and result.get("success"):
                    st.session_state.optimization_results = result
                    st.session_state.optimized_resume = result["data"].get("optimized_resume")
                    st.success("Resume optimized successfully!")
                    st.balloons()
                else:
                    st.error(f"Optimization failed: {result.get('message', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Optimization error: {str(e)}")


def _show_results_section():
    """Show optimization results and comparisons"""
    st.subheader("📊 Optimization Results")
    
    if not st.session_state.optimization_results:
        st.info("No optimization results yet. Optimize your resume first!")
        return
    
    results = st.session_state.optimization_results
    data = results.get("data", {})
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Job Match Score", f"{data.get('job_match_score', 0)}%")
    
    with col2:
        keywords_added = len(data.get('keywords_added', []))
        st.metric("Keywords Added", keywords_added)
    
    with col3:
        changes_made = len(data.get('changes_made', []))
        st.metric("Changes Made", changes_made)
    
    with col4:
        st.metric("Status", "✅ Optimized")
    
    # Show optimization summary
    st.write("### Optimization Summary")
    optimization_summary = data.get("optimization_summary", {})
    
    if isinstance(optimization_summary, dict):
        # Professional summary
        if "professional_summary" in optimization_summary:
            st.write("**Optimized Professional Summary:**")
            st.info(optimization_summary["professional_summary"])
        
        # Keywords added
        if "keywords" in optimization_summary:
            st.write("**Keywords Added:**")
            keywords = optimization_summary["keywords"]
            if keywords:
                st.write(", ".join(keywords))
        
        # Changes made
        if "changes" in optimization_summary:
            st.write("**Changes Made:**")
            changes = optimization_summary["changes"]
            if changes:
                for change in changes:
                    st.write(f"• {change}")
    
    # Show industry insights if available
    if "industry_insights" in data:
        with st.expander("🔍 Industry Research Insights"):
            st.write(data["industry_insights"])
    
    # Show salary insights if available
    if "salary_insights" in data:
        with st.expander("💰 Salary Insights"):
            st.write(data["salary_insights"])
    
    # Download options
    st.write("### Download Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Optimized Resume"):
            # Create downloadable content
            resume_json = json.dumps(st.session_state.optimized_resume, indent=2)
            st.download_button(
                label="Download as JSON",
                data=resume_json,
                file_name=f"optimized_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📋 Copy to Clipboard"):
            st.info("Copy functionality would be implemented here")


async def _optimize_resume(
    job_description: str,
    company_name: str,
    job_title: str,
    industry: str,
    optimization_type: str,
    approach: str
) -> Dict[str, Any]:
    """Run async resume optimization"""
    try:
        # Initialize the agent
        config = Config()
        agent = ResumeOptimizerAgent(config=config.__dict__)
        
        # Create task based on optimization type
        if optimization_type == "Research-Enhanced Optimization":
            task_type = "optimize_with_research"
        else:
            task_type = "optimize_resume"
        
        # Create task
        task = AgentTask(
            task_type=task_type,
            input_data={
                "job_description": job_description,
                "current_resume": st.session_state.resume_data,
                "company_name": company_name,
                "job_title": job_title,
                "industry": industry,
                "approach": approach
            }
        )
        
        # Create context
        context = AgentContext(
            session_id=f"resume_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id="streamlit_user",
            shared_data={"optimization_approach": approach}
        )
        
        # Execute the task
        result = await agent.execute(task, context)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Optimization failed: {str(e)}"
        }

if __name__ == "__main__":
    show_resume_manager()