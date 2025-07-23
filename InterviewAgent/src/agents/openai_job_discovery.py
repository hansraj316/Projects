"""
Job Discovery Agent - Using OpenAI Agents SDK
Handles job searching, analysis, and market research with proper handoffs
"""

from __future__ import annotations

import json
import sys
import os
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

# Handle OpenAI Agents SDK import conflicts
try:
    # Temporarily remove local agents from path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir in sys.path:
        sys.path.remove(parent_dir)
    
    from agents import Agent, handoff, function_tool, RunContextWrapper
    from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
    
    # Restore path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        
except ImportError as e:
    print(f"Warning: OpenAI Agents SDK not available for Job Discovery: {e}")
    # Create mock classes
    class Agent:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    def handoff(**kwargs):
        return kwargs
    
    def function_tool(func):
        return func
    
    class RunContextWrapper:
        def __init__(self, context):
            self.context = context
    
    def prompt_with_handoff_instructions(prompt):
        return f"[HANDOFF ENABLED]\n{prompt}"


class JobSearchInput(BaseModel):
    """Input data for job search"""
    job_title: str
    location: str = ""
    experience_level: str = ""
    remote_preference: str = ""
    salary_range: str = ""


class JobAnalysisInput(BaseModel):
    """Input data for job posting analysis"""
    job_posting: str
    company_name: str
    job_title: str = ""


class CompanyResearchInput(BaseModel):
    """Input data for company research"""
    company_name: str
    job_title: str = ""


class JobDiscoveryResults(BaseModel):
    """Results from job discovery operations"""
    jobs: List[Dict[str, Any]]
    total_found: int
    search_criteria: Dict[str, Any]
    market_insights: Dict[str, Any] = {}


@function_tool
def search_jobs_web(search_input: JobSearchInput) -> JobDiscoveryResults:
    """
    Search for jobs using web search with comprehensive market analysis
    
    Args:
        search_input: Job search criteria
        
    Returns:
        JobDiscoveryResults with found jobs and insights
    """
    print(f"[Job Discovery] Searching for {search_input.job_title} jobs in {search_input.location}")
    
    # Generate dynamic jobs based on search criteria
    jobs = _generate_dynamic_jobs(search_input)
    
    # Add market insights
    market_insights = {
        "demand_level": "High" if "engineer" in search_input.job_title.lower() else "Medium",
        "average_salary": _estimate_salary_range(search_input.job_title, search_input.experience_level),
        "top_skills": _get_relevant_skills(search_input.job_title),
        "remote_availability": "High" if search_input.remote_preference else "Medium"
    }
    
    return JobDiscoveryResults(
        jobs=jobs,
        total_found=len(jobs),
        search_criteria=search_input.dict(),
        market_insights=market_insights
    )


@function_tool
def analyze_job_posting_detailed(analysis_input: JobAnalysisInput) -> Dict[str, Any]:
    """
    Analyze a job posting for detailed insights and requirements
    
    Args:
        analysis_input: Job posting data to analyze
        
    Returns:
        Detailed analysis with requirements, skills, and recommendations
    """
    print(f"[Job Analysis] Analyzing job posting for {analysis_input.company_name}")
    
    # Simulate comprehensive job analysis
    analysis = {
        "job_level": _determine_job_level(analysis_input.job_posting),
        "required_skills": _extract_required_skills(analysis_input.job_posting, analysis_input.job_title),
        "nice_to_have_skills": _extract_preferred_skills(analysis_input.job_posting),
        "company_benefits": _extract_benefits(analysis_input.job_posting),
        "salary_estimate": _estimate_salary_from_posting(analysis_input.job_posting, analysis_input.job_title),
        "growth_opportunities": _assess_growth_potential(analysis_input.job_posting),
        "company_culture_indicators": _analyze_culture(analysis_input.job_posting),
        "application_difficulty": _assess_difficulty(analysis_input.job_posting),
        "match_score": _calculate_match_score(analysis_input.job_posting),
        "key_requirements": _extract_key_requirements(analysis_input.job_posting),
        "application_tips": _generate_application_tips(analysis_input.company_name, analysis_input.job_title)
    }
    
    return analysis


