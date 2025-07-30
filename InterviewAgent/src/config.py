"""
Configuration management for InterviewAgent
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import openai

from src.core.security import get_security_config, SecurityError
from src.core.exceptions import ConfigurationError

# Load environment variables
load_dotenv()

@dataclass(frozen=True)
class DatabaseConfig:
    """Immutable database configuration"""
    url: str
    key: str
    service_role_key: Optional[str] = None
    
    def __post_init__(self):
        if not self.url:
            raise ConfigurationError("SUPABASE_URL is required")
        if not self.key:
            raise ConfigurationError("SUPABASE_KEY is required")

@dataclass(frozen=True)
class OpenAIConfig:
    """Immutable OpenAI configuration"""
    api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4000
    
    def __post_init__(self):
        if not self.api_key:
            raise ConfigurationError("OPENAI_API_KEY is required")
        if not (0.0 <= self.temperature <= 2.0):
            raise ConfigurationError("OpenAI temperature must be between 0.0 and 2.0")
        if not (1 <= self.max_tokens <= 128000):
            raise ConfigurationError("OpenAI max_tokens must be between 1 and 128000")

@dataclass(frozen=True)
class SecurityConfig:
    """Immutable security configuration"""
    master_key_set: bool
    encryption_enabled: bool
    environment: str
    
@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration"""
    database: DatabaseConfig
    openai: OpenAIConfig
    security: SecurityConfig
    app_name: str = "InterviewAgent"
    debug: bool = False
    log_level: str = "INFO"
    user_name: str = "User"
    user_email: str = "user@example.com"
    
    # Gmail Configuration (optional)
    gmail_email: Optional[str] = None
    gmail_app_password: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables with security validation"""
        security_config = get_security_config()
        
        # Validate security before loading sensitive data
        security_validation = security_config.validate_security_requirements()
        
        # Load secure configuration
        secure_config = security_config.get_secure_config()
        
        # Validate required configuration
        supabase_url = os.getenv('SUPABASE_URL')
        if not supabase_url:
            raise ConfigurationError("SUPABASE_URL environment variable is required")
        
        # Create configuration with secure credentials
        return cls(
            database=DatabaseConfig(
                url=supabase_url,
                key=secure_config.get('supabase_key', ''),
                service_role_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            ),
            openai=OpenAIConfig(
                api_key=secure_config.get('openai_api_key', ''),
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                temperature=cls._safe_float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
                max_tokens=cls._safe_int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
            ),
            security=SecurityConfig(
                master_key_set=security_validation['master_key_set'],
                encryption_enabled=any(api['encrypted'] for api in security_validation['api_keys'].values()),
                environment=security_validation['environment']
            ),
            app_name=os.getenv('APP_NAME', 'InterviewAgent'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            user_name=os.getenv('USER_NAME', 'User'),
            user_email=os.getenv('USER_EMAIL', 'user@example.com'),
            gmail_email=os.getenv('GMAIL_EMAIL'),
            gmail_app_password=os.getenv('GMAIL_APP_PASSWORD')
        )
    
    @staticmethod
    def _safe_float(value: str) -> float:
        """Safely convert string to float with validation"""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ConfigurationError(f"Invalid float value: {value}")
    
    @staticmethod
    def _safe_int(value: str) -> int:
        """Safely convert string to int with validation"""
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ConfigurationError(f"Invalid integer value: {value}")
    
    def validate(self) -> None:
        """Validate the complete configuration"""
        # Validate paths exist
        paths = self.get_paths()
        for path_name, path in paths.items():
            if not path.parent.exists():
                raise ConfigurationError(f"Parent directory for {path_name} does not exist: {path.parent}")
    
    def get_paths(self) -> Dict[str, Path]:
        """Get application paths"""
        project_root = Path(__file__).parent.parent
        return {
            'project_root': project_root,
            'data_dir': project_root / 'data',
            'templates_dir': project_root / 'templates',
            'logs_dir': project_root / 'logs'
        }
    
    def ensure_directories(self) -> None:
        """Create required directories if they don't exist"""
        paths = self.get_paths()
        for path_name in ['data_dir', 'templates_dir', 'logs_dir']:
            path = paths[path_name]
            path.mkdir(exist_ok=True)

class Config:
    """Legacy configuration class for backward compatibility"""
    
    def __init__(self):
        self._app_config = AppConfig.from_env()
        self._app_config.ensure_directories()
        
        # Expose legacy attributes for backward compatibility
        self._setup_legacy_attributes()
    
    def _setup_legacy_attributes(self):
        """Setup legacy attributes for backward compatibility"""
        # Database
        self.SUPABASE_URL = self._app_config.database.url
        self.SUPABASE_KEY = self._app_config.database.key
        self.SUPABASE_SERVICE_ROLE_KEY = self._app_config.database.service_role_key
        
        # OpenAI
        self.OPENAI_API_KEY = self._app_config.openai.api_key
        self.OPENAI_MODEL = self._app_config.openai.model
        self.OPENAI_TEMPERATURE = self._app_config.openai.temperature
        self.OPENAI_MAX_TOKENS = self._app_config.openai.max_tokens
        
        # Gmail
        self.GMAIL_EMAIL = self._app_config.gmail_email
        self.GMAIL_APP_PASSWORD = self._app_config.gmail_app_password
        
        # Application
        self.APP_NAME = self._app_config.app_name
        self.DEBUG = self._app_config.debug
        self.LOG_LEVEL = self._app_config.log_level
        self.USER_NAME = self._app_config.user_name
        self.USER_EMAIL = self._app_config.user_email
        
        # Paths
        paths = self._app_config.get_paths()
        self.PROJECT_ROOT = paths['project_root']
        self.DATA_DIR = paths['data_dir']
        self.TEMPLATES_DIR = paths['templates_dir']
        self.LOGS_DIR = paths['logs_dir']
        
        # Deprecated encryption key (use security module instead)
        self.ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present"""
        try:
            self._app_config.validate()
            return True
        except ConfigurationError as e:
            raise ValueError(str(e)) from e
    
    def get_openai_client(self) -> openai.OpenAI:
        """Get configured OpenAI client with security validation"""
        try:
            return openai.OpenAI(api_key=self._app_config.openai.api_key)
        except Exception as e:
            raise SecurityError("Failed to create OpenAI client") from e
    
    def get_responses_client(self) -> openai.OpenAI:
        """Get configured OpenAI client for Responses API with security validation"""
        try:
            return openai.OpenAI(api_key=self._app_config.openai.api_key)
        except Exception as e:
            raise SecurityError("Failed to create OpenAI Responses client") from e
    
    def get_app_config(self) -> AppConfig:
        """Get the immutable application configuration"""
        return self._app_config
    
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