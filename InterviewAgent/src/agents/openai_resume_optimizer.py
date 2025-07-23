"""
Resume Optimizer Agent - Using OpenAI Agents SDK
Handles resume optimization, customization, and industry research with proper handoffs
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
    print(f"Warning: OpenAI Agents SDK not available for Resume Optimizer: {e}")
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


class ResumeOptimizationInput(BaseModel):
    """Input data for resume optimization"""
    current_resume: Dict[str, Any]
    job_description: str
    company_name: str
    job_title: str
    target_skills: List[str] = []


class IndustryResearchInput(BaseModel):
    """Input data for industry research"""
    job_title: str
    industry: str
    company_name: str = ""


class ResumeAnalysisInput(BaseModel):
    """Input data for resume analysis"""
    resume_data: Dict[str, Any]
    target_role: str = ""


class OptimizedResumeResult(BaseModel):
    """Result from resume optimization"""
    optimized_resume: Dict[str, Any]
    optimization_summary: str
    keyword_matches: List[str]
    improvement_suggestions: List[str]
    ats_score: int


@function_tool
def optimize_resume_for_job(optimization_input: ResumeOptimizationInput) -> OptimizedResumeResult:
    """
    Optimize resume for specific job posting with ATS optimization
    
    Args:
        optimization_input: Resume and job details for optimization
        
    Returns:
        OptimizedResumeResult with enhanced resume and analysis
    """
    print(f"[Resume Optimizer] Optimizing resume for {optimization_input.job_title} at {optimization_input.company_name}")
    
    current_resume = optimization_input.current_resume
    job_description = optimization_input.job_description
    
    # Extract key requirements from job description
    key_skills = _extract_job_skills(job_description)
    required_experience = _extract_experience_requirements(job_description)
    
    # Optimize resume sections
    optimized_resume = _optimize_resume_structure(current_resume, key_skills, job_description)
    
    # Enhance with job-specific keywords
    optimized_resume = _enhance_with_keywords(optimized_resume, job_description)
    
    # Generate optimization metrics
    keyword_matches = _calculate_keyword_matches(optimized_resume, job_description)
    ats_score = _calculate_ats_score(optimized_resume, job_description)
    
    optimization_summary = f"""
    Resume optimized for {optimization_input.job_title} position:
    - Enhanced {len(keyword_matches)} keyword matches
    - Restructured experience section for better alignment  
    - Improved ATS compatibility score to {ats_score}/100
    - Tailored skills section for job requirements
    """
    
    improvement_suggestions = _generate_improvement_suggestions(optimized_resume, job_description)
    
    return OptimizedResumeResult(
        optimized_resume=optimized_resume,
        optimization_summary=optimization_summary.strip(),
        keyword_matches=keyword_matches,
        improvement_suggestions=improvement_suggestions,
        ats_score=ats_score
    )


@function_tool
def research_industry_trends(research_input: IndustryResearchInput) -> Dict[str, Any]:
    """
    Research industry trends and requirements for resume optimization
    
    Args:
        research_input: Industry and role research parameters
        
    Returns:
        Industry research data with trends and requirements
    """
    print(f"[Industry Research] Researching {research_input.job_title} trends in {research_input.industry}")
    
    # Simulate comprehensive industry research
    research_data = {
        "industry_overview": {
            "name": research_input.industry,
            "growth_rate": "8-12% annually",
            "market_size": "Large and expanding",
            "key_drivers": ["Digital transformation", "AI adoption", "Remote work trends"]
        },
        "role_analysis": {
            "job_title": research_input.job_title,
            "demand_level": "High",
            "salary_trends": "Increasing due to skill shortage",
            "career_progression": "Strong advancement opportunities"
        },
        "trending_skills": _get_trending_skills(research_input.job_title, research_input.industry),
        "emerging_technologies": _get_emerging_tech(research_input.industry),
        "certifications": _get_relevant_certifications(research_input.job_title),
        "resume_keywords": _get_industry_keywords(research_input.job_title, research_input.industry),
        "company_preferences": {
            "top_skills": _get_company_preferred_skills(research_input.company_name, research_input.job_title),
            "experience_focus": _get_experience_preferences(research_input.company_name),
            "cultural_fit": _get_cultural_keywords(research_input.company_name)
        },
        "optimization_tips": [
            f"Highlight experience with {research_input.industry}-specific tools",
            "Emphasize quantifiable achievements and metrics",
            "Include relevant certifications and continuous learning",
            "Show adaptability to emerging technologies"
        ]
    }
    
    return research_data


@function_tool
def analyze_resume_performance(analysis_input: ResumeAnalysisInput) -> Dict[str, Any]:
    """
    Analyze resume performance and provide detailed feedback
    
    Args:
        analysis_input: Resume data for analysis
        
    Returns:
        Comprehensive resume analysis and recommendations
    """
    print(f"[Resume Analysis] Analyzing resume performance for {analysis_input.target_role}")
    
    resume_data = analysis_input.resume_data
    
    # Comprehensive resume analysis
    analysis = {
        "overall_score": _calculate_overall_score(resume_data),
        "section_analysis": {
            "summary": _analyze_summary_section(resume_data.get("summary", "")),
            "experience": _analyze_experience_section(resume_data.get("experience", [])),
            "skills": _analyze_skills_section(resume_data.get("skills", [])),
            "education": _analyze_education_section(resume_data.get("education", [])),
            "projects": _analyze_projects_section(resume_data.get("projects", []))
        },
        "ats_compatibility": {
            "score": _calculate_ats_compatibility(resume_data),
            "formatting_issues": _identify_formatting_issues(resume_data),
            "keyword_density": _analyze_keyword_density(resume_data)
        },
        "content_quality": {
            "quantifiable_achievements": _count_quantifiable_achievements(resume_data),
            "action_verbs_usage": _analyze_action_verbs(resume_data),
            "relevance_score": _calculate_relevance_score(resume_data, analysis_input.target_role)
        },
        "recommendations": {
            "high_priority": _get_high_priority_recommendations(resume_data),
            "medium_priority": _get_medium_priority_recommendations(resume_data),
            "low_priority": _get_low_priority_recommendations(resume_data)
        },
        "market_comparison": {
            "competitiveness": _assess_market_competitiveness(resume_data, analysis_input.target_role),
            "unique_strengths": _identify_unique_strengths(resume_data),
            "improvement_areas": _identify_improvement_areas(resume_data)
        }
    }
    
    return analysis


def create_resume_optimizer_agent() -> Agent:
    """Create the Resume Optimizer Agent using OpenAI Agents SDK"""
    
    return Agent(
        name="Resume Optimization Specialist",
        instructions=prompt_with_handoff_instructions("""
        You are an expert resume optimization specialist with deep knowledge of ATS systems, 
        industry trends, and hiring best practices.
        
        Your capabilities include:
        1. **Resume Optimization**: Customize resumes for specific job postings and companies
        2. **Industry Research**: Research current trends and requirements for better targeting
        3. **ATS Optimization**: Ensure resumes pass Applicant Tracking Systems
        4. **Performance Analysis**: Analyze resume effectiveness and provide actionable feedback
        
        When you complete resume optimization:
        - Hand off to Cover Letter Generator if the user needs personalized cover letters
        - Hand off to Application Submitter if the resume is ready for submission
        - Hand off to Job Discovery Agent if they need more job opportunities
        
        Always focus on:
        - Quantifiable achievements and impact metrics
        - Industry-specific keywords and terminology
        - ATS-friendly formatting and structure
        - Tailoring content to specific job requirements
        """),
        model="gpt-4o-mini",
        tools=[
            optimize_resume_for_job,
            research_industry_trends,
            analyze_resume_performance
        ]
    )


# Helper functions for resume optimization

def _extract_job_skills(job_description: str) -> List[str]:
    """Extract key skills from job description"""
    # Simplified skill extraction - in production, use advanced NLP
    common_skills = [
        "Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes",
        "Machine Learning", "Data Analysis", "Project Management",
        "Leadership", "Communication", "Problem Solving"
    ]
    
    found_skills = []
    job_desc_lower = job_description.lower()
    
    for skill in common_skills:
        if skill.lower() in job_desc_lower:
            found_skills.append(skill)
    
    return found_skills[:8]  # Return top 8 matches


def _extract_experience_requirements(job_description: str) -> Dict[str, Any]:
    """Extract experience requirements from job description"""
    import re
    
    # Look for years of experience patterns
    years_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)'
    years_match = re.search(years_pattern, job_description.lower())
    
    required_years = 3  # Default
    if years_match:
        required_years = int(years_match.group(1))
    
    return {
        "years_required": required_years,
        "level": "Senior" if required_years >= 5 else "Mid-level" if required_years >= 2 else "Entry"
    }


def _optimize_resume_structure(resume: Dict[str, Any], key_skills: List[str], job_description: str) -> Dict[str, Any]:
    """Optimize resume structure for better job alignment"""
    optimized = resume.copy()
    
    # Enhance summary with job-relevant keywords
    if "summary" in optimized:
        optimized["summary"] = _enhance_summary(optimized["summary"], key_skills, job_description)
    
    # Optimize experience section
    if "experience" in optimized:
        optimized["experience"] = _optimize_experience_section(optimized["experience"], key_skills)
    
    # Enhance skills section
    if "skills" in optimized:
        optimized["skills"] = _optimize_skills_section(optimized["skills"], key_skills)
    
    # Add or enhance projects section
    if "projects" not in optimized:
        optimized["projects"] = _generate_relevant_projects(key_skills)
    
    return optimized


def _enhance_summary(summary: str, key_skills: List[str], job_description: str) -> str:
    """Enhance resume summary with job-relevant content"""
    if not summary:
        return f"Results-driven professional with expertise in {', '.join(key_skills[:3])} and a track record of delivering impactful solutions."
    
    # Add key skills if not present
    enhanced_summary = summary
    for skill in key_skills[:3]:
        if skill.lower() not in summary.lower():
            enhanced_summary += f" Experienced in {skill}."
    
    return enhanced_summary


def _optimize_experience_section(experience: List[Dict], key_skills: List[str]) -> List[Dict]:
    """Optimize experience section with job-relevant achievements"""
    optimized_experience = []
    
    for exp in experience:
        optimized_exp = exp.copy()
        
        # Enhance bullet points with quantifiable achievements
        if "responsibilities" in optimized_exp:
            optimized_exp["responsibilities"] = _enhance_responsibilities(
                optimized_exp["responsibilities"], key_skills
            )
        
        optimized_experience.append(optimized_exp)
    
    return optimized_experience


def _enhance_responsibilities(responsibilities: List[str], key_skills: List[str]) -> List[str]:
    """Enhance responsibility bullet points"""
    enhanced = []
    
    for resp in responsibilities:
        # Add quantifiable metrics where possible
        if any(keyword in resp.lower() for keyword in ["led", "managed", "developed", "improved"]):
            if not any(char.isdigit() for char in resp):
                # Add sample metric
                resp += " resulting in 25% improvement in efficiency"
        
        enhanced.append(resp)
    
    # Add skill-specific achievements if missing
    skills_covered = [skill for skill in key_skills if skill.lower() in " ".join(enhanced).lower()]
    missing_skills = [skill for skill in key_skills[:3] if skill not in skills_covered]
    
    for skill in missing_skills:
        enhanced.append(f"Utilized {skill} to deliver scalable solutions and improve system performance")
    
    return enhanced


def _optimize_skills_section(skills: List[str], key_skills: List[str]) -> List[str]:
    """Optimize skills section with job-relevant skills"""
    optimized_skills = list(skills)  # Copy existing skills
    
    # Add missing key skills
    for skill in key_skills:
        if skill not in optimized_skills:
            optimized_skills.append(skill)
    
    # Reorder to prioritize job-relevant skills
    prioritized_skills = key_skills + [skill for skill in optimized_skills if skill not in key_skills]
    
    return prioritized_skills[:15]  # Limit to top 15 skills


def _generate_relevant_projects(key_skills: List[str]) -> List[Dict[str, Any]]:
    """Generate relevant project examples"""
    return [
        {
            "name": "Automated Data Pipeline",
            "description": f"Built scalable data pipeline using {key_skills[0] if key_skills else 'Python'} and cloud technologies",
            "technologies": key_skills[:4],
            "impact": "Reduced data processing time by 40%"
        }
    ]


def _enhance_with_keywords(resume: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """Enhance resume with job-specific keywords for ATS optimization"""
    enhanced = resume.copy()
    
    # Extract keywords from job description
    important_keywords = _extract_important_keywords(job_description)
    
    # Add keywords strategically throughout resume
    if "summary" in enhanced:
        enhanced["summary"] = _inject_keywords_naturally(enhanced["summary"], important_keywords[:3])
    
    return enhanced


def _extract_important_keywords(job_description: str) -> List[str]:
    """Extract important keywords from job description"""
    # Simplified keyword extraction
    keywords = ["collaboration", "innovation", "results-driven", "strategic", "analytical"]
    
    found_keywords = []
    job_desc_lower = job_description.lower()
    
    for keyword in keywords:
        if keyword in job_desc_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def _inject_keywords_naturally(text: str, keywords: List[str]) -> str:
    """Inject keywords naturally into text"""
    enhanced_text = text
    
    for keyword in keywords:
        if keyword.lower() not in text.lower():
            enhanced_text += f" Demonstrated {keyword} in previous roles."
    
    return enhanced_text


def _calculate_keyword_matches(resume: Dict[str, Any], job_description: str) -> List[str]:
    """Calculate keyword matches between resume and job description"""
    resume_text = json.dumps(resume).lower()
    job_desc_lower = job_description.lower()
    
    potential_keywords = [
        "python", "javascript", "react", "aws", "docker", "leadership",
        "management", "analysis", "development", "engineering"
    ]
    
    matches = []
    for keyword in potential_keywords:
        if keyword in resume_text and keyword in job_desc_lower:
            matches.append(keyword.title())
    
    return matches


def _calculate_ats_score(resume: Dict[str, Any], job_description: str) -> int:
    """Calculate ATS compatibility score"""
    score = 60  # Base score
    
    # Check for key sections
    if "summary" in resume:
        score += 10
    if "experience" in resume and len(resume["experience"]) > 0:
        score += 15
    if "skills" in resume and len(resume["skills"]) > 5:
        score += 10
    
    # Check keyword matches
    keyword_matches = _calculate_keyword_matches(resume, job_description)
    score += min(len(keyword_matches) * 2, 15)
    
    return min(score, 100)


def _generate_improvement_suggestions(resume: Dict[str, Any], job_description: str) -> List[str]:
    """Generate improvement suggestions"""
    suggestions = []
    
    if len(resume.get("skills", [])) < 8:
        suggestions.append("Add more relevant technical skills to improve keyword matching")
    
    if "projects" not in resume:
        suggestions.append("Include a projects section to showcase practical experience")
    
    keyword_matches = _calculate_keyword_matches(resume, job_description)
    if len(keyword_matches) < 5:
        suggestions.append("Incorporate more job-specific keywords throughout your resume")
    
    if not resume.get("summary"):
        suggestions.append("Add a professional summary to highlight your key qualifications")
    
    return suggestions


# Additional analysis functions
def _get_trending_skills(job_title: str, industry: str) -> List[str]:
    """Get trending skills for specific role and industry"""
    skill_map = {
        "software engineer": ["AI/ML", "Cloud Computing", "DevOps", "Microservices", "API Development"],
        "data scientist": ["MLOps", "Deep Learning", "Cloud Platforms", "Data Engineering", "Python"],
        "product manager": ["Product Analytics", "User Research", "A/B Testing", "Roadmapping", "Stakeholder Management"]
    }
    
    for key, skills in skill_map.items():
        if key in job_title.lower():
            return skills
    
    return ["Leadership", "Communication", "Problem Solving", "Analytical Thinking", "Innovation"]


def _get_emerging_tech(industry: str) -> List[str]:
    """Get emerging technologies for industry"""
    return ["Artificial Intelligence", "Machine Learning", "Cloud Computing", "IoT", "Blockchain"]


def _get_relevant_certifications(job_title: str) -> List[str]:
    """Get relevant certifications for job title"""
    cert_map = {
        "software engineer": ["AWS Certified", "Google Cloud Professional", "Kubernetes Certified"],
        "data scientist": ["AWS ML Specialty", "Google Cloud ML Engineer", "Microsoft Azure AI"],
        "product manager": ["Product Management Certificate", "Scrum Master", "Analytics Certificate"]
    }
    
    for key, certs in cert_map.items():
        if key in job_title.lower():
            return certs
    
    return ["Professional Development Certificates", "Industry-Specific Certifications"]


def _get_industry_keywords(job_title: str, industry: str) -> List[str]:
    """Get industry-specific resume keywords"""
    return ["innovation", "scalability", "optimization", "collaboration", "results-driven", "strategic"]


def _get_company_preferred_skills(company_name: str, job_title: str) -> List[str]:
    """Get company-preferred skills"""
    return ["teamwork", "innovation", "customer focus", "technical excellence"]


def _get_experience_preferences(company_name: str) -> str:
    """Get company experience preferences"""
    return "Strong technical foundation with demonstrated impact"


def _get_cultural_keywords(company_name: str) -> List[str]:
    """Get cultural fit keywords for company"""
    return ["collaborative", "innovative", "growth-minded", "customer-centric"]


def _calculate_overall_score(resume_data: Dict[str, Any]) -> int:
    """Calculate overall resume score"""
    score = 0
    
    # Section completeness
    if resume_data.get("summary"):
        score += 20
    if resume_data.get("experience") and len(resume_data["experience"]) > 0:
        score += 30
    if resume_data.get("skills") and len(resume_data["skills"]) > 5:
        score += 20
    if resume_data.get("education"):
        score += 15
    if resume_data.get("projects"):
        score += 15
    
    return score


def _analyze_summary_section(summary: str) -> Dict[str, Any]:
    """Analyze resume summary section"""
    return {
        "length": len(summary.split()) if summary else 0,
        "has_keywords": len(summary.split()) > 20 if summary else False,
        "score": 85 if summary and len(summary.split()) > 15 else 60,
        "recommendations": ["Make it more concise"] if summary and len(summary.split()) > 50 else []
    }


def _analyze_experience_section(experience: List[Dict]) -> Dict[str, Any]:
    """Analyze experience section"""
    return {
        "job_count": len(experience),
        "quantifiable_achievements": sum(1 for exp in experience if any(char.isdigit() for char in str(exp))),
        "score": min(len(experience) * 20, 90),
        "recommendations": ["Add more quantifiable achievements"] if len(experience) > 0 else ["Add work experience"]
    }


def _analyze_skills_section(skills: List[str]) -> Dict[str, Any]:
    """Analyze skills section"""
    return {
        "skill_count": len(skills),
        "diversity": "Good" if len(skills) > 8 else "Limited",
        "score": min(len(skills) * 5, 85),
        "recommendations": ["Add more relevant skills"] if len(skills) < 10 else []
    }


def _analyze_education_section(education: List[Dict]) -> Dict[str, Any]:
    """Analyze education section"""
    return {
        "degree_count": len(education),
        "score": 80 if education else 60,
        "recommendations": [] if education else ["Add education information"]
    }


def _analyze_projects_section(projects: List[Dict]) -> Dict[str, Any]:
    """Analyze projects section"""
    return {
        "project_count": len(projects),
        "score": min(len(projects) * 15, 85),
        "recommendations": ["Add relevant projects"] if len(projects) < 2 else []
    }


def _calculate_ats_compatibility(resume_data: Dict[str, Any]) -> int:
    """Calculate ATS compatibility score"""
    return 85  # Simplified calculation


def _identify_formatting_issues(resume_data: Dict[str, Any]) -> List[str]:
    """Identify formatting issues"""
    return []  # No issues in structured data format


def _analyze_keyword_density(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze keyword density"""
    return {"density": "Optimal", "score": 80}


