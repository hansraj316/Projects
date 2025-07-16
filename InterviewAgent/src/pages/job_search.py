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
from database.operations import get_db_operations

def show_job_search():
    """Display the job search page with AI-powered job discovery"""
    
    st.header("🔍 AI-Powered Job Discovery")
    
    # Initialize session state and load previous searches
    if 'discovered_jobs' not in st.session_state:
        st.session_state.discovered_jobs = []
        # Load previous job searches from database
        _load_previous_job_searches()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'market_analysis' not in st.session_state:
        st.session_state.market_analysis = None
    if 'company_research' not in st.session_state:
        st.session_state.company_research = {}
    if 'job_search_history' not in st.session_state:
        st.session_state.job_search_history = []
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Job Search", "📈 Market Analysis", "🏢 Company Research", "📋 Saved Jobs", "📚 Search History"])
    
    with tab1:
        _show_job_search_section()
    
    with tab2:
        _show_market_analysis_section()
    
    with tab3:
        _show_company_research_section()
    
    with tab4:
        _show_saved_jobs_section()
    
    with tab5:
        _show_search_history_section()


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
                    
                    # Save to database
                    try:
                        db_ops = get_db_operations()
                        
                        # Get or create user for single-user MVP
                        user = db_ops.get_or_create_user(
                            email="user@interviewagent.local",
                            full_name="InterviewAgent User"
                        )
                        
                        search_criteria = {
                            "job_title": job_title,
                            "location": location,
                            "experience_level": experience_level,
                            "company_size": company_size,
                            "remote_preference": remote_preference,
                            "salary_range": salary_range,
                            "required_skills": required_skills,
                            "industry": industry
                        }
                        
                        # Save job search to database
                        job_search = db_ops.create_job_search(
                            user_id=user.id,  # Use proper UUID from user
                            search_query=f"{job_title} in {location or 'any location'}",
                            search_criteria=search_criteria,
                            jobs_found=len(jobs),
                            search_results=result["data"]
                        )
                        
                        st.success(f"Found {len(jobs)} job opportunities! Search saved to database.")
                        
                        # Refresh search history
                        _refresh_search_history()
                        
                    except Exception as db_error:
                        st.warning(f"Jobs found but database save failed: {str(db_error)}")
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
    
    # Display jobs with search context
    for i, job in enumerate(filtered_jobs):
        # Enhanced job card display with search metadata
        search_info = ""
        if job.get('search_query'):
            search_info = f" (from: {job.get('search_query')})"
        
        with st.expander(f"📄 {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}{search_info}"):
            # Job header with key info
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Location:** {job.get('location', 'Not specified')}")
                st.write(f"**Experience:** {job.get('experience_level', 'Not specified')}")
            
            with col2:
                st.write(f"**Salary:** {job.get('salary_range', 'Not specified')}")
                st.write(f"**Source:** {job.get('source', 'Web search')}")
            
            with col3:
                st.write(f"**Posted:** {job.get('posted_date', 'Unknown')}")
                if job.get('skills'):
                    skills_count = len(job['skills'])
                    st.write(f"**Skills Required:** {skills_count}")
            
            with col4:
                if st.button("💾 Save Job", key=f"search_save_{i}"):
                    job["saved"] = True
                    st.success("Job saved!")
                    st.rerun()
                
                if st.button("🏢 Research Company", key=f"search_research_{i}"):
                    company_name = job.get("company", "")
                    if company_name:
                        _research_company_async(company_name)
            
            # Job description/summary
            if job.get("summary"):
                st.write("**Job Summary:**")
                st.write(job["summary"])
            
            # Skills section
            if job.get("skills"):
                st.write("**Required Skills:**")
                # Display skills as tags
                skills_text = " • ".join(job["skills"])
                st.markdown(f"🏷️ {skills_text}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔍 Analyze Job", key=f"search_analyze_{i}"):
                    st.info("Job analysis feature will be implemented")
            
            with col2:
                if st.button("📝 Generate Cover Letter", key=f"search_cover_letter_{i}"):
                    st.info("Cover letter generation will be implemented")
            
            with col3:
                if st.button("🚀 Quick Apply", key=f"search_apply_{i}"):
                    st.info("Application feature will be implemented")


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
        with st.expander(f"⭐ {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}"):
            # Enhanced layout matching search results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Location:** {job.get('location', 'Not specified')}")
                st.write(f"**Experience:** {job.get('experience_level', 'Not specified')}")
            
            with col2:
                st.write(f"**Salary:** {job.get('salary_range', 'Not specified')}")
                st.write(f"**Source:** {job.get('source', 'Web search')}")
            
            with col3:
                saved_date = job.get("discovered_at", "")
                if saved_date:
                    try:
                        date_obj = datetime.fromisoformat(saved_date.replace('Z', '+00:00'))
                        st.write(f"**Saved:** {date_obj.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        st.write(f"**Saved:** {saved_date}")
                else:
                    st.write("**Saved:** Recently")
                
                if job.get('skills'):
                    skills_count = len(job['skills'])
                    st.write(f"**Skills Required:** {skills_count}")
            
            with col4:
                if st.button("🗑️ Remove", key=f"saved_remove_{i}"):
                    job["saved"] = False
                    st.success("Job removed from saved list!")
                    st.rerun()
            
            # Job description/summary
            if job.get("summary"):
                st.write("**Job Summary:**")
                st.write(job["summary"])
            
            # Skills section
            if job.get("skills"):
                st.write("**Required Skills:**")
                skills_text = " • ".join(job["skills"])
                st.markdown(f"🏷️ {skills_text}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔍 Analyze Job", key=f"saved_analyze_{i}"):
                    st.info("Job analysis feature will be implemented")
            
            with col2:
                if st.button("📝 Generate Cover Letter", key=f"saved_cover_letter_{i}"):
                    st.info("Cover letter generation will be implemented")
            
            with col3:
                if st.button("🚀 Apply Now", key=f"saved_apply_{i}"):
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
            task_id=f"search_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type="search_jobs",
            description=f"Search for {job_title} jobs in {location or 'any location'}",
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
        
        # Get or create user for context
        config = Config()
        from database.operations import get_db_operations
        db_ops = get_db_operations()
        user = db_ops.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        
        # Create context
        context = AgentContext(
            user_id=user.id,
            metadata={"search_type": "job_discovery", "session_id": f"job_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
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
            task_id=f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type="analyze_market_trends",
            description=f"Analyze market trends for {job_title} in {industry or 'any industry'}",
            input_data={
                "job_title": job_title,
                "industry": industry,
                "location": location
            }
        )
        
        # Get or create user for context
        from database.operations import get_db_operations
        db_ops = get_db_operations()
        user = db_ops.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        
        # Create context
        context = AgentContext(
            user_id=user.id,
            metadata={"analysis_type": "market_trends", "session_id": f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
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
            task_id=f"company_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type="research_company",
            description=f"Research company information for {company_name}",
            input_data={
                "company_name": company_name
            }
        )
        
        # Get or create user for context
        from database.operations import get_db_operations
        db_ops = get_db_operations()
        user = db_ops.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        
        # Create context
        context = AgentContext(
            user_id=user.id,
            metadata={"research_type": "company_info", "session_id": f"company_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
        )
        
        # Execute the task
        result = await agent.execute(task, context)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Company research failed: {str(e)}"
        }


def _load_previous_job_searches():
    """Load previous job searches from database into session state"""
    try:
        db_ops = get_db_operations()
        
        # Get or create user
        user = db_ops.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        
        # Get ALL job searches (no limit for history)
        job_searches = db_ops.get_job_searches(user.id, limit=100)  # Increased limit
        st.session_state.job_search_history = job_searches
        
        # Load jobs from recent searches into discovered_jobs
        for search in job_searches:
            if search.search_results:
                try:
                    # Handle both dict and JSON string formats
                    if isinstance(search.search_results, str):
                        search_data = json.loads(search.search_results)
                    else:
                        search_data = search.search_results
                    
                    if 'jobs' in search_data:
                        jobs = search_data['jobs']
                    else:
                        continue
                except (json.JSONDecodeError, TypeError):
                    continue
                for job in jobs:
                    # Add metadata about which search this came from
                    try:
                        if search.created_at:
                            # Handle timezone-aware datetime
                            if search.created_at.tzinfo is not None:
                                discovered_time = search.created_at.replace(tzinfo=None)
                            else:
                                discovered_time = search.created_at
                            job["discovered_at"] = discovered_time.isoformat()
                        else:
                            job["discovered_at"] = datetime.now().isoformat()
                    except Exception:
                        job["discovered_at"] = datetime.now().isoformat()
                    
                    job["saved"] = False
                    job["search_id"] = search.id
                    job["search_query"] = search.search_query
                
                # Add jobs to discovered_jobs with better deduplication
                existing_jobs = {
                    f"{job.get('title', '')}_{job.get('company', '')}_{job.get('job_id', '')}" 
                    for job in st.session_state.discovered_jobs
                }
                
                for job in jobs:
                    # Create unique key using job_id if available, otherwise fallback to title+company
                    job_key = f"{job.get('title', '')}_{job.get('company', '')}_{job.get('job_id', '')}"
                    if job_key not in existing_jobs:
                        st.session_state.discovered_jobs.append(job)
                        existing_jobs.add(job_key)
        
    except Exception as e:
        st.error(f"Failed to load previous job searches: {str(e)}")


def _refresh_search_history():
    """Refresh search history after new search"""
    try:
        db_ops = get_db_operations()
        
        # Get or create user
        user = db_ops.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        
        # Refresh job search history
        job_searches = db_ops.get_job_searches(user.id, limit=100)  # Increased limit
        st.session_state.job_search_history = job_searches
        
    except Exception as e:
        st.error(f"Failed to refresh search history: {str(e)}")


def _show_search_history_section():
    """Show previous job search history"""
    st.subheader("📚 Job Search History")
    
    if not st.session_state.job_search_history:
        st.info("No previous job searches found. Start a new search to build your history!")
        return
    
    # Search history metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_searches = len(st.session_state.job_search_history)
    total_jobs = sum(search.jobs_found for search in st.session_state.job_search_history)
    
    with col1:
        st.metric("Total Searches", total_searches)
    
    with col2:
        st.metric("Total Jobs Found", total_jobs)
    
    with col3:
        avg_jobs = total_jobs / total_searches if total_searches > 0 else 0
        st.metric("Avg Jobs/Search", f"{avg_jobs:.1f}")
    
    with col4:
        recent_search = st.session_state.job_search_history[0] if st.session_state.job_search_history else None
        if recent_search and recent_search.created_at:
            # Handle timezone-aware datetime comparison
            try:
                # Make both datetimes timezone-naive for comparison
                if recent_search.created_at.tzinfo is not None:
                    # If created_at is timezone-aware, convert to naive UTC
                    search_time = recent_search.created_at.replace(tzinfo=None)
                else:
                    # If already naive, use as-is
                    search_time = recent_search.created_at
                
                current_time = datetime.now()
                days_ago = (current_time - search_time).days
                st.metric("Last Search", f"{days_ago} days ago")
            except Exception:
                st.metric("Last Search", "Recently")
    
    # Search history list
    st.write("### Recent Searches")
    
    for i, search in enumerate(st.session_state.job_search_history):
        with st.expander(f"🔍 {search.search_query} ({search.jobs_found} jobs found)"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Handle timezone-aware datetime display
                try:
                    if search.created_at:
                        # Format datetime, handling timezone-aware dates
                        if search.created_at.tzinfo is not None:
                            # Convert to local time for display
                            display_time = search.created_at.replace(tzinfo=None)
                        else:
                            display_time = search.created_at
                        st.write(f"**Search Date:** {display_time.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.write("**Search Date:** Unknown")
                except Exception:
                    st.write("**Search Date:** Recently")
                
                st.write(f"**Jobs Found:** {search.jobs_found}")
                
                # Show search criteria
                if search.search_criteria:
                    st.write("**Search Criteria:**")
                    try:
                        # Handle both dict and JSON string formats
                        if isinstance(search.search_criteria, str):
                            criteria = json.loads(search.search_criteria)
                        else:
                            criteria = search.search_criteria
                        
                        if criteria.get('job_title'):
                            st.write(f"• Job Title: {criteria['job_title']}")
                        if criteria.get('location'):
                            st.write(f"• Location: {criteria['location']}")
                        if criteria.get('experience_level'):
                            st.write(f"• Experience: {criteria['experience_level']}")
                        if criteria.get('remote_preference'):
                            st.write(f"• Remote: {criteria['remote_preference']}")
                    except (json.JSONDecodeError, TypeError) as e:
                        st.write("• Search criteria format error")
            
            with col2:
                # Action buttons
                if st.button("🔄 Repeat Search", key=f"repeat_search_{i}"):
                    st.info("Repeat search functionality will be implemented")
                
                if st.button("📊 View Results", key=f"view_results_{i}"):
                    # Load this search results into current view
                    if search.search_results:
                        try:
                            # Handle both dict and JSON string formats
                            if isinstance(search.search_results, str):
                                search_data = json.loads(search.search_results)
                            else:
                                search_data = search.search_results
                            
                            st.session_state.search_results = {
                                "success": True,
                                "data": search_data
                            }
                            st.success("Search results loaded! Check the Job Search tab.")
                            st.rerun()
                        except (json.JSONDecodeError, TypeError) as e:
                            st.error(f"Failed to load search results: {str(e)}")
                
                if st.button("🗑️ Delete Search", key=f"delete_search_{i}"):
                    st.warning("Delete search functionality will be implemented")


if __name__ == "__main__":
    show_job_search()