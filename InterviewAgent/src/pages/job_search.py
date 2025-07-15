"""
Job Search page for InterviewAgent Streamlit app
"""

import streamlit as st
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.job_discovery import JobDiscoveryAgent
from agents.base_agent import AgentTask, AgentContext
from config import Config

def show_job_search():
    """Display the job search page with AI-powered job discovery"""
    
    st.header("🔍 AI-Powered Job Discovery")
    
    # Initialize session state
    if 'discovered_jobs' not in st.session_state:
        st.session_state.discovered_jobs = []
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'market_analysis' not in st.session_state:
        st.session_state.market_analysis = None
    if 'company_research' not in st.session_state:
        st.session_state.company_research = {}
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Job Search", "📈 Market Analysis", "🏢 Company Research", "📋 Saved Jobs"])
    
    with tab1:
        _show_job_search_section()
    
    with tab2:
        _show_market_analysis_section()
    
    with tab3:
        _show_company_research_section()
    
    with tab4:
        _show_saved_jobs_section()


def _show_job_search_section():
    """Show AI-powered job search interface"""
    st.subheader("🎯 Intelligent Job Search")
    
    # Search criteria
    st.write("### Search Criteria")
    col1, col2 = st.columns(2)
    
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
        location = st.text_input("Location", placeholder="e.g., San Francisco, Remote")
        experience_level = st.selectbox(
            "Experience Level",
            ["Any", "Entry Level", "Mid Level", "Senior Level", "Executive"],
            index=0
        )
    
    with col2:
        company_size = st.selectbox(
            "Company Size",
            ["Any", "Startup (1-50)", "Small (51-200)", "Medium (201-1000)", "Large (1000+)"],
            index=0
        )
        remote_preference = st.selectbox(
            "Remote Work",
            ["Any", "Remote Only", "Hybrid", "On-site"],
            index=0
        )
        salary_range = st.text_input("Salary Range", placeholder="e.g., $80k-$120k")
    
    # Additional filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2 = st.columns(2)
        
        with col1:
            required_skills = st.text_area(
                "Required Skills (comma-separated)",
                placeholder="Python, JavaScript, React, AWS",
                height=80
            )
        
        with col2:
            excluded_companies = st.text_area(
                "Exclude Companies (comma-separated)",
                placeholder="Company A, Company B",
                height=80
            )
        
        industry = st.text_input("Industry", placeholder="e.g., Technology, Healthcare")
        job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Internship"])
    
    # Search button
    if st.button("🚀 Search Jobs with AI", type="primary"):
        if not job_title:
            st.error("Please provide a job title")
            return
        
        # Show search progress
        with st.spinner("Searching for jobs using AI..."):
            try:
                # Run async job search
                result = asyncio.run(_search_jobs(
                    job_title=job_title,
                    location=location,
                    experience_level=experience_level,
                    company_size=company_size,
                    remote_preference=remote_preference,
                    salary_range=salary_range,
                    required_skills=required_skills,
                    industry=industry
                ))
                
                if result and result.get("success"):
                    st.session_state.search_results = result
                    jobs = result["data"].get("jobs", [])
                    
                    # Add to discovered jobs
                    for job in jobs:
                        job["discovered_at"] = datetime.now().isoformat()
                        job["saved"] = False
                    
                    st.session_state.discovered_jobs.extend(jobs)
                    
                    st.success(f"Found {len(jobs)} job opportunities!")
                    st.balloons()
                else:
                    st.error(f"Search failed: {result.get('message', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Search error: {str(e)}")
    
    # Show search results
    if st.session_state.search_results:
        _show_search_results()


