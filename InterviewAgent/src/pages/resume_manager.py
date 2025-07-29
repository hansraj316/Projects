"""
Resume Manager page for InterviewAgent Streamlit app
"""

import streamlit as st
import asyncio
import json
import tempfile
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from ..agents.resume_optimizer import ResumeOptimizerAgent
from ..agents.base_agent import AgentTask, AgentContext
from ..config import get_config
from ..utils.file_handler import FileHandler, extract_text_from_file

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
        
        # Initialize file handler
        file_handler = FileHandler()
        
        # Validate the uploaded file
        validation = file_handler.validate_file(uploaded_file, uploaded_file.name)
        
        if not validation.get("valid", False):
            st.error(f"File validation failed: {validation.get('error', 'Unknown error')}")
            return
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{validation['file_size'] / (1024*1024):.2f} MB")
        with col2:
            st.metric("File Type", validation['file_extension'].upper())
        with col3:
            st.metric("Status", "✅ Valid")
        
        # Process the uploaded file with progress
        with st.spinner("Processing resume..."):
            try:
                # Save file temporarily
                save_result = file_handler.save_file(uploaded_file, uploaded_file.name, "streamlit_user")
                
                if not save_result.get("success", False):
                    st.error(f"Failed to save file: {save_result.get('error', 'Unknown error')}")
                    return
                
                file_path = save_result["file_path"]
                
                # Extract text from file
                st.info("Extracting text from resume...")
                text_result = extract_text_from_file(file_path)
                
                if not text_result.get("success", False):
                    st.error(f"Failed to extract text: {text_result.get('error', 'Unknown error')}")
                    return
                
                extracted_text = text_result["text"]
                
                # Display extraction info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words Extracted", text_result.get("word_count", 0))
                with col2:
                    st.metric("Characters", text_result.get("char_count", 0))
                with col3:
                    if "page_count" in text_result:
                        st.metric("Pages", text_result["page_count"])
                    else:
                        st.metric("Type", text_result.get("file_type", "").upper())
                
                # Show extracted text preview
                with st.expander("📄 Preview Extracted Text"):
                    st.text_area(
                        "Extracted Text (first 2000 characters)", 
                        extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else ""),
                        height=300,
                        disabled=True
                    )
                
                # Parse resume with AI
                st.info("Parsing resume with AI...")
                config = Config()
                parse_result = parse_resume_from_text(extracted_text, config)
                
                if not parse_result.get("success", False):
                    st.error(f"Failed to parse resume: {parse_result.get('error', 'Unknown error')}")
                    # Fallback to basic structure
                    st.session_state.resume_data = _create_fallback_resume_data(uploaded_file.name, extracted_text)
                else:
                    # Use parsed data
                    parsed_data = parse_result["data"]
                    st.session_state.resume_data = _convert_parsed_data_to_display_format(parsed_data, uploaded_file.name)
                    st.success("Resume parsed successfully with AI!")
                
                # Clean up temporary file
                file_handler.delete_file(file_path)
                
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                # Fallback to basic structure
                st.session_state.resume_data = _create_fallback_resume_data(uploaded_file.name, "")
        
        # Display parsed resume data
        st.subheader("📋 Parsed Resume Data")
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
        task_id = f"resume_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            description=f"Optimize resume for {job_title} at {company_name}",
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
            user_id="streamlit_user",
            metadata={"optimization_approach": approach}
        )
        
        # Execute the task
        result = await agent.execute(task, context)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Optimization failed: {str(e)}"
        }

def _create_fallback_resume_data(filename: str, extracted_text: str) -> Dict[str, Any]:
    """Create fallback resume data when parsing fails"""
    # Try to extract basic info from text
    lines = extracted_text.split('\n') if extracted_text else []
    
    # Simple name extraction (assume first non-empty line with proper format)
    name = "Unknown"
    email = None
    phone = None
    
    import re
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and len(line.split()) >= 2 and len(line.split()) <= 4:
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
                name = line
                break
    
    # Extract email and phone
    if extracted_text:
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', extracted_text)
        if email_match:
            email = email_match.group()
        
        phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', extracted_text)
        if phone_match:
            phone = phone_match.group()
    
    return {
        "name": name,
        "email": email or "Not found",
        "phone": phone or "Not found",
        "professional_summary": "Professional summary not extracted. Please edit manually.",
        "skills": [],
        "experience": [],
        "education": [],
        "uploaded_file": filename,
        "upload_date": datetime.now().isoformat(),
        "parsing_status": "fallback_used",
        "extracted_text_length": len(extracted_text) if extracted_text else 0
    }


def _convert_parsed_data_to_display_format(parsed_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Convert AI-parsed data to display format compatible with existing UI"""
    personal_info = parsed_data.get("personal_info", {})
    skills_data = parsed_data.get("skills", {})
    
    # Flatten skills into a single list for display
    all_skills = []
    for skill_category in skills_data.values():
        if isinstance(skill_category, list):
            all_skills.extend(skill_category)
    
    # Convert experience data
    experience_list = []
    for exp in parsed_data.get("experience", []):
        if isinstance(exp, dict):
            experience_entry = {
                "company": exp.get("company", "Unknown Company"),
                "position": exp.get("position", "Unknown Position"),
                "duration": f"{exp.get('start_date', 'Unknown')} - {exp.get('end_date', 'Unknown')}",
                "achievements": exp.get("achievements", [])
            }
            if exp.get("description"):
                if not experience_entry["achievements"]:
                    experience_entry["achievements"] = [exp["description"]]
                else:
                    experience_entry["achievements"].insert(0, exp["description"])
            experience_list.append(experience_entry)
    
    # Convert education data
    education_list = []
    for edu in parsed_data.get("education", []):
        if isinstance(edu, dict):
            education_list.append({
                "degree": edu.get("degree", "Unknown Degree"),
                "school": edu.get("institution", "Unknown School"),
                "year": edu.get("graduation_date", "Unknown Year")
            })
    
    return {
        "name": personal_info.get("name", "Unknown"),
        "email": personal_info.get("email", "Not found"),
        "phone": personal_info.get("phone", "Not found"),
        "professional_summary": parsed_data.get("professional_summary", "Not found"),
        "skills": all_skills,
        "experience": experience_list,
        "education": education_list,
        "uploaded_file": filename,
        "upload_date": datetime.now().isoformat(),
        "parsing_status": "ai_parsed",
        "full_parsed_data": parsed_data  # Keep the full structured data for future use
    }


if __name__ == "__main__":
    show_resume_manager()