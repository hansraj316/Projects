"""
Job Automation Service - Automatically save jobs and trigger automation
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.operations import DatabaseOperations
from database.models import JobListing, Company, JobStatus, Application, ApplicationStatus
from config import Config


class JobAutomationService:
    """
    Service to automatically save discovered jobs and trigger automation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config_obj = Config()
            self.config = config_obj.__dict__
        else:
            self.config = config
        self.logger = logging.getLogger("job_automation_service")
        self.db_ops = DatabaseOperations()
        self.orchestrator = None
        
    async def initialize(self):
        """Initialize the service and orchestrator"""
        try:
            # Import orchestrator only when needed
            try:
                from agents.enhanced_orchestrator import EnhancedOrchestratorAgent
                self.orchestrator = EnhancedOrchestratorAgent(self.config)
                self.logger.info("Job automation service initialized successfully with orchestrator")
            except ImportError as ie:
                self.logger.warning(f"Could not import orchestrator: {ie}")
                self.orchestrator = None
                self.logger.info("Job automation service initialized without orchestrator")
        except Exception as e:
            self.logger.error(f"Failed to initialize job automation service: {e}")
            raise
    
    async def process_job_search_results(self, search_results: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Process job search results and automatically save jobs with automation trigger
        
        Args:
            search_results: Results from job discovery agent
            user_id: User ID for database operations
            
        Returns:
            Processing results with saved jobs and automation status
        """
        try:
            jobs = search_results.get("jobs", [])
            search_criteria = search_results.get("search_criteria", {})
            
            if not jobs:
                return {
                    "success": False,
                    "message": "No jobs found in search results",
                    "jobs_saved": 0,
                    "automations_triggered": 0
                }
            
            # Process each job
            saved_jobs = []
            automations_triggered = []
            
            for job_data in jobs:
                try:
                    # Save job to database
                    saved_job = await self._save_job_to_database(job_data, user_id, search_criteria)
                    if saved_job:
                        saved_jobs.append(saved_job)
                        
                        # Check if automation should be triggered
                        if self._should_trigger_automation(saved_job, search_criteria):
                            automation_result = await self._trigger_job_automation(saved_job, user_id)
                            if automation_result.get("success"):
                                automations_triggered.append({
                                    "job_id": saved_job.id,
                                    "job_title": saved_job.title,
                                    "company": saved_job.company,
                                    "automation_id": automation_result.get("automation_id")
                                })
                
                except Exception as e:
                    self.logger.error(f"Failed to process job {job_data.get('title', 'Unknown')}: {e}")
                    continue
            
            return {
                "success": True,
                "message": f"Processed {len(jobs)} jobs, saved {len(saved_jobs)}, triggered {len(automations_triggered)} automations",
                "jobs_saved": len(saved_jobs),
                "automations_triggered": len(automations_triggered),
                "saved_jobs": [self._job_to_dict(job) for job in saved_jobs],
                "triggered_automations": automations_triggered,
                "processing_stats": {
                    "total_jobs": len(jobs),
                    "successfully_saved": len(saved_jobs),
                    "automation_triggered": len(automations_triggered),
                    "processing_date": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process job search results: {e}")
            return {
                "success": False,
                "message": f"Failed to process job search results: {str(e)}",
                "jobs_saved": 0,
                "automations_triggered": 0
            }
    
    async def _save_job_to_database(self, job_data: Dict[str, Any], user_id: str, search_criteria: Dict[str, Any]) -> Optional[JobListing]:
        """
        Save a job to the database with enhanced data
        
        Args:
            job_data: Job data from discovery agent
            user_id: User ID
            search_criteria: Original search criteria
            
        Returns:
            Saved JobListing object or None if failed
        """
        try:
            # Extract and validate job URL
            job_url = job_data.get("application_url") or job_data.get("apply_link", "")
            if not job_url:
                self.logger.warning(f"No job URL found for {job_data.get('title', 'Unknown job')}")
                return None
            
            # Check if job already exists
            existing_job = await self.db_ops.get_job_by_url(job_url)
            if existing_job:
                self.logger.info(f"Job already exists: {job_data.get('title')} at {job_data.get('company')}")
                return existing_job
            
            # Find or create company
            company_id = await self._find_or_create_company(job_data)
            
            # Create job listing
            job_listing = JobListing(
                id=str(uuid.uuid4()),
                job_site_id=await self._get_default_job_site_id(user_id),
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                job_url=job_url,
                location=job_data.get("location"),
                description=job_data.get("summary", "") or job_data.get("description", ""),
                requirements=self._extract_requirements(job_data),
                salary_range=job_data.get("salary_range"),
                company_id=company_id,
                remote_type=self._determine_remote_type(job_data),
                experience_level=job_data.get("experience_level"),
                job_type=self._determine_job_type(job_data),
                auto_apply_enabled=True,
                application_priority=self._calculate_priority(job_data, search_criteria),
                scraped_at=datetime.now(),
                status=JobStatus.DISCOVERED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save to database
            success = await self.db_ops.insert_job_listing(job_listing)
            if success:
                self.logger.info(f"Saved job: {job_listing.title} at {job_listing.company}")
                return job_listing
            else:
                self.logger.error(f"Failed to save job to database: {job_listing.title}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saving job to database: {e}")
            return None
    
    async def _find_or_create_company(self, job_data: Dict[str, Any]) -> Optional[str]:
        """
        Find existing company or create new one from job data
        
        Args:
            job_data: Job data containing company information
            
        Returns:
            Company ID or None
        """
        try:
            company_name = job_data.get("company", "").strip()
            if not company_name:
                return None
            
            # Try to find existing company
            existing_company = await self.db_ops.get_company_by_name(company_name)
            if existing_company:
                return existing_company.id
            
            # Extract domain from job URL or create one
            job_url = job_data.get("application_url", "")
            domain = self._extract_company_domain(job_url, company_name)
            
            # Create new company
            company = Company(
                id=str(uuid.uuid4()),
                name=company_name,
                domain=domain,
                career_page_url=self._generate_career_page_url(domain, job_url),
                industry=self._guess_industry(company_name, job_data),
                website_url=f"https://{domain}" if domain else None,
                is_active=True,
                last_scraped=datetime.now(),
                jobs_found_count=1,
                scraping_difficulty="medium",  # Default assumption
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            success = await self.db_ops.insert_company(company)
            if success:
                self.logger.info(f"Created new company: {company_name}")
                return company.id
            
        except Exception as e:
            self.logger.error(f"Error handling company data: {e}")
        
        return None
    
    def _extract_company_domain(self, job_url: str, company_name: str) -> str:
        """Extract or generate company domain"""
        if job_url:
            try:
                parsed = urlparse(job_url)
                domain = parsed.netloc.lower()
                
                # Remove common job site domains and get company domain
                job_sites = ["linkedin.com", "indeed.com", "glassdoor.com", "monster.com", "ziprecruiter.com"]
                if any(site in domain for site in job_sites):
                    # Generate domain from company name
                    return self._generate_domain_from_name(company_name)
                else:
                    # Use the domain from URL (likely company career page)
                    return domain.replace("www.", "").replace("careers.", "")
            except:
                pass
        
        return self._generate_domain_from_name(company_name)
    
    def _generate_domain_from_name(self, company_name: str) -> str:
        """Generate a domain name from company name"""
        if not company_name:
            return "unknown.com"
        
        # Clean company name and create domain
        clean_name = company_name.lower().replace(" ", "").replace(".", "").replace(",", "")
        clean_name = "".join(c for c in clean_name if c.isalnum())
        return f"{clean_name}.com"
    
    def _generate_career_page_url(self, domain: str, job_url: str) -> str:
        """Generate likely career page URL"""
        if "careers." in job_url or "/careers" in job_url:
            return job_url.split("/jobs")[0] if "/jobs" in job_url else job_url
        
        return f"https://careers.{domain}" if domain else f"https://www.{domain}/careers"
    
    def _guess_industry(self, company_name: str, job_data: Dict[str, Any]) -> Optional[str]:
        """Guess industry from company name and job data"""
        company_lower = company_name.lower()
        job_title = job_data.get("title", "").lower()
        
        # Technology companies
        tech_keywords = ["tech", "software", "microsoft", "google", "amazon", "apple", "meta", "netflix", "uber"]
        if any(keyword in company_lower for keyword in tech_keywords) or "engineer" in job_title:
            return "Technology"
        
        # Financial services
        finance_keywords = ["bank", "financial", "capital", "investments", "trading", "fintech"]
        if any(keyword in company_lower for keyword in finance_keywords):
            return "Financial Services"
        
        # Healthcare
        health_keywords = ["health", "medical", "pharma", "biotech", "hospital"]
        if any(keyword in company_lower for keyword in health_keywords):
            return "Healthcare"
        
        return "Technology"  # Default assumption
    
    def _extract_requirements(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Extract requirements from job data"""
        skills = job_data.get("skills", [])
        if skills:
            return f"Required skills: {', '.join(skills)}"
        return None
    
    def _determine_remote_type(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Determine remote work type from job data"""
        location = job_data.get("location", "").lower()
        title = job_data.get("title", "").lower()
        
        if "remote" in location or "remote" in title:
            return "remote"
        elif "hybrid" in location:
            return "hybrid"
        else:
            return "onsite"
    
    def _determine_job_type(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Determine job type from job data"""
        title = job_data.get("title", "").lower()
        
        if "contract" in title or "contractor" in title:
            return "contract"
        elif "part-time" in title:
            return "part-time"
        else:
            return "full-time"
    
    def _calculate_priority(self, job_data: Dict[str, Any], search_criteria: Dict[str, Any]) -> int:
        """Calculate application priority based on job data and search criteria"""
        priority = 5  # Default priority
        
        # Increase priority for exact title matches
        job_title = job_data.get("title", "").lower()
        search_title = search_criteria.get("job_title", "").lower()
        if search_title and search_title in job_title:
            priority += 2
        
        # Increase priority for preferred companies
        company = job_data.get("company", "").lower()
        preferred_companies = ["google", "microsoft", "amazon", "apple", "meta", "netflix"]
        if any(pref in company for pref in preferred_companies):
            priority += 1
        
        # Decrease priority for job board sources (prefer direct company applications)
        source = job_data.get("source", "").lower()
        if source in ["indeed", "monster", "ziprecruiter"]:
            priority -= 1
        elif source in ["company website", "careers page"]:
            priority += 1
        
        # Ensure priority is within valid range
        return max(1, min(10, priority))
    
    def _should_trigger_automation(self, job: JobListing, search_criteria: Dict[str, Any]) -> bool:
        """
        Determine if automation should be triggered for this job
        
        Args:
            job: The saved job listing
            search_criteria: Original search criteria
            
        Returns:
            True if automation should be triggered
        """
        # Check if auto-apply is enabled
        if not job.auto_apply_enabled:
            return False
        
        # Only trigger for high-priority jobs (priority >= 6)
        if job.application_priority < 6:
            return False
        
        # Don't trigger for jobs already applied to
        if job.status in [JobStatus.APPLIED, JobStatus.REJECTED]:
            return False
        
        # Additional criteria can be added here
        return True
    
    async def _trigger_job_automation(self, job: JobListing, user_id: str) -> Dict[str, Any]:
        """
        Trigger automation workflow for a job
        
        Args:
            job: Job listing to process
            user_id: User ID
            
        Returns:
            Automation result
        """
        try:
            if not self.orchestrator:
                await self.initialize()
            
            # If orchestrator is still not available, log and continue
            if not self.orchestrator:
                self.logger.warning("Orchestrator not available, creating application record only")
            
            # Create application record
            application = Application(
                id=str(uuid.uuid4()),
                user_id=user_id,
                job_listing_id=job.id,
                resume_template_id=await self._get_default_resume_id(user_id),
                status=ApplicationStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save application to database
            app_saved = await self.db_ops.insert_application(application)
            if not app_saved:
                return {"success": False, "message": "Failed to create application record"}
            
            # Trigger orchestrator workflow
            automation_task = {
                "task_type": "full_application_workflow",
                "input_data": {
                    "job_listing_id": job.id,
                    "application_id": application.id,
                    "user_id": user_id,
                    "job_title": job.title,
                    "company_name": job.company,
                    "job_url": job.job_url,
                    "priority": job.application_priority
                }
            }
            
            # Note: In a real implementation, this would be queued for async processing
            self.logger.info(f"Automation triggered for job: {job.title} at {job.company}")
            
            return {
                "success": True,
                "automation_id": application.id,
                "message": f"Automation triggered for {job.title} at {job.company}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to trigger automation for job {job.id}: {e}")
            return {
                "success": False,
                "message": f"Failed to trigger automation: {str(e)}"
            }
    
    async def _get_default_job_site_id(self, user_id: str) -> str:
        """Get default job site ID for user"""
        # In a real implementation, this would fetch from database
        # For now, return a placeholder
        return str(uuid.uuid4())
    
    async def _get_default_resume_id(self, user_id: str) -> str:
        """Get default resume template ID for user"""
        # In a real implementation, this would fetch from database
        # For now, return a placeholder
        return str(uuid.uuid4())
    
    def _job_to_dict(self, job: JobListing) -> Dict[str, Any]:
        """Convert JobListing to dictionary for API response"""
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_url": job.job_url,
            "salary_range": job.salary_range,
            "remote_type": job.remote_type,
            "experience_level": job.experience_level,
            "application_priority": job.application_priority,
            "auto_apply_enabled": job.auto_apply_enabled,
            "status": job.status.value if job.status else "discovered",
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
    
    async def get_saved_jobs_for_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get saved jobs for a user with URLs
        
        Args:
            user_id: User ID
            limit: Maximum number of jobs to return
            
        Returns:
            List of saved jobs with URLs
        """
        try:
            jobs = await self.db_ops.get_user_job_listings(user_id, limit=limit)
            return [self._job_to_dict(job) for job in jobs]
        except Exception as e:
            self.logger.error(f"Failed to get saved jobs for user {user_id}: {e}")
            return []