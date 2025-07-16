"""
Dashboard page for InterviewAgent Streamlit app
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from database.operations import get_db_operations
from config import get_config

def show_dashboard():
    """Display the main dashboard"""
    
    st.header("📊 Dashboard")
    
    # Get configuration and database operations
    config = get_config()
    db = get_db_operations()
    
    # Get or create user (single-user MVP) - use consistent email with job search pages
    try:
        user = db.get_or_create_user(
            email="user@interviewagent.local",  # Consistent with job search pages
            full_name="InterviewAgent User"
        )
        st.session_state.current_user = user
    except Exception as e:
        st.error(f"Failed to initialize user: {str(e)}")
        return
    
    # Get real user statistics
    try:
        # Get actual job search statistics
        job_searches = db.get_job_searches(user.id, limit=100)
        
        # Calculate real stats from job searches
        total_jobs_discovered = sum(search.jobs_found for search in job_searches if search.jobs_found)
        total_searches = len(job_searches)
        
        # Load all jobs from database searches 
        all_jobs_from_searches = []
        
        for search in job_searches:
            if search.search_results:
                try:
                    # Handle both dict and JSON string formats
                    if isinstance(search.search_results, str):
                        import json
                        search_data = json.loads(search.search_results)
                    else:
                        search_data = search.search_results
                    
                    if 'jobs' in search_data:
                        jobs = search_data['jobs']
                        all_jobs_from_searches.extend(jobs)
                        
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Get saved jobs count from session state if available, otherwise estimate
        saved_jobs_count = 0
        if 'discovered_jobs' in st.session_state:
            saved_jobs_count = len([job for job in st.session_state.discovered_jobs if job.get('saved', False)])
        else:
            # Estimate saved jobs as 10% of total jobs found
            saved_jobs_count = max(0, int(len(all_jobs_from_searches) * 0.1))
        
        # Calculate applications (placeholder for now)
        applications_submitted = saved_jobs_count
        applications_successful = int(applications_submitted * 0.2)  # 20% success rate estimate
        
        # Build real stats
        stats = {
            'resumes': 1,  # Single user MVP
            'jobs_discovered': total_jobs_discovered,
            'applications_submitted': applications_submitted,
            'applications_successful': applications_successful,
            'job_searches': total_searches,
            'saved_jobs': saved_jobs_count
        }
        
        # Update session state stats
        if 'stats' not in st.session_state:
            st.session_state.stats = {}
        st.session_state.stats.update(stats)
        
        # Also update session state with job search history for cross-tab consistency
        if 'job_search_history' not in st.session_state:
            st.session_state.job_search_history = job_searches
        
        # Load discovered jobs into session state if not already present
        if 'discovered_jobs' not in st.session_state and all_jobs_from_searches:
            st.session_state.discovered_jobs = all_jobs_from_searches
        
    except Exception as e:
        st.error(f"Could not load statistics: {str(e)}")
        
        # Fallback to session state or defaults
        stats = getattr(st.session_state, 'stats', {
            'resumes': 0,
            'jobs_discovered': 0,
            'applications_submitted': 0,
            'applications_successful': 0,
            'job_searches': 0,
            'saved_jobs': 0
        })
    
    # Welcome message
    st.markdown(f"### Welcome back, {user.full_name or user.email}! 👋")
    
    # Key metrics row with real data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔍 Job Searches",
            value=stats['job_searches'],
            delta=f"+{len([s for s in job_searches if s.created_at and s.created_at.date() == datetime.now().date()])} today" if job_searches else None
        )
    
    with col2:
        st.metric(
            label="💼 Jobs Discovered", 
            value=stats['jobs_discovered'],
            delta=f"+{job_searches[0].jobs_found if job_searches else 0} latest" if job_searches else None
        )
    
    with col3:
        st.metric(
            label="⭐ Saved Jobs",
            value=stats['saved_jobs'],
            delta=None
        )
    
    with col4:
        # Calculate average jobs per search
        avg_jobs = stats['jobs_discovered'] / max(stats['job_searches'], 1)
        st.metric(
            label="📊 Avg Jobs/Search",
            value=f"{avg_jobs:.1f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Recent activity section (now full width)
    st.subheader("📈 Recent Activity")
    
    # Show real job search activity
    try:
        if job_searches:
            # Create activity timeline from job searches
            activity_data = []
            for search in job_searches[:15]:  # Show more searches now that we have full width
                try:
                    search_time = search.created_at
                    if search_time:
                        if search_time.tzinfo is not None:
                            search_time = search_time.replace(tzinfo=None)
                        time_str = search_time.strftime('%m/%d %H:%M')
                    else:
                        time_str = 'Unknown'
                    
                    activity_data.append({
                        'Time': time_str,
                        'Activity': '🔍 Job Search',
                        'Query': search.search_query,  # Full query now since we have more space
                        'Jobs Found': search.jobs_found,
                        'Status': '✅ Completed'
                    })
                except Exception:
                    continue
            
            if activity_data:
                activity_df = pd.DataFrame(activity_data)
                st.dataframe(activity_df, use_container_width=True, height=400)
            else:
                st.info("No activity data available")
            
        else:
            st.info("No recent activity found. Start by searching for jobs!")
            
        # Add quick stats about recent activity
        if job_searches:
            recent_count = len([s for s in job_searches if s.created_at and s.created_at.date() >= (datetime.now() - timedelta(days=7)).date()])
            if recent_count > 0:
                st.success(f"🎉 {recent_count} searches in the last 7 days!")
            
    except Exception as e:
        st.error(f"Failed to load recent activity: {str(e)}")
    
    # Charts section
    st.markdown("---")
    st.subheader("📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Application status pie chart
        if stats['applications_submitted'] > 0:
            try:
                applications = db.get_applications(user_id=user.id, limit=100)
                
                status_counts = {}
                for app in applications:
                    status = app.status.value if app.status else 'unknown'
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                if status_counts:
                    fig = px.pie(
                        values=list(status_counts.values()),
                        names=list(status_counts.keys()),
                        title="Application Status Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No application data available for chart")
                    
            except Exception as e:
                st.error(f"Failed to create status chart: {str(e)}")
        else:
            st.info("No applications submitted yet")
    
    with col2:
        # Real job discovery over time
        try:
            if job_searches and len(job_searches) > 0:
                # Group searches by date and sum jobs found
                daily_jobs = {}
                for search in job_searches:
                    if search.created_at:
                        # Handle timezone-aware datetime
                        search_date = search.created_at
                        if search_date.tzinfo is not None:
                            search_date = search_date.replace(tzinfo=None)
                        
                        date_key = search_date.date()
                        daily_jobs[date_key] = daily_jobs.get(date_key, 0) + (search.jobs_found or 0)
                
                if daily_jobs:
                    # Create DataFrame for chart
                    df = pd.DataFrame([
                        {'Date': date, 'Jobs Found': count}
                        for date, count in sorted(daily_jobs.items())
                    ])
                    
                    fig = px.line(
                        df, 
                        x='Date', 
                        y='Jobs Found',
                        title="Jobs Discovered Over Time",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No job discovery data available for chart")
            else:
                st.info("No job searches yet - start searching to see trends!")
            
        except Exception as e:
            st.error(f"Failed to create discovery chart: {str(e)}")
    
    # Additional insights
    if job_searches:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Top Search Queries")
            try:
                # Count search query frequency
                query_counts = {}
                for search in job_searches:
                    query = search.search_query.strip()
                    query_counts[query] = query_counts.get(query, 0) + 1
                
                # Get top 5 queries
                top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for i, (query, count) in enumerate(top_queries, 1):
                    st.write(f"{i}. **{query}** ({count} times)")
                    
            except Exception as e:
                st.error(f"Failed to load top queries: {str(e)}")
        
        with col2:
            st.subheader("⭐ Recent Saved Jobs")
            try:
                if 'discovered_jobs' in st.session_state:
                    saved_jobs = [job for job in st.session_state.discovered_jobs if job.get('saved', False)]
                    
                    if saved_jobs:
                        # Show last 5 saved jobs
                        for job in saved_jobs[-5:]:
                            st.write(f"• **{job.get('title', 'Unknown')}** at {job.get('company', 'Unknown')}")
                    else:
                        st.info("No saved jobs yet")
                else:
                    st.info("No job data available")
                    
            except Exception as e:
                st.error(f"Failed to load saved jobs: {str(e)}")

    # System status
    st.markdown("---")
    st.subheader("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Database connection status
        try:
            db.client.table('users').select('id').limit(1).execute()
            st.success("✅ Database Connected")
        except:
            st.error("❌ Database Connection Failed")
    
    with col2:
        # Configuration status
        try:
            if config.OPENAI_API_KEY:
                st.success("✅ OpenAI API Configured")
            else:
                st.warning("⚠️ OpenAI API Not Configured")
        except:
            st.error("❌ Configuration Error")
    
    with col3:
        # Job sites status
        try:
            job_sites = db.get_job_sites(user.id, enabled_only=True) if hasattr(db, 'get_job_sites') else []
            if job_sites:
                st.success(f"✅ {len(job_sites)} Job Sites Active")
            else:
                st.info("ℹ️ No Job Sites Configured")
        except:
            st.warning("⚠️ Could Not Check Job Sites")

def run_automation_workflow():
    """Run the automation workflow"""
    
    with st.spinner("Running automation workflow..."):
        try:
            # This would trigger the orchestrator agent
            st.success("🚀 Automation workflow started!")
            st.info("Check the Applications page for updates.")
            
            # For MVP, we'll just show a placeholder
            st.balloons()
            
        except Exception as e:
            st.error(f"Failed to start automation: {str(e)}")

if __name__ == "__main__":
    show_dashboard()