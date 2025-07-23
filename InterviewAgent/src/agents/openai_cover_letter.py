"""
Cover Letter Generator Agent - Using OpenAI Agents SDK
Handles personalized cover letter generation with company research and proper handoffs
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
    print(f"Warning: OpenAI Agents SDK not available for Cover Letter Generator: {e}")
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


class CoverLetterInput(BaseModel):
    """Input data for cover letter generation"""
    job_data: Dict[str, Any]
    user_profile: Dict[str, Any]
    company_name: str
    job_title: str
    optimized_resume: Dict[str, Any] = {}


class CompanyResearchInput(BaseModel):
    """Input data for company research"""
    company_name: str
    job_title: str = ""
    industry: str = ""


class CoverLetterCustomizationInput(BaseModel):
    """Input data for cover letter customization"""
    base_cover_letter: str
    job_requirements: List[str]
    company_culture: Dict[str, Any]
    user_achievements: List[str] = []


class GeneratedCoverLetterResult(BaseModel):
    """Result from cover letter generation"""
    cover_letter: str
    personalization_summary: str
    key_highlights: List[str]
    company_research_insights: Dict[str, Any]
    customization_score: int


@function_tool
def generate_personalized_cover_letter(input_data: CoverLetterInput) -> GeneratedCoverLetterResult:
    """
    Generate a personalized cover letter based on job data and user profile
    
    Args:
        input_data: Job and user information for cover letter generation
        
    Returns:
        GeneratedCoverLetterResult with personalized cover letter and insights
    """
    print(f"[Cover Letter Generator] Creating cover letter for {input_data.job_title} at {input_data.company_name}")
    
    job_data = input_data.job_data
    user_profile = input_data.user_profile
    
    # Extract key information
    user_name = user_profile.get("name", "")
    user_experience = user_profile.get("experience", [])
    user_skills = user_profile.get("skills", [])
    
    # Generate company research insights
    company_insights = _research_company_insights(input_data.company_name, input_data.job_title)
    
    # Create personalized cover letter
    cover_letter = _create_personalized_cover_letter(
        user_name=user_name,
        company_name=input_data.company_name,
        job_title=input_data.job_title,
        job_data=job_data,
        user_profile=user_profile,
        company_insights=company_insights
    )
    
    # Generate key highlights
    key_highlights = _extract_key_highlights(cover_letter, user_experience, job_data)
    
    # Calculate customization score
    customization_score = _calculate_customization_score(cover_letter, job_data, company_insights)
    
    personalization_summary = f"""
    Cover letter personalized for {input_data.company_name}:
    - Highlighted {len(key_highlights)} key qualifications
    - Incorporated company research insights
    - Aligned with {input_data.job_title} requirements
    - Customization score: {customization_score}/100
    """
    
    return GeneratedCoverLetterResult(
        cover_letter=cover_letter,
        personalization_summary=personalization_summary.strip(),
        key_highlights=key_highlights,
        company_research_insights=company_insights,
        customization_score=customization_score
    )


@function_tool
def research_company_culture(research_input: CompanyResearchInput) -> Dict[str, Any]:
    """
    Research company culture and values for cover letter personalization
    
    Args:
        research_input: Company research parameters
        
    Returns:
        Comprehensive company culture and values data
    """
    print(f"[Company Culture Research] Researching {research_input.company_name} culture")
    
    # Simulate comprehensive company culture research
    culture_data = {
        "company_overview": {
            "name": research_input.company_name,
            "mission": _get_company_mission(research_input.company_name),
            "values": _get_company_values(research_input.company_name),
            "culture_keywords": _get_culture_keywords(research_input.company_name)
        },
        "work_environment": {
            "work_style": _get_work_style(research_input.company_name),
            "team_structure": "Collaborative cross-functional teams",
            "innovation_focus": "High emphasis on innovation and creativity",
            "growth_opportunities": "Strong focus on employee development"
        },
        "recent_initiatives": [
            "Sustainability and environmental responsibility programs",
            "Diversity, equity, and inclusion initiatives",
            "Employee wellness and work-life balance programs",
            "Digital transformation and innovation projects"
        ],
        "leadership_style": {
            "approach": "Collaborative and empowering leadership",
            "communication": "Open and transparent communication",
            "decision_making": "Data-driven with employee input"
        },
        "employee_experience": {
            "satisfaction_level": "Above industry average",
            "retention_rate": "Strong employee retention",
            "career_progression": "Clear advancement opportunities",
            "learning_culture": "Continuous learning and development"
        },
        "industry_position": {
            "market_leader": _is_market_leader(research_input.company_name),
            "competitive_advantages": _get_competitive_advantages(research_input.company_name),
            "future_vision": "Leading digital transformation in the industry"
        }
    }
    
    return culture_data


@function_tool
def customize_cover_letter_content(customization_input: CoverLetterCustomizationInput) -> Dict[str, Any]:
    """
    Customize cover letter content based on specific job requirements and company culture
    
    Args:
        customization_input: Customization parameters
        
    Returns:
        Customized cover letter with specific adjustments
    """
    print("[Cover Letter Customization] Customizing content for specific requirements")
    
    base_letter = customization_input.base_cover_letter
    job_requirements = customization_input.job_requirements
    company_culture = customization_input.company_culture
    
    # Customize opening paragraph
    customized_opening = _customize_opening_paragraph(base_letter, company_culture)
    
    # Enhance experience alignment
    enhanced_experience = _align_experience_with_requirements(
        base_letter, job_requirements, customization_input.user_achievements
    )
    
    # Add company-specific insights
    company_connection = _add_company_specific_insights(base_letter, company_culture)
    
    # Strengthen closing
    enhanced_closing = _enhance_closing_paragraph(base_letter, company_culture)
    
    # Generate final customized version
    customized_letter = _assemble_customized_letter(
        customized_opening, enhanced_experience, company_connection, enhanced_closing
    )
    
    customization_analysis = {
        "original_length": len(base_letter.split()),
        "customized_length": len(customized_letter.split()),
        "requirements_addressed": len(job_requirements),
        "culture_elements_incorporated": len(company_culture.get("values", [])),
        "personalization_level": "High",
        "readability_score": 85,
        "engagement_factors": [
            "Company-specific research integration",
            "Job requirement alignment",
            "Cultural fit demonstration",
            "Quantified achievement highlights"
        ]
    }
    
    return {
        "customized_cover_letter": customized_letter,
        "customization_analysis": customization_analysis,
        "improvement_suggestions": _get_improvement_suggestions(customized_letter)
    }


def create_cover_letter_agent() -> Agent:
    """Create the Cover Letter Generator Agent using OpenAI Agents SDK"""
    
    return Agent(
        name="Cover Letter Specialist",
        instructions=prompt_with_handoff_instructions("""
        You are an expert cover letter specialist with deep knowledge of persuasive writing, 
        company research, and job application best practices.
        
        Your capabilities include:
        1. **Personalized Cover Letters**: Create compelling, customized cover letters for specific jobs
        2. **Company Research**: Research company culture, values, and recent developments
        3. **Content Customization**: Tailor content to match job requirements and company culture
        4. **Achievement Highlighting**: Showcase relevant accomplishments and experiences
        
        When you complete cover letter generation:
        - Hand off to Application Submitter if the cover letter is ready for submission
        - Hand off to Resume Optimizer if additional resume adjustments are needed
        - Hand off to Job Discovery Agent if they need more job opportunities
        
        Always focus on:
        - Genuine interest and enthusiasm for the role and company
        - Specific examples and quantified achievements
        - Clear connection between candidate skills and job requirements
        - Professional yet personable tone
        """),
        model="gpt-4o-mini",
        tools=[
            generate_personalized_cover_letter,
            research_company_culture,
            customize_cover_letter_content
        ]
    )


# Helper functions for cover letter generation

def _research_company_insights(company_name: str, job_title: str) -> Dict[str, Any]:
    """Research company insights for personalization"""
    return {
        "company_mission": _get_company_mission(company_name),
        "recent_news": [
            f"{company_name} recently announced expansion in AI technology",
            f"Strong Q4 performance with continued growth",
            f"New sustainability initiatives launched"
        ],
        "values_alignment": _get_company_values(company_name),
        "industry_leadership": f"{company_name} is recognized as an industry leader",
        "growth_opportunities": f"Excellent career growth in {job_title} roles",
        "work_culture": "Collaborative, innovative, and inclusive environment"
    }


def _get_company_mission(company_name: str) -> str:
    """Get company mission statement"""
    missions = {
        "Google": "To organize the world's information and make it universally accessible and useful",
        "Microsoft": "To empower every person and every organization on the planet to achieve more",
        "Apple": "To bring the best user experience to customers through innovative hardware, software, and services",
        "Amazon": "To be Earth's Most Customer-Centric Company",
        "Meta": "To bring the world closer together",
        "Netflix": "To entertain the world"
    }
    return missions.get(company_name, "To drive innovation and create value for customers and stakeholders")


def _get_company_values(company_name: str) -> List[str]:
    """Get company core values"""
    values_map = {
        "Google": ["Focus on the user", "Democracy on the web", "Fast is better than slow"],
        "Microsoft": ["Respect", "Integrity", "Accountability"],
        "Apple": ["Innovation", "Quality", "Simplicity"],
        "Amazon": ["Customer obsession", "Ownership", "Invent and simplify"]
    }
    return values_map.get(company_name, ["Innovation", "Integrity", "Excellence", "Collaboration"])


def _get_culture_keywords(company_name: str) -> List[str]:
    """Get culture-specific keywords"""
    return ["innovative", "collaborative", "growth-minded", "customer-focused", "results-driven"]


def _get_work_style(company_name: str) -> str:
    """Get company work style"""
    return "Hybrid with flexible remote options and collaborative in-person work"


def _is_market_leader(company_name: str) -> bool:
    """Check if company is a market leader"""
    leaders = ["Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix"]
    return company_name in leaders


def _get_competitive_advantages(company_name: str) -> List[str]:
    """Get company competitive advantages"""
    return [
        "Strong technology platform",
        "Talented workforce",
        "Global market presence",
        "Innovation culture"
    ]


def _create_personalized_cover_letter(user_name: str, company_name: str, job_title: str,
                                     job_data: Dict[str, Any], user_profile: Dict[str, Any],
                                     company_insights: Dict[str, Any]) -> str:
    """Create personalized cover letter content"""
    
    # Extract user information
    user_experience = user_profile.get("experience", [])
    user_skills = user_profile.get("skills", [])
    user_achievements = user_profile.get("achievements", [])
    
    # Get relevant experience
    relevant_experience = _get_most_relevant_experience(user_experience, job_title)
    top_skills = user_skills[:5] if user_skills else ["problem-solving", "communication", "teamwork"]
    
    # Generate cover letter sections
    opening = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. Having researched {company_name}'s mission to {company_insights.get('company_mission', 'drive innovation')}, I am excited about the opportunity to contribute to your team's continued success."""

    experience_paragraph = f"""In my previous role as {relevant_experience.get('title', 'a professional')}, I have developed expertise in {', '.join(top_skills[:3])}. """
    
    if user_achievements:
        achievement = user_achievements[0] if isinstance(user_achievements, list) else str(user_achievements)
        experience_paragraph += f"One of my key accomplishments includes {achievement}, which demonstrates my ability to deliver results that align with {company_name}'s standards of excellence."
    else:
        experience_paragraph += f"I have consistently delivered high-quality results while working collaboratively with cross-functional teams."

    company_connection = f"""What particularly attracts me to {company_name} is your commitment to {', '.join(company_insights.get('values_alignment', ['innovation', 'excellence'])[:2])}. Your recent initiatives in {company_insights.get('recent_news', ['technology advancement'])[0] if company_insights.get('recent_news') else 'industry leadership'} align perfectly with my passion for driving meaningful impact through technology."""

    skills_alignment = f"""My technical skills in {', '.join(top_skills[:4])} directly support the requirements outlined in your job posting. I am particularly excited about the opportunity to {_get_role_specific_excitement(job_title)} while contributing to {company_name}'s mission."""

    closing = f"""I would welcome the opportunity to discuss how my background and enthusiasm can contribute to {company_name}'s continued success. Thank you for considering my application, and I look forward to hearing from you.

Best regards,
{user_name}"""

    cover_letter = f"{opening}\n\n{experience_paragraph}\n\n{company_connection}\n\n{skills_alignment}\n\n{closing}"
    
    return cover_letter


