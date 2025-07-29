"""
Applications page for InterviewAgent Streamlit app
"""

import streamlit as st
import asyncio
import json
from typing import Dict, Any
from datetime import datetime

from ..agents.cover_letter_generator import CoverLetterAgent
from ..agents.base_agent import AgentTask, AgentContext
from ..config import get_config

def show_applications():
    """Display the applications tracking page with cover letter generation"""
    
    st.header("📝 Applications & Cover Letters")
    
    # Initialize session state for cover letters
    if 'cover_letters' not in st.session_state:
        st.session_state.cover_letters = []
    if 'current_cover_letter' not in st.session_state:
        st.session_state.current_cover_letter = None
    if 'cover_letter_results' not in st.session_state:
        st.session_state.cover_letter_results = None
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "✍️ Generate Cover Letter", "📋 Cover Letter Library", "🎯 Application Tracking"])
    
    with tab1:
        _show_overview_section()
    
    with tab2:
        _show_cover_letter_generation()
    
    with tab3:
        _show_cover_letter_library()
    
    with tab4:
        _show_application_tracking()


def _show_overview_section():
    """Show application overview and metrics"""
    st.subheader("📊 Application Overview")
    
    # Application metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cover_letter_count = len(st.session_state.cover_letters)
        st.metric("Cover Letters", cover_letter_count)
    
    with col2:
        st.metric("Applications", 0)
    
    with col3:
        st.metric("Pending", 0)
    
    with col4:
        st.metric("Responses", 0)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if st.session_state.cover_letters:
        st.write("**Recent Cover Letters:**")
        for letter in st.session_state.cover_letters[-3:]:  # Show last 3
            metadata = letter.get('metadata', {})
            st.write(f"• {metadata.get('job_title', 'Unknown Position')} at {metadata.get('company_name', 'Unknown Company')}")
    else:
        st.info("No cover letters generated yet. Use the Generate Cover Letter tab to get started!")


def _show_cover_letter_generation():
    """Show cover letter generation interface"""
    st.subheader("✍️ AI Cover Letter Generation")
    
    # Job information section
    st.write("### Job Information")
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g., Google")
        job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
    
    with col2:
        hiring_manager = st.text_input("Hiring Manager", placeholder="e.g., John Smith (optional)")
        if not hiring_manager:
            hiring_manager = "Hiring Manager"
    
    # Job description
    st.write("### Job Description")
    job_description = st.text_area(
        "Paste the job description:",
        height=200,
        placeholder="Paste the complete job description here..."
    )
    
    # Candidate information
    st.write("### Candidate Information")
    with st.expander("📝 Enter Your Information"):
        col1, col2 = st.columns(2)
        
        with col1:
            candidate_name = st.text_input("Your Name", placeholder="John Doe")
            candidate_email = st.text_input("Email", placeholder="john.doe@email.com")
            candidate_phone = st.text_input("Phone", placeholder="+1 (555) 123-4567")
        
        with col2:
            current_position = st.text_input("Current Position", placeholder="Senior Developer")
            years_experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=5)
            location = st.text_input("Location", placeholder="San Francisco, CA")
        
        # Key achievements
        achievements = st.text_area(
            "Key Achievements (one per line):",
            placeholder="• Increased system performance by 40%\n• Led a team of 5 developers\n• Implemented CI/CD pipeline",
            height=100
        )
    
    # Generation options
    st.write("### Generation Options")
    col1, col2 = st.columns(2)
    
    with col1:
        generation_type = st.selectbox(
            "Generation Type",
            ["Standard Cover Letter", "Research-Enhanced Cover Letter"],
            help="Research-enhanced uses web search for current company information"
        )
    
    with col2:
        letter_tone = st.selectbox(
            "Letter Tone",
            ["Professional", "Enthusiastic", "Analytical"],
            help="Different tones for different company cultures"
        )
    
    # Generate button
    if st.button("🚀 Generate Cover Letter", type="primary"):
        if not job_description or not company_name or not job_title:
            st.error("Please provide job description, company name, and job title")
            return
        
        if not candidate_name:
            st.error("Please provide your name")
            return
        
        # Prepare candidate information
        candidate_info = {
            "name": candidate_name,
            "email": candidate_email,
            "phone": candidate_phone,
            "current_position": current_position,
            "years_experience": years_experience,
            "location": location,
            "achievements": [line.strip() for line in achievements.split('\n') if line.strip()]
        }
        
        # Show generation progress
        with st.spinner("Generating your personalized cover letter..."):
            try:
                # Run async cover letter generation
                result = asyncio.run(_generate_cover_letter(
                    job_description=job_description,
                    company_name=company_name,
                    job_title=job_title,
                    hiring_manager=hiring_manager,
                    candidate_info=candidate_info,
                    generation_type=generation_type,
                    letter_tone=letter_tone
                ))
                
                if result and result.get("success"):
                    st.session_state.cover_letter_results = result
                    st.session_state.current_cover_letter = result["data"].get("cover_letter")
                    
                    # Add to library
                    st.session_state.cover_letters.append({
                        "cover_letter": result["data"].get("cover_letter"),
                        "metadata": result.get("metadata", {}),
                        "generated_at": datetime.now().isoformat(),
                        "quality_score": result["data"].get("quality_score", 0)
                    })
                    
                    st.success("Cover letter generated successfully!")
                    st.balloons()
                else:
                    st.error(f"Generation failed: {result.get('message', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Generation error: {str(e)}")
    
    # Show results if available
    if st.session_state.cover_letter_results:
        _show_cover_letter_results()


