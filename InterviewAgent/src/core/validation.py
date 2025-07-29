"""
Input validation utilities for InterviewAgent

Provides comprehensive validation for user inputs, API data, and system parameters.
"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

from .protocols import IValidator
from .exceptions import ValidationError

class InputValidator(IValidator):
    """Comprehensive input validator"""
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # API key patterns
    API_KEY_PATTERNS = {
        'openai': re.compile(r'^sk-[a-zA-Z0-9]{48}$|^sk-proj-[a-zA-Z0-9]{48}$'),
        'supabase': re.compile(r'^[a-zA-Z0-9]{64}$'),
        'anthropic': re.compile(r'^sk-ant-[a-zA-Z0-9\-_]{95}$')
    }
    
    # Job title patterns (common job titles)
    JOB_TITLE_KEYWORDS = {
        'software', 'engineer', 'developer', 'programmer', 'architect',
        'manager', 'lead', 'senior', 'junior', 'intern', 'analyst',
        'scientist', 'consultant', 'specialist', 'coordinator', 'director'
    }
    
    # Suspicious input patterns
    SUSPICIOUS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'(union|select|insert|update|delete|drop|create|alter)\s+', re.IGNORECASE),
        re.compile(r'\.\./', re.IGNORECASE),
        re.compile(r'[<>"\']', re.IGNORECASE)
    ]
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format and deliverability"""
        if not email or not isinstance(email, str):
            return False
        
        try:
            # Basic format check
            if not self.EMAIL_PATTERN.match(email):
                return False
            
            # Use email-validator for comprehensive validation
            validated_email = validate_email(email)
            return bool(validated_email)
            
        except (EmailNotValidError, Exception):
            return False
    
    def validate_api_key(self, key: str, key_type: str) -> bool:
        """Validate API key format for specific service"""
        if not key or not isinstance(key, str):
            return False
        
        if key_type not in self.API_KEY_PATTERNS:
            # Generic validation for unknown key types
            return 20 <= len(key) <= 200 and key.isalnum() or '-' in key or '_' in key
        
        pattern = self.API_KEY_PATTERNS[key_type]
        return bool(pattern.match(key))
    
    def validate_job_data(self, job_data: Dict[str, Any]) -> bool:
        """Validate job listing data structure and content"""
        if not isinstance(job_data, dict):
            return False
        
        # Required fields
        required_fields = ['title', 'company', 'location', 'description']
        for field in required_fields:
            if field not in job_data or not job_data[field]:
                return False
        
        # Validate individual fields
        try:
            # Title validation
            if not self._validate_job_title(job_data['title']):
                return False
            
            # Company validation
            if not self._validate_company_name(job_data['company']):
                return False
            
            # Location validation
            if not self._validate_location(job_data['location']):
                return False
            
            # Description validation
            if not self._validate_job_description(job_data['description']):
                return False
            
            # URL validation (if provided)
            if 'url' in job_data and job_data['url']:
                if not self._validate_url(job_data['url']):
                    return False
            
            # Salary validation (if provided)
            if 'salary_range' in job_data and job_data['salary_range']:
                if not self._validate_salary_range(job_data['salary_range']):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not isinstance(input_data, str):
            return str(input_data) if input_data is not None else ""
        
        # Remove suspicious patterns
        sanitized = input_data
        for pattern in self.SUSPICIOUS_PATTERNS:
            sanitized = pattern.sub('', sanitized)
        
        # Basic HTML entity encoding for safety
        sanitized = (sanitized
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        
        return sanitized.strip()
    
    def _validate_job_title(self, title: str) -> bool:
        """Validate job title"""
        if not title or len(title) < 3 or len(title) > 200:
            return False
        
        # Check for suspicious content
        if any(pattern.search(title) for pattern in self.SUSPICIOUS_PATTERNS):
            return False
        
        # Check if it contains at least one job-related keyword
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in self.JOB_TITLE_KEYWORDS)
    
    def _validate_company_name(self, company: str) -> bool:
        """Validate company name"""
        if not company or len(company) < 2 or len(company) > 100:
            return False
        
        # Check for suspicious content
        if any(pattern.search(company) for pattern in self.SUSPICIOUS_PATTERNS):
            return False
        
        # Basic company name pattern (letters, numbers, spaces, common punctuation)
        company_pattern = re.compile(r'^[a-zA-Z0-9\s\.\-&,\'()]+$')
        return bool(company_pattern.match(company))
    
    def _validate_location(self, location: str) -> bool:
        """Validate job location"""
        if not location or len(location) < 2 or len(location) > 100:
            return False
        
        # Check for suspicious content
        if any(pattern.search(location) for pattern in self.SUSPICIOUS_PATTERNS):
            return False
        
        # Remote locations are valid
        if location.lower() in ['remote', 'work from home', 'anywhere']:
            return True
        
        # Basic location pattern (letters, spaces, commas, periods)
        location_pattern = re.compile(r'^[a-zA-Z\s\.,\-()]+$')
        return bool(location_pattern.match(location))
    
    def _validate_job_description(self, description: str) -> bool:
        """Validate job description"""
        if not description or len(description) < 50 or len(description) > 10000:
            return False
        
        # Check for suspicious content (more lenient for descriptions)
        script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
        if script_pattern.search(description):
            return False
        
        return True
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url or len(url) > 2000:
            return False
        
        try:
            parsed = urllib.parse.urlparse(url)
            return bool(parsed.scheme in ['http', 'https'] and parsed.netloc)
        except Exception:
            return False
    
    def _validate_salary_range(self, salary_range: Union[Dict, str]) -> bool:
        """Validate salary range data"""
        if isinstance(salary_range, str):
            # Simple string validation
            return len(salary_range) <= 100 and not any(pattern.search(salary_range) for pattern in self.SUSPICIOUS_PATTERNS)
        
        if isinstance(salary_range, dict):
            # Structured salary data
            if 'min' in salary_range and 'max' in salary_range:
                try:
                    min_salary = int(salary_range['min'])
                    max_salary = int(salary_range['max'])
                    return 0 <= min_salary <= max_salary <= 1000000  # Reasonable salary range
                except (ValueError, TypeError):
                    return False
        
        return False
    
    def validate_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Validate user preferences structure"""
        if not isinstance(preferences, dict):
            return False
        
        try:
            # Validate job search preferences
            if 'job_search' in preferences:
                job_prefs = preferences['job_search']
                if not isinstance(job_prefs, dict):
                    return False
                
                # Validate keywords
                if 'keywords' in job_prefs:
                    keywords = job_prefs['keywords']
                    if not isinstance(keywords, list) or len(keywords) > 50:
                        return False
                    
                    for keyword in keywords:
                        if not isinstance(keyword, str) or len(keyword) > 50:
                            return False
                
                # Validate salary range
                if 'salary_min' in job_prefs:
                    salary_min = job_prefs['salary_min']
                    if not isinstance(salary_min, (int, float)) or salary_min < 0:
                        return False
            
            # Validate automation preferences
            if 'automation' in preferences:
                auto_prefs = preferences['automation']
                if not isinstance(auto_prefs, dict):
                    return False
                
                # Validate max applications per day
                if 'max_applications_per_day' in auto_prefs:
                    max_apps = auto_prefs['max_applications_per_day']
                    if not isinstance(max_apps, int) or not (1 <= max_apps <= 100):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def validate_agent_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate agent task data"""
        if not isinstance(task_data, dict):
            return False
        
        # Required fields
        required_fields = ['task_type', 'description']
        for field in required_fields:
            if field not in task_data or not task_data[field]:
                return False
        
        # Validate task type
        valid_task_types = [
            'discover_jobs', 'optimize_resume', 'generate_cover_letter',
            'submit_application', 'send_notification'
        ]
        if task_data['task_type'] not in valid_task_types:
            return False
        
        # Validate description length
        description = task_data['description']
        if not isinstance(description, str) or len(description) < 10 or len(description) > 500:
            return False
        
        # Validate priority if provided
        if 'priority' in task_data:
            valid_priorities = ['low', 'medium', 'high', 'critical']
            if task_data['priority'] not in valid_priorities:
                return False
        
        return True
    
    def validate_search_criteria(self, criteria: Dict[str, Any]) -> bool:
        """Validate job search criteria"""
        if not isinstance(criteria, dict):
            return False
        
        try:
            # Validate keywords
            if 'keywords' in criteria:
                keywords = criteria['keywords']
                if keywords is not None:
                    if not isinstance(keywords, list) or len(keywords) > 20:
                        return False
                    
                    for keyword in keywords:
                        if not isinstance(keyword, str) or len(keyword) > 50:
                            return False
                        
                        # Check for suspicious content
                        if any(pattern.search(keyword) for pattern in self.SUSPICIOUS_PATTERNS):
                            return False
            
            # Validate location
            if 'location' in criteria and criteria['location']:
                if not self._validate_location(criteria['location']):
                    return False
            
            # Validate company
            if 'company' in criteria and criteria['company']:
                if not self._validate_company_name(criteria['company']):
                    return False
            
            # Validate salary range
            if 'salary_min' in criteria:
                salary_min = criteria['salary_min']
                if salary_min is not None and (not isinstance(salary_min, (int, float)) or salary_min < 0):
                    return False
            
            if 'salary_max' in criteria:
                salary_max = criteria['salary_max']
                if salary_max is not None and (not isinstance(salary_max, (int, float)) or salary_max < 0):
                    return False
            
            # Validate limit
            if 'limit' in criteria:
                limit = criteria['limit']
                if not isinstance(limit, int) or not (1 <= limit <= 1000):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def validate_file_upload(self, file_data: Dict[str, Any]) -> bool:
        """Validate file upload data"""
        if not isinstance(file_data, dict):
            return False
        
        # Required fields
        required_fields = ['filename', 'content_type', 'size']
        for field in required_fields:
            if field not in file_data:
                return False
        
        # Validate filename
        filename = file_data['filename']
        if not isinstance(filename, str) or len(filename) > 255:
            return False
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Validate file extension
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return False
        
        # Validate content type
        content_type = file_data['content_type']
        allowed_types = [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'application/rtf'
        ]
        if content_type not in allowed_types:
            return False
        
        # Validate file size (max 10MB)
        size = file_data['size']
        if not isinstance(size, int) or size > 10 * 1024 * 1024:
            return False
        
        return True