def _get_most_relevant_experience(experience_list: List[Dict], job_title: str) -> Dict[str, Any]:
    """Get most relevant experience entry"""
    if not experience_list:
        return {"title": "Professional", "company": "Previous Role"}
    
    # Simple relevance matching - in production, use more sophisticated matching
    for exp in experience_list:
        if any(word in exp.get("title", "").lower() for word in job_title.lower().split()):
            return exp
    
    return experience_list[0]  # Return first experience if no match


def _get_role_specific_excitement(job_title: str) -> str:
    """Get role-specific excitement statement"""
    excitement_map = {
        "engineer": "develop innovative solutions and work with cutting-edge technologies",
        "manager": "lead talented teams and drive strategic initiatives",  
        "designer": "create exceptional user experiences and innovative designs",
        "analyst": "derive insights from data and support data-driven decisions",
        "consultant": "solve complex business challenges and drive organizational success"
    }
    
    for key, excitement in excitement_map.items():
        if key in job_title.lower():
            return excitement
    
    return "make a meaningful impact and contribute to innovative projects"


def _extract_key_highlights(cover_letter: str, user_experience: List[Dict], job_data: Dict[str, Any]) -> List[str]:
    """Extract key highlights from cover letter"""
    highlights = []
    
    # Extract from user experience
    if user_experience:
        highlights.append(f"Experience as {user_experience[0].get('title', 'Professional')}")
    
    # Extract from job alignment
    job_skills = job_data.get("skills", [])
    if job_skills:
        highlights.append(f"Skills alignment with {len(job_skills)} required competencies")
    
    # Extract from cover letter content
    if "achievement" in cover_letter.lower():
        highlights.append("Quantified achievements and impact metrics")
    
    if "mission" in cover_letter.lower():
        highlights.append("Company mission and values alignment")
    
    if "passion" in cover_letter.lower():
        highlights.append("Demonstrated passion for role and industry")
    
    return highlights[:5]  # Return top 5 highlights


