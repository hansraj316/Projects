"""
Custom exceptions for InterviewAgent

Provides a hierarchy of custom exceptions for better error handling and debugging.
"""

from typing import Optional, Dict, Any
import traceback
from datetime import datetime

class InterviewAgentException(Exception):
    """Base exception for InterviewAgent"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now()
        self.stack_trace = traceback.format_exc() if cause else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "stack_trace": self.stack_trace,
            "cause": str(self.cause) if self.cause else None
        }

class ConfigurationError(InterviewAgentException):
    """Configuration-related errors"""
    pass

class SecurityError(InterviewAgentException):
    """Security-related errors"""
    pass

class DatabaseError(InterviewAgentException):
    """Database operation errors"""
    pass

class AgentExecutionError(InterviewAgentException):
    """Agent execution errors"""
    
    def __init__(self, agent_name: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        self.agent_name = agent_name
        enhanced_context = {"agent_name": agent_name}
        if context:
            enhanced_context.update(context)
        super().__init__(message, enhanced_context, cause)

class ValidationError(InterviewAgentException):
    """Input validation errors"""
    
    def __init__(self, field: str, value: Any, message: str, context: Optional[Dict[str, Any]] = None):
        self.field = field
        self.value = value
        enhanced_context = {"field": field, "value": str(value)}
        if context:
            enhanced_context.update(context)
        super().__init__(message, enhanced_context)

class AuthenticationError(InterviewAgentException):
    """Authentication-related errors"""
    pass

class AuthorizationError(InterviewAgentException):
    """Authorization-related errors"""
    pass

class ExternalServiceError(InterviewAgentException):
    """External service integration errors"""
    
    def __init__(self, service_name: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        self.service_name = service_name
        enhanced_context = {"service_name": service_name}
        if context:
            enhanced_context.update(context)
        super().__init__(message, enhanced_context, cause)

class RateLimitError(ExternalServiceError):
    """Rate limiting errors"""
    
    def __init__(self, service_name: str, retry_after: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        self.retry_after = retry_after
        enhanced_context = {"retry_after": retry_after}
        if context:
            enhanced_context.update(context)
        message = f"Rate limit exceeded for {service_name}"
        if retry_after:
            message += f", retry after {retry_after} seconds"
        super().__init__(service_name, message, enhanced_context)

class JobSearchError(InterviewAgentException):
    """Job search specific errors"""
    pass

class ResumeProcessingError(InterviewAgentException):
    """Resume processing specific errors"""
    pass

class AutomationError(InterviewAgentException):
    """Web automation specific errors"""
    
    def __init__(self, automation_type: str, message: str, context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        self.automation_type = automation_type
        enhanced_context = {"automation_type": automation_type}
        if context:
            enhanced_context.update(context)
        super().__init__(message, enhanced_context, cause)