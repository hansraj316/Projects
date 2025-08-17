"""
Job Service - Business logic for job management

Handles job discovery, search, and management operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

from repositories.interfaces import IJobRepository, IApplicationRepository
from core.protocols import ILogger, IValidator, IEventBus, IMetrics
from core.exceptions import ValidationError, DatabaseError
from agents.base_agent import BaseAgent, AgentTask, AgentContext, AgentResult

class JobSearchCriteria:
    """Job search criteria with validation"""
    
    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        remote_only: bool = False,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        limit: int = 50
    ):
        self.keywords = keywords or []
        self.location = location
        self.company = company
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.remote_only = remote_only
        self.job_type = job_type
        self.experience_level = experience_level
        self.limit = min(limit, 1000)  # Cap at 1000 results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "keywords": self.keywords,
            "location": self.location,
            "company": self.company,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "remote_only": self.remote_only,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "limit": self.limit
        }
    
    def validate(self, validator: IValidator) -> None:
        """Validate search criteria"""
        if self.salary_min is not None and self.salary_min < 0:
            raise ValidationError("salary_min", self.salary_min, "Minimum salary cannot be negative")
        
        if self.salary_max is not None and self.salary_max < 0:
            raise ValidationError("salary_max", self.salary_max, "Maximum salary cannot be negative")
        
        if (self.salary_min is not None and self.salary_max is not None 
            and self.salary_min > self.salary_max):
            raise ValidationError("salary_range", f"{self.salary_min}-{self.salary_max}", 
                                "Minimum salary cannot be greater than maximum salary")
        
        if self.limit <= 0:
            raise ValidationError("limit", self.limit, "Limit must be positive")

class JobService:
    """Service for job-related business logic"""
    
    def __init__(
        self,
        job_repository: IJobRepository,
        application_repository: IApplicationRepository,
        job_discovery_agent: BaseAgent,
        logger: ILogger,
        validator: IValidator,
        event_bus: IEventBus,
        metrics: IMetrics
    ):
        self._job_repo = job_repository
        self._application_repo = application_repository
        self._job_discovery_agent = job_discovery_agent
        self._logger = logger
        self._validator = validator
        self._event_bus = event_bus
        self._metrics = metrics
    
    async def search_jobs(
        self, 
        criteria: JobSearchCriteria, 
        user_id: str,
        use_ai_discovery: bool = True
    ) -> Dict[str, Any]:
        """
        Search for jobs using criteria with optional AI discovery
        
        Args:
            criteria: Search criteria
            user_id: User performing the search
            use_ai_discovery: Whether to use AI agent for discovery
            
        Returns:
            Dictionary containing search results and metadata
        """
        start_time = datetime.now()
        
        try:
            # Validate search criteria
            criteria.validate(self._validator)
            
            # Log search start
            self._logger.info("Starting job search", extra={
                "user_id": user_id,
                "criteria": criteria.to_dict(),
                "use_ai_discovery": use_ai_discovery
            })
            
            # Record search metrics
            self._metrics.increment_counter("job_search.started", {"user_id": user_id})
            
            # Search existing jobs in database
            db_jobs = await self._search_database_jobs(criteria)
            
            # Optionally use AI agent for discovery
            ai_jobs = []
            if use_ai_discovery:
                ai_jobs = await self._discover_jobs_with_ai(criteria, user_id)
            
            # Combine and deduplicate results
            all_jobs = self._merge_job_results(db_jobs, ai_jobs)
            
            # Apply final filtering and sorting
            filtered_jobs = self._apply_final_filters(all_jobs, criteria)
            
            # Prepare results
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "jobs": filtered_jobs[:criteria.limit],
                "total_found": len(filtered_jobs),
                "db_results": len(db_jobs),
                "ai_results": len(ai_jobs),
                "execution_time_seconds": execution_time,
                "criteria": criteria.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Record metrics
            self._metrics.record_histogram("job_search.execution_time", execution_time * 1000)
            self._metrics.increment_counter("job_search.completed", {
                "user_id": user_id,
                "results_count": str(len(filtered_jobs))
            })
            
            # Publish event
            self._event_bus.publish("job_search.completed", {
                "user_id": user_id,
                "results_count": len(filtered_jobs),
                "criteria": criteria.to_dict()
            })
            
            self._logger.info("Job search completed successfully", extra={
                "user_id": user_id,
                "results_count": len(filtered_jobs),
                "execution_time": execution_time
            })
            
            return result
            
        except ValidationError as e:
            self._logger.warning("Job search validation failed", extra={
                "user_id": user_id,
                "error": str(e),
                "field": e.field
            })
            self._metrics.increment_counter("job_search.validation_error", {"user_id": user_id})
            
            return {
                "success": False,
                "error": str(e),
                "error_type": "validation_error",
                "jobs": [],
                "total_found": 0
            }
            
        except Exception as e:
            self._logger.error("Job search failed", extra={
                "user_id": user_id,
                "error": str(e),
                "criteria": criteria.to_dict()
            })
            self._metrics.increment_counter("job_search.error", {"user_id": user_id})
            
            return {
                "success": False,
                "error": "An error occurred during job search",
                "error_type": "internal_error",
                "jobs": [],
                "total_found": 0
            }
    
    async def _search_database_jobs(self, criteria: JobSearchCriteria) -> List[Dict[str, Any]]:
        """Search for jobs in the database"""
        try:
            return await self._job_repo.find_by_criteria(criteria.to_dict())
        except DatabaseError as e:
            self._logger.error("Database job search failed", extra={"error": str(e)})
            return []
    
    async def _discover_jobs_with_ai(self, criteria: JobSearchCriteria, user_id: str) -> List[Dict[str, Any]]:
        """Use AI agent to discover new jobs"""
        try:
            # Create agent task
            task = AgentTask(
                task_type="discover_jobs",
                description="Discover new job listings based on search criteria",
                input_data=criteria.to_dict()
            )
            
            # Create agent context
            context = AgentContext(
                user_id=user_id,
                preferences={"search_criteria": criteria.to_dict()}
            )
            
            # Execute agent task
            result = await self._job_discovery_agent.execute_with_error_handling(task, context)
            
            if result.success and result.data:
                jobs = result.data.get("jobs", [])
                
                # Save discovered jobs to database
                saved_jobs = []
                for job_data in jobs:
                    try:
                        # Validate job data
                        if self._validator.validate_job_data(job_data):
                            saved_job = await self._job_repo.create(job_data)
                            saved_jobs.append(saved_job)
                    except Exception as e:
                        self._logger.warning("Failed to save discovered job", extra={
                            "job_data": job_data,
                            "error": str(e)
                        })
                
                self._logger.info("AI job discovery completed", extra={
                    "discovered_count": len(jobs),
                    "saved_count": len(saved_jobs)
                })
                
                return saved_jobs
                
            else:
                self._logger.warning("AI job discovery failed", extra={
                    "error": result.error,
                    "criteria": criteria.to_dict()
                })
                return []
                
        except Exception as e:
            self._logger.error("AI job discovery error", extra={
                "error": str(e),
                "criteria": criteria.to_dict()
            })
            return []
    
    def _merge_job_results(self, db_jobs: List[Dict[str, Any]], ai_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate job results from different sources"""
        # Use URL and title+company as deduplication keys
        seen = set()
        merged_jobs = []
        
        # Add database jobs first (they're already validated)
        for job in db_jobs:
            key = self._get_job_dedup_key(job)
            if key not in seen:
                seen.add(key)
                job["source"] = "database"
                merged_jobs.append(job)
        
        # Add AI discovered jobs
        for job in ai_jobs:
            key = self._get_job_dedup_key(job)
            if key not in seen:
                seen.add(key)
                job["source"] = "ai_discovery"
                merged_jobs.append(job)
        
        return merged_jobs
    
    def _get_job_dedup_key(self, job: Dict[str, Any]) -> str:
        """Generate deduplication key for job"""
        url = job.get("url", "").strip().lower()
        if url:
            return f"url:{url}"
        
        title = job.get("title", "").strip().lower()
        company = job.get("company", "").strip().lower()
        return f"title_company:{title}:{company}"
    
    def _apply_final_filters(self, jobs: List[Dict[str, Any]], criteria: JobSearchCriteria) -> List[Dict[str, Any]]:
        """Apply final filtering and sorting to job results"""
        filtered_jobs = []
        
        for job in jobs:
            # Apply additional filters not handled by database query
            if self._job_matches_criteria(job, criteria):
                filtered_jobs.append(job)
        
        # Sort by relevance score (if available) or creation date
        filtered_jobs.sort(key=lambda x: (
            x.get("relevance_score", 0),
            x.get("created_at", datetime.min)
        ), reverse=True)
        
        return filtered_jobs
    
    def _job_matches_criteria(self, job: Dict[str, Any], criteria: JobSearchCriteria) -> bool:
        """Check if job matches search criteria"""
        # Additional filtering logic can be added here
        # For now, assume database query handles most filtering
        return True
    
    async def get_job_details(self, job_id: str, user_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific job"""
        try:
            self._logger.info("Fetching job details", extra={
                "job_id": job_id,
                "user_id": user_id
            })
            
            job = await self._job_repo.get_by_id(job_id)
            
            if not job:
                return {
                    "success": False,
                    "error": "Job not found",
                    "error_type": "not_found"
                }
            
            # Check if user has already applied
            applications = await self._application_repo.find_by_job(job_id)
            user_application = next((app for app in applications if app.get("user_id") == user_id), None)
            
            # Add application status to job details
            job["user_application_status"] = user_application.get("status") if user_application else None
            job["user_applied"] = bool(user_application)
            
            self._metrics.increment_counter("job_details.viewed", {"user_id": user_id})
            
            return {
                "success": True,
                "job": job
            }
            
        except Exception as e:
            self._logger.error("Failed to get job details", extra={
                "job_id": job_id,
                "user_id": user_id,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": "Failed to retrieve job details",
                "error_type": "internal_error"
            }
    
    async def get_recommended_jobs(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get job recommendations for user based on preferences and history"""
        try:
            # Get recent applications to understand user preferences
            recent_applications = await self._application_repo.get_application_history(user_id, limit=20)
            
            # Extract preferences from application history
            keywords = set()
            locations = set()
            companies = set()
            
            for app in recent_applications:
                if app.get("job_title"):
                    # Simple keyword extraction from job titles
                    title_words = app["job_title"].lower().split()
                    keywords.update(word for word in title_words if len(word) > 3)
                
                if app.get("location"):
                    locations.add(app["location"])
                
                if app.get("company"):
                    companies.add(app["company"])
            
            # Create search criteria based on user preferences
            criteria = JobSearchCriteria(
                keywords=list(keywords)[:10],  # Limit keywords
                limit=limit * 2  # Get more results for better filtering
            )
            
            # Search for jobs
            search_result = await self.search_jobs(criteria, user_id, use_ai_discovery=False)
            
            if search_result["success"]:
                # Filter out jobs user has already applied to
                applied_job_ids = {app.get("job_id") for app in recent_applications}
                recommended_jobs = [
                    job for job in search_result["jobs"] 
                    if job.get("id") not in applied_job_ids
                ][:limit]
                
                return {
                    "success": True,
                    "jobs": recommended_jobs,
                    "total_found": len(recommended_jobs),
                    "based_on_applications": len(recent_applications)
                }
            else:
                return search_result
                
        except Exception as e:
            self._logger.error("Failed to get job recommendations", extra={
                "user_id": user_id,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": "Failed to generate job recommendations",
                "error_type": "internal_error",
                "jobs": []
            }
    
    async def get_job_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get job statistics (system-wide or user-specific)"""
        try:
            filters = {"user_id": user_id} if user_id else None
            
            total_jobs = await self._job_repo.count(filters)
            recent_jobs = await self._job_repo.find_recent(days=7)
            
            # Get application statistics if user-specific
            application_stats = {}
            if user_id:
                application_stats = await self._application_repo.get_statistics(user_id)
            
            return {
                "success": True,
                "statistics": {
                    "total_jobs": total_jobs,
                    "recent_jobs_count": len(recent_jobs),
                    "application_stats": application_stats
                }
            }
            
        except Exception as e:
            self._logger.error("Failed to get job statistics", extra={
                "user_id": user_id,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": "Failed to retrieve job statistics",
                "error_type": "internal_error"
            }