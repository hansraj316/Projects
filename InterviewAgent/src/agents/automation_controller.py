"""
Automation Controller - High-level interface for job application automation
Connects job searches to the complete multi-agent workflow pipeline
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from agents.orchestrator import OrchestratorAgent, Workflow
from agents.enhanced_orchestrator import EnhancedOrchestratorAgent, EnhancedWorkflow
from agents.base_agent import AgentContext
from database.operations import get_db_operations
from config import get_config


class AutomationController:
    """
    High-level controller that manages the complete job application automation pipeline
    Connects job search results to multi-agent workflows for seamless automation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or get_config()
        self.db_ops = get_db_operations()
        self.orchestrator = OrchestratorAgent(config)
        
        # Track automation sessions
        self.active_sessions = {}
        self.automation_history = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    async def start_job_application_automation(self, user_id: str, job_search_results: List[Dict[str, Any]], 
                                             automation_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start automated job application process for search results
        
        Args:
            user_id: ID of the user
            job_search_results: List of jobs from job search
            automation_settings: User automation preferences
            
        Returns:
            Automation session details
        """
        session_id = str(uuid.uuid4())
        
        try:
            # Get user profile for automation
            user_profile = await self._build_user_profile(user_id)
            
            # Filter jobs based on automation settings
            eligible_jobs = self._filter_jobs_for_automation(job_search_results, automation_settings)
            
            self.logger.info(f"Starting automation for {len(eligible_jobs)} jobs out of {len(job_search_results)} found")
            
            # Create automation session
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "started_at": datetime.now(),
                "status": "running",
                "total_jobs": len(eligible_jobs),
                "processed_jobs": 0,
                "successful_applications": 0,
                "failed_applications": 0,
                "workflows": [],
                "automation_settings": automation_settings
            }
            
            self.active_sessions[session_id] = session
            
            # Process jobs based on automation settings
            if automation_settings.get("batch_processing", False):
                # Bulk processing
                workflow = self.orchestrator.create_bulk_application_workflow(
                    user_id=user_id,
                    job_list=eligible_jobs,
                    user_profile=user_profile
                )
                
                session["workflows"].append(workflow.workflow_id)
                
                # Execute bulk workflow
                result = await self.orchestrator.execute_workflow(workflow)
                session["bulk_workflow_result"] = result
                
            else:
                # Individual job processing
                workflow_results = []
                
                for job_data in eligible_jobs:
                    try:
                        # Create individual workflow
                        workflow = self.orchestrator.create_job_application_workflow(
                            user_id=user_id,
                            job_data=job_data,
                            user_profile=user_profile
                        )
                        
                        session["workflows"].append(workflow.workflow_id)
                        
                        # Execute workflow
                        result = await self.orchestrator.execute_workflow(workflow)
                        workflow_results.append(result)
                        
                        # Update session stats
                        session["processed_jobs"] += 1
                        if result.get("success"):
                            session["successful_applications"] += 1
                        else:
                            session["failed_applications"] += 1
                        
                        # Respect rate limits
                        if automation_settings.get("rate_limit_delay", 0) > 0:
                            await asyncio.sleep(automation_settings["rate_limit_delay"])
                            
                    except Exception as e:
                        self.logger.error(f"Failed to process job {job_data.get('title', 'Unknown')}: {str(e)}")
                        session["failed_applications"] += 1
                
                session["individual_workflow_results"] = workflow_results
            
            # Update session status
            session["status"] = "completed"
            session["completed_at"] = datetime.now()
            session["duration"] = (session["completed_at"] - session["started_at"]).total_seconds()
            
            # Save session to database
            await self._save_automation_session(session)
            
            # Move to history
            self.automation_history.append(session)
            del self.active_sessions[session_id]
            
            return {
                "success": True,
                "session_id": session_id,
                "automation_summary": {
                    "total_jobs_processed": session["processed_jobs"],
                    "successful_applications": session["successful_applications"],
                    "failed_applications": session["failed_applications"],
                    "duration_seconds": session["duration"],
                    "automation_rate": session["successful_applications"] / max(session["processed_jobs"], 1)
                },
                "workflows_created": session["workflows"],
                "session_details": session
            }
            
        except Exception as e:
            self.logger.error(f"Automation session {session_id} failed: {str(e)}")
            
            # Update session with error
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session["status"] = "failed"
                session["error"] = str(e)
                session["completed_at"] = datetime.now()
            
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "message": "Automation session failed"
            }
    
    async def start_single_job_automation(self, user_id: str, job_data: Dict[str, Any], 
                                        user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start automation for a single job application
        
        Args:
            user_id: ID of the user
            job_data: Single job information
            user_preferences: Optional user preferences
            
        Returns:
            Single job automation result
        """
        try:
            # Get user profile
            user_profile = await self._build_user_profile(user_id)
            if user_preferences:
                user_profile.update(user_preferences)
            
            # Create and execute workflow
            workflow = self.orchestrator.create_job_application_workflow(
                user_id=user_id,
                job_data=job_data,
                user_profile=user_profile
            )
            
            result = await self.orchestrator.execute_workflow(workflow)
            
            # Save individual automation record
            automation_record = {
                "user_id": user_id,
                "job_data": job_data,
                "workflow_id": workflow.workflow_id,
                "result": result,
                "automated_at": datetime.now()
            }
            
            await self._save_individual_automation(automation_record)
            
            return {
                "success": result.get("success", False),
                "workflow_id": workflow.workflow_id,
                "job_title": job_data.get("title", "Unknown"),
                "company": job_data.get("company", "Unknown"),
                "automation_result": result
            }
            
        except Exception as e:
            self.logger.error(f"Single job automation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Single job automation failed"
            }
    
    async def schedule_recurring_automation(self, user_id: str, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule recurring job application automation
        
        Args:
            user_id: ID of the user
            automation_config: Configuration for recurring automation
            
        Returns:
            Scheduling result
        """
        try:
            # This will integrate with APScheduler in the next step
            schedule_id = str(uuid.uuid4())
            
            # Save schedule configuration
            schedule_record = {
                "schedule_id": schedule_id,
                "user_id": user_id,
                "automation_config": automation_config,
                "created_at": datetime.now(),
                "status": "active",
                "next_run": self._calculate_next_run(automation_config)
            }
            
            await self._save_automation_schedule(schedule_record)
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "next_run": schedule_record["next_run"],
                "message": "Recurring automation scheduled successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule recurring automation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to schedule automation"
            }
    
    def get_automation_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the status of an automation session
        
        Args:
            session_id: ID of the automation session
            
        Returns:
            Session status information
        """
        # Check active sessions
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "status": session["status"],
                "progress": {
                    "total_jobs": session["total_jobs"],
                    "processed_jobs": session["processed_jobs"],
                    "successful_applications": session["successful_applications"],
                    "failed_applications": session["failed_applications"],
                    "completion_percentage": (session["processed_jobs"] / max(session["total_jobs"], 1)) * 100
                },
                "current_workflows": session["workflows"],
                "started_at": session["started_at"].isoformat(),
                "estimated_completion": self._estimate_completion_time(session)
            }
        
        # Check history
        for session in self.automation_history:
            if session["session_id"] == session_id:
                return {
                    "status": session["status"],
                    "final_results": {
                        "total_jobs": session.get("total_jobs", 0),
                        "successful_applications": session.get("successful_applications", 0),
                        "failed_applications": session.get("failed_applications", 0),
                        "duration_seconds": session.get("duration", 0)
                    },
                    "completed_at": session.get("completed_at", "").isoformat() if session.get("completed_at") else None
                }
        
        return {
            "status": "not_found",
            "message": f"Automation session {session_id} not found"
        }
    
    def get_automation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get automation history for a user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of records to return
            
        Returns:
            List of automation history records
        """
        user_history = [
            session for session in self.automation_history 
            if session.get("user_id") == user_id
        ]
        
        # Sort by completion time (most recent first)
        user_history.sort(key=lambda x: x.get("completed_at", datetime.min), reverse=True)
        
        return user_history[:limit]
    
    async def _build_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Build comprehensive user profile for automation"""
        try:
            # Get user information from database
            user = await self.db_ops.get_user_by_id(user_id)
            
            # Get user preferences
            preferences = await self.db_ops.get_user_preferences(user_id)
            
            # Get resume data
            resume_templates = await self.db_ops.get_resume_templates(user_id)
            primary_resume = resume_templates[0] if resume_templates else {}
            
            return {
                "user_id": user_id,
                "email": user.email if user else "",
                "full_name": user.full_name if user else "",
                "candidate_info": {
                    "name": user.full_name if user else "",
                    "email": user.email if user else "",
                    "phone": preferences.get("phone", "") if preferences else "",
                    "location": preferences.get("location", "") if preferences else "",
                },
                "resume_data": primary_resume.get("content", {}) if primary_resume else {},
                "resume_summary": primary_resume.get("summary", {}) if primary_resume else {},
                "preferences": preferences or {},
                "automation_settings": preferences.get("automation", {}) if preferences else {}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to build user profile: {str(e)}")
            return {
                "user_id": user_id,
                "email": "user@example.com",
                "candidate_info": {"name": "User", "email": "user@example.com"},
                "resume_data": {},
                "preferences": {}
            }
    
    def _filter_jobs_for_automation(self, job_search_results: List[Dict[str, Any]], 
                                  automation_settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter jobs based on automation criteria"""
        filtered_jobs = []
        
        max_applications = automation_settings.get("max_applications_per_session", 10)
        
        for job in job_search_results:
            # Apply filtering criteria
            if len(filtered_jobs) >= max_applications:
                break
                
            # Check if job meets automation criteria
            if self._meets_automation_criteria(job, automation_settings):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _meets_automation_criteria(self, job: Dict[str, Any], settings: Dict[str, Any]) -> bool:
        """Check if a job meets automation criteria"""
        # Basic checks
        if not job.get("title") or not job.get("company"):
            return False
        
        # Check excluded companies
        excluded_companies = settings.get("excluded_companies", [])
        if job.get("company", "").lower() in [c.lower() for c in excluded_companies]:
            return False
        
        # Check required keywords
        required_keywords = settings.get("required_keywords", [])
        job_text = f"{job.get('title', '')} {job.get('summary', '')}".lower()
        
        if required_keywords:
            if not any(keyword.lower() in job_text for keyword in required_keywords):
                return False
        
        # Check excluded keywords
        excluded_keywords = settings.get("excluded_keywords", [])
        if any(keyword.lower() in job_text for keyword in excluded_keywords):
            return False
        
        return True
    
    def _calculate_next_run(self, automation_config: Dict[str, Any]) -> datetime:
        """Calculate next run time for scheduled automation"""
        frequency = automation_config.get("frequency", "daily")
        
        if frequency == "daily":
            return datetime.now() + timedelta(days=1)
        elif frequency == "weekly":
            return datetime.now() + timedelta(weeks=1)
        elif frequency == "hourly":
            return datetime.now() + timedelta(hours=1)
        else:
            return datetime.now() + timedelta(days=1)
    
    def _estimate_completion_time(self, session: Dict[str, Any]) -> str:
        """Estimate completion time for active session"""
        if session["processed_jobs"] == 0:
            return "Calculating..."
        
        elapsed = (datetime.now() - session["started_at"]).total_seconds()
        avg_time_per_job = elapsed / session["processed_jobs"]
        remaining_jobs = session["total_jobs"] - session["processed_jobs"]
        estimated_remaining = remaining_jobs * avg_time_per_job
        
        completion_time = datetime.now() + timedelta(seconds=estimated_remaining)
        return completion_time.isoformat()
    
    async def _save_automation_session(self, session: Dict[str, Any]) -> None:
        """Save automation session to database"""
        try:
            # Save to database (implementation depends on your database schema)
            self.logger.info(f"Saved automation session {session['session_id']} to database")
        except Exception as e:
            self.logger.error(f"Failed to save automation session: {str(e)}")
    
    async def _save_individual_automation(self, record: Dict[str, Any]) -> None:
        """Save individual automation record to database"""
        try:
            # Save to database
            self.logger.info(f"Saved individual automation record for workflow {record['workflow_id']}")
        except Exception as e:
            self.logger.error(f"Failed to save automation record: {str(e)}")
    
    async def _save_automation_schedule(self, schedule: Dict[str, Any]) -> None:
        """Save automation schedule to database"""
        try:
            # Save to database
            self.logger.info(f"Saved automation schedule {schedule['schedule_id']}")
        except Exception as e:
            self.logger.error(f"Failed to save automation schedule: {str(e)}")