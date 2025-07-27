"""
Database models and operations for InterviewAgent
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json

class ApplicationStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FAILED = "failed"
    CONFIRMED = "confirmed"

class JobStatus(Enum):
    DISCOVERED = "discovered"
    FILTERED = "filtered"
    APPLIED = "applied"
    REJECTED = "rejected"

class AgentStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class User:
    """User model for single-user MVP"""
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class ResumeTemplate:
    """Resume template model"""
    id: str
    user_id: str
    name: str
    content: str
    file_url: Optional[str] = None
    is_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class JobSite:
    """Job site configuration model"""
    id: str
    user_id: str
    name: str
    url: str
    is_enabled: bool = True
    credentials_encrypted: Optional[str] = None
    last_scraped: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Company:
    """Company model for career page tracking"""
    id: str
    name: str
    domain: str
    career_page_url: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_active: bool = True
    last_scraped: Optional[datetime] = None
    jobs_found_count: int = 0
    scraping_difficulty: Optional[str] = None  # easy, medium, hard
    scraping_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class JobListing:
    """Job listing model"""
    id: str
    job_site_id: str
    title: str
    company: str
    job_url: str  # Required field - always save job URLs
    location: Optional[str] = None
    description: str = ""
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    company_id: Optional[str] = None  # Link to Company model
    remote_type: Optional[str] = None  # remote, hybrid, onsite
    experience_level: Optional[str] = None  # entry, mid, senior
    job_type: Optional[str] = None  # full-time, part-time, contract
    auto_apply_enabled: bool = True  # Enable automatic application
    application_priority: int = 5  # 1-10 priority for application order
    scraped_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    status: JobStatus = JobStatus.DISCOVERED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Application:
    """Application model"""
    id: str
    user_id: str
    job_listing_id: str
    resume_template_id: str
    cover_letter_content: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    application_data: Optional[Dict[str, Any]] = None
    submitted_at: Optional[datetime] = None
    confirmation_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Schedule:
    """Schedule model for automation"""
    id: str
    user_id: str
    name: str
    cron_expression: str
    is_active: bool = True
    job_sites: List[str] = None
    filters: Dict[str, Any] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.job_sites is None:
            self.job_sites = []
        if self.filters is None:
            self.filters = {}

@dataclass
class AgentLog:
    """Agent activity log model"""
    id: str
    user_id: Optional[str]
    agent_type: str
    action: str
    status: AgentStatus = AgentStatus.STARTED
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class AgentResult:
    """Agent result model for storing agent outputs"""
    id: str
    user_id: str
    agent_type: str
    task_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CoverLetter:
    """Cover letter model for storing generated cover letters"""
    id: str
    user_id: str
    job_title: str
    company_name: str
    cover_letter_content: str
    quality_score: Optional[int] = None
    generation_type: str = "standard"
    agent_result_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class OptimizedResume:
    """Optimized resume model for storing resume optimizations"""
    id: str
    user_id: str
    original_resume_id: str
    job_title: str
    company_name: str
    optimized_content: str
    job_match_score: Optional[int] = None
    optimization_type: str = "standard"
    agent_result_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class JobSearch:
    """Job search model for storing job search results"""
    id: str
    user_id: str
    search_query: str
    search_criteria: Dict[str, Any]
    jobs_found: int
    search_results: Dict[str, Any]
    agent_result_id: Optional[str] = None
    created_at: Optional[datetime] = None

# Utility functions for model conversion
def dict_to_model(data: Dict[str, Any], model_class):
    """Convert dictionary to model instance"""
    if not data:
        return None
    
    # Handle datetime conversion
    datetime_fields = ['created_at', 'updated_at', 'scraped_at', 'applied_at', 'submitted_at', 'last_run', 'next_run', 'last_scraped']
    
    for field in datetime_fields:
        if field in data and data[field]:
            if isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    data[field] = None
    
    # Handle enum conversion
    if model_class == Application and 'status' in data:
        if isinstance(data['status'], str):
            data['status'] = ApplicationStatus(data['status'])
    
    if model_class == JobListing and 'status' in data:
        if isinstance(data['status'], str):
            data['status'] = JobStatus(data['status'])
    
    if model_class == AgentLog and 'status' in data:
        if isinstance(data['status'], str):
            data['status'] = AgentStatus(data['status'])
    
    # Handle JSON fields
    json_fields = ['application_data', 'confirmation_data', 'filters', 'data', 'job_sites']
    for field in json_fields:
        if field in data and isinstance(data[field], str):
            try:
                data[field] = json.loads(data[field])
            except (json.JSONDecodeError, TypeError):
                if field == 'job_sites':
                    data[field] = []
                else:
                    data[field] = {}
    
    # Filter data to only include fields that exist in the model
    import inspect
    model_fields = [param.name for param in inspect.signature(model_class).parameters.values()]
    filtered_data = {k: v for k, v in data.items() if k in model_fields}
    
    try:
        return model_class(**filtered_data)
    except TypeError as e:
        # Log the error and return None
        import logging
        logging.error(f"Failed to create {model_class.__name__} from data: {filtered_data}, error: {str(e)}")
        return None

def model_to_dict(model_instance) -> Dict[str, Any]:
    """Convert model instance to dictionary for database storage"""
    if not model_instance:
        return {}
    
    result = {}
    
    for key, value in model_instance.__dict__.items():
        if value is None:
            result[key] = None
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, Enum):
            result[key] = value.value
        elif isinstance(value, (list, dict)):
            result[key] = json.dumps(value) if value else json.dumps([]) if isinstance(value, list) else json.dumps({})
        else:
            result[key] = value
    
    return result