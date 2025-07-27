"""
Database operations for InterviewAgent
"""

from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_supabase_client
from database.models import (
    User, ResumeTemplate, JobSite, JobListing, Application, Schedule, AgentLog,
    AgentResult, CoverLetter, OptimizedResume, JobSearch, Company,
    dict_to_model, model_to_dict,
    ApplicationStatus, JobStatus, AgentStatus
)
import supabase  # Add this if not already present

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Database operations manager"""
    
    def __init__(self):
        try:
            self.client = get_supabase_client()
        except Exception as e:
            logger.warning(f"Failed to connect to Supabase, using mock mode: {str(e)}")
            self.client = None
    
    # User operations
    def get_or_create_user(self, email: str, full_name: str = None) -> User:
        """Get existing user or create new one (for single-user MVP)"""
        
        # Mock user for testing
        if self.client is None:
            return User(
                id=str(uuid.uuid4()),
                email=email,
                full_name=full_name or "Test User",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        try:
            # Try to get existing user
            result = self.client.table('users').select('*').eq('email', email).execute()
            
            if result.data:
                return dict_to_model(result.data[0], User)
            
            # Create new user
            user_data = {
                'id': str(uuid.uuid4()),
                'email': email,
                'full_name': full_name,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.client.table('users').insert(user_data).execute()
            return dict_to_model(result.data[0], User)
            
        except supabase.PostgrestAPIError as e:
            logger.error(f"Supabase API error in get_or_create_user: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_or_create_user: {str(e)}")
            raise
    
    # Resume operations
    def create_resume_template(self, user_id: str, name: str, content: str, 
                             file_url: str = None, is_default: bool = False) -> ResumeTemplate:
        """Create new resume template"""
        try:
            resume_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'name': name,
                'content': content,
                'file_url': file_url,
                'is_default': is_default,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.client.table('resume_templates').insert(resume_data).execute()
            return dict_to_model(result.data[0], ResumeTemplate)
            
        except Exception as e:
            logger.error(f"Failed to create resume template: {str(e)}")
            raise
    
    def get_resume_templates(self, user_id: str) -> List[ResumeTemplate]:
        """Get all resume templates for user"""
        try:
            result = self.client.table('resume_templates').select('*').eq('user_id', user_id).execute()
            return [dict_to_model(item, ResumeTemplate) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get resume templates: {str(e)}")
            return []
    
    def update_resume_template(self, resume_id: str, **kwargs) -> bool:
        """Update resume template"""
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            result = self.client.table('resume_templates').update(kwargs).eq('id', resume_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to update resume template: {str(e)}")
            return False
    
    def delete_resume_template(self, resume_id: str) -> bool:
        """Delete resume template"""
        try:
            result = self.client.table('resume_templates').delete().eq('id', resume_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to delete resume template: {str(e)}")
            return False
    
    # Job site operations
    def create_job_site(self, user_id: str, name: str, url: str, 
                       credentials_encrypted: str = None) -> JobSite:
        """Create new job site configuration"""
        try:
            site_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'name': name,
                'url': url,
                'is_enabled': True,
                'credentials_encrypted': credentials_encrypted,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.client.table('job_sites').insert(site_data).execute()
            return dict_to_model(result.data[0], JobSite)
            
        except Exception as e:
            logger.error(f"Failed to create job site: {str(e)}")
            raise
    
    def get_job_sites(self, user_id: str, enabled_only: bool = False) -> List[JobSite]:
        """Get job sites for user"""
        
        # Mock job sites for testing
        if self.client is None:
            mock_sites = []
            sites_data = [
                ("LinkedIn", "https://linkedin.com/jobs"),
                ("Indeed", "https://indeed.com"),
                ("Glassdoor", "https://glassdoor.com")
            ]
            
            for name, url in sites_data:
                mock_sites.append(JobSite(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=name,
                    url=url,
                    is_enabled=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
            return mock_sites
        
        try:
            query = self.client.table('job_sites').select('*').eq('user_id', user_id)
            if enabled_only:
                query = query.eq('is_enabled', True)
            
            result = query.execute()
            return [dict_to_model(item, JobSite) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get job sites: {str(e)}")
            return []
    
    def update_job_site(self, site_id: str, **kwargs) -> bool:
        """Update job site configuration"""
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            result = self.client.table('job_sites').update(kwargs).eq('id', site_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to update job site: {str(e)}")
            return False
    
    # Job listing operations
    def create_job_listing(self, job_site_id: str, title: str, company: str, 
                          job_url: str, **kwargs) -> JobListing:
        """Create new job listing"""
        try:
            job_data = {
                'id': str(uuid.uuid4()),
                'job_site_id': job_site_id,
                'title': title,
                'company': company,
                'job_url': job_url,
                'status': JobStatus.DISCOVERED.value,
                'scraped_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('job_listings').insert(job_data).execute()
            return dict_to_model(result.data[0], JobListing)
            
        except Exception as e:
            logger.error(f"Failed to create job listing: {str(e)}")
            raise
    
    def get_job_listings(self, job_site_id: str = None, status: JobStatus = None, 
                        limit: int = None) -> List[JobListing]:
        """Get job listings with optional filtering"""
        try:
            query = self.client.table('job_listings').select('*')
            
            if job_site_id:
                query = query.eq('job_site_id', job_site_id)
            if status:
                query = query.eq('status', status.value)
            if limit:
                query = query.limit(limit)
                
            query = query.order('created_at', desc=True)
            result = query.execute()
            return [dict_to_model(item, JobListing) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get job listings: {str(e)}")
            return []
    
    def update_job_listing(self, job_id: str, **kwargs) -> bool:
        """Update job listing"""
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            result = self.client.table('job_listings').update(kwargs).eq('id', job_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to update job listing: {str(e)}")
            return False
    
    # Application operations
    def create_application(self, user_id: str, job_listing_id: str, 
                          resume_template_id: str, **kwargs) -> Application:
        """Create new application"""
        try:
            app_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'job_listing_id': job_listing_id,
                'resume_template_id': resume_template_id,
                'status': ApplicationStatus.PENDING.value,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('applications').insert(app_data).execute()
            return dict_to_model(result.data[0], Application)
            
        except Exception as e:
            logger.error(f"Failed to create application: {str(e)}")
            raise
    
    def get_applications(self, user_id: str, status: ApplicationStatus = None,
                        limit: int = None) -> List[Application]:
        """Get applications for user"""
        try:
            query = self.client.table('applications').select('*').eq('user_id', user_id)
            
            if status:
                query = query.eq('status', status.value)
            if limit:
                query = query.limit(limit)
                
            query = query.order('created_at', desc=True)
            result = query.execute()
            return [dict_to_model(item, Application) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get applications: {str(e)}")
            return []
    
    def update_application(self, app_id: str, **kwargs) -> bool:
        """Update application"""
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            result = self.client.table('applications').update(kwargs).eq('id', app_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to update application: {str(e)}")
            return False
    
    # Agent log operations
    def create_agent_log(self, user_id: str, agent_type: str, action: str, 
                        status: AgentStatus = AgentStatus.STARTED, **kwargs) -> AgentLog:
        """Create agent activity log"""
        try:
            log_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'agent_type': agent_type,
                'action': action,
                'status': status.value,
                'created_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('agent_logs').insert(log_data).execute()
            return dict_to_model(result.data[0], AgentLog)
            
        except Exception as e:
            logger.error(f"Failed to create agent log: {str(e)}")
            raise
    
    def get_agent_logs(self, user_id: str = None, agent_type: str = None,
                      limit: int = 50) -> List[AgentLog]:
        """Get agent logs"""
        
        # Mock agent logs for testing
        if self.client is None:
            mock_logs = []
            for i in range(5):
                mock_logs.append(AgentLog(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    agent_type=f"test_agent_{i % 3}",
                    action=f"test_action_{i}",
                    status=AgentStatus.COMPLETED if i % 2 == 0 else AgentStatus.STARTED,
                    duration_ms=1000 + (i * 200),
                    created_at=datetime.now() - timedelta(hours=i)
                ))
            return mock_logs
        
        try:
            query = self.client.table('agent_logs').select('*')
            
            if user_id:
                query = query.eq('user_id', user_id)
            if agent_type:
                query = query.eq('agent_type', agent_type)
                
            query = query.order('created_at', desc=True).limit(limit)
            result = query.execute()
            return [dict_to_model(item, AgentLog) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get agent logs: {str(e)}")
            return []
    
    # Statistics and analytics
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        
        # Mock stats for testing
        if self.client is None:
            return {
                'resumes': 2,
                'jobs_discovered': 15,
                'applications_submitted': 8,
                'applications_successful': 3,
                'job_sites': 3
            }
        
        try:
            stats = {
                'resumes': 0,
                'jobs_discovered': 0,
                'applications_submitted': 0,
                'applications_successful': 0,
                'job_sites': 0
            }
            
            # Count resumes
            result = self.client.table('resume_templates').select('id').eq('user_id', user_id).execute()
            stats['resumes'] = len(result.data)
            
            # Count job sites
            result = self.client.table('job_sites').select('id').eq('user_id', user_id).execute()
            stats['job_sites'] = len(result.data)
            
            # Count applications
            result = self.client.table('applications').select('id', 'status').eq('user_id', user_id).execute()
            stats['applications_submitted'] = len(result.data)
            stats['applications_successful'] = len([app for app in result.data if app['status'] in ['submitted', 'confirmed']])
            
            # Count discovered jobs (from user's job sites)
            user_sites = self.get_job_sites(user_id)
            site_ids = [site.id for site in user_sites]
            
            if site_ids:
                result = self.client.table('job_listings').select('id').in_('job_site_id', site_ids).execute()
                stats['jobs_discovered'] = len(result.data)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {
                'resumes': 0,
                'jobs_discovered': 0,
                'applications_submitted': 0,
                'applications_successful': 0,
                'job_sites': 0
            }
    
    # Agent Result operations
    def create_agent_result(self, user_id: str, agent_type: str, task_type: str,
                           input_data: Dict[str, Any], output_data: Dict[str, Any],
                           success: bool, **kwargs) -> AgentResult:
        """Create agent result record"""
        if self.client is None:
            # Mock result for testing
            return AgentResult(
                id=str(uuid.uuid4()),
                user_id=user_id,
                agent_type=agent_type,
                task_type=task_type,
                input_data=input_data,
                output_data=output_data,
                success=success,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        try:
            result_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'agent_type': agent_type,
                'task_type': task_type,
                'input_data': json.dumps(input_data),
                'output_data': json.dumps(output_data),
                'success': success,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('agent_results').insert(result_data).execute()
            return dict_to_model(result.data[0], AgentResult)
            
        except Exception as e:
            logger.error(f"Failed to create agent result: {str(e)}")
            raise
    
    def get_agent_results(self, user_id: str, agent_type: str = None, 
                         task_type: str = None, limit: int = 50) -> List[AgentResult]:
        """Get agent results"""
        if self.client is None:
            return []
        
        try:
            query = self.client.table('agent_results').select('*').eq('user_id', user_id)
            
            if agent_type:
                query = query.eq('agent_type', agent_type)
            if task_type:
                query = query.eq('task_type', task_type)
            
            query = query.order('created_at', desc=True).limit(limit)
            result = query.execute()
            return [dict_to_model(item, AgentResult) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get agent results: {str(e)}")
            return []
    
    # Cover Letter operations
    def create_cover_letter(self, user_id: str, job_title: str, company_name: str,
                           cover_letter_content: str, **kwargs) -> CoverLetter:
        """Create cover letter record"""
        if self.client is None:
            # Mock cover letter for testing
            return CoverLetter(
                id=str(uuid.uuid4()),
                user_id=user_id,
                job_title=job_title,
                company_name=company_name,
                cover_letter_content=cover_letter_content,
                quality_score=kwargs.get('quality_score', 85),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        try:
            letter_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'job_title': job_title,
                'company_name': company_name,
                'cover_letter_content': cover_letter_content,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('cover_letters').insert(letter_data).execute()
            return dict_to_model(result.data[0], CoverLetter)
            
        except Exception as e:
            logger.error(f"Failed to create cover letter: {str(e)}")
            raise
    
    def get_cover_letters(self, user_id: str, limit: int = 50) -> List[CoverLetter]:
        """Get cover letters for user"""
        if self.client is None:
            return []
        
        try:
            query = self.client.table('cover_letters').select('*').eq('user_id', user_id)
            query = query.order('created_at', desc=True).limit(limit)
            result = query.execute()
            return [dict_to_model(item, CoverLetter) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get cover letters: {str(e)}")
            return []
    
    # Optimized Resume operations
    def create_optimized_resume(self, user_id: str, original_resume_id: str,
                               job_title: str, company_name: str,
                               optimized_content: str, **kwargs) -> OptimizedResume:
        """Create optimized resume record"""
        if self.client is None:
            # Mock optimized resume for testing
            return OptimizedResume(
                id=str(uuid.uuid4()),
                user_id=user_id,
                original_resume_id=original_resume_id,
                job_title=job_title,
                company_name=company_name,
                optimized_content=optimized_content,
                job_match_score=kwargs.get('job_match_score', 87),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        try:
            resume_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'original_resume_id': original_resume_id,
                'job_title': job_title,
                'company_name': company_name,
                'optimized_content': optimized_content,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('optimized_resumes').insert(resume_data).execute()
            return dict_to_model(result.data[0], OptimizedResume)
            
        except Exception as e:
            logger.error(f"Failed to create optimized resume: {str(e)}")
            raise
    
    def get_optimized_resumes(self, user_id: str, limit: int = 50) -> List[OptimizedResume]:
        """Get optimized resumes for user"""
        if self.client is None:
            return []
        
        try:
            query = self.client.table('optimized_resumes').select('*').eq('user_id', user_id)
            query = query.order('created_at', desc=True).limit(limit)
            result = query.execute()
            return [dict_to_model(item, OptimizedResume) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get optimized resumes: {str(e)}")
            return []
    
    # Job Search operations
    def create_job_search(self, user_id: str, search_query: str,
                         search_criteria: Dict[str, Any], jobs_found: int,
                         search_results: Dict[str, Any], **kwargs) -> JobSearch:
        """Create job search record"""
        if self.client is None:
            # Mock job search for testing
            return JobSearch(
                id=str(uuid.uuid4()),
                user_id=user_id,
                search_query=search_query,
                search_criteria=search_criteria,
                jobs_found=jobs_found,
                search_results=search_results,
                created_at=datetime.now()
            )
        
        try:
            search_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'search_query': search_query,
                'search_criteria': json.dumps(search_criteria),
                'jobs_found': jobs_found,
                'search_results': json.dumps(search_results),
                'created_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('job_searches').insert(search_data).execute()
            return dict_to_model(result.data[0], JobSearch)
            
        except Exception as e:
            logger.error(f"Failed to create job search: {str(e)}")
            raise
    
    def get_job_searches(self, user_id: str, limit: int = 50) -> List[JobSearch]:
        """Get job searches for user"""
        if self.client is None:
            return []
        
        try:
            query = self.client.table('job_searches').select('*').eq('user_id', user_id)
            query = query.order('created_at', desc=True).limit(limit)
            result = query.execute()
            return [dict_to_model(item, JobSearch) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get job searches: {str(e)}")
            return []
    
    # Company operations
    async def insert_company(self, company: Company) -> bool:
        """Insert company into database"""
        if self.client is None:
            logger.info(f"Mock mode: Would insert company {company.name}")
            return True
        
        try:
            company_data = model_to_dict(company)
            result = self.client.table('companies').insert(company_data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to insert company: {str(e)}")
            return False
    
    async def get_company_by_name(self, company_name: str) -> Optional[Company]:
        """Get company by name"""
        if self.client is None:
            return None
        
        try:
            result = self.client.table('companies').select('*').eq('name', company_name).execute()
            if result.data:
                return dict_to_model(result.data[0], Company)
            return None
        except Exception as e:
            logger.error(f"Failed to get company by name: {str(e)}")
            return None
    
    async def get_company_by_domain(self, domain: str) -> Optional[Company]:
        """Get company by domain"""
        if self.client is None:
            return None
        
        try:
            result = self.client.table('companies').select('*').eq('domain', domain).execute()
            if result.data:
                return dict_to_model(result.data[0], Company)
            return None
        except Exception as e:
            logger.error(f"Failed to get company by domain: {str(e)}")
            return None
    
    # Enhanced Job Listing operations
    async def insert_job_listing(self, job_listing: JobListing) -> bool:
        """Insert job listing into database"""
        if self.client is None:
            logger.info(f"Mock mode: Would insert job {job_listing.title} at {job_listing.company}")
            return True
        
        try:
            job_data = model_to_dict(job_listing)
            result = self.client.table('job_listings').insert(job_data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to insert job listing: {str(e)}")
            return False
    
    async def get_job_by_url(self, job_url: str) -> Optional[JobListing]:
        """Get job listing by URL"""
        if self.client is None:
            return None
        
        try:
            result = self.client.table('job_listings').select('*').eq('job_url', job_url).execute()
            if result.data:
                return dict_to_model(result.data[0], JobListing)
            return None
        except Exception as e:
            logger.error(f"Failed to get job by URL: {str(e)}")
            return None
    
    async def get_user_job_listings(self, user_id: str, limit: int = 50) -> List[JobListing]:
        """Get job listings for a user (through job sites)"""
        if self.client is None:
            # Return mock job listings
            mock_jobs = []
            for i in range(min(5, limit)):
                mock_jobs.append(JobListing(
                    id=str(uuid.uuid4()),
                    job_site_id=str(uuid.uuid4()),
                    title=f"Software Engineer {i+1}",
                    company=f"Company {i+1}",
                    job_url=f"https://example.com/job/{i+1}",
                    location="San Francisco, CA",
                    description="Exciting opportunity",
                    salary_range="$120k-$150k",
                    auto_apply_enabled=True,
                    application_priority=5,
                    status=JobStatus.DISCOVERED,
                    created_at=datetime.now()
                ))
            return mock_jobs
        
        try:
            # Get user's job sites first
            user_sites = self.get_job_sites(user_id)
            if not user_sites:
                return []
            
            site_ids = [site.id for site in user_sites]
            
            query = self.client.table('job_listings').select('*').in_('job_site_id', site_ids)
            query = query.order('created_at', desc=True).limit(limit)
            
            result = query.execute()
            return [dict_to_model(item, JobListing) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get user job listings: {str(e)}")
            return []
    
    # Enhanced Application operations
    async def insert_application(self, application: Application) -> bool:
        """Insert application into database"""
        if self.client is None:
            logger.info(f"Mock mode: Would insert application {application.id}")
            return True
        
        try:
            app_data = model_to_dict(application)
            result = self.client.table('applications').insert(app_data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to insert application: {str(e)}")
            return False

# Global database operations instance
_db_ops = None

def get_db_operations() -> DatabaseOperations:
    """Get database operations instance"""
    global _db_ops
    if _db_ops is None:
        _db_ops = DatabaseOperations()
    return _db_ops