def _calculate_customization_score(cover_letter: str, job_data: Dict[str, Any], company_insights: Dict[str, Any]) -> int:
    """Calculate customization score for cover letter"""
    score = 60  # Base score
    
    # Check for company name mentions
    company_name = job_data.get("company", "")
    if company_name and company_name.lower() in cover_letter.lower():
        score += 15
    
    # Check for job title mentions
    job_title = job_data.get("title", "")
    if job_title and job_title.lower() in cover_letter.lower():
        score += 10
    
    # Check for skills alignment
    job_skills = job_data.get("skills", [])
    skill_matches = sum(1 for skill in job_skills if skill.lower() in cover_letter.lower())
    score += min(skill_matches * 3, 15)
    
    # Check for company insights integration
    if any(value.lower() in cover_letter.lower() for value in company_insights.get("values_alignment", [])):
        score += 10
    
    return min(score, 100)


def _customize_opening_paragraph(base_letter: str, company_culture: Dict[str, Any]) -> str:
    """Customize opening paragraph with company culture insights"""
    lines = base_letter.split('\n')
    opening_lines = lines[:3]  # First 3 lines typically contain opening
    
    # Add company culture element
    culture_values = company_culture.get("company_overview", {}).get("values", [])
    if culture_values:
        opening_lines.append(f"I am particularly drawn to your commitment to {culture_values[0].lower()}.")
    
    return '\n'.join(opening_lines)


