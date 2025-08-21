"""
Comprehensive input validation framework for InterviewAgent

Provides secure validation for all user inputs, API parameters, and data structures
to prevent injection attacks and ensure data integrity.
"""

import re
import html
from typing import Any, Dict, List, Optional, Union, TypeVar, Type
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, validator, Field
from urllib.parse import urlparse
import logging

from .exceptions import ValidationError, SecurityError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class SanitizationLevel(Enum):
    """Levels of input sanitization"""
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    sanitized_data: Any
    errors: List[str]
    warnings: List[str]


class SecureInputValidator:
    """
    Comprehensive input validation and sanitization
    """
    
    # Dangerous patterns that should be rejected
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # JavaScript URLs
        r'data:.*base64',            # Base64 data URLs
        r'eval\s*\(',                # eval() calls
        r'exec\s*\(',                # exec() calls
        r'__import__',               # Import statements
        r'subprocess',               # Subprocess calls
        r'os\.system',               # OS system calls
        r'open\s*\(',                # File operations
        r'file\s*\(',                # File operations
        r'\.\./',                    # Directory traversal
        r'\/etc\/passwd',            # System file access
        r'DROP\s+TABLE',             # SQL DROP
        r'DELETE\s+FROM',            # SQL DELETE
        r'UPDATE\s+.*SET',           # SQL UPDATE
        r'INSERT\s+INTO',            # SQL INSERT
        r'UNION\s+SELECT',           # SQL UNION
        r'OR\s+1\s*=\s*1',          # SQL injection
        r"'\s*OR\s*'1'\s*=\s*'1",   # SQL injection
        r';\s*DROP',                 # SQL injection
    ]
    
    def __init__(self, sanitization_level: SanitizationLevel = SanitizationLevel.STRICT):
        self.sanitization_level = sanitization_level
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]
    
    def validate_and_sanitize(self, data: Any, field_name: str = "input") -> ValidationResult:
        """
        Validate and sanitize input data
        
        Args:
            data: Input data to validate
            field_name: Name of the field for error reporting
            
        Returns:
            ValidationResult with sanitized data and validation status
        """
        errors = []
        warnings = []
        
        try:
            if isinstance(data, str):
                sanitized_data = self._sanitize_string(data, field_name, errors, warnings)
            elif isinstance(data, dict):
                sanitized_data = self._sanitize_dict(data, field_name, errors, warnings)
            elif isinstance(data, list):
                sanitized_data = self._sanitize_list(data, field_name, errors, warnings)
            elif isinstance(data, (int, float, bool, type(None))):
                sanitized_data = data  # Safe primitive types
            else:
                errors.append(f"Unsupported data type for field '{field_name}': {type(data)}")
                sanitized_data = None
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                sanitized_data=sanitized_data,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Input validation failed for field '{field_name}'", extra={"error": str(e)})
            return ValidationResult(
                is_valid=False,
                sanitized_data=None,
                errors=[f"Validation error for field '{field_name}': Internal processing error"],
                warnings=[]
            )
    
    def _sanitize_string(self, value: str, field_name: str, errors: List[str], warnings: List[str]) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            errors.append(f"Field '{field_name}' must be a string")
            return ""
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                errors.append(f"Field '{field_name}' contains potentially dangerous content")
                logger.warning(f"Dangerous pattern detected in field '{field_name}'")
                return ""
        
        # Basic sanitization
        sanitized = value.strip()
        
        if self.sanitization_level in [SanitizationLevel.STRICT, SanitizationLevel.PARANOID]:
            # HTML escape
            sanitized = html.escape(sanitized, quote=True)
            
            # Remove null bytes
            sanitized = sanitized.replace('\x00', '')
            
            # Limit length to prevent DoS
            max_length = 10000 if self.sanitization_level == SanitizationLevel.STRICT else 1000
            if len(sanitized) > max_length:
                warnings.append(f"Field '{field_name}' truncated to {max_length} characters")
                sanitized = sanitized[:max_length]
        
        if self.sanitization_level == SanitizationLevel.PARANOID:
            # Remove any remaining suspicious characters
            sanitized = re.sub(r'[<>&"\'`]', '', sanitized)
        
        return sanitized
    
    def _sanitize_dict(self, value: dict, field_name: str, errors: List[str], warnings: List[str]) -> dict:
        """Sanitize dictionary input"""
        if not isinstance(value, dict):
            errors.append(f"Field '{field_name}' must be a dictionary")
            return {}
        
        sanitized = {}
        
        for key, val in value.items():
            # Sanitize key
            key_result = self.validate_and_sanitize(key, f"{field_name}.key")
            if not key_result.is_valid:
                errors.extend(key_result.errors)
                continue
            
            # Sanitize value
            val_result = self.validate_and_sanitize(val, f"{field_name}.{key}")
            if not val_result.is_valid:
                errors.extend(val_result.errors)
                continue
            
            sanitized[key_result.sanitized_data] = val_result.sanitized_data
            warnings.extend(key_result.warnings)
            warnings.extend(val_result.warnings)
        
        return sanitized
    
    def _sanitize_list(self, value: list, field_name: str, errors: List[str], warnings: List[str]) -> list:
        """Sanitize list input"""
        if not isinstance(value, list):
            errors.append(f"Field '{field_name}' must be a list")
            return []
        
        sanitized = []
        
        for i, item in enumerate(value):
            item_result = self.validate_and_sanitize(item, f"{field_name}[{i}]")
            if not item_result.is_valid:
                errors.extend(item_result.errors)
                continue
            
            sanitized.append(item_result.sanitized_data)
            warnings.extend(item_result.warnings)
        
        return sanitized