def _show_search_results():
    """Display job search results"""
    st.write("### Search Results")
    
    results = st.session_state.search_results
    data = results.get("data", {})
    jobs = data.get("jobs", [])
    
    if not jobs:
        st.info("No jobs found for your criteria")
        return
    
    # Search metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Jobs Found", len(jobs))
    
    with col2:
        search_criteria = data.get("search_criteria", {})
        st.metric("Location", search_criteria.get("location", "Any"))
    
    with col3:
        st.metric("Experience Level", search_criteria.get("experience_level", "Any"))
    
    with col4:
        st.metric("Remote Options", search_criteria.get("remote_preference", "Any"))
    
    # Sort and filter options
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox(
            "Sort by:",
            ["Most Recent", "Company Name", "Job Title", "Relevance"]
        )
    
    with col2:
        show_only_remote = st.checkbox("Show only remote jobs")
    
    # Filter jobs
    filtered_jobs = jobs
    if show_only_remote:
        filtered_jobs = [job for job in jobs if "remote" in job.get("location", "").lower()]
    
    # Sort jobs
    if sort_by == "Company Name":
        filtered_jobs.sort(key=lambda x: x.get("company", ""))
    elif sort_by == "Job Title":
        filtered_jobs.sort(key=lambda x: x.get("title", ""))
    
    # Display jobs
    for i, job in enumerate(filtered_jobs):
        with st.expander(f"📄 {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Location:** {job.get('location', 'Not specified')}")
                st.write(f"**Experience:** {job.get('experience_level', 'Not specified')}")
            
            with col2:
                st.write(f"**Skills:** {', '.join(job.get('skills', []))}")
                st.write(f"**Source:** {job.get('source', 'Web search')}")
            
            with col3:
                if st.button("💾 Save Job", key=f"save_{i}"):
                    job["saved"] = True
                    st.success("Job saved!")
                
                if st.button("🏢 Research Company", key=f"research_{i}"):
                    company_name = job.get("company", "")
                    if company_name:
                        _research_company_async(company_name)
            
            # Job description/summary
            if job.get("summary"):
                st.write("**Summary:**")
                st.write(job["summary"])
            
            # Job analysis button
            if st.button("🔍 Analyze Job", key=f"analyze_{i}"):
                st.info("Job analysis feature will be implemented")


def _show_market_analysis_section():
    """Show market trends and analysis"""
    st.subheader("📈 Market Analysis")
    
    # Market analysis form
    col1, col2 = st.columns(2)
    
    with col1:
        job_title = st.text_input("Job Title for Analysis", placeholder="e.g., Data Scientist")
        industry = st.text_input("Industry", placeholder="e.g., Technology")
    
    with col2:
        location = st.text_input("Location Focus", placeholder="e.g., San Francisco")
    
    if st.button("📊 Analyze Market Trends"):
        if not job_title:
            st.error("Please provide a job title")
            return
        
        with st.spinner("Analyzing market trends..."):
            try:
                result = asyncio.run(_analyze_market_trends(
                    job_title=job_title,
                    industry=industry,
                    location=location
                ))
                
                if result and result.get("success"):
                    st.session_state.market_analysis = result
                    st.success("Market analysis completed!")
                else:
                    st.error(f"Analysis failed: {result.get('message', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")
    
    # Show market analysis results
    if st.session_state.market_analysis:
        _show_market_analysis_results()


def _show_market_analysis_results():
    """Display market analysis results"""
    st.write("### Market Analysis Results")
    
    results = st.session_state.market_analysis
    data = results.get("data", {})
    trends = data.get("market_trends", {})
    
    # Market metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Demand Level", trends.get("demand_level", "Unknown"))
    
    with col2:
        st.metric("Salary Trends", trends.get("salary_trends", "Unknown"))
    
    with col3:
        st.metric("Growth Projection", trends.get("growth_projection", "Unknown"))
    
    with col4:
        st.metric("Remote Work Trend", trends.get("remote_work_trend", "Unknown"))
    
    # Top skills
    if trends.get("top_skills"):
        st.write("### In-Demand Skills")
        skills = trends["top_skills"]
        cols = st.columns(len(skills))
        for i, skill in enumerate(skills):
            with cols[i]:
                st.write(f"**{skill}**")
    
    # Full analysis
    if "trends_summary" in data:
        with st.expander("📋 Full Market Analysis"):
            st.write(data["trends_summary"])


def _show_company_research_section():
    """Show company research interface"""
    st.subheader("🏢 Company Research")
    
    # Company research form
    company_name = st.text_input("Company Name", placeholder="e.g., Google")
    
    if st.button("🔍 Research Company"):
        if not company_name:
            st.error("Please provide a company name")
            return
        
        with st.spinner("Researching company..."):
            try:
                result = asyncio.run(_research_company(company_name))
                
                if result and result.get("success"):
                    st.session_state.company_research[company_name] = result
                    st.success("Company research completed!")
                else:
                    st.error(f"Research failed: {result.get('message', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Research error: {str(e)}")
    
    # Show company research results
    if st.session_state.company_research:
        _show_company_research_results()


def _show_company_research_results():
    """Display company research results"""
    st.write("### Company Research Results")
    
    for company_name, result in st.session_state.company_research.items():
        with st.expander(f"🏢 {company_name}"):
            data = result.get("data", {})
            company_data = data.get("company_research", {})
            
            # Company overview
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Industry:** {company_data.get('industry', 'Unknown')}")
                st.write(f"**Size:** {company_data.get('size', 'Unknown')}")
            
            with col2:
                st.write(f"**Culture:** {company_data.get('culture', 'Unknown')}")
                st.write(f"**Recent News:** {company_data.get('recent_news', 'None')}")
            
            # Application tips
            if company_data.get('application_tips'):
                st.write("**Application Tips:**")
                st.info(company_data['application_tips'])
            
            # Full research
            if "research_summary" in data:
                with st.expander("📋 Full Research Summary"):
                    st.write(data["research_summary"])


