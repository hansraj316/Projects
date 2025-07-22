"""
AI-powered resume parser for InterviewAgent
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import the agents
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from config import get_config

logger = logging.getLogger(__name__)

class ResumeParser(BaseAgent):
    """AI-powered resume parser that structures raw text into organized resume data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="resume_parser",
            description="You are an expert resume parser and data extraction specialist. You analyze resume text and extract structured information including personal details, work experience, education, skills, and other relevant sections. You format this information in a standardized JSON structure.",
            config=config
        )
    
    async def execute(self, task, context):
        """Execute resume parsing task (required by BaseAgent)"""
        return await self.parse_resume_text(task.input_data.get("text", ""))
    
    async def parse_resume_text(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured information
        
        Args:
            resume_text: Raw text extracted from resume file
            
        Returns:
            Structured resume data
        """
        try:
            if not resume_text or not resume_text.strip():
                return {
                    "success": False,
                    "error": "No text provided for parsing"
                }
            
            # Use AI to parse the resume
            parsing_prompt = self._create_parsing_prompt(resume_text)
            parsed_result = self.get_response(parsing_prompt)
            
            # Parse the AI response
            structured_data = self._parse_ai_response(parsed_result)
            
            # Validate and clean the structured data
            cleaned_data = self._validate_and_clean_data(structured_data)
            
            # Add metadata
            cleaned_data.update({
                "parsed_at": datetime.now().isoformat(),
                "text_length": len(resume_text),
                "word_count": len(resume_text.split()),
                "parser_version": "1.0"
            })
            
            logger.info("Resume parsed successfully")
            return {
                "success": True,
                "data": cleaned_data,
                "message": "Resume parsed successfully"
            }
            
        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
            return {
                "success": False,
                "error": f"Failed to parse resume: {str(e)}"
            }
    
    def _create_parsing_prompt(self, resume_text: str) -> str:
        """Create parsing prompt for AI"""
        return f"""
        Please analyze this resume text and extract all information into a structured JSON format:

        Resume Text:
        {resume_text}

        Extract the following information and format as JSON:

        {{
            "personal_info": {{
                "name": "Full name",
                "email": "email@example.com",
                "phone": "phone number",
                "location": "city, state/country",
                "linkedin": "LinkedIn URL if found",
                "github": "GitHub URL if found",
                "portfolio": "Portfolio/website URL if found"
            }},
            "professional_summary": "Professional summary or objective statement",
            "skills": {{
                "technical": ["list of technical skills"],
                "soft": ["list of soft skills"],
                "languages": ["programming languages if applicable"],
                "tools": ["software tools and platforms"],
                "other": ["other relevant skills"]
            }},
            "experience": [
                {{
                    "company": "Company name",
                    "position": "Job title/position",
                    "location": "City, State",
                    "start_date": "Start date",
                    "end_date": "End date or Present",
                    "duration": "Duration calculated",
                    "description": "Job description",
                    "achievements": ["List of achievements and responsibilities"],
                    "technologies": ["Technologies used in this role"]
                }}
            ],
            "education": [
                {{
                    "institution": "School/University name",
                    "degree": "Degree type and field",
                    "location": "City, State",
                    "graduation_date": "Graduation date or year",
                    "gpa": "GPA if mentioned",
                    "honors": "Any honors or distinctions",
                    "relevant_coursework": ["Relevant courses if mentioned"]
                }}
            ],
            "certifications": [
                {{
                    "name": "Certification name",
                    "issuer": "Issuing organization",
                    "date": "Date obtained",
                    "expiry": "Expiry date if applicable",
                    "credential_id": "ID if provided"
                }}
            ],
            "projects": [
                {{
                    "name": "Project name",
                    "description": "Project description",
                    "technologies": ["Technologies used"],
                    "url": "Project URL if available",
                    "date": "Project date or duration"
                }}
            ],
            "awards": [
                {{
                    "name": "Award name",
                    "issuer": "Issuing organization",
                    "date": "Date received",
                    "description": "Award description"
                }}
            ],
            "publications": [
                {{
                    "title": "Publication title",
                    "authors": ["Author names"],
                    "journal": "Journal or conference name",
                    "date": "Publication date",
                    "url": "URL if available"
                }}
            ],
            "volunteer_experience": [
                {{
                    "organization": "Organization name",
                    "position": "Volunteer position",
                    "duration": "Duration",
                    "description": "Description of work"
                }}
            ]
        }}

        Instructions:
        1. Extract all available information from the resume text
        2. If information is not found, use null for that field
        3. Be accurate and don't make up information
        4. Preserve the original formatting and terminology used in the resume
        5. For dates, keep the original format from the resume
        6. Return only valid JSON, no additional text
        7. If multiple phone numbers or emails exist, include the primary one
        8. Group similar skills appropriately in the skills categories
        """
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON data"""
        try:
            # Try to parse as JSON directly
            return json.loads(ai_response)
        except json.JSONDecodeError:
            try:
                # Try to find JSON within the response
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    # Create fallback structure
                    return self._create_fallback_structure(ai_response)
            except Exception as e:
                logger.warning(f"Could not parse AI response as JSON: {e}")
                return self._create_fallback_structure(ai_response)
    
    def _create_fallback_structure(self, ai_response: str) -> Dict[str, Any]:
        """Create fallback structure when JSON parsing fails"""
        # Basic extraction using regex patterns
        name = self._extract_name(ai_response)
        email = self._extract_email(ai_response)
        phone = self._extract_phone(ai_response)
        
        return {
            "personal_info": {
                "name": name,
                "email": email,
                "phone": phone,
                "location": None,
                "linkedin": self._extract_linkedin(ai_response),
                "github": self._extract_github(ai_response),
                "portfolio": None
            },
            "professional_summary": self._extract_summary(ai_response),
            "skills": {
                "technical": [],
                "soft": [],
                "languages": [],
                "tools": [],
                "other": []
            },
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "awards": [],
            "publications": [],
            "volunteer_experience": [],
            "parsing_note": "Fallback parsing used - manual review recommended"
        }
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name using regex patterns"""
        # Look for name patterns at the beginning of the resume
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            # Simple name pattern: 2-4 words, starting with capital letters
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2}$', line):
                return line
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'  # International
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL"""
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9-]+'
        matches = re.findall(linkedin_pattern, text)
        return matches[0] if matches else None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL"""
        github_pattern = r'https?://(?:www\.)?github\.com/[A-Za-z0-9-]+'
        matches = re.findall(github_pattern, text)
        return matches[0] if matches else None
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary"""
        # Look for common summary section headers
        summary_keywords = [
            'summary', 'professional summary', 'profile', 'objective',
            'career objective', 'professional profile', 'about'
        ]
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            for keyword in summary_keywords:
                if keyword in line_lower and len(line_lower) < 50:
                    # Found a section header, get the content
                    summary_lines = []
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not self._is_section_header(next_line):
                            summary_lines.append(next_line)
                        elif summary_lines:  # Stop if we hit another section
                            break
                    
                    if summary_lines:
                        return ' '.join(summary_lines)
        
        return None
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is likely a section header"""
        header_keywords = [
            'experience', 'education', 'skills', 'certifications',
            'projects', 'awards', 'publications', 'volunteer'
        ]
        
        line_lower = line.lower().strip()
        return (
            any(keyword in line_lower for keyword in header_keywords) and
            len(line) < 50 and
            not line.endswith('.')
        )
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the parsed data"""
        if not isinstance(data, dict):
            return self._create_empty_structure()
        
        # Ensure all required sections exist
        required_sections = [
            'personal_info', 'professional_summary', 'skills', 'experience',
            'education', 'certifications', 'projects', 'awards',
            'publications', 'volunteer_experience'
        ]
        
        for section in required_sections:
            if section not in data:
                if section == 'personal_info':
                    data[section] = {}
                elif section == 'skills':
                    data[section] = {
                        "technical": [], "soft": [], "languages": [],
                        "tools": [], "other": []
                    }
                elif section == 'professional_summary':
                    data[section] = None
                else:
                    data[section] = []
        
        # Clean personal info
        if not isinstance(data['personal_info'], dict):
            data['personal_info'] = {}
        
        personal_fields = ['name', 'email', 'phone', 'location', 'linkedin', 'github', 'portfolio']
        for field in personal_fields:
            if field not in data['personal_info']:
                data['personal_info'][field] = None
        
        # Clean skills section
        if not isinstance(data['skills'], dict):
            data['skills'] = {"technical": [], "soft": [], "languages": [], "tools": [], "other": []}
        
        skill_categories = ['technical', 'soft', 'languages', 'tools', 'other']
        for category in skill_categories:
            if category not in data['skills'] or not isinstance(data['skills'][category], list):
                data['skills'][category] = []
        
        # Ensure list sections are actually lists
        list_sections = ['experience', 'education', 'certifications', 'projects', 'awards', 'publications', 'volunteer_experience']
        for section in list_sections:
            if not isinstance(data[section], list):
                data[section] = []
        
        return data
    
    def _create_empty_structure(self) -> Dict[str, Any]:
        """Create empty resume structure"""
        return {
            "personal_info": {
                "name": None,
                "email": None,
                "phone": None,
                "location": None,
                "linkedin": None,
                "github": None,
                "portfolio": None
            },
            "professional_summary": None,
            "skills": {
                "technical": [],
                "soft": [],
                "languages": [],
                "tools": [],
                "other": []
            },
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "awards": [],
            "publications": [],
            "volunteer_experience": []
        }


def parse_resume_from_text(resume_text: str, config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function to parse resume text
    
    Args:
        resume_text: Raw text from resume
        config: Optional configuration
        
    Returns:
        Parsed resume data
    """
    try:
        if not config:
            config = get_config()
        
        parser = ResumeParser(config.__dict__ if hasattr(config, '__dict__') else config)
        
        # Use sync parsing for convenience function
        parsing_prompt = parser._create_parsing_prompt(resume_text)
        parsed_result = parser.get_response(parsing_prompt)
        structured_data = parser._parse_ai_response(parsed_result)
        cleaned_data = parser._validate_and_clean_data(structured_data)
        
        # Add metadata
        cleaned_data.update({
            "parsed_at": datetime.now().isoformat(),
            "text_length": len(resume_text),
            "word_count": len(resume_text.split()),
            "parser_version": "1.0"
        })
        
        return {
            "success": True,
            "data": cleaned_data,
            "message": "Resume parsed successfully"
        }
        
    except Exception as e:
        logger.error(f"Resume parsing error: {e}")
        return {
            "success": False,
            "error": f"Failed to parse resume: {str(e)}"
        }