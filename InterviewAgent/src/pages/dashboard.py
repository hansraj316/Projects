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
    
    # Get or create user (single-user MVP)
    try:
        user = db.get_or_create_user(
            email=config.USER_EMAIL,
            full_name=config.USER_NAME
        )
        st.session_state.current_user = user
    except Exception as e:
        st.error(f"Failed to initialize user: {str(e)}")
        return
    
    # Get user statistics
    try:
        stats = db.get_user_stats(user.id)
        
        # Update session state stats
        st.session_state.stats.update(stats)
        
    except Exception as e:
        st.warning(f"Could not load statistics: {str(e)}")
        stats = st.session_state.stats
    
    # Welcome message
    st.markdown(f"### Welcome back, {user.full_name or user.email}! 👋")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Resume Templates",
            value=stats['resumes'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="🔍 Jobs Discovered", 
            value=stats['jobs_discovered'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="📝 Applications Submitted",
            value=stats['applications_submitted'],
            delta=None
        )
    
    with col4:
        success_rate = (stats['applications_successful'] / max(stats['applications_submitted'], 1)) * 100
        st.metric(
            label="✅ Success Rate",
            value=f"{success_rate:.1f}%",
            delta=None
        )
    
    st.markdown("---")
    
    # Recent activity section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Recent Activity")
        
        # Get recent agent logs
        try:
            recent_logs = db.get_agent_logs(user_id=user.id, limit=10)
            
            if recent_logs:
                # Create activity timeline
                activity_data = []
                for log in recent_logs:
                    activity_data.append({
                        'Time': log.created_at.strftime('%H:%M') if log.created_at else 'Unknown',
                        'Agent': log.agent_type.replace('_', ' ').title(),
                        'Action': log.action.replace('_', ' ').title(),
                        'Status': log.status.value.title() if log.status else 'Unknown',
                        'Duration': f"{log.duration_ms}ms" if log.duration_ms else 'N/A'
                    })
                
                activity_df = pd.DataFrame(activity_data)
                
                # Color code by status
                def style_status(val):
                    if val == 'Completed':
                        return 'color: green'
                    elif val == 'Failed':
                        return 'color: red'
                    elif val == 'Started':
                        return 'color: orange'
                    return ''
                
                styled_df = activity_df.style.applymap(style_status, subset=['Status'])
                st.dataframe(styled_df, use_container_width=True)
                
            else:
                st.info("No recent activity found. Start by uploading a resume or configuring job sites!")
                
        except Exception as e:
            st.error(f"Failed to load recent activity: {str(e)}")
    
    with col2:
        st.subheader("🎯 Quick Actions")
        
        # Quick action buttons
        if st.button("📄 Upload Resume", use_container_width=True):
            st.info("Navigate to Resume Manager from the sidebar")
        
        if st.button("🔍 Search Jobs", use_container_width=True):
            st.info("Navigate to Job Search from the sidebar")
        
        if st.button("⚙️ Configure Sites", use_container_width=True):
            st.info("Navigate to Settings from the sidebar")
        
        if st.button("🤖 Run Automation", use_container_width=True):
            run_automation_workflow()
    
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
        # Job discovery over time (simulated data for MVP)
        try:
            # Create sample data for the last 7 days
            dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
            
            # Simulate job discovery data
            job_counts = [2, 5, 3, 8, 4, 6, 7]  # This would come from real data
            
            df = pd.DataFrame({
                'Date': dates,
                'Jobs Found': job_counts
            })
            
            fig = px.line(
                df, 
                x='Date', 
                y='Jobs Found',
                title="Jobs Discovered (Last 7 Days)",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Failed to create discovery chart: {str(e)}")
    
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