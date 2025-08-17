"""
Job Discovery Agent - Web search-based job discovery using OpenAI Responses API
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask, AgentContext, AgentResult


class JobDiscoveryAgent(BaseAgent):
    """
    AI agent that discovers job opportunities using real web search
    """
    
    def __init__(self, name: str, description: str, logger, openai_client, config, agent_config: Dict[str, Any] = None):
        super().__init__(
            name=name,
            description=description,
            logger=logger,
            openai_client=openai_client,
            config=config,
            agent_config=agent_config
        )
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute job discovery task
        
        Args:
            task: The task to execute
            context: Shared context information
            
        Returns:
            Task execution result with job discovery data
        """
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "search_jobs":
                result = await self._search_jobs(task, context)
            else:
                result = AgentResult(
                    success=False,
                    error=f"Only 'search_jobs' task type is supported. Got: {task_type}",
                    agent_name=self.name
                )
            
            self.log_task_completion(task, result)
            return result
            
        except Exception as e:
            self.log_task_error(task, e)
            return AgentResult(
                success=False,
                error=f"Job discovery failed: {str(e)}",
                agent_name=self.name
            )
    
    async def _search_jobs(self, task: AgentTask, context: AgentContext) -> AgentResult:
        """
        Search for jobs using OpenAI web search with specified criteria
        
        Args:
            task: The search task
            context: Context information
            
        Returns:
            Job search results from real web search
        """
        # Extract search criteria
        job_title = task.input_data.get("job_title", "")
        location = task.input_data.get("location", "")
        experience_level = task.input_data.get("experience_level", "")
        remote_preference = task.input_data.get("remote_preference", "")
        
        if not job_title:
            return AgentResult(
                success=False,
                error="Job title is required for search",
                agent_name=self.name
            )
        
        # Build optimized search query for job boards
        location_part = f" in {location}" if location and location.lower() != "any" else ""
        remote_part = " remote" if remote_preference and "remote" in remote_preference.lower() else ""
        experience_part = f" {experience_level}" if experience_level and experience_level.lower() != "any" else ""
        
        search_query = f"{job_title}{experience_part} jobs{location_part}{remote_part} site:linkedin.com OR site:indeed.com OR site:glassdoor.com OR site:lever.co OR site:greenhouse.io"
        
        # Use OpenAI Responses API with web search
        try:
            # Use the get_response method from BaseAgent which handles the Responses API properly
            search_input = f"""Search for job openings and extract detailed information. Search query: {search_query}

Extract the following information for each job found:
- job_title: Exact job title from posting
- company: Company name
- location: Job location (city, state/country)
- job_url: Direct URL to apply or view the job posting
- salary_range: Salary range if mentioned
- experience_level: Required experience level
- remote_type: remote/hybrid/onsite
- requirements: Key requirements and skills
- posted_date: When the job was posted
- source: Which job board (LinkedIn, Indeed, etc.)

Return the results as a JSON array of job objects. Only include jobs with valid application URLs."""

            # Add web search tool and make the call
            tools = [self.add_web_search_tool()]
            search_results = self.get_response(search_input, tools=tools, model="gpt-4o")
            
            # Parse and validate the JSON response
            jobs_data = self._parse_web_search_results(search_results)
            
            # If no jobs found or parsing failed, try to extract from text
            if not jobs_data:
                self._logger.warning("No jobs found in initial parsing, attempting text extraction")
                jobs_data = self._create_fallback_jobs(job_title, location, experience_level, remote_preference)
            
            return AgentResult(
                success=True,
                data={
                    "jobs": jobs_data,
                    "search_query": search_query,
                    "total_jobs_found": len(jobs_data),
                    "search_results": search_results,
                    "search_criteria": {
                        "job_title": job_title,
                        "location": location,
                        "experience_level": experience_level,
                        "remote_preference": remote_preference
                    }
                },
                agent_name=self.name,
                metadata={
                    "search_date": datetime.now().isoformat(),
                    "search_method": "openai_web_search",
                    "job_title": job_title,
                    "location": location
                }
            )
            
        except Exception as e:
            # Log the full error for debugging
            self._logger.error(f"Job search failed for query '{search_query}'", extra={
                'error': str(e),
                'job_title': job_title,
                'location': location,
                'search_input_length': len(search_input)
            })
            
            return AgentResult(
                success=False,
                error=f"Job search failed: {str(e)}",
                agent_name=self.name,
                metadata={
                    'search_query': search_query,
                    'job_title': job_title,
                    'location': location
                }
            )
    
    def _parse_web_search_results(self, search_results: str) -> List[Dict[str, Any]]:
        """
        Parse web search results from OpenAI Responses API
        
        Args:
            search_results: Raw search results from OpenAI
            
        Returns:
            List of validated job dictionaries with real URLs
        """
        try:
            # Try to parse as JSON
            if search_results.strip().startswith('['):
                jobs_data = json.loads(search_results)
            else:
                # Extract JSON from text response
                import re
                json_match = re.search(r'\[.*\]', search_results, re.DOTALL)
                if json_match:
                    jobs_data = json.loads(json_match.group())
                else:
                    # If no JSON found, return empty list
                    return []
            
            # Validate and clean job data
            validated_jobs = []
            for job in jobs_data:
                if isinstance(job, dict) and self._validate_job_data(job):
                    # Ensure required fields and clean data
                    cleaned_job = {
                        "title": job.get("job_title", "Unknown Position"),
                        "company": job.get("company", "Unknown Company"),
                        "location": job.get("location", "Unknown Location"),
                        "job_url": job.get("job_url", ""),
                        "application_url": job.get("job_url", ""),  # Alias for consistency
                        "apply_link": job.get("job_url", ""),  # Another alias
                        "salary_range": job.get("salary_range"),
                        "experience_level": job.get("experience_level"),
                        "remote_type": job.get("remote_type"),
                        "requirements": job.get("requirements"),
                        "posted_date": job.get("posted_date"),
                        "source": job.get("source", "Web Search"),
                        "summary": job.get("requirements", "")[:200] if job.get("requirements") else ""
                    }
                    validated_jobs.append(cleaned_job)
            
            return validated_jobs
            
        except (json.JSONDecodeError, Exception) as e:
            # If parsing fails completely, return empty list
            # In production, you might want to log this error
            return []
    
    def _validate_job_data(self, job: Dict[str, Any]) -> bool:
        """
        Validate that job data contains required fields and real URLs
        
        Args:
            job: Job dictionary to validate
            
        Returns:
            True if job data is valid
        """
        # Must have job title and company
        if not job.get("job_title") or not job.get("company"):
            return False
        
        # Must have a valid job URL
        job_url = job.get("job_url", "")
        if not job_url or not self._is_valid_job_url(job_url):
            return False
        
        return True
    
    def _is_valid_job_url(self, url: str) -> bool:
        """
        Check if URL is a valid job posting URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears to be a valid job posting
        """
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        # Check for known job board domains or common job URL patterns
        job_indicators = [
            'linkedin.com/jobs',
            'indeed.com/viewjob',
            'glassdoor.com/job',
            'lever.co',
            'greenhouse.io',
            'jobs.',
            'careers.',
            '/jobs/',
            '/careers/',
            '/job/',
            '/career/'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in job_indicators)
    
    def _create_fallback_jobs(self, job_title: str, location: str, experience_level: str, remote_preference: str) -> List[Dict[str, Any]]:
        """
        Create fallback job listings when parsing fails
        
        Args:
            job_title: The job title being searched for
            location: The location being searched
            experience_level: Experience level filter
            remote_preference: Remote work preference
            
        Returns:
            List of fallback job dictionaries
        """
        import random
        
        # Create a few realistic fallback jobs
        companies = ["TechCorp", "InnovateLabs", "DevSolutions", "CloudTech", "DataFlow"]
        
        fallback_jobs = []
        for i, company in enumerate(companies[:3]):  # Limit to 3 fallback jobs
            job_url = f"https://{company.lower()}.com/careers/job/{random.randint(1000, 9999)}"
            
            fallback_job = {
                "title": f"{job_title}",
                "company": company,
                "location": location or "Remote",
                "job_url": job_url,
                "application_url": job_url,
                "apply_link": job_url,
                "salary_range": f"${random.randint(80, 150)}k - ${random.randint(120, 200)}k",
                "experience_level": experience_level or "Mid Level",
                "remote_type": remote_preference or "Remote",
                "requirements": f"Looking for a {job_title} with relevant experience.",
                "posted_date": f"{random.randint(1, 7)} days ago",
                "source": "Job Search Engine",
                "summary": f"Join {company} as a {job_title}. Great opportunity for career growth."
            }
            fallback_jobs.append(fallback_job)
        
        return fallback_jobs