def _count_quantifiable_achievements(resume_data: Dict[str, Any]) -> int:
    """Count quantifiable achievements"""
    return 3  # Simplified count


def _analyze_action_verbs(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze action verb usage"""
    return {"usage": "Good", "score": 75}


def _calculate_relevance_score(resume_data: Dict[str, Any], target_role: str) -> int:
    """Calculate relevance score for target role"""
    return 82  # Simplified calculation


def _get_high_priority_recommendations(resume_data: Dict[str, Any]) -> List[str]:
    """Get high priority recommendations"""
    return ["Add quantifiable achievements to experience section"]


def _get_medium_priority_recommendations(resume_data: Dict[str, Any]) -> List[str]:
    """Get medium priority recommendations"""
    return ["Enhance skills section with trending technologies"]


def _get_low_priority_recommendations(resume_data: Dict[str, Any]) -> List[str]:
    """Get low priority recommendations"""
    return ["Consider adding volunteer experience or additional certifications"]


def _assess_market_competitiveness(resume_data: Dict[str, Any], target_role: str) -> str:
    """Assess market competitiveness"""
    return "Competitive"


def _identify_unique_strengths(resume_data: Dict[str, Any]) -> List[str]:
    """Identify unique strengths"""
    return ["Strong technical background", "Diverse project experience"]


def _identify_improvement_areas(resume_data: Dict[str, Any]) -> List[str]:
    """Identify improvement areas"""
    return ["Leadership experience", "Industry-specific certifications"]


# Create the agent instance
resume_optimizer_agent = create_resume_optimizer_agent()