def _align_experience_with_requirements(base_letter: str, job_requirements: List[str], user_achievements: List[str]) -> str:
    """Align experience section with job requirements"""
    # Extract experience section (typically middle paragraphs)
    lines = base_letter.split('\n')
    experience_section = []
    
    # Add requirement-specific experience
    if job_requirements:
        req = job_requirements[0]
        experience_section.append(f"My experience directly addresses your requirement for {req.lower()}.")
    
    # Add user achievements if available
    if user_achievements:
        achievement = user_achievements[0]
        experience_section.append(f"Specifically, {achievement}")
    
    return '\n'.join(experience_section)


def _add_company_specific_insights(base_letter: str, company_culture: Dict[str, Any]) -> str:
    """Add company-specific insights to demonstrate research"""
    insights = []
    
    recent_initiatives = company_culture.get("recent_initiatives", [])
    if recent_initiatives:
        insights.append(f"I am impressed by your recent focus on {recent_initiatives[0].lower()}.")
    
    work_environment = company_culture.get("work_environment", {})
    if work_environment.get("innovation_focus"):
        insights.append("Your emphasis on innovation aligns perfectly with my career aspirations.")
    
    return '\n'.join(insights)


def _enhance_closing_paragraph(base_letter: str, company_culture: Dict[str, Any]) -> str:
    """Enhance closing paragraph with cultural fit"""
    closing = "I am excited about the opportunity to contribute to your team's success"
    
    culture_keywords = company_culture.get("company_overview", {}).get("culture_keywords", [])
    if culture_keywords:
        closing += f" while embracing your {culture_keywords[0]} culture"
    
    closing += ". I look forward to discussing how my background can add value to your organization."
    
    return closing


def _assemble_customized_letter(opening: str, experience: str, insights: str, closing: str) -> str:
    """Assemble final customized cover letter"""
    sections = [opening, experience, insights, closing]
    return '\n\n'.join(section for section in sections if section.strip())


def _get_improvement_suggestions(cover_letter: str) -> List[str]:
    """Generate improvement suggestions for cover letter"""
    suggestions = []
    
    word_count = len(cover_letter.split())
    if word_count > 400:
        suggestions.append("Consider shortening the letter for better readability (target: 300-350 words)")
    elif word_count < 250:
        suggestions.append("Consider adding more specific examples and achievements")
    
    if "I" in cover_letter[:100]:  # Check opening
        suggestions.append("Consider starting with a company-focused opening rather than 'I'")
    
    if cover_letter.count("innovative") > 2:
        suggestions.append("Vary descriptive language to avoid repetition")
    
    if not any(char.isdigit() for char in cover_letter):
        suggestions.append("Include quantified achievements for stronger impact")
    
    return suggestions


# Create the agent instance
cover_letter_agent = create_cover_letter_agent()