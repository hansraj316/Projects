"""
Automation page for InterviewAgent Streamlit app
Provides complete automation control and monitoring interface
"""

import streamlit as st
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd

from agents.automation_controller import AutomationController
from automation.scheduler import AutomationScheduler
from database.operations import get_db_operations
from config import get_config
from agents.openai_automation_agent import monitor_automation_progress


def show_automation():
    """Display the automation control and monitoring interface"""
    
    st.header("🤖 Job Application Automation")
    st.markdown("**Complete workflow: Job Search → Resume Optimization → Cover Letter → Database → Playwright MCP**")
    
    # Initialize automation components
    if 'automation_controller' not in st.session_state:
        config = get_config()
        st.session_state.automation_controller = AutomationController(config.__dict__)
        st.session_state.automation_scheduler = AutomationScheduler(config.__dict__)
        
        # Start scheduler in background
        try:
            from utils.async_utils import run_async_in_streamlit
            run_async_in_streamlit(st.session_state.automation_scheduler.start_scheduler())
        except Exception as e:
            st.error(f"Failed to start scheduler: {str(e)}")
    
    # Create tabs for different automation functions
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚀 Start Automation", 
        "📅 Schedule Automation", 
        "📊 Monitor Progress", 
        "📋 Automation History", 
        "📈 Analytics", 
        "⚙️ Settings"
    ])
    
    with tab1:
        _show_start_automation()
    
    with tab2:
        _show_schedule_automation()
    
    with tab3:
        _show_monitor_progress()
    
    with tab4:
        _show_automation_history()
    
    with tab5:
        _show_automation_analytics()
    
    with tab6:
        _show_automation_settings()