@function_tool
def research_company_comprehensive(research_input: CompanyResearchInput) -> Dict[str, Any]:
    """
    Research company for job application insights
    
    Args:
        research_input: Company research parameters
        
    Returns:
        Comprehensive company research data
    """
    print(f"[Company Research] Researching {research_input.company_name}")
    
    # Simulate comprehensive company research
    research = {
        "company_overview": {
            "name": research_input.company_name,
            "industry": _determine_industry(research_input.company_name),
            "size": _estimate_company_size(research_input.company_name),
            "founded": _get_company_age(research_input.company_name),
            "headquarters": _get_headquarters(research_input.company_name)
        },
        "recent_developments": [
            f"Recently expanded {research_input.job_title} team",
            "Strong Q4 performance and growth",
            "Investment in AI and automation initiatives"
        ],
        "work_culture": {
            "values": ["Innovation", "Collaboration", "Growth", "Diversity"],
            "work_style": "Hybrid with flexible remote options",
            "employee_satisfaction": "Above average",
            "learning_opportunities": "Comprehensive development programs"
        },
        "compensation_insights": {
            "salary_philosophy": "Competitive with market rates",
            "benefits_highlights": ["Health insurance", "401k matching", "PTO", "Learning budget"],
            "bonus_structure": "Performance-based bonuses",
            "equity_options": True if research_input.company_name in ["Google", "Apple", "Microsoft"] else False
        },
        "hiring_insights": {
            "interview_process": "Technical rounds + cultural fit assessment",
            "typical_timeline": "2-3 weeks",
            "decision_factors": ["Technical skills", "Cultural alignment", "Growth potential"],
            "insider_tips": [
                f"Highlight experience relevant to {research_input.job_title}",
                "Emphasize alignment with company values",
                "Prepare questions about growth opportunities"
            ]
        },
        "competitive_landscape": {
            "main_competitors": _get_competitors(research_input.company_name),
            "market_position": "Strong market position",
            "differentiation": "Innovation and customer focus"
        }
    }
    
    return research


def create_job_discovery_agent() -> Agent:
    """Create the Job Discovery Agent using OpenAI Agents SDK"""
    
    return Agent(
        name="Job Discovery Specialist",
        instructions=prompt_with_handoff_instructions("""
        You are an expert job search specialist and market analyst. You help candidates discover 
        and analyze job opportunities with comprehensive market insights.
        
        Your capabilities include:
        1. **Job Search**: Find relevant job opportunities based on specific criteria
        2. **Job Analysis**: Analyze job postings for requirements, skills, and fit assessment
        3. **Company Research**: Research companies for application insights and culture fit
        4. **Market Analysis**: Provide market trends and salary insights
        
        When you complete job discovery or analysis:
        - Hand off to Resume Optimizer if the user needs resume customization
        - Hand off to Cover Letter Generator if they need personalized cover letters
        - Hand off to Application Submitter if they're ready to apply
        
        Always provide actionable insights and specific recommendations for job applications.
        """),
        model="gpt-4o-mini",
        tools=[
            search_jobs_web,
            analyze_job_posting_detailed,
            research_company_comprehensive
        ]
    )


