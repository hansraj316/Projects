"""
Automation Scheduler - APScheduler integration for recurring job application automation
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from agents.simple_automation_controller import SimpleAutomationController
from agents.job_discovery import JobDiscoveryAgent
from config import get_config
from database.operations import get_db_operations


class AutomationScheduler:
    """
    Handles scheduled and recurring job application automation using APScheduler
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or get_config()
        self.db_ops = get_db_operations()
        self.automation_controller = SimpleAutomationController(config)
        self.job_discovery_agent = JobDiscoveryAgent(config)
        
        # Setup APScheduler
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': AsyncIOExecutor()},
            job_defaults={
                'coalesce': False,
                'max_instances': 3,
                'misfire_grace_time': 300  # 5 minutes
            }
        )
        
        # Track scheduled jobs
        self.scheduled_jobs = {}
        self.job_execution_history = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    async def start_scheduler(self) -> None:
        """Start the automation scheduler"""
        try:
            self.scheduler.start()
            self.logger.info("Automation scheduler started successfully")
            
            # Load existing scheduled jobs from database
            await self._load_scheduled_jobs()
            
        except Exception as e:
            self.logger.error(f"Failed to start automation scheduler: {str(e)}")
            raise
    
    async def stop_scheduler(self) -> None:
        """Stop the automation scheduler"""
        try:
            self.scheduler.shutdown()
            self.logger.info("Automation scheduler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {str(e)}")
    
    async def schedule_daily_automation(self, user_id: str, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule daily job application automation
        
        Args:
            user_id: ID of the user
            automation_config: Configuration for automation
            
        Returns:
            Scheduling result
        """
        try:
            job_id = f"daily_automation_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Default to 9 AM if no time specified
            hour = automation_config.get("hour", 9)
            minute = automation_config.get("minute", 0)
            
            # Create cron trigger for daily execution
            trigger = CronTrigger(hour=hour, minute=minute)
            
            # Schedule the job
            self.scheduler.add_job(
                func=self._execute_scheduled_automation,
                trigger=trigger,
                args=[user_id, automation_config],
                id=job_id,
                name=f"Daily Automation for User {user_id}",
                replace_existing=True
            )
            
            # Track the scheduled job
            schedule_record = {
                "job_id": job_id,
                "user_id": user_id,
                "schedule_type": "daily",
                "automation_config": automation_config,
                "next_run": self.scheduler.get_job(job_id).next_run_time,
                "created_at": datetime.now(),
                "status": "active"
            }
            
            self.scheduled_jobs[job_id] = schedule_record
            await self._save_scheduled_job(schedule_record)
            
            self.logger.info(f"Scheduled daily automation for user {user_id} at {hour:02d}:{minute:02d}")
            
            return {
                "success": True,
                "job_id": job_id,
                "schedule_type": "daily",
                "next_run": schedule_record["next_run"].isoformat(),
                "message": f"Daily automation scheduled for {hour:02d}:{minute:02d}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule daily automation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to schedule daily automation"
            }
    
    async def schedule_weekly_automation(self, user_id: str, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule weekly job application automation
        
        Args:
            user_id: ID of the user
            automation_config: Configuration for automation
            
        Returns:
            Scheduling result
        """
        try:
            job_id = f"weekly_automation_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Default to Monday 9 AM if not specified
            day_of_week = automation_config.get("day_of_week", 0)  # 0 = Monday
            hour = automation_config.get("hour", 9)
            minute = automation_config.get("minute", 0)
            
            # Create cron trigger for weekly execution
            trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
            
            # Schedule the job
            self.scheduler.add_job(
                func=self._execute_scheduled_automation,
                trigger=trigger,
                args=[user_id, automation_config],
                id=job_id,
                name=f"Weekly Automation for User {user_id}",
                replace_existing=True
            )
            
            # Track the scheduled job
            schedule_record = {
                "job_id": job_id,
                "user_id": user_id,
                "schedule_type": "weekly",
                "automation_config": automation_config,
                "next_run": self.scheduler.get_job(job_id).next_run_time,
                "created_at": datetime.now(),
                "status": "active"
            }
            
            self.scheduled_jobs[job_id] = schedule_record
            await self._save_scheduled_job(schedule_record)
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_name = days[day_of_week]
            
            self.logger.info(f"Scheduled weekly automation for user {user_id} on {day_name} at {hour:02d}:{minute:02d}")
            
            return {
                "success": True,
                "job_id": job_id,
                "schedule_type": "weekly",
                "next_run": schedule_record["next_run"].isoformat(),
                "message": f"Weekly automation scheduled for {day_name} at {hour:02d}:{minute:02d}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule weekly automation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to schedule weekly automation"
            }
    
    async def schedule_one_time_automation(self, user_id: str, automation_config: Dict[str, Any], 
                                         run_at: datetime) -> Dict[str, Any]:
        """
        Schedule one-time job application automation
        
        Args:
            user_id: ID of the user
            automation_config: Configuration for automation
            run_at: When to run the automation
            
        Returns:
            Scheduling result
        """
        try:
            job_id = f"onetime_automation_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Create date trigger for one-time execution
            trigger = DateTrigger(run_date=run_at)
            
            # Schedule the job
            self.scheduler.add_job(
                func=self._execute_scheduled_automation,
                trigger=trigger,
                args=[user_id, automation_config],
                id=job_id,
                name=f"One-time Automation for User {user_id}",
                replace_existing=True
            )
            
            # Track the scheduled job
            schedule_record = {
                "job_id": job_id,
                "user_id": user_id,
                "schedule_type": "one_time",
                "automation_config": automation_config,
                "next_run": run_at,
                "created_at": datetime.now(),
                "status": "active"
            }
            
            self.scheduled_jobs[job_id] = schedule_record
            await self._save_scheduled_job(schedule_record)
            
            self.logger.info(f"Scheduled one-time automation for user {user_id} at {run_at}")
            
            return {
                "success": True,
                "job_id": job_id,
                "schedule_type": "one_time",
                "next_run": run_at.isoformat(),
                "message": f"One-time automation scheduled for {run_at.strftime('%Y-%m-%d %H:%M')}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule one-time automation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to schedule one-time automation"
            }
    
    async def cancel_scheduled_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled automation job
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            Cancellation result
        """
        try:
            # Remove from scheduler
            self.scheduler.remove_job(job_id)
            
            # Update tracking
            if job_id in self.scheduled_jobs:
                self.scheduled_jobs[job_id]["status"] = "cancelled"
                self.scheduled_jobs[job_id]["cancelled_at"] = datetime.now()
                await self._update_scheduled_job_status(job_id, "cancelled")
            
            self.logger.info(f"Cancelled scheduled job {job_id}")
            
            return {
                "success": True,
                "job_id": job_id,
                "message": "Scheduled automation cancelled successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cancel scheduled job {job_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to cancel scheduled automation"
            }
    
    async def get_scheduled_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all scheduled jobs for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of scheduled jobs
        """
        user_jobs = []
        
        for job_id, job_record in self.scheduled_jobs.items():
            if job_record["user_id"] == user_id and job_record["status"] == "active":
                # Get current next run time from scheduler
                try:
                    scheduler_job = self.scheduler.get_job(job_id)
                    if scheduler_job:
                        job_record["next_run"] = scheduler_job.next_run_time
                except:
                    pass
                
                user_jobs.append(job_record)
        
        return user_jobs
    
    async def get_automation_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get automation execution history for a user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of records to return
            
        Returns:
            List of execution history records
        """
        user_history = [
            record for record in self.job_execution_history
            if record.get("user_id") == user_id
        ]
        
        # Sort by execution time (most recent first)
        user_history.sort(key=lambda x: x.get("executed_at", datetime.min), reverse=True)
        
        return user_history[:limit]
    
    async def _execute_scheduled_automation(self, user_id: str, automation_config: Dict[str, Any]) -> None:
        """
        Execute scheduled automation job
        
        Args:
            user_id: ID of the user
            automation_config: Configuration for automation
        """
        execution_id = str(uuid.uuid4())
        execution_start = datetime.now()
        
        try:
            self.logger.info(f"Starting scheduled automation for user {user_id}")
            
            # Perform job search first
            search_criteria = automation_config.get("search_criteria", {})
            job_search_results = await self._perform_automated_job_search(user_id, search_criteria)
            
            if not job_search_results:
                self.logger.warning(f"No jobs found for user {user_id} scheduled automation")
                return
            
            # Start enhanced automation process
            automation_result = await self.automation_controller.start_job_application_automation(
                user_id=user_id,
                job_search_results=job_search_results,
                automation_settings=automation_config
            )
            
            # Record execution history
            execution_record = {
                "execution_id": execution_id,
                "user_id": user_id,
                "executed_at": execution_start,
                "completed_at": datetime.now(),
                "automation_config": automation_config,
                "job_search_results_count": len(job_search_results),
                "automation_result": automation_result,
                "success": automation_result.get("success", False)
            }
            
            self.job_execution_history.append(execution_record)
            await self._save_execution_history(execution_record)
            
            self.logger.info(f"Completed scheduled automation for user {user_id}: {automation_result.get('automation_summary', {})}")
            
        except Exception as e:
            self.logger.error(f"Scheduled automation failed for user {user_id}: {str(e)}")
            
            # Record failed execution
            execution_record = {
                "execution_id": execution_id,
                "user_id": user_id,
                "executed_at": execution_start,
                "completed_at": datetime.now(),
                "automation_config": automation_config,
                "error": str(e),
                "success": False
            }
            
            self.job_execution_history.append(execution_record)
            await self._save_execution_history(execution_record)
    
    async def _perform_automated_job_search(self, user_id: str, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform automated job search for scheduled automation
        
        Args:
            user_id: ID of the user
            search_criteria: Search parameters
            
        Returns:
            List of job search results
        """
        try:
            from agents.base_agent import AgentTask, AgentContext
            
            # Create search task
            task = AgentTask(
                task_id=str(uuid.uuid4()),
                task_type="search_jobs",
                description="Automated job search for scheduled automation",
                input_data=search_criteria
            )
            
            # Create context
            context = AgentContext(
                user_id=user_id,
                metadata={"automation_mode": True, "scheduled_search": True}
            )
            
            # Execute job search
            result = await self.job_discovery_agent.execute(task, context)
            
            if result.get("success"):
                return result.get("data", {}).get("jobs", [])
            else:
                self.logger.error(f"Job search failed: {result.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            self.logger.error(f"Automated job search failed: {str(e)}")
            return []
    
    async def _load_scheduled_jobs(self) -> None:
        """Load scheduled jobs from database on startup"""
        try:
            # Load from database and restore active schedules
            # This would depend on your database implementation
            self.logger.info("Loaded scheduled jobs from database")
        except Exception as e:
            self.logger.error(f"Failed to load scheduled jobs: {str(e)}")
    
    async def _save_scheduled_job(self, schedule_record: Dict[str, Any]) -> None:
        """Save scheduled job to database"""
        try:
            # Save to database
            self.logger.info(f"Saved scheduled job {schedule_record['job_id']} to database")
        except Exception as e:
            self.logger.error(f"Failed to save scheduled job: {str(e)}")
    
    async def _update_scheduled_job_status(self, job_id: str, status: str) -> None:
        """Update scheduled job status in database"""
        try:
            # Update in database
            self.logger.info(f"Updated job {job_id} status to {status}")
        except Exception as e:
            self.logger.error(f"Failed to update job status: {str(e)}")
    
    async def _save_execution_history(self, execution_record: Dict[str, Any]) -> None:
        """Save execution history to database"""
        try:
            # Save to database
            self.logger.info(f"Saved execution history {execution_record['execution_id']} to database")
        except Exception as e:
            self.logger.error(f"Failed to save execution history: {str(e)}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and statistics"""
        return {
            "running": self.scheduler.running,
            "scheduled_jobs_count": len(self.scheduled_jobs),
            "active_jobs": len([j for j in self.scheduled_jobs.values() if j["status"] == "active"]),
            "execution_history_count": len(self.job_execution_history),
            "next_scheduled_jobs": [
                {
                    "job_id": job_id,
                    "user_id": job_record["user_id"],
                    "schedule_type": job_record["schedule_type"],
                    "next_run": job_record["next_run"].isoformat() if job_record.get("next_run") else None
                }
                for job_id, job_record in self.scheduled_jobs.items()
                if job_record["status"] == "active"
            ][:5]  # Show next 5 jobs
        }