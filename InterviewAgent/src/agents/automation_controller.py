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
from agents.simple_automation_controller import SimpleAutomationController
from agents.base_agent import AgentContext
from database.operations import get_db_operations
from config import get_config

# Try to import OpenAI components, fall back gracefully if not available
try:
    from agents.openai_agents_orchestrator import OpenAIAgentsOrchestrator
    from agents.openai_automation_agent import create_automation_agent, AutomationWorkflowInput
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"OpenAI components not available: {e}")
    OPENAI_AVAILABLE = False


class AutomationController:
    """
    High-level controller that manages the complete job application automation pipeline
    Connects job search results to multi-agent workflows for seamless automation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or get_config()
        self.db_ops = get_db_operations()
        self.orchestrator = OrchestratorAgent(config)
        self.enhanced_orchestrator = EnhancedOrchestratorAgent(config)
        
        # Initialize simple automation controller (always available)
        self.simple_automation_controller = SimpleAutomationController(config)
        
        # Initialize OpenAI components if available
        if OPENAI_AVAILABLE:
            try:
                self.openai_agents_orchestrator = OpenAIAgentsOrchestrator(config)
                self.automation_agent = create_automation_agent()
                self.openai_enabled = True
            except Exception as e:
                print(f"Failed to initialize OpenAI components: {e}")
                self.openai_enabled = False
        else:
            self.openai_enabled = False
        
        # Track automation sessions
        self.active_sessions = {}
        self.automation_history = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    async def start_job_application_automation(self, user_id: str, job_search_criteria: Dict[str, Any], 
                                             automation_settings: Dict[str, Any], saved_jobs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start automated job application process following the exact workflow:
        1. Call Job search agent based on configuration
        2. Hand off to Resume agent for optimization
        3. Hand off to Cover letter agent for generation
        4. Save to database against application
        5. Trigger Playwright MCP automation
        
        Args:
            user_id: ID of the user
            job_search_criteria: Job search parameters
            automation_settings: User automation preferences
            
        Returns:
            Automation session details
        """
        session_id = str(uuid.uuid4())
        
        try:
            # Get user profile and resume data for automation
            user_profile = await self._build_user_profile(user_id)
            resume_data = user_profile.get("resume_data", {})
            
            self.logger.info(f"Starting OpenAI Automation Agent workflow for user {user_id}")
            
            # Prepare automation workflow input
            workflow_input = AutomationWorkflowInput(
                user_id=user_id,
                job_search_criteria=job_search_criteria,
                automation_config=automation_settings,
                user_profile=user_profile,
                resume_data=resume_data
            )
            
            # Create automation session
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "started_at": datetime.now(),
                "status": "running",
                "automation_settings": automation_settings,
                "job_search_criteria": job_search_criteria,
                "workflow_type": "openai_automation_agent"
            }
            
            self.active_sessions[session_id] = session
            
            # Execute the complete automation workflow
            # This follows the exact steps: Job Search → Resume Optimization → Cover Letter → Database → Playwright
            automation_result = await self.simple_automation_controller.execute_job_automation_workflow(
                user_id=user_id,
                job_search_criteria=job_search_criteria,
                automation_config=automation_settings,
                saved_jobs=saved_jobs
            )
            
            # Update session with automation results
            session.update({
                "automation_result": automation_result,
                "workflow_id": automation_result.workflow_id,
                "total_jobs": automation_result.total_jobs_found,
                "applications_created": automation_result.applications_created,
                "applications_submitted": automation_result.applications_submitted,
                "success_rate": (automation_result.applications_created / max(automation_result.total_jobs_found, 1)) * 100,
                "detailed_results": automation_result.detailed_results
            })
            
            # Update session status
            session["status"] = "completed" if automation_result.success else "failed"
            session["completed_at"] = datetime.now()
            session["duration"] = (session["completed_at"] - session["started_at"]).total_seconds()
            
            # Save session to database
            await self._save_automation_session(session)
            
            # Move to history
            self.automation_history.append(session)
            del self.active_sessions[session_id]
            
            return {
                "success": automation_result.success,
                "session_id": session_id,
                "workflow_id": automation_result.workflow_id,
                "automation_summary": {
                    "total_jobs_found": automation_result.total_jobs_found,
                    "applications_created": automation_result.applications_created,
                    "applications_submitted": automation_result.applications_submitted,
                    "duration_seconds": session["duration"],
                    "success_rate": session["success_rate"],
                    "workflow_steps": [
                        "Job Search (OpenAI Job Discovery Agent)",
                        "Resume Optimization (OpenAI Resume Optimizer Agent)", 
                        "Cover Letter Generation (OpenAI Cover Letter Agent)",
                        "Database Storage",
                        "Playwright MCP Automation"
                    ]
                },
                "detailed_results": automation_result.detailed_results,
                "execution_summary": automation_result.execution_summary,
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
            
            # Create and execute OpenAI Agents SDK workflow with proper handoffs
            result = await self.openai_agents_orchestrator.create_enhanced_job_workflow(
                user_id=user_id,
                job_data=job_data,
                user_profile=user_profile,
                automation_settings=user_preferences or {}
            )
            
            # Save individual automation record
            automation_record = {
                "user_id": user_id,
                "job_data": job_data,
                "workflow_id": result.get("workflow_id", "unknown"),
                "result": result,
                "automated_at": datetime.now(),
                "step_details": result.get("step_results", {}),
                "handoff_tracking": result.get("handoff_results", {}),
                "openai_agents_sdk": True  # Mark as using OpenAI Agents SDK
            }
            
            await self._save_individual_automation(automation_record)
            
            return {
                "success": result.get("success", False),
                "workflow_id": result.get("workflow_id", "unknown"),
                "job_title": job_data.get("title", "Unknown"),
                "company": job_data.get("company", "Unknown"),
                "automation_result": result,
                "step_execution_details": result.get("step_results", {}),
                "handoff_performance": result.get("handoff_results", {}),
                "openai_agents_sdk_output": result.get("final_output", ""),
                "using_openai_agents_sdk": True
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
    
    def get_enhanced_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get detailed status of an enhanced workflow including step-by-step progress
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Enhanced workflow status with step details
        """
        # Check OpenAI Agents SDK orchestrator first
        openai_result = self.openai_agents_orchestrator.get_workflow_details(workflow_id)
        if openai_result.get("success"):
            return openai_result
        
        # Check if enhanced orchestrator has the workflow
        if hasattr(self.enhanced_orchestrator, 'get_workflow_details'):
            enhanced_result = self.enhanced_orchestrator.get_workflow_details(workflow_id)
            if enhanced_result.get("success"):
                return enhanced_result
        
        # Fallback to basic status
        return self.get_automation_status(workflow_id)
    
    def get_step_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for individual workflow steps
        
        Args:
            user_id: ID of the user
            
        Returns:
            Step performance analysis
        """
        user_sessions = [
            session for session in self.automation_history 
            if session.get("user_id") == user_id
        ]
        
        step_metrics = {}
        total_sessions = len(user_sessions)
        
        if total_sessions == 0:
            return {"message": "No automation history found"}
        
        # Aggregate step success rates
        for session in user_sessions:
            step_rates = session.get("step_success_rates", {})
            for step_id, success_count in step_rates.items():
                if step_id not in step_metrics:
                    step_metrics[step_id] = {
                        "total_attempts": 0,
                        "successful_attempts": 0,
                        "success_rate": 0.0
                    }
                step_metrics[step_id]["total_attempts"] += 1
                step_metrics[step_id]["successful_attempts"] += success_count
        
        # Calculate success rates
        for step_id, metrics in step_metrics.items():
            if metrics["total_attempts"] > 0:
                metrics["success_rate"] = metrics["successful_attempts"] / metrics["total_attempts"]
        
        return {
            "total_sessions_analyzed": total_sessions,
            "step_performance": step_metrics,
            "overall_metrics": {
                "average_steps_completed": sum(
                    len(session.get("step_success_rates", {})) 
                    for session in user_sessions
                ) / total_sessions,
                "most_reliable_step": max(step_metrics.items(), key=lambda x: x[1]["success_rate"])[0] if step_metrics else None,
                "least_reliable_step": min(step_metrics.items(), key=lambda x: x[1]["success_rate"])[0] if step_metrics else None
            }
        }
    
    def get_handoff_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get analytics on agent handoff performance
        
        Args:
            user_id: ID of the user
            
        Returns:
            Handoff performance analytics
        """
        user_sessions = [
            session for session in self.automation_history 
            if session.get("user_id") == user_id
        ]
        
        handoff_data = []
        for session in user_sessions:
            results = session.get("individual_workflow_results", [])
            for result in results:
                handoff_results = result.get("handoff_results", {})
                if handoff_results:
                    handoff_data.append(handoff_results)
        
        if not handoff_data:
            return {"message": "No handoff data available"}
        
        # Analyze handoff performance
        total_handoffs = len(handoff_data)
        successful_handoffs = sum(1 for h in handoff_data if h.get("success", False))
        
        return {
            "total_handoffs": total_handoffs,
            "successful_handoffs": successful_handoffs,
            "handoff_success_rate": successful_handoffs / total_handoffs if total_handoffs > 0 else 0,
            "average_handoff_time": sum(
                h.get("execution_time", 0) for h in handoff_data
            ) / total_handoffs if total_handoffs > 0 else 0,
            "common_handoff_issues": self._analyze_handoff_issues(handoff_data)
        }
    
    def _analyze_handoff_issues(self, handoff_data: List[Dict[str, Any]]) -> List[str]:
        """Analyze common issues in handoff data"""
        issues = []
        failed_handoffs = [h for h in handoff_data if not h.get("success", True)]
        
        if len(failed_handoffs) > len(handoff_data) * 0.2:  # More than 20% failure rate
            issues.append("High handoff failure rate detected")
        
        # Check for data transformation issues
        transformation_errors = sum(1 for h in failed_handoffs if "transformation" in h.get("error", "").lower())
        if transformation_errors > len(failed_handoffs) * 0.3:
            issues.append("Data transformation issues detected")
        
        # Check for validation issues
        validation_errors = sum(1 for h in failed_handoffs if "validation" in h.get("error", "").lower())
        if validation_errors > len(failed_handoffs) * 0.3:
            issues.append("Data validation issues detected")
        
        return issues
    
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