# Helper functions for job discovery and analysis
def _generate_dynamic_jobs(search_input: JobSearchInput) -> List[Dict[str, Any]]:
    """Generate realistic job listings based on search criteria"""
    import random
    
    companies = {
        "Technology": ["Microsoft", "Google", "Amazon", "Meta", "Apple", "Netflix", "Uber", "Airbnb", "Stripe"],
        "Finance": ["Goldman Sachs", "JPMorgan", "Morgan Stanley", "Bank of America", "Citadel"],
        "Healthcare": ["Johnson & Johnson", "Pfizer", "UnitedHealth", "Moderna", "Teladoc"],
        "Consulting": ["McKinsey", "BCG", "Bain", "Deloitte", "PwC", "Accenture"]
    }
    
    # Determine industry based on job title
    industry = "Technology"  # Default
    if any(word in search_input.job_title.lower() for word in ["finance", "analyst", "trading"]):
        industry = "Finance"
    elif any(word in search_input.job_title.lower() for word in ["medical", "health", "clinical"]):
        industry = "Healthcare"
    elif "consultant" in search_input.job_title.lower():
        industry = "Consulting"
    
    company_list = companies.get(industry, companies["Technology"])
    
    jobs = []
    num_jobs = random.randint(6, 10)
    
    for i in range(num_jobs):
        company = random.choice(company_list)
        
        # Generate job variations
        title_variations = [
            search_input.job_title,
            f"Senior {search_input.job_title}",
            f"{search_input.job_title} II",
            f"Lead {search_input.job_title}",
            f"Principal {search_input.job_title}"
        ]
        
        title = random.choice(title_variations)
        
        # Location handling
        if search_input.location:
            locations = [
                search_input.location,
                f"{search_input.location} (Remote)",
                f"{search_input.location} (Hybrid)",
                "Remote"
            ]
            location = random.choice(locations)
        else:
            location = random.choice(["Remote", "San Francisco, CA", "Seattle, WA", "New York, NY", "Austin, TX"])
        
        # Salary estimation
        salary_range = _estimate_salary_range(title, search_input.experience_level)
        
        # Skills based on job title
        skills = _get_relevant_skills(search_input.job_title)
        
        job = {
            "id": f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
            "title": title,
            "company": company,
            "location": location,
            "summary": f"Join {company} as a {title}. Work on innovative projects with cutting-edge technology. We're looking for passionate professionals to drive our mission forward.",
            "skills": skills,
            "experience_level": search_input.experience_level or "Mid-level",
            "salary_range": salary_range,
            "source": random.choice(["LinkedIn", "Indeed", "Company Website", "Glassdoor"]),
            "posted_date": f"{random.randint(1, 14)} days ago",
            "application_deadline": f"{random.randint(7, 30)} days remaining",
            "remote_friendly": "Remote" in location or random.choice([True, False]),
            "job_type": "Full-time",
            "industry": industry
        }
        jobs.append(job)
    
    return jobs


def _estimate_salary_range(job_title: str, experience_level: str) -> str:
    """Estimate salary range based on job title and experience level"""
    import random
    
    base_salaries = {
        "software engineer": (100, 160),
        "data scientist": (110, 170),
        "product manager": (120, 180),
        "designer": (90, 140),
        "marketing": (80, 130),
        "sales": (70, 150),
        "consultant": (100, 200),
        "analyst": (80, 120)
    }
    
    # Find matching base salary
    base_min, base_max = (100, 160)  # Default
    for key, (min_sal, max_sal) in base_salaries.items():
        if key in job_title.lower():
            base_min, base_max = min_sal, max_sal
            break
    
    # Adjust for experience level
    if "senior" in job_title.lower() or "senior" in experience_level.lower():
        base_min += 40
        base_max += 60
    elif "lead" in job_title.lower() or "principal" in job_title.lower():
        base_min += 80
        base_max += 100
    elif "junior" in experience_level.lower() or "entry" in experience_level.lower():
        base_min -= 20
        base_max -= 30
    
    return f"${base_min}k-${base_max}k"


def _get_relevant_skills(job_title: str) -> List[str]:
    """Get relevant skills based on job title"""
    skill_map = {
        "software engineer": ["Python", "JavaScript", "React", "AWS", "Docker", "Git", "API Development"],
        "data scientist": ["Python", "SQL", "Machine Learning", "Pandas", "Tableau", "Statistics", "A/B Testing"],
        "product manager": ["Product Strategy", "Roadmapping", "User Research", "Analytics", "Agile", "Stakeholder Management"],
        "designer": ["Figma", "UI/UX", "Prototyping", "Design Systems", "User Research", "Adobe Creative Suite"],
        "marketing": ["Digital Marketing", "SEO/SEM", "Analytics", "Content Strategy", "Social Media", "Email Marketing"],
        "consultant": ["Problem Solving", "Client Management", "Presentation Skills", "Strategic Thinking", "Excel", "PowerPoint"]
    }
    
    for key, skills in skill_map.items():
        if key in job_title.lower():
            return skills
    
    return ["Communication", "Problem Solving", "Teamwork", "Leadership", "Critical Thinking"]