def _show_saved_jobs_section():
    """Show saved jobs and management"""
    st.subheader("📋 Saved Jobs")
    
    # Filter saved jobs
    saved_jobs = [job for job in st.session_state.discovered_jobs if job.get("saved", False)]
    
    if not saved_jobs:
        st.info("No saved jobs yet. Save jobs from your search results!")
        return
    
    # Saved jobs metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Saved Jobs", len(saved_jobs))
    
    with col2:
        remote_count = len([job for job in saved_jobs if "remote" in job.get("location", "").lower()])
        st.metric("Remote Jobs", remote_count)
    
    with col3:
        companies = set(job.get("company", "") for job in saved_jobs)
        st.metric("Companies", len(companies))
    
    with col4:
        st.metric("Applied", 0)  # Placeholder for future functionality
    
    # Display saved jobs
    for i, job in enumerate(saved_jobs):
        with st.expander(f"📄 {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Location:** {job.get('location', 'Not specified')}")
                st.write(f"**Skills:** {', '.join(job.get('skills', []))}")
            
            with col2:
                saved_date = job.get("discovered_at", "")
                if saved_date:
                    try:
                        date_obj = datetime.fromisoformat(saved_date.replace('Z', '+00:00'))
                        st.write(f"**Saved:** {date_obj.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        st.write(f"**Saved:** {saved_date}")
            
            with col3:
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    job["saved"] = False
                    st.success("Job removed from saved list!")
                    st.rerun()
                
                if st.button("📝 Apply", key=f"apply_{i}"):
                    st.info("Application feature will be implemented")


def _research_company_async(company_name: str):
    """Trigger async company research"""
    try:
        result = asyncio.run(_research_company(company_name))
        if result and result.get("success"):
            st.session_state.company_research[company_name] = result
            st.success(f"Research completed for {company_name}!")
        else:
            st.error(f"Research failed: {result.get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Research error: {str(e)}")


async def _search_jobs(
    job_title: str,
    location: str,
    experience_level: str,
    company_size: str,
    remote_preference: str,
    salary_range: str,
    required_skills: str,
    industry: str
) -> Dict[str, Any]:
    """Run async job search"""
    try:
        # Initialize the agent
        config = Config()
        agent = JobDiscoveryAgent(config=config.__dict__)
        
        # Create task
        task = AgentTask(
            task_type="search_jobs",
            input_data={
                "job_title": job_title,
                "location": location,
                "experience_level": experience_level,
                "company_size": company_size,
                "remote_preference": remote_preference,
                "salary_range": salary_range,
                "required_skills": required_skills,
                "industry": industry
            }
        )
        
        # Create context
        context = AgentContext(
            session_id=f"job_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id="streamlit_user",
            shared_data={"search_type": "job_discovery"}
        )
        
        # Execute the task
        result = await agent.execute(task, context)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Job search failed: {str(e)}"
        }


async def _analyze_market_trends(
    job_title: str,
    industry: str,
    location: str
) -> Dict[str, Any]:
    """Run async market analysis"""
    try:
        # Initialize the agent
        config = Config()
        agent = JobDiscoveryAgent(config=config.__dict__)
        
        # Create task
        task = AgentTask(
            task_type="analyze_market_trends",
            input_data={
                "job_title": job_title,
                "industry": industry,
                "location": location
            }
        )
        
        # Create context
        context = AgentContext(
            session_id=f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id="streamlit_user",
            shared_data={"analysis_type": "market_trends"}
        )
        
        # Execute the task
        result = await agent.execute(task, context)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Market analysis failed: {str(e)}"
        }


async def _research_company(company_name: str) -> Dict[str, Any]:
    """Run async company research"""
    try:
        # Initialize the agent
        config = Config()
        agent = JobDiscoveryAgent(config=config.__dict__)
        
        # Create task
        task = AgentTask(
            task_type="research_company",
            input_data={
                "company_name": company_name
            }
        )
        
        # Create context
        context = AgentContext(
            session_id=f"company_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id="streamlit_user",
            shared_data={"research_type": "company_info"}
        )
        
        # Execute the task
        result = await agent.execute(task, context)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Company research failed: {str(e)}"
        }


if __name__ == "__main__":
    show_job_search()