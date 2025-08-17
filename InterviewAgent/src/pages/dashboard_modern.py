"""
Modern Dashboard with ShadCN-inspired components for InterviewAgent
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from database.operations import get_db_operations
from config import get_config

def inject_shadcn_styles():
    """Inject ShadCN-inspired CSS styles into the Streamlit app"""
    
    st.markdown("""
    <style>
    /* Import Inter font for modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global CSS Variables (ShadCN color palette) */
    :root {
        --background: 0 0% 100%;
        --foreground: 222.2 84% 4.9%;
        --card: 0 0% 100%;
        --card-foreground: 222.2 84% 4.9%;
        --popover: 0 0% 100%;
        --popover-foreground: 222.2 84% 4.9%;
        --primary: 221.2 83.2% 53.3%;
        --primary-foreground: 210 40% 98%;
        --secondary: 210 40% 96%;
        --secondary-foreground: 222.2 84% 4.9%;
        --muted: 210 40% 96%;
        --muted-foreground: 215.4 16.3% 46.9%;
        --accent: 210 40% 96%;
        --accent-foreground: 222.2 84% 4.9%;
        --destructive: 0 84.2% 60.2%;
        --destructive-foreground: 210 40% 98%;
        --border: 214.3 31.8% 91.4%;
        --input: 214.3 31.8% 91.4%;
        --ring: 221.2 83.2% 53.3%;
        --radius: 0.5rem;
    }
    
    /* Override Streamlit default styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* ShadCN Card Component */
    .shadcn-card {
        background: hsl(var(--card));
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        transition: all 0.2s ease-in-out;
        margin-bottom: 1rem;
    }
    
    .shadcn-card:hover {
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        transform: translateY(-1px);
    }
    
    /* ShadCN Metric Card */
    .metric-card {
        background: hsl(var(--card));
        border: 1px solid hsl(var(--border));
        border-radius: var(--radius);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease-in-out;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        border-color: hsl(var(--primary));
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, hsl(var(--primary)), hsl(var(--accent)));
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: hsl(var(--foreground));
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: hsl(var(--muted-foreground));
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        margin-top: 0.5rem;
        display: inline-block;
    }
    
    .metric-delta.positive {
        background: rgb(220 252 231);
        color: rgb(21 128 61);
    }
    
    .metric-delta.neutral {
        background: hsl(var(--muted));
        color: hsl(var(--muted-foreground));
    }
    
    /* ShadCN Badge */
    .shadcn-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 9999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 500;
        line-height: 1;
        transition: all 0.2s ease-in-out;
    }
    
    .badge-success {
        background: rgb(220 252 231);
        color: rgb(21 128 61);
    }
    
    .badge-warning {
        background: rgb(254 249 195);
        color: rgb(161 98 7);
    }
    
    .badge-error {
        background: rgb(254 226 226);
        color: rgb(185 28 28);
    }
    
    .badge-info {
        background: hsl(var(--primary)) / 0.1;
        color: hsl(var(--primary));
    }
    
    /* ShadCN Button */
    .shadcn-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius);
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border: 1px solid transparent;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        text-decoration: none;
    }
    
    .button-primary {
        background: hsl(var(--primary));
        color: hsl(var(--primary-foreground));
    }
    
    .button-primary:hover {
        background: hsl(var(--primary)) / 0.9;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .button-secondary {
        background: hsl(var(--secondary));
        color: hsl(var(--secondary-foreground));
        border: 1px solid hsl(var(--border));
    }
    
    .button-secondary:hover {
        background: hsl(var(--accent));
    }
    
    /* Modern Typography */
    .page-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: hsl(var(--foreground));
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .page-subtitle {
        font-size: 1.125rem;
        color: hsl(var(--muted-foreground));
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: hsl(var(--foreground));
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Activity Timeline */
    .activity-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid hsl(var(--border));
        transition: background-color 0.2s ease-in-out;
    }
    
    .activity-item:hover {
        background: hsl(var(--muted)) / 0.5;
    }
    
    .activity-item:last-child {
        border-bottom: none;
    }
    
    .activity-icon {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.25rem;
    }
    
    .activity-icon.search {
        background: hsl(var(--primary)) / 0.1;
        color: hsl(var(--primary));
    }
    
    .activity-content {
        flex: 1;
    }
    
    .activity-title {
        font-weight: 500;
        color: hsl(var(--foreground));
        margin-bottom: 0.25rem;
    }
    
    .activity-subtitle {
        font-size: 0.875rem;
        color: hsl(var(--muted-foreground));
    }
    
    .activity-time {
        font-size: 0.875rem;
        color: hsl(var(--muted-foreground));
        margin-left: auto;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        border-radius: var(--radius);
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-success {
        background: rgb(220 252 231);
        color: rgb(21 128 61);
        border: 1px solid rgb(187 247 208);
    }
    
    .status-warning {
        background: rgb(254 249 195);
        color: rgb(161 98 7);
        border: 1px solid rgb(253 230 138);
    }
    
    .status-error {
        background: rgb(254 226 226);
        color: rgb(185 28 28);
        border: 1px solid rgb(252 165 165);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: hsl(var(--muted));
    }
    
    ::-webkit-scrollbar-thumb {
        background: hsl(var(--border));
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: hsl(var(--muted-foreground));
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .page-title {
            font-size: 1.875rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """Create a modern ShadCN-style metric card"""
    
    delta_html = ""
    if delta:
        delta_class = "positive" if "+" in delta else "neutral"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_card(title: str, status: str, status_type: str = "success"):
    """Create a status indicator card"""
    
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    
    icon = status_icons.get(status_type, "ℹ️")
    
    return f"""
    <div class="status-indicator status-{status_type}">
        <span>{icon}</span>
        <div>
            <div style="font-weight: 600;">{title}</div>
            <div style="font-size: 0.8rem; opacity: 0.8;">{status}</div>
        </div>
    </div>
    """

def create_activity_item(icon: str, title: str, subtitle: str, time: str):
    """Create an activity timeline item"""
    
    return f"""
    <div class="activity-item">
        <div class="activity-icon search">{icon}</div>
        <div class="activity-content">
            <div class="activity-title">{title}</div>
            <div class="activity-subtitle">{subtitle}</div>
        </div>
        <div class="activity-time">{time}</div>
    </div>
    """

def show_modern_dashboard():
    """Display the modern ShadCN-inspired dashboard"""
    
    # Inject custom styles
    inject_shadcn_styles()
    
    # Get configuration and database operations
    config = get_config()
    db = get_db_operations()
    
    # Get or create user (single-user MVP)
    try:
        user = db.get_or_create_user(
            email="user@interviewagent.local",
            full_name="InterviewAgent User"
        )
        st.session_state.current_user = user
    except Exception as e:
        st.error(f"Failed to initialize user: {str(e)}")
        return
    
    # Page Header with modern typography
    st.markdown("""
    <div class="page-title">🤖 InterviewAgent Dashboard</div>
    <div class="page-subtitle">AI-Powered Job Application Automation System</div>
    """, unsafe_allow_html=True)
    
    # Get real user statistics
    try:
        job_searches = db.get_job_searches(user.id, limit=100)
        
        # Calculate real stats from job searches
        total_jobs_discovered = sum(search.jobs_found for search in job_searches if search.jobs_found)
        total_searches = len(job_searches)
        
        # Load all jobs from database searches 
        all_jobs_from_searches = []
        for search in job_searches:
            if search.search_results:
                try:
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
        
        # Get saved jobs count
        saved_jobs_count = 0
        if 'discovered_jobs' in st.session_state:
            saved_jobs_count = len([job for job in st.session_state.discovered_jobs if job.get('saved', False)])
        else:
            saved_jobs_count = max(0, int(len(all_jobs_from_searches) * 0.1))
        
        # Calculate applications
        applications_submitted = saved_jobs_count
        applications_successful = int(applications_submitted * 0.2)
        
        # Build stats
        stats = {
            'resumes': 1,
            'jobs_discovered': total_jobs_discovered,
            'applications_submitted': applications_submitted,
            'applications_successful': applications_successful,
            'job_searches': total_searches,
            'saved_jobs': saved_jobs_count
        }
        
        # Update session state
        if 'stats' not in st.session_state:
            st.session_state.stats = {}
        st.session_state.stats.update(stats)
        
    except Exception as e:
        st.error(f"Could not load statistics: {str(e)}")
        stats = getattr(st.session_state, 'stats', {
            'resumes': 0,
            'jobs_discovered': 0,
            'applications_submitted': 0,
            'applications_successful': 0,
            'job_searches': 0,
            'saved_jobs': 0
        })
    
    # Welcome message with user greeting
    st.markdown(f"""
    <div class="shadcn-card">
        <h3 style="margin: 0 0 0.5rem 0; color: hsl(var(--foreground));">Welcome back, {user.full_name or user.email}! 👋</h3>
        <p style="margin: 0; color: hsl(var(--muted-foreground));">Here's your job search activity overview.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics with modern cards
    st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        today_searches = len([s for s in job_searches if s.created_at and s.created_at.date() == datetime.now().date()]) if job_searches else 0
        delta = f"+{today_searches} today" if today_searches > 0 else None
        st.markdown(create_metric_card("Job Searches", str(stats['job_searches']), delta, "🔍"), unsafe_allow_html=True)
    
    with col2:
        latest_jobs = job_searches[0].jobs_found if job_searches else 0
        delta = f"+{latest_jobs} latest" if latest_jobs > 0 else None
        st.markdown(create_metric_card("Jobs Discovered", str(stats['jobs_discovered']), delta, "💼"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("Saved Jobs", str(stats['saved_jobs']), None, "⭐"), unsafe_allow_html=True)
    
    with col4:
        avg_jobs = stats['jobs_discovered'] / max(stats['job_searches'], 1)
        st.markdown(create_metric_card("Avg Jobs/Search", f"{avg_jobs:.1f}", None, "📈"), unsafe_allow_html=True)
    
    # Activity and Analytics Section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">📈 Recent Activity</div>', unsafe_allow_html=True)
        
        # Create modern activity timeline
        activity_html = '<div class="shadcn-card" style="padding: 0;">'
        
        try:
            if job_searches:
                for search in job_searches[:8]:  # Show 8 recent searches
                    try:
                        search_time = search.created_at
                        if search_time:
                            if search_time.tzinfo is not None:
                                search_time = search_time.replace(tzinfo=None)
                            time_str = search_time.strftime('%m/%d %H:%M')
                        else:
                            time_str = 'Unknown'
                        
                        activity_html += create_activity_item(
                            "🔍",
                            "Job Search Completed",
                            f"{search.search_query} • {search.jobs_found or 0} jobs found",
                            time_str
                        )
                    except Exception:
                        continue
            else:
                activity_html += '<div style="padding: 2rem; text-align: center; color: hsl(var(--muted-foreground));">No recent activity found.<br>Start searching for jobs!</div>'
        
        except Exception as e:
            activity_html += f'<div style="padding: 2rem; text-align: center; color: hsl(var(--destructive));">Failed to load activity: {str(e)}</div>'
        
        activity_html += '</div>'
        st.markdown(activity_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title">📊 Analytics</div>', unsafe_allow_html=True)
        
        # Application status chart with modern styling
        if stats['applications_submitted'] > 0:
            try:
                applications = db.get_applications(user_id=user.id, limit=100)
                
                status_counts = {}
                for app in applications:
                    status = app.status.value if app.status else 'pending'
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                if status_counts:
                    fig = px.pie(
                        values=list(status_counts.values()),
                        names=list(status_counts.keys()),
                        title="Application Status",
                        color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
                    )
                    fig.update_layout(
                        font_family="Inter",
                        title_font_size=16,
                        title_font_color="hsl(222.2, 84%, 4.9%)",
                        showlegend=True,
                        margin=dict(t=50, b=20, l=20, r=20),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown('<div class="shadcn-card" style="text-align: center; color: hsl(var(--muted-foreground));">No application data available</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(f'<div class="shadcn-card" style="text-align: center; color: hsl(var(--destructive));">Failed to create chart: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="shadcn-card" style="text-align: center; color: hsl(var(--muted-foreground));">No applications submitted yet</div>', unsafe_allow_html=True)
    
    # Insights Section
    st.markdown('<div class="section-title">💡 Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h4 style="color: hsl(var(--foreground)); margin-bottom: 1rem;">🔥 Top Search Queries</h4>', unsafe_allow_html=True)
        
        insights_html = '<div class="shadcn-card">'
        try:
            if job_searches:
                query_counts = {}
                for search in job_searches:
                    query = search.search_query.strip()
                    query_counts[query] = query_counts.get(query, 0) + 1
                
                top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for i, (query, count) in enumerate(top_queries, 1):
                    insights_html += f'''
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid hsl(var(--border));">
                        <span style="font-weight: 500; color: hsl(var(--foreground));">{i}. {query}</span>
                        <span class="shadcn-badge badge-info">{count} searches</span>
                    </div>
                    '''
                
                if not top_queries:
                    insights_html += '<div style="text-align: center; color: hsl(var(--muted-foreground)); padding: 2rem;">No search queries yet</div>'
            else:
                insights_html += '<div style="text-align: center; color: hsl(var(--muted-foreground)); padding: 2rem;">No search queries yet</div>'
        except Exception as e:
            insights_html += f'<div style="text-align: center; color: hsl(var(--destructive)); padding: 2rem;">Failed to load queries: {str(e)}</div>'
        
        insights_html += '</div>'
        st.markdown(insights_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h4 style="color: hsl(var(--foreground)); margin-bottom: 1rem;">⭐ Recent Saved Jobs</h4>', unsafe_allow_html=True)
        
        saved_jobs_html = '<div class="shadcn-card">'
        try:
            if 'discovered_jobs' in st.session_state:
                saved_jobs = [job for job in st.session_state.discovered_jobs if job.get('saved', False)]
                
                if saved_jobs:
                    for job in saved_jobs[-5:]:
                        saved_jobs_html += f'''
                        <div style="padding: 0.75rem 0; border-bottom: 1px solid hsl(var(--border));">
                            <div style="font-weight: 500; color: hsl(var(--foreground));">{job.get('title', 'Unknown Position')}</div>
                            <div style="font-size: 0.875rem; color: hsl(var(--muted-foreground));">at {job.get('company', 'Unknown Company')}</div>
                        </div>
                        '''
                else:
                    saved_jobs_html += '<div style="text-align: center; color: hsl(var(--muted-foreground)); padding: 2rem;">No saved jobs yet</div>'
            else:
                saved_jobs_html += '<div style="text-align: center; color: hsl(var(--muted-foreground)); padding: 2rem;">No job data available</div>'
        except Exception as e:
            saved_jobs_html += f'<div style="text-align: center; color: hsl(var(--destructive)); padding: 2rem;">Failed to load saved jobs: {str(e)}</div>'
        
        saved_jobs_html += '</div>'
        st.markdown(saved_jobs_html, unsafe_allow_html=True)
    
    # System Status Section
    st.markdown('<div class="section-title">🔧 System Status</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            db.client.table('users').select('id').limit(1).execute()
            st.markdown(create_status_card("Database", "Connected", "success"), unsafe_allow_html=True)
        except:
            st.markdown(create_status_card("Database", "Connection Failed", "error"), unsafe_allow_html=True)
    
    with col2:
        try:
            if config.OPENAI_API_KEY:
                st.markdown(create_status_card("OpenAI API", "Configured", "success"), unsafe_allow_html=True)
            else:
                st.markdown(create_status_card("OpenAI API", "Not Configured", "warning"), unsafe_allow_html=True)
        except:
            st.markdown(create_status_card("OpenAI API", "Configuration Error", "error"), unsafe_allow_html=True)
    
    with col3:
        try:
            job_sites = db.get_job_sites(user.id, enabled_only=True) if hasattr(db, 'get_job_sites') else []
            if job_sites:
                st.markdown(create_status_card("Job Sites", f"{len(job_sites)} Active", "success"), unsafe_allow_html=True)
            else:
                st.markdown(create_status_card("Job Sites", "No Sites Configured", "info"), unsafe_allow_html=True)
        except:
            st.markdown(create_status_card("Job Sites", "Could Not Check", "warning"), unsafe_allow_html=True)
    
    # Quick Actions Footer
    st.markdown('<div class="section-title">🚀 Quick Actions</div>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("🔍 Search Jobs", key="dashboard_search", use_container_width=True):
            st.switch_page("pages/job_search.py") if hasattr(st, 'switch_page') else st.info("Navigate to Job Search from the sidebar")
    
    with action_col2:
        if st.button("📄 Manage Resumes", key="dashboard_resume", use_container_width=True):
            st.switch_page("pages/resume_manager.py") if hasattr(st, 'switch_page') else st.info("Navigate to Resume Manager from the sidebar")
    
    with action_col3:
        if st.button("🤖 Configure AI", key="dashboard_ai", use_container_width=True):
            st.switch_page("pages/ai_agents.py") if hasattr(st, 'switch_page') else st.info("Navigate to AI Agents from the sidebar")
    
    with action_col4:
        if st.button("⚙️ Settings", key="dashboard_settings", use_container_width=True):
            st.switch_page("pages/settings.py") if hasattr(st, 'switch_page') else st.info("Navigate to Settings from the sidebar")

if __name__ == "__main__":
    show_modern_dashboard()