def _show_cover_letter_results():
    """Show generated cover letter results"""
    st.write("### Generated Cover Letter")
    
    results = st.session_state.cover_letter_results
    data = results.get("data", {})
    cover_letter = data.get("cover_letter", {})
    
    # Quality metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        quality_score = data.get("quality_score", 0)
        st.metric("Quality Score", f"{quality_score}/100")
    
    with col2:
        word_count = data.get("word_count", 0)
        st.metric("Word Count", word_count)
    
    with col3:
        personalization_count = len(data.get("personalization_elements", []))
        st.metric("Personalization", personalization_count)
    
    with col4:
        st.metric("Status", "✅ Generated")
    
    # Display the cover letter
    if isinstance(cover_letter, dict):
        # Show structured cover letter
        st.write("**Cover Letter:**")
        
        # Header
        if cover_letter.get("header"):
            for line in cover_letter["header"]:
                st.write(line)
        
        # Salutation
        if cover_letter.get("salutation"):
            st.write(f"\n{cover_letter['salutation']}")
        
        # Body paragraphs
        if cover_letter.get("body_paragraphs"):
            for paragraph in cover_letter["body_paragraphs"]:
                st.write(f"\n{paragraph}")
        
        # Closing
        if cover_letter.get("closing"):
            st.write(f"\n{cover_letter['closing']}")
        
        # Signature
        if cover_letter.get("signature"):
            st.write(f"\n{cover_letter['signature']}")
        
        # Show full text in a text area for easy copying
        st.write("**Full Text (Copy-friendly):**")
        full_text = cover_letter.get("full_text", "")
        st.text_area("", value=full_text, height=300)
    
    # Show additional insights
    if "company_research" in data:
        with st.expander("🔍 Company Research Used"):
            st.write(data["company_research"])
    
    if "key_points" in data:
        with st.expander("🎯 Key Points Highlighted"):
            key_points = data["key_points"]
            for point in key_points:
                st.write(f"• {point}")
    
    if "personalization_elements" in data:
        with st.expander("🎨 Personalization Elements"):
            elements = data["personalization_elements"]
            for element in elements:
                st.write(f"• {element}")


