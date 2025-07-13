"""
Configuration management for InterviewAgent
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables"""
        
        # Supabase Configuration
        self.SUPABASE_URL = os.getenv('SUPABASE_URL')
        self.SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        self.SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        
        # Gmail Configuration
        self.GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
        self.GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
        
        # Encryption
        self.ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
        
        # Application Settings
        self.APP_NAME = os.getenv('APP_NAME', 'InterviewAgent')
        self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # User Configuration (Single User MVP)
        self.USER_NAME = os.getenv('USER_NAME', 'User')
        self.USER_EMAIL = os.getenv('USER_EMAIL', 'user@example.com')
        
        # Paths
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self.DATA_DIR = self.PROJECT_ROOT / 'data'
        self.TEMPLATES_DIR = self.PROJECT_ROOT / 'templates'
        self.LOGS_DIR = self.PROJECT_ROOT / 'logs'
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.TEMPLATES_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY', 
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            'APP_NAME': self.APP_NAME,
            'DEBUG': self.DEBUG,
            'LOG_LEVEL': self.LOG_LEVEL,
            'USER_NAME': self.USER_NAME,
            'USER_EMAIL': self.USER_EMAIL,
            'PROJECT_ROOT': str(self.PROJECT_ROOT),
            'DATA_DIR': str(self.DATA_DIR),
            'TEMPLATES_DIR': str(self.TEMPLATES_DIR),
            'LOGS_DIR': str(self.LOGS_DIR)
        }

# Global configuration instance
_config = None

def load_config() -> Dict[str, Any]:
    """Load and return configuration as dictionary"""
    global _config
    if _config is None:
        _config = Config()
        _config.validate_config()
    return _config.to_dict()

def get_config() -> Config:
    """Get configuration instance"""
    global _config
    if _config is None:
        _config = Config()
        _config.validate_config()
    return _config

# Job site configurations
JOB_SITES_CONFIG = {
    'linkedin': {
        'name': 'LinkedIn',
        'url': 'https://www.linkedin.com/jobs',
        'search_url': 'https://www.linkedin.com/jobs/search',
        'requires_login': True,
        'selectors': {
            'job_cards': '[data-job-id]',
            'job_title': '.job-search-card__title',
            'company': '.job-search-card__subtitle-link',
            'location': '.job-search-card__location',
            'apply_button': '.jobs-apply-button'
        }
    },
    'indeed': {
        'name': 'Indeed',
        'url': 'https://www.indeed.com',
        'search_url': 'https://www.indeed.com/jobs',
        'requires_login': False,
        'selectors': {
            'job_cards': '[data-jk]',
            'job_title': '[data-testid="job-title"]',
            'company': '[data-testid="company-name"]',
            'location': '[data-testid="job-location"]',
            'apply_button': '.jobsearch-ApplyButton'
        }
    },
    'glassdoor': {
        'name': 'Glassdoor',
        'url': 'https://www.glassdoor.com',
        'search_url': 'https://www.glassdoor.com/Job',
        'requires_login': True,
        'selectors': {
            'job_cards': '[data-test="job-card"]',
            'job_title': '[data-test="job-title"]',
            'company': '[data-test="employer-name"]',
            'location': '[data-test="job-location"]',
            'apply_button': '[data-test="apply-button"]'
        }
    }
}

# Default user preferences
DEFAULT_USER_PREFERENCES = {
    'job_search': {
        'keywords': ['software engineer', 'developer', 'programmer'],
        'location': 'Remote',
        'salary_min': 80000,
        'experience_level': 'mid-level',
        'job_types': ['full-time', 'contract'],
        'remote_preference': 'remote_only'
    },
    'automation': {
        'auto_apply': False,
        'max_applications_per_day': 10,
        'schedule_enabled': False,
        'schedule_time': '09:00',
        'notification_email': True
    },
    'filters': {
        'exclude_keywords': ['senior', 'lead', 'manager'],
        'company_blacklist': [],
        'min_company_size': 10,
        'industry_preferences': []
    }
}