class JobSearchCriteriaValidator(BaseModel):
    """Validated job search criteria"""
    job_title: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    keywords: List[str] = Field(default_factory=list, max_items=20)
    salary_min: Optional[int] = Field(None, ge=0, le=1000000)
    salary_max: Optional[int] = Field(None, ge=0, le=2000000)
    experience_level: Optional[str] = Field(None, pattern=r'^(entry|junior|mid|senior|lead|executive)$')
    job_types: List[str] = Field(default_factory=list, max_items=10)
    remote_preference: Optional[str] = Field(None, pattern=r'^(onsite|hybrid|remote|remote_only)$')
    
    @validator('job_title', 'location')
    def validate_required_strings(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        # Check for SQL injection patterns
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        if any(char in v.lower() for char in dangerous_chars):
            raise ValueError('Field contains invalid characters')
        return v.strip()
    
    @validator('keywords', 'job_types')
    def validate_string_lists(cls, v):
        if not isinstance(v, list):
            return []
        validated = []
        for item in v:
            if isinstance(item, str) and item.strip() and len(item.strip()) <= 100:
                validated.append(item.strip())
        return validated[:20]  # Limit to 20 items
    
    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        if v is not None and 'salary_min' in values and values['salary_min'] is not None:
            if v < values['salary_min']:
                raise ValueError('Maximum salary must be greater than minimum salary')
        return v


class UserProfileValidator(BaseModel):
    """Validated user profile data"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = Field(None, pattern=r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$')
    address: Optional[str] = Field(None, max_length=200)
    linkedin_url: Optional[str] = Field(None, max_length=200)
    work_authorization: Optional[str] = Field(default='yes', pattern=r'^(yes|no|visa_required)$')
    requires_sponsorship: Optional[str] = Field(default='no', pattern=r'^(yes|no)$')
    availability: Optional[str] = Field(None, max_length=100)
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not re.match(r'^[a-zA-Z\s\'-]+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        return v.strip()
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        if v:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError('Invalid URL format')
            if 'linkedin.com' not in parsed.netloc.lower():
                raise ValueError('Must be a LinkedIn URL')
        return v
    
    @validator('address')
    def validate_address(cls, v):
        if v:
            # Basic address validation - no HTML or scripts
            if re.search(r'[<>&"\'`]', v):
                raise ValueError('Address contains invalid characters')
        return v.strip() if v else None


class AutomationConfigValidator(BaseModel):
    """Validated automation configuration"""
    auto_apply: bool = Field(default=False)
    max_applications_per_day: int = Field(default=5, ge=1, le=50)
    rate_limit_delay: int = Field(default=5, ge=1, le=300)  # seconds
    schedule_enabled: bool = Field(default=False)
    schedule_time: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    notification_email: bool = Field(default=True)
    optimize_resume_per_job: bool = Field(default=True)
    
    @validator('schedule_time')
    def validate_schedule_time(cls, v, values):
        if values.get('schedule_enabled') and not v:
            raise ValueError('Schedule time is required when scheduling is enabled')
        return v


def validate_model_input(data: Dict[str, Any], model_class: Type[T]) -> T:
    """
    Validate input data against a Pydantic model
    
    Args:
        data: Input data dictionary
        model_class: Pydantic model class to validate against
        
    Returns:
        Validated model instance
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # First pass through security validation
        validator = SecureInputValidator(SanitizationLevel.STRICT)
        validation_result = validator.validate_and_sanitize(data, "input_data")
        
        if not validation_result.is_valid:
            raise ValidationError("input_data", data, f"Security validation failed: {'; '.join(validation_result.errors)}")
        
        # Then validate with Pydantic model
        return model_class(**validation_result.sanitized_data)
        
    except ValueError as e:
        raise ValidationError("model_validation", data, f"Model validation failed: {str(e)}") from e
    except Exception as e:
        logger.error("Unexpected validation error", extra={"error": str(e), "model": model_class.__name__})
        raise ValidationError("validation_internal", data, "Input validation failed due to internal error") from e


def sanitize_error_message(error: Exception, context: str = "") -> str:
    """
    Sanitize error messages to prevent information disclosure
    
    Args:
        error: Exception to sanitize
        context: Context for the error
        
    Returns:
        Sanitized error message safe for user display
    """
    # Map internal errors to safe user messages
    safe_messages = {
        "ValidationError": "The provided input is invalid. Please check your data and try again.",
        "SecurityError": "A security check failed. Please contact support if this persists.",
        "ConfigurationError": "There was a configuration issue. Please contact support.",
        "DatabaseError": "A database error occurred. Please try again later.",
        "ConnectionError": "Unable to connect to external service. Please try again later.",
        "TimeoutError": "The operation timed out. Please try again.",
        "FileNotFoundError": "A required file was not found. Please contact support.",
        "PermissionError": "Insufficient permissions to complete the operation.",
    }
    
    error_type = type(error).__name__
    safe_message = safe_messages.get(error_type, "An unexpected error occurred. Please try again later.")
    
    # Log the actual error for debugging (in a secure manner)
    logger.error(f"Error in {context}", extra={
        "error_type": error_type,
        "sanitized_message": safe_message,
        "context": context
    })
    
    return safe_message


# Global validator instance
_global_validator: Optional[SecureInputValidator] = None

def get_global_validator() -> SecureInputValidator:
    """Get global input validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = SecureInputValidator(SanitizationLevel.STRICT)
    return _global_validator