def _show_start_automation():
    """Show manual automation start interface with OpenAI Agents SDK workflow"""
    st.subheader("🚀 Start Job Application Automation")
    st.markdown("**OpenAI Agents SDK Workflow: Job Discovery → Resume Optimizer → Cover Letter → Database → Playwright**")
    
    # Check if user has saved jobs to automate
    if 'discovered_jobs' in st.session_state and st.session_state.discovered_jobs:
        saved_jobs = [job for job in st.session_state.discovered_jobs if job.get('saved', False)]
        
        if saved_jobs:
            st.success(f"📋 Found {len(saved_jobs)} saved jobs ready for automation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Automation Options")
                
                # Automation mode selection
                automation_mode = st.selectbox(
                    "Automation Mode",
                    ["Single Job", "Batch Processing", "All Saved Jobs"],
                    help="Choose how many jobs to process"
                )
                
                # Job selection based on mode
                if automation_mode == "Single Job":
                    job_options = [f"{job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}" 
                                 for job in saved_jobs]
                    selected_job_index = st.selectbox(
                        "Select Job",
                        range(len(job_options)),
                        format_func=lambda x: job_options[x]
                    )
                    jobs_to_process = [saved_jobs[selected_job_index]]
                    
                elif automation_mode == "Batch Processing":
                    max_jobs = st.slider("Maximum Jobs to Process", 1, len(saved_jobs), 5)
                    jobs_to_process = saved_jobs[:max_jobs]
                    
                else:  # All Saved Jobs
                    jobs_to_process = saved_jobs
                
                # Rate limiting
                rate_limit = st.slider(
                    "Delay Between Applications (seconds)",
                    0, 300, 60,
                    help="Delay between job applications to respect rate limits"
                )
                
                # Email notifications
                email_notifications = st.checkbox(
                    "Send Email Notifications",
                    value=True,
                    help="Receive email updates during automation"
                )
            
            with col2:
                st.write("### Automation Preview")
                
                # Show jobs that will be processed
                st.write(f"**Jobs to Process:** {len(jobs_to_process)}")
                
                for i, job in enumerate(jobs_to_process[:3]):  # Show first 3
                    st.write(f"{i+1}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                
                if len(jobs_to_process) > 3:
                    st.write(f"... and {len(jobs_to_process) - 3} more")
                
                # Estimated time
                estimated_time = len(jobs_to_process) * 3 + rate_limit * len(jobs_to_process)  # 3 min per job + delays
                st.write(f"**Estimated Time:** {estimated_time // 60} minutes")
                
                # Safety checks
                st.write("### Safety Checks")
                if rate_limit < 30:
                    st.warning("⚠️ Low rate limit may trigger anti-bot measures")
                if len(jobs_to_process) > 10:
                    st.warning("⚠️ High volume automation - consider splitting into batches")
                
                st.success("✅ All safety checks passed")
            
            # Start automation button
            st.markdown("---")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button("🚀 Start Automation", type="primary", use_container_width=True):
                    _start_automation_workflow_new({
                        "job_title": "Software Engineer",  # From saved jobs
                        "location": "Remote",
                        "experience_level": "Mid-level"
                    }, {
                        "rate_limit_delay": rate_limit,
                        "email_notifications": email_notifications,
                        "automation_mode": automation_mode,
                        "max_applications_per_run": len(jobs_to_process),
                        "auto_submit": True,
                        "optimize_resume_per_job": True
                    }, jobs_to_process)
            
            with col2:
                if st.button("📋 Preview Steps", use_container_width=True):
                    _show_automation_preview(jobs_to_process)
            
            with col3:
                if st.button("⚙️ Advanced Settings", use_container_width=True):
                    _show_advanced_automation_settings()
        
        else:
            st.info("💡 No saved jobs found. Go to Job Search and save some jobs first!")
            
            if st.button("🔍 Go to Job Search"):
                st.switch_page("src/pages/job_search.py")
    
    else:
        st.info("🔍 No jobs discovered yet. Start by searching for jobs!")
        
        if st.button("🔍 Start Job Search"):
            st.switch_page("pages/job_search.py")


def _show_schedule_automation():
    """Show automation scheduling interface"""
    st.subheader("📅 Schedule Recurring Automation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Schedule Configuration")
        
        # Schedule type
        schedule_type = st.selectbox(
            "Schedule Type",
            ["Daily", "Weekly", "One-time"],
            help="Choose how often to run automation"
        )
        
        # Schedule timing
        if schedule_type == "Daily":
            hour = st.slider("Hour (24-hour format)", 0, 23, 9)
            minute = st.slider("Minute", 0, 59, 0)
            schedule_config = {"hour": hour, "minute": minute}
            
        elif schedule_type == "Weekly":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_of_week = st.selectbox("Day of Week", days)
            hour = st.slider("Hour (24-hour format)", 0, 23, 9)
            minute = st.slider("Minute", 0, 59, 0)
            schedule_config = {
                "day_of_week": days.index(day_of_week),
                "hour": hour,
                "minute": minute
            }
            
        else:  # One-time
            date = st.date_input("Date", datetime.now().date() + timedelta(days=1))
            time = st.time_input("Time", datetime.now().time())
            run_at = datetime.combine(date, time)
            schedule_config = {"run_at": run_at}
        
        # Search criteria for scheduled automation
        st.write("### Job Search Criteria")
        search_job_title = st.text_input("Job Title", "Software Engineer")
        search_location = st.text_input("Location", "Remote")
        search_keywords = st.text_input("Required Keywords (comma-separated)", "Python, AI")
        
        # Automation settings
        st.write("### Automation Settings")
        max_applications = st.slider("Max Applications per Run", 1, 20, 5)
        auto_apply_threshold = st.slider("Auto-apply Match Threshold (%)", 50, 100, 80)
    
    with col2:
        st.write("### Schedule Preview")
        
        # Show schedule details
        if schedule_type == "Daily":
            st.write(f"**Frequency:** Every day at {hour:02d}:{minute:02d}")
            next_run = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= datetime.now():
                next_run += timedelta(days=1)
                
        elif schedule_type == "Weekly":
            st.write(f"**Frequency:** Every {days[schedule_config['day_of_week']]} at {hour:02d}:{minute:02d}")
            next_run = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Calculate next occurrence of the day
            days_ahead = schedule_config['day_of_week'] - next_run.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
            
        else:  # One-time
            st.write(f"**Frequency:** One-time on {run_at.strftime('%Y-%m-%d %H:%M')}")
            next_run = run_at
        
        st.write(f"**Next Run:** {next_run.strftime('%Y-%m-%d %H:%M')}")
        
        # Show search criteria
        st.write("### Search Configuration")
        st.write(f"**Job Title:** {search_job_title}")
        st.write(f"**Location:** {search_location}")
        st.write(f"**Keywords:** {search_keywords}")
        st.write(f"**Max Applications:** {max_applications}")
        
        # Estimated impact
        st.write("### Estimated Impact")
        st.write(f"**Expected Jobs Found:** 5-15 per run")
        st.write(f"**Applications per Run:** Up to {max_applications}")
        
        if schedule_type == "Daily":
            st.write(f"**Weekly Applications:** Up to {max_applications * 7}")
        elif schedule_type == "Weekly":
            st.write(f"**Monthly Applications:** Up to {max_applications * 4}")
    
    # Schedule button
    st.markdown("---")
    
    if st.button("📅 Schedule Automation", type="primary", use_container_width=True):
        _schedule_automation_job(schedule_type, schedule_config, {
            "search_criteria": {
                "job_title": search_job_title,
                "location": search_location,
                "required_skills": search_keywords
            },
            "max_applications_per_session": max_applications,
            "auto_apply_threshold": auto_apply_threshold
        })


def _show_monitor_progress():
    """Show automation progress monitoring"""
    st.subheader("📊 Automation Progress Monitor")
    
    # Get active sessions
    if hasattr(st.session_state, 'automation_controller'):
        controller = st.session_state.automation_controller
        
        # Check for active sessions
        active_sessions = getattr(controller, 'active_sessions', {})
        
        if active_sessions:
            st.write("### Active Automation Sessions")
            
            for session_id, session in active_sessions.items():
                with st.expander(f"🔄 Session {session_id[:8]}... - {session['status'].title()}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Jobs", session['total_jobs'])
                        st.metric("Processed", session['processed_jobs'])
                    
                    with col2:
                        st.metric("Successful", session['successful_applications'])
                        st.metric("Failed", session['failed_applications'])
                    
                    with col3:
                        progress = session['processed_jobs'] / max(session['total_jobs'], 1)
                        st.metric("Progress", f"{progress:.1%}")
                        
                        if session['status'] == 'running':
                            st.progress(progress)
                    
                    # Show enhanced workflow details
                    if 'workflows' in session:
                        st.write(f"**Active Workflows:** {len(session['workflows'])}")
                        for workflow_id in session['workflows'][-3:]:  # Show last 3
                            st.write(f"• {workflow_id}")
                    
                    # Show step success rates if available
                    if 'step_success_rates' in session and session['step_success_rates']:
                        st.write("**Step Performance:**")
                        for step_id, success_count in session['step_success_rates'].items():
                            step_name = step_id.replace('_', ' ').title()
                            st.write(f"• {step_name}: {success_count} successes")
                    
                    # Control buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📊 View Details", key=f"details_{session_id}"):
                            _show_enhanced_session_details(session_id)
                    
                    with col2:
                        if st.button(f"📈 Step Analytics", key=f"analytics_{session_id}"):
                            _show_step_analytics(session_id)
                    
                    with col3:
                        if session['status'] == 'running':
                            if st.button(f"⏸️ Pause", key=f"pause_{session_id}"):
                                st.warning("Pause functionality will be implemented")
        
        else:
            st.info("No active automation sessions")
    
    # Show scheduler status
    st.write("### Scheduler Status")
    
    if hasattr(st.session_state, 'automation_scheduler'):
        scheduler = st.session_state.automation_scheduler
        
        try:
            status = scheduler.get_scheduler_status()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Scheduler Status", "Running" if status['running'] else "Stopped")
            
            with col2:
                st.metric("Scheduled Jobs", status['scheduled_jobs_count'])
            
            with col3:
                st.metric("Active Jobs", status['active_jobs'])
            
            with col4:
                st.metric("Executions", status['execution_history_count'])
            
            # Show next scheduled jobs
            if status['next_scheduled_jobs']:
                st.write("### Next Scheduled Jobs")
                
                for job in status['next_scheduled_jobs']:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**{job['schedule_type'].title()} Automation**")
                            st.write(f"User: {job['user_id']}")
                        
                        with col2:
                            if job['next_run']:
                                next_run = datetime.fromisoformat(job['next_run'])
                                st.write(f"Next: {next_run.strftime('%m/%d %H:%M')}")
                        
                        with col3:
                            if st.button(f"Cancel", key=f"cancel_{job['job_id']}"):
                                _cancel_scheduled_job(job['job_id'])
        
        except Exception as e:
            st.error(f"Failed to get scheduler status: {str(e)}")
    
    # Real-time updates
    if st.button("🔄 Refresh Status"):
        st.rerun()


def _show_automation_history():
    """Show automation execution history"""
    st.subheader("📋 Automation History")
    
    if hasattr(st.session_state, 'automation_controller'):
        controller = st.session_state.automation_controller
        
        # Get user ID (in a real app, this would come from authentication)
        user_id = "user@interviewagent.local"  # Placeholder
        
        try:
            history = controller.get_automation_history(user_id)
            
            if history:
                # Create history DataFrame
                history_data = []
                for session in history:
                    history_data.append({
                        "Date": session.get('completed_at', datetime.now()).strftime('%Y-%m-%d %H:%M'),
                        "Type": session.get('automation_mode', 'Unknown'),
                        "Jobs Processed": session.get('processed_jobs', 0),
                        "Successful": session.get('successful_applications', 0),
                        "Failed": session.get('failed_applications', 0),
                        "Duration": f"{session.get('duration', 0):.0f}s",
                        "Status": session.get('status', 'Unknown')
                    })
                
                df = pd.DataFrame(history_data)
                st.dataframe(df, use_container_width=True)
                
                # Summary statistics
                st.write("### Summary Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_sessions = len(history)
                    st.metric("Total Sessions", total_sessions)
                
                with col2:
                    total_applications = sum(s.get('successful_applications', 0) for s in history)
                    st.metric("Total Applications", total_applications)
                
                with col3:
                    if total_sessions > 0:
                        success_rate = sum(1 for s in history if s.get('status') == 'completed') / total_sessions
                        st.metric("Success Rate", f"{success_rate:.1%}")
                
                with col4:
                    if total_sessions > 0:
                        avg_duration = sum(s.get('duration', 0) for s in history) / total_sessions
                        st.metric("Avg Duration", f"{avg_duration:.0f}s")
            
            else:
                st.info("No automation history found")
        
        except Exception as e:
            st.error(f"Failed to load automation history: {str(e)}")
    
    # Export history
    if st.button("📥 Export History"):
        st.info("Export functionality will be implemented")


def _show_automation_settings():
    """Show automation configuration settings"""
    st.subheader("⚙️ Automation Settings")
    
    # Global automation settings
    st.write("### Global Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Safety settings
        st.write("#### Safety & Rate Limiting")
        
        max_daily_applications = st.slider("Max Daily Applications", 1, 50, 20)
        min_delay_between_apps = st.slider("Min Delay Between Applications (seconds)", 30, 300, 60)
        enable_safety_checks = st.checkbox("Enable Safety Checks", value=True)
        
        # Notification settings
        st.write("#### Notifications")
        
        email_notifications = st.checkbox("Email Notifications", value=True)
        notification_frequency = st.selectbox(
            "Notification Frequency",
            ["Every Application", "Hourly Summary", "Daily Summary", "Weekly Summary"]
        )
        
        # Auto-apply settings
        st.write("#### Auto-Apply Configuration")
        
        auto_apply_enabled = st.checkbox("Enable Auto-Apply", value=False)
        auto_apply_threshold = st.slider("Auto-Apply Match Threshold (%)", 70, 100, 85)
        
        excluded_companies = st.text_area(
            "Excluded Companies (one per line)",
            placeholder="Company A\nCompany B"
        )
    
    with col2:
        # Job filtering settings
        st.write("#### Job Filtering")
        
        required_keywords = st.text_area(
            "Required Keywords (one per line)",
            placeholder="Python\nRemote\nAI"
        )
        
        excluded_keywords = st.text_area(
            "Excluded Keywords (one per line)",
            placeholder="Senior\nManagement\nContract"
        )
        
        salary_min = st.number_input("Minimum Salary (optional)", min_value=0, value=0)
        
        # Resume settings
        st.write("#### Resume Configuration")
        
        auto_optimize_resume = st.checkbox("Auto-optimize Resume", value=True)
        generate_custom_cover_letter = st.checkbox("Generate Custom Cover Letters", value=True)
        
        # Backup settings
        st.write("#### Backup & Recovery")
        
        save_generated_documents = st.checkbox("Save Generated Documents", value=True)
        backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
    
    # Save settings
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            settings = {
                "global_settings": {
                    "max_daily_applications": max_daily_applications,
                    "min_delay_between_apps": min_delay_between_apps,
                    "enable_safety_checks": enable_safety_checks,
                    "email_notifications": email_notifications,
                    "notification_frequency": notification_frequency,
                    "auto_apply_enabled": auto_apply_enabled,
                    "auto_apply_threshold": auto_apply_threshold,
                    "excluded_companies": excluded_companies.split('\n') if excluded_companies else [],
                    "required_keywords": required_keywords.split('\n') if required_keywords else [],
                    "excluded_keywords": excluded_keywords.split('\n') if excluded_keywords else [],
                    "salary_min": salary_min,
                    "auto_optimize_resume": auto_optimize_resume,
                    "generate_custom_cover_letter": generate_custom_cover_letter,
                    "save_generated_documents": save_generated_documents,
                    "backup_frequency": backup_frequency
                }
            }
            
            # Save to session state
            st.session_state.automation_settings = settings
            st.success("Settings saved successfully!")
    
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.automation_settings = {}
            st.success("Settings reset to defaults!")
            st.rerun()


def _start_automation_workflow_new(job_search_criteria: Dict[str, Any], automation_settings: Dict[str, Any], saved_jobs: List[Dict[str, Any]] = None):
    """Start the new OpenAI Agents SDK automation workflow"""
    try:
        with st.spinner("Starting OpenAI Agents SDK automation workflow..."):
            # Get user ID
            user_id = "user_123"  # Placeholder
            
            # Log jobs being processed
            if saved_jobs:
                st.info(f"🎯 Processing {len(saved_jobs)} saved jobs from your job search")
                for i, job in enumerate(saved_jobs[:3], 1):
                    st.write(f"{i}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                if len(saved_jobs) > 3:
                    st.write(f"... and {len(saved_jobs) - 3} more jobs")
            else:
                st.warning("⚠️ No saved jobs provided - will use sample jobs for testing")
            
            # Start automation using new controller method
            controller = st.session_state.automation_controller
            
            # This would normally be async, but for demo purposes we'll simulate
            import asyncio
            result = asyncio.run(
                controller.start_job_application_automation(
                    user_id=user_id,
                    job_search_criteria=job_search_criteria,
                    automation_settings=automation_settings,
                    saved_jobs=saved_jobs
                )
            )
            
            if result["success"]:
                st.success("🎉 OpenAI Agents SDK automation workflow completed!")
                
                # Store session for monitoring
                st.session_state.current_automation_session = result["session_id"]
                st.session_state.current_workflow_id = result["workflow_id"]
                
                # Show summary
                summary = result["automation_summary"]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Jobs Found", summary["total_jobs_found"])
                
                with col2:
                    st.metric("Applications Created", summary["applications_created"])
                
                with col3:
                    st.metric("Applications Submitted", summary["applications_submitted"])
                
                with col4:
                    st.metric("Success Rate", f"{summary['success_rate']:.1f}%")
                
                # Show workflow steps executed
                st.write("### Workflow Steps Executed")
                for i, step in enumerate(summary["workflow_steps"], 1):
                    st.write(f"{i}. ✅ {step}")
                
                # Show detailed results if available
                if result.get("detailed_results"):
                    with st.expander("Detailed Step Results"):
                        for detail in result["detailed_results"]:
                            step_name = detail.get("step", "Unknown Step")
                            success = detail.get("success", False)
                            status_icon = "✅" if success else "❌"
                            
                            st.write(f"**{status_icon} {step_name}**")
                            if detail.get("job_title"):
                                st.write(f"   Job: {detail['job_title']} at {detail.get('company', 'Unknown')}")
                            if detail.get("timestamp"):
                                st.write(f"   Time: {detail['timestamp']}")
                            if not success and detail.get("error"):
                                st.error(f"   Error: {detail['error']}")
                
                st.info(f"📧 Email notifications sent for application confirmations")
                
                # Show next steps
                st.write("### Next Steps")
                st.write("1. ✅ Monitor progress in the 'Monitor Progress' tab")
                st.write("2. 📊 Review applications in the Applications tab")
                st.write("3. 📈 Check analytics for performance insights")
                
            else:
                st.error(f"❌ Automation failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Failed to start automation: {str(e)}")


def _show_automation_preview(jobs_to_process: List[Dict[str, Any]]):
    """Show automation steps preview"""
    st.subheader("📋 Automation Preview")
    
    st.write("### Automation Steps")
    
    for i, job in enumerate(jobs_to_process, 1):
        with st.expander(f"Job {i}: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}"):
            st.write("**Automation Steps:**")
            st.write("1. 🔍 Analyze job posting for requirements")
            st.write("2. 📄 Optimize resume for this specific role")
            st.write("3. 📝 Generate personalized cover letter")
            st.write("4. 🌐 Navigate to job application page")
            st.write("5. 📋 Fill out application form")
            st.write("6. 📎 Upload optimized resume and cover letter")
            st.write("7. ✅ Submit application")
            st.write("8. 📧 Send confirmation email")
            
            st.write("**Estimated Time:** 3-5 minutes")
            st.write("**Success Probability:** 85%")


def _show_advanced_automation_settings():
    """Show advanced automation configuration"""
    st.subheader("⚙️ Advanced Automation Settings")
    
    st.write("### Advanced Configuration")
    
    # This would open a modal or new section with advanced settings
    st.info("Advanced settings panel will be implemented")


def _schedule_automation_job(schedule_type: str, schedule_config: Dict[str, Any], automation_config: Dict[str, Any]):
    """Schedule an automation job"""
    try:
        with st.spinner("Scheduling automation job..."):
            scheduler = st.session_state.automation_scheduler
            user_id = "user@interviewagent.local"  # Placeholder
            
            # Combine configs
            full_config = {**schedule_config, **automation_config}
            
            # Schedule based on type
            from utils.async_utils import run_async_in_streamlit
            
            if schedule_type == "Daily":
                result = run_async_in_streamlit(scheduler.schedule_daily_automation(user_id, full_config))
            elif schedule_type == "Weekly":
                result = run_async_in_streamlit(scheduler.schedule_weekly_automation(user_id, full_config))
            else:  # One-time
                result = run_async_in_streamlit(scheduler.schedule_one_time_automation(user_id, full_config, schedule_config["run_at"]))
            
            if result["success"]:
                st.success(f"✅ {schedule_type} automation scheduled successfully!")
                st.write(f"**Job ID:** {result['job_id']}")
                st.write(f"**Next Run:** {result['next_run']}")
            else:
                st.error(f"❌ Failed to schedule automation: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Failed to schedule automation: {str(e)}")


def _show_enhanced_session_details(session_id: str):
    """Show enhanced session information with step-by-step details"""
    st.subheader(f"Enhanced Session Details: {session_id}")
    
    # Get enhanced workflow status
    if hasattr(st.session_state, 'automation_controller'):
        controller = st.session_state.automation_controller
        
        try:
            # Get enhanced workflow details
            enhanced_status = controller.get_enhanced_workflow_status(session_id)
            
            if enhanced_status.get("success", True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("### Workflow Overview")
                    st.write(f"**Status:** {enhanced_status.get('status', 'Unknown')}")
                    st.write(f"**Progress:** {enhanced_status.get('progress', 0):.1f}%")
                    
                    if 'step_results' in enhanced_status:
                        st.write("### Step Execution Details")
                        for step_id, step_result in enhanced_status['step_results'].items():
                            step_name = step_id.replace('_', ' ').title()
                            status_icon = "✅" if step_result.get('success') else "❌"
                            st.write(f"{status_icon} **{step_name}**")
                            if step_result.get('execution_time'):
                                st.write(f"   ⏱️ {step_result['execution_time']:.2f}s")
                            if not step_result.get('success') and step_result.get('error'):
                                st.error(f"   Error: {step_result['error']}")
                
                with col2:
                    st.write("### Handoff Performance")
                    if 'handoff_results' in enhanced_status:
                        handoff_data = enhanced_status['handoff_results']
                        successful_handoffs = sum(1 for h in handoff_data.values() if h.get('success'))
                        total_handoffs = len(handoff_data)
                        
                        if total_handoffs > 0:
                            success_rate = successful_handoffs / total_handoffs
                            st.metric("Handoff Success Rate", f"{success_rate:.1%}")
                            
                            for handoff_id, handoff_result in handoff_data.items():
                                status_icon = "🔄" if handoff_result.get('success') else "⚠️"
                                st.write(f"{status_icon} {handoff_id}")
                    else:
                        st.info("No handoff data available")
            else:
                st.error("Failed to load enhanced session details")
                
        except Exception as e:
            st.error(f"Error loading session details: {str(e)}")
    else:
        st.warning("Automation controller not available")


def _show_step_analytics(session_id: str):
    """Show step-by-step analytics for the session"""
    st.subheader(f"Step Analytics: {session_id}")
    
    if hasattr(st.session_state, 'automation_controller'):
        controller = st.session_state.automation_controller
        user_id = "user@interviewagent.local"  # Placeholder
        
        try:
            # Get step performance metrics
            step_metrics = controller.get_step_performance_metrics(user_id)
            
            if step_metrics.get("step_performance"):
                st.write("### Step Performance Analysis")
                
                # Create performance chart
                import pandas as pd
                
                performance_data = []
                for step_id, metrics in step_metrics["step_performance"].items():
                    performance_data.append({
                        "Step": step_id.replace('_', ' ').title(),
                        "Success Rate": metrics["success_rate"] * 100,
                        "Total Attempts": metrics["total_attempts"],
                        "Successful": metrics["successful_attempts"]
                    })
                
                df = pd.DataFrame(performance_data)
                st.dataframe(df, use_container_width=True)
                
                # Show overall metrics
                overall = step_metrics.get("overall_metrics", {})
                if overall:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Avg Steps Completed", f"{overall.get('average_steps_completed', 0):.1f}")
                    
                    with col2:
                        if overall.get('most_reliable_step'):
                            reliable_step = overall['most_reliable_step'].replace('_', ' ').title()
                            st.metric("Most Reliable Step", reliable_step)
                    
                    with col3:
                        if overall.get('least_reliable_step'):
                            unreliable_step = overall['least_reliable_step'].replace('_', ' ').title()
                            st.metric("Needs Improvement", unreliable_step)
            else:
                st.info("No step analytics data available")
                
        except Exception as e:
            st.error(f"Error loading step analytics: {str(e)}")
    else:
        st.warning("Automation controller not available")


def _show_automation_analytics():
    """Show comprehensive automation analytics"""
    st.subheader("📈 Automation Analytics")
    
    if hasattr(st.session_state, 'automation_controller'):
        controller = st.session_state.automation_controller
        user_id = "user@interviewagent.local"  # Placeholder
        
        # Create analytics sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Step Performance Analytics")
            
            try:
                step_metrics = controller.get_step_performance_metrics(user_id)
                
                if step_metrics.get("step_performance"):
                    # Create performance visualization
                    performance_data = []
                    for step_id, metrics in step_metrics["step_performance"].items():
                        performance_data.append({
                            "Step": step_id.replace('_', ' ').title(),
                            "Success Rate": metrics["success_rate"],
                            "Total Attempts": metrics["total_attempts"]
                        })
                    
                    import pandas as pd
                    df = pd.DataFrame(performance_data)
                    
                    # Show bar chart of success rates
                    st.bar_chart(df.set_index("Step")["Success Rate"])
                    
                    # Show summary metrics
                    overall = step_metrics.get("overall_metrics", {})
                    if overall:
                        st.write("**Key Insights:**")
                        if overall.get('most_reliable_step'):
                            st.success(f"✅ Most reliable: {overall['most_reliable_step'].replace('_', ' ').title()}")
                        if overall.get('least_reliable_step'):
                            st.warning(f"⚠️ Needs improvement: {overall['least_reliable_step'].replace('_', ' ').title()}")
                else:
                    st.info("No step performance data available yet")
                    
            except Exception as e:
                st.error(f"Error loading step analytics: {str(e)}")
        
        with col2:
            st.write("### Handoff Analytics")
            
            try:
                handoff_analytics = controller.get_handoff_analytics(user_id)
                
                if handoff_analytics.get("total_handoffs", 0) > 0:
                    # Show handoff metrics
                    col2a, col2b = st.columns(2)
                    
                    with col2a:
                        st.metric("Total Handoffs", handoff_analytics["total_handoffs"])
                        st.metric("Success Rate", f"{handoff_analytics['handoff_success_rate']:.1%}")
                    
                    with col2b:
                        st.metric("Successful", handoff_analytics["successful_handoffs"])
                        st.metric("Avg Time", f"{handoff_analytics['average_handoff_time']:.2f}s")
                    
                    # Show common issues
                    issues = handoff_analytics.get("common_handoff_issues", [])
                    if issues:
                        st.write("**Common Issues:**")
                        for issue in issues:
                            st.warning(f"• {issue}")
                    else:
                        st.success("✅ No common handoff issues detected")
                else:
                    st.info("No handoff data available yet")
                    
            except Exception as e:
                st.error(f"Error loading handoff analytics: {str(e)}")
        
        # Overall automation trends
        st.write("### Automation Trends")
        
        try:
            history = controller.get_automation_history(user_id, limit=20)
            
            if history:
                # Create trend data
                import pandas as pd
                from datetime import datetime
                
                trend_data = []
                for session in history:
                    if session.get("completed_at"):
                        trend_data.append({
                            "Date": session["completed_at"].strftime('%Y-%m-%d'),
                            "Applications": session.get("successful_applications", 0),
                            "Success Rate": session.get("successful_applications", 0) / max(session.get("processed_jobs", 1), 1)
                        })
                
                if trend_data:
                    df = pd.DataFrame(trend_data)
                    df = df.groupby("Date").agg({
                        "Applications": "sum",
                        "Success Rate": "mean"
                    }).reset_index()
                    
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        st.write("**Applications Over Time**")
                        st.line_chart(df.set_index("Date")["Applications"])
                    
                    with col4:
                        st.write("**Success Rate Trend**")
                        st.line_chart(df.set_index("Date")["Success Rate"])
                else:
                    st.info("Not enough data for trend analysis")
            else:
                st.info("No automation history available for trend analysis")
                
        except Exception as e:
            st.error(f"Error loading trend data: {str(e)}")
    else:
        st.warning("Automation controller not available")


def _cancel_scheduled_job(job_id: str):
    """Cancel a scheduled automation job"""
    try:
        scheduler = st.session_state.automation_scheduler
        from utils.async_utils import run_async_in_streamlit
        result = run_async_in_streamlit(scheduler.cancel_scheduled_job(job_id))
        
        if result["success"]:
            st.success("✅ Scheduled job cancelled successfully!")
            st.rerun()
        else:
            st.error(f"❌ Failed to cancel job: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Failed to cancel scheduled job: {str(e)}")


if __name__ == "__main__":
    show_automation()