def _show_cover_letter_library():
    """Show saved cover letters library"""
    st.subheader("📋 Cover Letter Library")
    
    if not st.session_state.cover_letters:
        st.info("No cover letters saved yet. Generate your first cover letter!")
        return
    
    # Search and filter
    search_term = st.text_input("🔍 Search cover letters", placeholder="Search by company or job title...")
    
    # Sort options
    sort_option = st.selectbox(
        "Sort by:",
        ["Most Recent", "Oldest First", "Quality Score", "Company Name"]
    )
    
    # Filter and sort cover letters
    filtered_letters = st.session_state.cover_letters
    
    if search_term:
        filtered_letters = [
            letter for letter in filtered_letters
            if search_term.lower() in letter.get("metadata", {}).get("company_name", "").lower()
            or search_term.lower() in letter.get("metadata", {}).get("job_title", "").lower()
        ]
    
    # Sort
    if sort_option == "Most Recent":
        filtered_letters.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
    elif sort_option == "Oldest First":
        filtered_letters.sort(key=lambda x: x.get("generated_at", ""))
    elif sort_option == "Quality Score":
        filtered_letters.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    elif sort_option == "Company Name":
        filtered_letters.sort(key=lambda x: x.get("metadata", {}).get("company_name", ""))
    
    # Display cover letters
    for i, letter in enumerate(filtered_letters):
        metadata = letter.get("metadata", {})
        cover_letter_data = letter.get("cover_letter", {})
        
        with st.expander(f"📄 {metadata.get('job_title', 'Unknown Position')} at {metadata.get('company_name', 'Unknown Company')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Quality Score:** {letter.get('quality_score', 0)}/100")
            
            with col2:
                generated_date = letter.get("generated_at", "")
                if generated_date:
                    try:
                        date_obj = datetime.fromisoformat(generated_date.replace('Z', '+00:00'))
                        st.write(f"**Generated:** {date_obj.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        st.write(f"**Generated:** {generated_date}")
            
            with col3:
                if st.button("📋 Use This Letter", key=f"use_{i}"):
                    st.session_state.current_cover_letter = cover_letter_data
                    st.success("Cover letter selected!")
            
            # Show preview
            if isinstance(cover_letter_data, dict):
                full_text = cover_letter_data.get("full_text", "")
                if full_text:
                    st.text_area("Preview:", value=full_text[:500] + "..." if len(full_text) > 500 else full_text, height=150, key=f"preview_{i}")


def _show_application_tracking():
    """Show application tracking interface"""
    st.subheader("🎯 Application Tracking")
    st.info("Application tracking functionality will be implemented here.")
    
    # Placeholder for application tracking
    st.write("### Application Pipeline")
    st.write("Future features:")
    st.write("• Track application status")
    st.write("• Monitor response rates")
    st.write("• Schedule follow-ups")
    st.write("• Integration with job boards")


async def _generate_cover_letter(
    job_description: str,
    company_name: str,
    job_title: str,
    hiring_manager: str,
    candidate_info: Dict[str, Any],
    generation_type: str,
    letter_tone: str
) -> Dict[str, Any]:
    """Run async cover letter generation"""
    try:
        # Initialize the agent
        config = Config()
        agent = CoverLetterAgent(config=config.__dict__)
        
        # Create task based on generation type
        if generation_type == "Research-Enhanced Cover Letter":
            task_type = "generate_with_research"
        else:
            task_type = "generate_cover_letter"
        
        # Create task
        task_id = f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            description=f"Generate cover letter for {job_title} at {company_name}",
            input_data={
                "job_description": job_description,
                "company_name": company_name,
                "job_title": job_title,
                "hiring_manager": hiring_manager,
                "candidate_info": candidate_info,
                "letter_tone": letter_tone
            }
        )
        
        # Create context
        context = AgentContext(
            user_id="streamlit_user",
            metadata={"letter_tone": letter_tone}
        )
        
        # Execute the task
        result = await agent.execute(task, context)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Cover letter generation failed: {str(e)}"
        }

if __name__ == "__main__":
    show_applications()