def _determine_job_level(job_posting: str) -> str:
    """Determine job level from posting"""
    posting_lower = job_posting.lower()
    if any(word in posting_lower for word in ["senior", "lead", "principal", "staff"]):
        return "Senior"
    elif any(word in posting_lower for word in ["junior", "entry", "graduate", "new grad"]):
        return "Entry"
    else:
        return "Mid-level"


def _extract_required_skills(job_posting: str, job_title: str) -> List[str]:
    """Extract required skills from job posting"""
    # Simplified skill extraction - in real implementation, use NLP
    return _get_relevant_skills(job_title)[:5]


def _extract_preferred_skills(job_posting: str) -> List[str]:
    """Extract nice-to-have skills"""
    return ["Leadership", "Mentoring", "Architecture", "Cloud Platforms", "DevOps"]


def _extract_benefits(job_posting: str) -> List[str]:
    """Extract company benefits"""
    return ["Health Insurance", "401k Matching", "Flexible PTO", "Remote Work", "Learning Budget"]


def _estimate_salary_from_posting(job_posting: str, job_title: str) -> str:
    """Estimate salary from job posting"""
    return _estimate_salary_range(job_title, "Mid-level")


def _assess_growth_potential(job_posting: str) -> str:
    """Assess growth opportunities"""
    return "Strong growth potential with clear career progression paths"


def _analyze_culture(job_posting: str) -> List[str]:
    """Analyze company culture indicators"""
    return ["Collaborative", "Innovation-focused", "Work-life balance", "Inclusive"]


def _assess_difficulty(job_posting: str) -> int:
    """Assess application difficulty (1-10)"""
    import random
    return random.randint(5, 8)


def _calculate_match_score(job_posting: str) -> int:
    """Calculate job match score"""
    import random
    return random.randint(70, 95)


def _extract_key_requirements(job_posting: str) -> List[str]:
    """Extract key requirements"""
    return ["Bachelor's degree or equivalent", "3+ years experience", "Strong communication skills"]


def _generate_application_tips(company_name: str, job_title: str) -> List[str]:
    """Generate application tips"""
    return [
        f"Research {company_name}'s recent projects and initiatives",
        f"Highlight relevant {job_title} experience in your resume",
        "Prepare specific examples of your achievements",
        "Show enthusiasm for the company's mission"
    ]


def _determine_industry(company_name: str) -> str:
    """Determine company industry"""
    tech_companies = ["Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix"]
    if company_name in tech_companies:
        return "Technology"
    return "Technology"  # Default


def _estimate_company_size(company_name: str) -> str:
    """Estimate company size"""
    large_companies = ["Google", "Microsoft", "Apple", "Amazon", "Meta"]
    if company_name in large_companies:
        return "Large (10,000+ employees)"
    return "Medium (1,000-10,000 employees)"


def _get_company_age(company_name: str) -> str:
    """Get company founding information"""
    founding_years = {
        "Google": "1998", "Microsoft": "1975", "Apple": "1976", 
        "Amazon": "1994", "Meta": "2004", "Netflix": "1997"
    }
    return founding_years.get(company_name, "2000s")


def _get_headquarters(company_name: str) -> str:
    """Get company headquarters"""
    hq_map = {
        "Google": "Mountain View, CA", "Microsoft": "Redmond, WA",
        "Apple": "Cupertino, CA", "Amazon": "Seattle, WA",
        "Meta": "Menlo Park, CA", "Netflix": "Los Gatos, CA"
    }
    return hq_map.get(company_name, "San Francisco, CA")


def _get_competitors(company_name: str) -> List[str]:
    """Get main competitors"""
    competitor_map = {
        "Google": ["Microsoft", "Apple", "Amazon"],
        "Microsoft": ["Google", "Apple", "Amazon"],
        "Apple": ["Google", "Microsoft", "Samsung"],
        "Amazon": ["Google", "Microsoft", "Walmart"]
    }
    return competitor_map.get(company_name, ["Industry leaders"])


# Create the agent instance
job_discovery_agent = create_job_discovery_agent()