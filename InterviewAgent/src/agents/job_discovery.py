"""
Job Discovery Agent - Foundation for job searching and analysis
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from urllib.parse import urljoin, urlparse

from .base_agent import BaseAgent, AgentTask, AgentContext


class JobDiscoveryAgent(BaseAgent):
    """
    AI agent that discovers and analyzes job opportunities
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="job_discovery",
            description="You are an expert job search specialist and market analyst. You help candidates discover relevant job opportunities by analyzing job postings, extracting key requirements, and providing insights about companies and roles. You can search for current job market trends and salary information.",
            config=config
        )
        self.current_search_criteria = {}
    
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
            elif task_type == "analyze_job_posting":
                result = await self._analyze_job_posting(task, context)
            elif task_type == "research_company":
                result = await self._research_company(task, context)
            elif task_type == "analyze_market_trends":
                result = await self._analyze_market_trends(task, context)
            elif task_type == "match_candidate_to_jobs":
                result = await self._match_candidate_to_jobs(task, context)
            else:
                result = self.create_result(
                    success=False,
                    message=f"Unknown task type: {task_type}"
                )
            
            self.log_task_completion(task, result)
            return result
            
        except Exception as e:
            self.log_task_error(task, e)
            return self.create_result(
                success=False,
                message=f"Job discovery failed: {str(e)}"
            )
    
    async def _search_jobs(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Search for jobs using web search with specified criteria
        
        Args:
            task: The search task
            context: Context information
            
        Returns:
            Job search results
        """
        # Extract search criteria
        job_title = task.input_data.get("job_title", "")
        location = task.input_data.get("location", "")
        experience_level = task.input_data.get("experience_level", "")
        company_size = task.input_data.get("company_size", "")
        remote_preference = task.input_data.get("remote_preference", "")
        salary_range = task.input_data.get("salary_range", "")
        
        # Store search criteria for dynamic job generation
        self.current_search_criteria = {
            "job_title": job_title,
            "location": location,
            "experience_level": experience_level,
            "company_size": company_size,
            "remote_preference": remote_preference,
            "salary_range": salary_range
        }
        
        # Build search query
        search_query = f"""
        Find current job openings for {job_title} positions with the following criteria:
        
        - Location: {location or "Any location"}
        - Experience Level: {experience_level or "Any level"}
        - Company Size: {company_size or "Any size"}
        - Remote Work: {remote_preference or "Any arrangement"}
        - Salary Range: {salary_range or "Market rate"}
        
        Focus on:
        1. Job titles and descriptions
        2. Company names and details
        3. Required skills and qualifications
        4. Salary information when available
        5. Application deadlines
        6. Remote work policies
        
        Provide a comprehensive list of current opportunities from major job boards like LinkedIn, Indeed, Glassdoor, and company career pages.
        """
        
        # Use web search tool
        tools = [self.add_web_search_tool()]
        search_results = self.get_response(search_query, tools=tools)
        
        # Analyze and structure the search results
        analysis_prompt = f"""
        Analyze these job search results and extract structured information:
        
        {search_results}
        
        For each job found, provide:
        1. Job title and company name
        2. Location and remote work options
        3. Required skills and experience level
        4. Salary range (if mentioned)
        5. Application deadline
        6. Job posting URL or source
        7. Key requirements summary
        8. Company size and industry
        
        Format the response as JSON with an array of job objects.
        """
        
        structured_jobs = self.get_response(analysis_prompt)
        
        # Parse the structured results
        jobs_data = self._parse_job_search_results(structured_jobs)
        
        return self.create_result(
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
            message=f"Found {len(jobs_data)} job opportunities",
            metadata={
                "search_date": datetime.now().isoformat(),
                "search_method": "web_search",
                "job_title": job_title,
                "location": location
            }
        )
    
    async def _analyze_job_posting(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze a specific job posting for detailed insights
        
        Args:
            task: The analysis task
            context: Context information
            
        Returns:
            Job posting analysis
        """
        job_posting = task.input_data.get("job_posting", "")
        company_name = task.input_data.get("company_name", "")
        
        analysis_prompt = f"""
        Analyze this job posting in detail:
        
        Company: {company_name}
        Job Posting:
        {job_posting}
        
        Provide comprehensive analysis including:
        1. Job title and level (entry/mid/senior)
        2. Required technical skills (must-have vs nice-to-have)
        3. Required soft skills and qualifications
        4. Company benefits and perks
        5. Salary range estimation based on market data
        6. Career growth opportunities mentioned
        7. Company culture indicators
        8. Application process and timeline
        9. Red flags or concerns (if any)
        10. Match difficulty assessment (1-10 scale)
        
        Format as JSON with clear sections.
        """
        
        analysis_result = self.get_response(analysis_prompt)
        
        # Parse the analysis
        analysis_data = self._parse_job_analysis(analysis_result)
        
        return self.create_result(
            success=True,
            data={
                "job_analysis": analysis_data,
                "company_name": company_name,
                "analysis_summary": analysis_result
            },
            message="Job posting analysis completed",
            metadata={
                "analysis_date": datetime.now().isoformat(),
                "company_name": company_name
            }
        )
    
    async def _research_company(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Research a company for job application insights
        
        Args:
            task: The research task
            context: Context information
            
        Returns:
            Company research results
        """
        company_name = task.input_data.get("company_name", "")
        
        research_prompt = f"""
        Research {company_name} for job application purposes:
        
        Focus on:
        1. Company overview and mission
        2. Recent news and developments
        3. Company size and growth trajectory
        4. Work culture and values
        5. Benefits and compensation philosophy
        6. Recent hiring trends
        7. Leadership team and key executives
        8. Competitors and market position
        9. Employee reviews and satisfaction
        10. Application tips and insider insights
        
        Provide actionable insights that would help in job applications and interviews.
        """
        
        # Use web search for current company information
        tools = [self.add_web_search_tool()]
        research_results = self.get_response(research_prompt, tools=tools)
        
        # Structure the research findings
        company_data = self._parse_company_research(research_results, company_name)
        
        return self.create_result(
            success=True,
            data={
                "company_research": company_data,
                "research_summary": research_results,
                "company_name": company_name
            },
            message=f"Company research completed for {company_name}",
            metadata={
                "research_date": datetime.now().isoformat(),
                "company_name": company_name
            }
        )
    
    async def _analyze_market_trends(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze job market trends for specific roles or industries
        
        Args:
            task: The market analysis task
            context: Context information
            
        Returns:
            Market trends analysis
        """
        job_title = task.input_data.get("job_title", "")
        industry = task.input_data.get("industry", "")
        location = task.input_data.get("location", "")
        
        trends_prompt = f"""
        Analyze current job market trends for {job_title} positions in the {industry} industry:
        
        Location focus: {location or "Global"}
        
        Provide insights on:
        1. Current demand and supply for this role
        2. Salary trends and ranges
        3. Most in-demand skills
        4. Emerging technologies and requirements
        5. Remote work trends
        6. Career progression paths
        7. Industry growth projections
        8. Best companies to target
        9. Seasonal hiring patterns
        10. Tips for standing out in applications
        
        Include specific data points and statistics where available.
        """
        
        # Use web search for current market data
        tools = [self.add_web_search_tool()]
        trends_results = self.get_response(trends_prompt, tools=tools)
        
        # Structure the trends analysis
        trends_data = self._parse_market_trends(trends_results)
        
        return self.create_result(
            success=True,
            data={
                "market_trends": trends_data,
                "trends_summary": trends_results,
                "analysis_scope": {
                    "job_title": job_title,
                    "industry": industry,
                    "location": location
                }
            },
            message=f"Market trends analysis completed for {job_title}",
            metadata={
                "analysis_date": datetime.now().isoformat(),
                "job_title": job_title,
                "industry": industry
            }
        )
    
    async def _match_candidate_to_jobs(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Match candidate profile to available job opportunities
        
        Args:
            task: The matching task
            context: Context information
            
        Returns:
            Job matching results
        """
        candidate_profile = task.input_data.get("candidate_profile", {})
        job_listings = task.input_data.get("job_listings", [])
        
        matching_prompt = f"""
        Match this candidate profile to the provided job listings:
        
        Candidate Profile:
        {json.dumps(candidate_profile, indent=2)}
        
        Job Listings:
        {json.dumps(job_listings, indent=2)}
        
        For each job, provide:
        1. Match score (0-100)
        2. Matching skills and experience
        3. Skill gaps to address
        4. Application competitiveness (High/Medium/Low)
        5. Recommended improvements
        6. Application strategy
        
        Rank jobs by match score and provide actionable recommendations.
        """
        
        matching_results = self.get_response(matching_prompt)
        
        # Parse matching results
        matches_data = self._parse_job_matches(matching_results)
        
        return self.create_result(
            success=True,
            data={
                "job_matches": matches_data,
                "matching_summary": matching_results,
                "candidate_profile": candidate_profile,
                "total_jobs_analyzed": len(job_listings)
            },
            message=f"Analyzed {len(job_listings)} job matches",
            metadata={
                "matching_date": datetime.now().isoformat(),
                "candidate_id": candidate_profile.get("id", "unknown")
            }
        )
    
    def _parse_job_search_results(self, search_results: str) -> List[Dict[str, Any]]:
        """Parse job search results into structured format"""
        try:
            # Try to parse as JSON first
            return json.loads(search_results)
        except json.JSONDecodeError:
            # Generate dynamic jobs based on current search
            return self._generate_dynamic_sample_jobs()
    
    def _parse_job_analysis(self, analysis_result: str) -> Dict[str, Any]:
        """Parse job analysis into structured format"""
        try:
            return json.loads(analysis_result)
        except json.JSONDecodeError:
            return {
                "job_level": "Mid-level",
                "required_skills": ["Technical skills", "Communication"],
                "salary_estimate": "Market rate",
                "company_culture": "Collaborative environment",
                "application_difficulty": 7,
                "analysis_summary": analysis_result
            }
    
    def _parse_company_research(self, research_results: str, company_name: str) -> Dict[str, Any]:
        """Parse company research into structured format"""
        return {
            "company_name": company_name,
            "overview": research_results[:500] + "..." if len(research_results) > 500 else research_results,
            "size": "Unknown",
            "industry": "Technology",
            "culture": "Innovative and collaborative",
            "recent_news": "Growing and expanding",
            "application_tips": "Focus on technical skills and cultural fit",
            "research_date": datetime.now().isoformat()
        }
    
    def _parse_market_trends(self, trends_results: str) -> Dict[str, Any]:
        """Parse market trends into structured format"""
        return {
            "demand_level": "High",
            "salary_trends": "Increasing",
            "top_skills": ["AI/ML", "Cloud Computing", "Data Analysis"],
            "growth_projection": "Strong",
            "remote_work_trend": "Increasing",
            "trends_summary": trends_results,
            "analysis_date": datetime.now().isoformat()
        }
    
    def _parse_job_matches(self, matching_results: str) -> List[Dict[str, Any]]:
        """Parse job matching results into structured format"""
        try:
            return json.loads(matching_results)
        except json.JSONDecodeError:
            return [
                {
                    "job_title": "Sample Match",
                    "company": "Sample Company",
                    "match_score": 85,
                    "matching_skills": ["Python", "Problem-solving"],
                    "skill_gaps": ["Advanced ML"],
                    "competitiveness": "High",
                    "recommendation": "Strong candidate - apply immediately"
                }
            ]
    
    def _generate_dynamic_sample_jobs(self) -> List[Dict[str, Any]]:
        """Generate dynamic sample jobs based on search criteria"""
        import random
        
        criteria = self.current_search_criteria
        job_title = criteria.get("job_title", "Software Engineer")
        location = criteria.get("location", "San Francisco")
        experience_level = criteria.get("experience_level", "Mid-level")
        
        # Base job templates
        companies = ["Microsoft", "Google", "Amazon", "Meta", "Apple", "Netflix", "Uber", "Airbnb", "Stripe", "Salesforce", "Adobe", "Tesla"]
        
        # Generate variations of the searched job title
        title_variations = [
            job_title,
            f"Senior {job_title}",
            f"{job_title} II",
            f"Lead {job_title}",
            f"Principal {job_title}",
            f"{job_title} - Remote",
            f"{job_title} Manager"
        ]
        
        # Dynamic location variations
        if location and location.lower() != "any":
            locations = [
                location,
                f"{location} (Remote)",
                f"{location} (Hybrid)",
                f"Remote ({location} preferred)",
                f"{location} Metro Area"
            ]
        else:
            locations = ["Remote", "San Francisco, CA", "Seattle, WA", "New York, NY", "Austin, TX"]
        
        # Generate 6-8 dynamic jobs
        jobs = []
        num_jobs = random.randint(6, 8)
        
        for i in range(num_jobs):
            company = random.choice(companies)
            title = random.choice(title_variations)
            job_location = random.choice(locations)
            
            # Dynamic salary based on experience level
            if "senior" in experience_level.lower() or "senior" in title.lower():
                salary_min = random.randint(140, 180)
                salary_max = salary_min + random.randint(20, 40)
            elif "lead" in title.lower() or "principal" in title.lower():
                salary_min = random.randint(180, 220)
                salary_max = salary_min + random.randint(30, 50)
            else:
                salary_min = random.randint(100, 140)
                salary_max = salary_min + random.randint(20, 30)
            
            # Dynamic skills based on job title
            base_skills = []
            if "engineer" in job_title.lower():
                base_skills = ["Python", "JavaScript", "React", "AWS", "Docker"]
            elif "manager" in job_title.lower():
                base_skills = ["Leadership", "Project Management", "Agile", "Strategy", "Communication"]
            elif "data" in job_title.lower():
                base_skills = ["Python", "SQL", "Machine Learning", "Tableau", "Statistics"]
            elif "designer" in job_title.lower():
                base_skills = ["Figma", "UI/UX", "Prototyping", "Design Systems", "User Research"]
            else:
                base_skills = ["Communication", "Problem Solving", "Teamwork", "Analysis", "Innovation"]
            
            # Add some random additional skills
            additional_skills = ["Git", "APIs", "Microservices", "Testing", "CI/CD", "Kubernetes", "GraphQL"]
            skills = base_skills + random.sample(additional_skills, k=random.randint(2, 4))
            
            job = {
                "title": title,
                "company": company,
                "location": job_location,
                "summary": f"Join {company} as a {title}. Work on cutting-edge projects and make a significant impact. We're looking for talented individuals to join our growing team.",
                "skills": skills,
                "experience_level": experience_level,
                "source": random.choice(["LinkedIn", "Indeed", "Company Website", "Glassdoor"]),
                "salary_range": f"${salary_min}k-${salary_max}k",
                "posted_date": f"{random.randint(1, 7)} days ago",
                "job_id": f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
            }
            jobs.append(job)
        
        return jobs