"""
Job Search page for InterviewAgent Streamlit app
"""

import streamlit as st
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

# Note: Path is already set by streamlit_app.py, so direct imports should work
from agents.job_discovery import JobDiscoveryAgent
from agents.base_agent import AgentTask, AgentContext

from config import Config
from database.operations import get_db_operations
from services.job_automation_service import JobAutomationService

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
    if st.button("🚀 Search Jobs with AI & Auto-Save", type="primary"):
        if not job_title:
            st.error("Please provide a job title")
            return
        
        # Show search progress
        with st.spinner("Searching for jobs and setting up automation..."):
            try:
                # Run async job search with automation
                result = asyncio.run(_search_jobs_with_automation(
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
                    automation_results = result.get("automation_results", {})
                    
                    # Show comprehensive results
                    jobs_saved = automation_results.get("jobs_saved", 0)
                    automations_triggered = automation_results.get("automations_triggered", 0)
                    
                    # Get actual jobs count from the result
                    jobs_found = len(result.get("data", {}).get("jobs", []))
                    
                    # Success message with automation details
                    success_msg = f"🎉 **Search Complete!**\n"
                    success_msg += f"• **{jobs_found} jobs** found and displayed\n"
                    if jobs_saved > 0:
                        success_msg += f"• **{jobs_saved} jobs** automatically saved to database\n"
                    if automations_triggered > 0:
                        success_msg += f"• **{automations_triggered} applications** queued for automation\n"
                    success_msg += f"• Jobs are now viewable with direct application URLs"
                    
                    st.success(success_msg)
                    
                    # Show automation summary
                    if automation_results.get("triggered_automations"):
                        with st.expander("🤖 Automation Queue Details"):
                            for automation in automation_results["triggered_automations"]:
                                st.write(f"✅ **{automation['job_title']}** at **{automation['company']}** - Automation ID: `{automation['automation_id'][:8]}...`")
                    
                    # Update session state for immediate display
                    jobs = result["data"].get("jobs", [])
                    for job in jobs:
                        job["discovered_at"] = datetime.now().isoformat()
                        job["saved"] = True  # All jobs are now auto-saved
                        job["automation_triggered"] = job.get("application_priority", 5) >= 6
                    
                    st.session_state.discovered_jobs.extend(jobs)
                    
                    # Refresh search history
                    _refresh_search_history()
                    _refresh_saved_jobs()  # Refresh saved jobs from database
                    
                    st.balloons()
                else:
                    # Improved error handling with specific error messages
                    error_message = result.get('message', 'Unknown error occurred')
                    if 'error' in result:
                        error_message = result['error']
                    
                    # Check for common error types and provide helpful messages
                    if 'API' in error_message or 'client' in error_message.lower():
                        st.error("🔧 **Job Search Service Issue**\n\nThe job search service is currently experiencing issues. This might be due to:\n- API configuration problems\n- Network connectivity issues\n- Service maintenance\n\nPlease try again in a few minutes.")
                    elif 'timeout' in error_message.lower():
                        st.error("⏰ **Search Timeout**\n\nThe job search took too long to complete. Try:\n- Simplifying your search criteria\n- Searching for a more specific job title\n- Trying again in a moment")
                    elif 'configuration' in error_message.lower():
                        st.error("⚙️ **Configuration Issue**\n\nThere's a configuration problem with the job search service. Please contact support or try again later.")
                    else:
                        st.error(f"❌ **Search Failed**\n\n{error_message}\n\nPlease try:\n- Checking your search criteria\n- Using a different job title\n- Trying again in a moment")
            
            except Exception as e:
                # Improved exception handling with specific error types
                error_str = str(e)
                if 'OpenAI' in error_str or 'API' in error_str:
                    st.error("🔧 **AI Service Unavailable**\n\nThe AI-powered job search is currently unavailable. This might be due to:\n- Service maintenance\n- API limits reached\n- Network connectivity issues\n\nPlease try again later.")
                elif 'timeout' in error_str.lower():
                    st.error("⏰ **Request Timeout**\n\nThe search request timed out. Please try again with simpler criteria.")
                elif 'connection' in error_str.lower() or 'network' in error_str.lower():
                    st.error("🌐 **Network Issue**\n\nUnable to connect to job search services. Please check your internet connection and try again.")
                else:
                    st.error(f"❌ **Unexpected Error**\n\nAn unexpected error occurred: {error_str}\n\nPlease try again or contact support if the issue persists.")
    
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
        
        # Add job status indicators
        job_status_icons = ""
        if job.get("saved"):
            job_status_icons += "💾 "
        if job.get("automation_triggered"):
            job_status_icons += "🤖 "
        
        with st.expander(f"{job_status_icons}📄 {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}{search_info}"):
            # Job URL prominently displayed
            job_url = job.get('application_url') or job.get('apply_link', '')
            if job_url:
                st.markdown(f"🔗 **Apply Here:** [{job_url}]({job_url})")
                if st.button("📋 Copy URL", key=f"copy_url_{i}"):
                    st.success("URL copied to clipboard! (Feature simulated)")
            else:
                st.warning("⚠️ No application URL available")
            
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
                
                # Show automation status
                if job.get("automation_triggered"):
                    st.success("🤖 Auto-apply queued")
                else:
                    st.info("⏳ Manual application")
            
            with col4:
                if job.get("saved"):
                    st.success("💾 Saved")
                else:
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
    
    # Load saved jobs from database
    if 'database_saved_jobs' not in st.session_state:
        st.session_state.database_saved_jobs = []
        _refresh_saved_jobs()
    
    # Combine session saved jobs with database saved jobs
    session_saved_jobs = [job for job in st.session_state.discovered_jobs if job.get("saved", False)]
    database_saved_jobs = st.session_state.database_saved_jobs
    
    # Merge and deduplicate
    all_saved_jobs = []
    seen_urls = set()
    
    for job in database_saved_jobs + session_saved_jobs:
        job_url = job.get('job_url') or job.get('application_url') or job.get('apply_link', '')
        if job_url and job_url not in seen_urls:
            seen_urls.add(job_url)
            all_saved_jobs.append(job)
    
    if not all_saved_jobs:
        st.info("No saved jobs yet. Search for jobs to automatically save them!")
        return
    
    # Saved jobs metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Saved Jobs", len(all_saved_jobs))
    
    with col2:
        remote_count = len([job for job in all_saved_jobs if "remote" in job.get("location", "").lower()])
        st.metric("Remote Jobs", remote_count)
    
    with col3:
        companies = set(job.get("company", "") for job in all_saved_jobs)
        st.metric("Companies", len(companies))
    
    with col4:
        auto_apply_count = len([job for job in all_saved_jobs if job.get("auto_apply_enabled", False)])
        st.metric("Auto-Apply Enabled", auto_apply_count)
    
    # Sort options
    col1, col2 = st.columns(2)
    with col1:
        sort_option = st.selectbox("Sort by:", ["Priority (High to Low)", "Date Added", "Company", "Job Title"])
    with col2:
        if st.button("🔄 Refresh from Database"):
            _refresh_saved_jobs()
            st.rerun()
    
    # Sort jobs
    if sort_option == "Priority (High to Low)":
        all_saved_jobs.sort(key=lambda x: x.get("application_priority", 5), reverse=True)
    elif sort_option == "Date Added":
        all_saved_jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort_option == "Company":
        all_saved_jobs.sort(key=lambda x: x.get("company", ""))
    elif sort_option == "Job Title":
        all_saved_jobs.sort(key=lambda x: x.get("title", ""))
    
    # Display saved jobs
    for i, job in enumerate(all_saved_jobs):
        # Priority indicator
        priority = job.get('application_priority', 5)
        priority_color = "🔴" if priority >= 8 else "🟡" if priority >= 6 else "🟢"
        auto_apply_status = "🤖" if job.get('auto_apply_enabled', False) else "👤"
        
        with st.expander(f"{priority_color}{auto_apply_status} {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')} (Priority: {priority})"):
            # Job URL prominently displayed
            job_url = job.get('job_url') or job.get('application_url') or job.get('apply_link', '')
            if job_url:
                st.markdown(f"🔗 **Apply Here:** [{job_url}]({job_url})")
                col_url1, col_url2 = st.columns(2)
                with col_url1:
                    if st.button("📋 Copy URL", key=f"copy_saved_url_{i}"):
                        st.success("URL copied to clipboard! (Feature simulated)")
                with col_url2:
                    if st.button("🌐 Open in New Tab", key=f"open_saved_url_{i}"):
                        st.success("Opening URL in new tab! (Feature simulated)")
            else:
                st.warning("⚠️ No application URL available")
            
            # Enhanced layout
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Location:** {job.get('location', 'Not specified')}")
                st.write(f"**Experience:** {job.get('experience_level', 'Not specified')}")
                st.write(f"**Remote Type:** {job.get('remote_type', 'Not specified')}")
            
            with col2:
                st.write(f"**Salary:** {job.get('salary_range', 'Not specified')}")
                st.write(f"**Source:** {job.get('source', 'Database')}")
                st.write(f"**Job Type:** {job.get('job_type', 'Not specified')}")
            
            with col3:
                # Show creation/discovery date
                saved_date = job.get("created_at") or job.get("discovered_at", "")
                if saved_date:
                    try:
                        if isinstance(saved_date, str):
                            date_obj = datetime.fromisoformat(saved_date.replace('Z', '+00:00'))
                        else:
                            date_obj = saved_date
                        st.write(f"**Saved:** {date_obj.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        st.write(f"**Saved:** {saved_date}")
                else:
                    st.write("**Saved:** Recently")
                
                if job.get('skills'):
                    skills_count = len(job['skills'])
                    st.write(f"**Skills Required:** {skills_count}")
                else:
                    st.write("**Skills:** Not specified")
                
                # Show automation status
                if job.get('auto_apply_enabled', False):
                    st.success(f"🤖 Auto-apply (Priority {priority})")
                else:
                    st.info("👤 Manual application")
            
            with col4:
                # Toggle auto-apply
                if job.get('auto_apply_enabled', False):
                    if st.button("🔇 Disable Auto-Apply", key=f"disable_auto_{i}"):
                        st.success("Auto-apply disabled!")
                        # This would update the database in real implementation
                else:
                    if st.button("🔔 Enable Auto-Apply", key=f"enable_auto_{i}"):
                        st.success("Auto-apply enabled!")
                        # This would update the database in real implementation
                
                if st.button("🗑️ Remove", key=f"saved_remove_{i}"):
                    st.success("Job removed from saved list!")
                    # This would remove from database in real implementation
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
        
        # Create simple logger implementation
        class SimpleLogger:
            def info(self, message, **kwargs):
                pass
            def warning(self, message, **kwargs):
                pass
            def error(self, message, **kwargs):
                pass
        
        agent = JobDiscoveryAgent(
            name="job_discovery",
            description="AI-powered job discovery agent",
            logger=SimpleLogger(),
            openai_client=config.get_openai_client(),
            config=config
        )
        
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
        
        # Convert AgentResult to dict format
        if hasattr(result, 'success'):
            return result.to_dict()
        else:
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
        
        # Create simple logger implementation
        class SimpleLogger:
            def info(self, message, **kwargs):
                pass
            def warning(self, message, **kwargs):
                pass
            def error(self, message, **kwargs):
                pass
        
        agent = JobDiscoveryAgent(
            name="job_discovery",
            description="AI-powered job discovery agent",
            logger=SimpleLogger(),
            openai_client=config.get_openai_client(),
            config=config
        )
        
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
        
        # Create simple logger implementation
        class SimpleLogger:
            def info(self, message, **kwargs):
                pass
            def warning(self, message, **kwargs):
                pass
            def error(self, message, **kwargs):
                pass
        
        agent = JobDiscoveryAgent(
            name="job_discovery",
            description="AI-powered job discovery agent",
            logger=SimpleLogger(),
            openai_client=config.get_openai_client(),
            config=config
        )
        
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


async def _search_jobs_with_automation(
    job_title: str,
    location: str,
    experience_level: str,
    company_size: str,
    remote_preference: str,
    salary_range: str,
    required_skills: str,
    industry: str
) -> Dict[str, Any]:
    """Run async job search with automation service integration"""
    try:
        # First run the regular job search
        search_result = await _search_jobs(
            job_title=job_title,
            location=location,
            experience_level=experience_level,
            company_size=company_size,
            remote_preference=remote_preference,
            salary_range=salary_range,
            required_skills=required_skills,
            industry=industry
        )
        
        if not search_result.get("success"):
            return search_result
        
        # Initialize automation service
        config = Config()
        automation_service = JobAutomationService(config=config.__dict__)
        await automation_service.initialize()
        
        # Get user for database operations
        db_ops = get_db_operations()
        user = db_ops.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        
        # Process jobs with automation service
        automation_result = await automation_service.process_job_search_results(
            search_results=search_result,
            user_id=user.id
        )
        
        # Enhance the search result with automation data
        search_result["automation_results"] = automation_result
        
        # Save job search to database  
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
        
        job_search = db_ops.create_job_search(
            user_id=user.id,
            search_query=f"{job_title} in {location or 'any location'}",
            search_criteria=search_criteria,
            jobs_found=automation_result.get("jobs_saved", 0),
            search_results=search_result["data"]
        )
        
        return search_result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Job search with automation failed: {str(e)}"
        }


def _refresh_saved_jobs():
    """Refresh saved jobs from database"""
    try:
        config = Config()
        automation_service = JobAutomationService(config=config.__dict__)
        
        # Get user
        db_ops = get_db_operations()
        user = db_ops.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        
        # Get saved jobs from database
        saved_jobs = asyncio.run(automation_service.get_saved_jobs_for_user(user.id))
        st.session_state.database_saved_jobs = saved_jobs
        
    except Exception as e:
        st.error(f"Failed to refresh saved jobs: {str(e)}")
        st.session_state.database_saved_jobs = []


if __name__ == "__main__":
    show_job_search()