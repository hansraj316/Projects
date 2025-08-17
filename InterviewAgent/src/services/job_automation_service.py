"""
Job Automation Service - Simplified service for Streamlit integration

Provides job search and automation functionality compatible with the existing Streamlit UI.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from config import get_config
from database.operations import get_db_operations
from agents.job_discovery import JobDiscoveryAgent
from agents.base_agent import AgentTask, AgentContext

logger = logging.getLogger(__name__)

class JobAutomationService:
    """
    Simplified automation service for job search and processing
    Compatible with existing Streamlit UI expectations
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._initialized = False
        self._job_discovery_agent = None
        self._db_ops = None
    
    async def initialize(self):
        """Initialize the service with required components"""
        try:
            self._db_ops = get_db_operations()
            
            # Initialize job discovery agent
            app_config = get_config()
            
            # Create simple logger implementation
            class SimpleLogger:
                def info(self, message, **kwargs):
                    logger.info(message)
                def warning(self, message, **kwargs):
                    logger.warning(message)
                def error(self, message, **kwargs):
                    logger.error(message)
            
            self._job_discovery_agent = JobDiscoveryAgent(
                name="job_discovery",
                description="AI-powered job discovery agent",
                logger=SimpleLogger(),
                openai_client=app_config.get_openai_client(),
                config=app_config
            )
            
            self._initialized = True
            logger.info("JobAutomationService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize JobAutomationService: {e}")
            raise
    
    async def process_job_search_results(
        self, 
        search_results: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process job search results and handle automation triggers
        
        Args:
            search_results: Results from job search
            user_id: User ID performing the search
            
        Returns:
            Automation processing results
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            jobs = search_results.get("data", {}).get("jobs", [])
            
            # Save jobs to database
            saved_jobs = []
            automation_triggered = 0
            triggered_automations = []
            
            for job in jobs:
                try:
                    # Save job to database
                    saved_job = await self._save_job_to_database(job, user_id)
                    if saved_job:
                        saved_jobs.append(saved_job)
                        
                        # Check if automation should be triggered
                        priority = job.get("application_priority", 5)
                        if priority >= 6:
                            automation_triggered += 1
                            triggered_automations.append({
                                "job_id": saved_job.get("id"),
                                "job_title": job.get("title", "Unknown"),
                                "company": job.get("company", "Unknown"),
                                "automation_id": f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(triggered_automations)}"
                            })
                
                except Exception as e:
                    logger.warning(f"Failed to process job: {e}")
                    continue
            
            return {
                "success": True,
                "saved_jobs_count": len(saved_jobs),
                "automation_triggered_count": automation_triggered,
                "triggered_automations": triggered_automations,
                "jobs": saved_jobs
            }
            
        except Exception as e:
            logger.error(f"Failed to process job search results: {e}")
            return {
                "success": False,
                "error": str(e),
                "saved_jobs_count": 0,
                "automation_triggered_count": 0,
                "triggered_automations": []
            }
    
    async def _save_job_to_database(self, job: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """Save a job to the database"""
        try:
            # Prepare job data for database
            job_data = {
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "url": job.get("url", ""),
                "description": job.get("description", ""),
                "salary_range": job.get("salary_range", ""),
                "requirements": job.get("requirements", []),
                "benefits": job.get("benefits", []),
                "job_type": job.get("job_type", ""),
                "experience_level": job.get("experience_level", ""),
                "remote_friendly": job.get("remote_friendly", False),
                "application_priority": job.get("application_priority", 5),
                "source": "ai_discovery",
                "discovered_by": user_id,
                "discovered_at": datetime.now().isoformat(),
                "status": "discovered"
            }
            
            # Use database operations to save job
            saved_job = await self._db_ops.save_job(job_data)
            return saved_job
            
        except Exception as e:
            logger.error(f"Failed to save job to database: {e}")
            return None
    
    async def get_saved_jobs_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get saved jobs for a user from the database"""
        try:
            if not self._db_ops:
                self._db_ops = get_db_operations()
            
            # Get jobs discovered by this user
            saved_jobs = await self._db_ops.get_jobs_by_user(user_id)
            
            return saved_jobs or []
            
        except Exception as e:
            logger.error(f"Failed to get saved jobs for user {user_id}: {e}")
            return []
    
    async def search_jobs_with_ai(
        self, 
        search_criteria: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Search for jobs using AI agent
        
        Args:
            search_criteria: Search parameters
            user_id: User performing the search
            
        Returns:
            Search results
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Create agent task
            task = AgentTask(
                task_type="discover_jobs",
                description="Discover job listings based on search criteria",
                input_data=search_criteria
            )
            
            # Create agent context
            context = AgentContext(
                user_id=user_id,
                preferences={"search_criteria": search_criteria}
            )
            
            # Execute search with AI agent
            result = await self._job_discovery_agent.execute_with_error_handling(task, context)
            
            if result.success and result.data:
                return {
                    "success": True,
                    "data": result.data
                }
            else:
                return {
                    "success": False,
                    "message": result.error or "AI job search failed",
                    "data": {"jobs": []}
                }
                
        except Exception as e:
            logger.error(f"AI job search failed: {e}")
            return {
                "success": False,
                "message": f"AI job search error: {str(e)}",
                "data": {"jobs": []}
            }