"""
Consistent error handling for InterviewAgent

Provides centralized error handling, logging, and recovery mechanisms.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable, Type
from datetime import datetime
from functools import wraps

from .protocols import ILogger, IMetrics
from .exceptions import (
    InterviewAgentException, AgentExecutionError, DatabaseError,
    ValidationError, SecurityError, ConfigurationError
)

class ErrorHandler:
    """Centralized error handler with comprehensive logging and metrics"""
    
    def __init__(self, logger: ILogger, metrics: Optional[IMetrics] = None):
        self._logger = logger
        self._metrics = metrics
        self._error_handlers: Dict[Type[Exception], Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default error handlers for common exception types"""
        self._error_handlers[ValidationError] = self._handle_validation_error
        self._error_handlers[DatabaseError] = self._handle_database_error
        self._error_handlers[SecurityError] = self._handle_security_error
        self._error_handlers[ConfigurationError] = self._handle_configuration_error
        self._error_handlers[AgentExecutionError] = self._handle_agent_error
    
    def handle_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle any error with appropriate logging and response generation
        
        Args:
            error: The exception that occurred
            context: Additional context information
            operation: The operation that was being performed
            user_id: User ID if applicable
            
        Returns:
            Standardized error response dictionary
        """
        error_context = {
            "operation": operation,
            "user_id": user_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            error_context.update(context)
        
        # Get stack trace for detailed logging
        stack_trace = traceback.format_exc()
        error_context["stack_trace"] = stack_trace
        
        # Log the error
        self._log_error(error, error_context)
        
        # Record metrics if available
        if self._metrics:
            self._record_error_metrics(error, error_context)
        
        # Use specific handler if available
        error_type = type(error)
        if error_type in self._error_handlers:
            return self._error_handlers[error_type](error, error_context)
        
        # Check for parent class handlers
        for exc_type, handler in self._error_handlers.items():
            if isinstance(error, exc_type):
                return handler(error, error_context)
        
        # Default handler for unknown errors
        return self._handle_unknown_error(error, error_context)
    
    def _log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with appropriate level based on error type"""
        error_msg = f"Error in {context.get('operation', 'unknown operation')}: {str(error)}"
        
        if isinstance(error, (SecurityError, DatabaseError)):
            self._logger.critical(error_msg, extra=context)
        elif isinstance(error, (ConfigurationError, AgentExecutionError)):
            self._logger.error(error_msg, extra=context)
        elif isinstance(error, ValidationError):
            self._logger.warning(error_msg, extra=context)
        else:
            self._logger.error(error_msg, extra=context)
    
    def _record_error_metrics(self, error: Exception, context: Dict[str, Any]):
        """Record error metrics for monitoring"""
        try:
            tags = {
                "error_type": type(error).__name__,
                "operation": context.get("operation", "unknown")
            }
            
            if context.get("user_id"):
                tags["user_id"] = context["user_id"]
            
            self._metrics.increment_counter("errors.total", tags)
            
            # Record specific error type metrics
            if isinstance(error, ValidationError):
                self._metrics.increment_counter("errors.validation", {"field": error.field})
            elif isinstance(error, AgentExecutionError):
                self._metrics.increment_counter("errors.agent", {"agent": error.agent_name})
            elif isinstance(error, DatabaseError):
                self._metrics.increment_counter("errors.database", {})
            elif isinstance(error, SecurityError):
                self._metrics.increment_counter("errors.security", {})
                
        except Exception as metrics_error:
            self._logger.warning(f"Failed to record error metrics: {metrics_error}")
    
    def _handle_validation_error(self, error: ValidationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors"""
        return {
            "success": False,
            "error_type": "validation_error",
            "error_message": str(error),
            "field": error.field,
            "value": str(error.value) if hasattr(error, 'value') else None,
            "user_friendly_message": self._get_user_friendly_validation_message(error),
            "timestamp": context["timestamp"]
        }
    
    def _handle_database_error(self, error: DatabaseError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database errors"""
        return {
            "success": False,
            "error_type": "database_error",
            "error_message": "A database error occurred",
            "user_friendly_message": "We're experiencing technical difficulties. Please try again later.",
            "timestamp": context["timestamp"],
            "retry_after_seconds": 30
        }
    
    def _handle_security_error(self, error: SecurityError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security errors"""
        # Don't expose security details to prevent information leakage
        return {
            "success": False,
            "error_type": "security_error",
            "error_message": "A security error occurred",
            "user_friendly_message": "Access denied. Please check your credentials and try again.",
            "timestamp": context["timestamp"]
        }
    
    def _handle_configuration_error(self, error: ConfigurationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration errors"""
        return {
            "success": False,
            "error_type": "configuration_error",
            "error_message": str(error),
            "user_friendly_message": "The system is not properly configured. Please contact support.",
            "timestamp": context["timestamp"]
        }
    
    def _handle_agent_error(self, error: AgentExecutionError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent execution errors"""
        return {
            "success": False,
            "error_type": "agent_error",
            "error_message": str(error),
            "agent_name": error.agent_name,
            "user_friendly_message": f"The {error.agent_name} agent encountered an error. Please try again.",
            "timestamp": context["timestamp"],
            "retry_recommended": True
        }
    
    def _handle_unknown_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown/unexpected errors"""
        return {
            "success": False,
            "error_type": "internal_error",
            "error_message": "An unexpected error occurred",
            "user_friendly_message": "Something went wrong. Please try again later.",
            "timestamp": context["timestamp"],
            "support_reference": context.get("timestamp", "")
        }
    
    def _get_user_friendly_validation_message(self, error: ValidationError) -> str:
        """Generate user-friendly validation error messages"""
        field = error.field
        value = getattr(error, 'value', None)
        
        field_messages = {
            "email": "Please enter a valid email address.",
            "password": "Password must meet security requirements.",
            "api_key": "Invalid API key format.",
            "job_title": "Job title must be at least 3 characters long.",
            "company": "Company name must be valid.",
            "location": "Please enter a valid location.",
            "salary_min": "Minimum salary must be a positive number.",
            "salary_max": "Maximum salary must be a positive number.",
            "keywords": "Keywords must be valid text.",
            "limit": "Limit must be between 1 and 1000."
        }
        
        return field_messages.get(field, f"Invalid {field}. Please check your input.")
    
    def register_handler(self, exception_type: Type[Exception], handler: Callable):
        """Register custom error handler for specific exception type"""
        self._error_handlers[exception_type] = handler
    
    def create_error_decorator(self, operation_name: str):
        """Create decorator for automatic error handling in functions"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    context = {
                        "function": func.__name__,
                        "args": str(args)[:200],  # Limit arg logging
                        "kwargs": str(kwargs)[:200]
                    }
                    error_response = self.handle_error(e, context, operation_name)
                    return error_response
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context = {
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200]
                    }
                    error_response = self.handle_error(e, context, operation_name)
                    return error_response
            
            # Return appropriate wrapper based on function type
            if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator

class CircuitBreaker:
    """Circuit breaker pattern for handling repeated failures"""
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        # Return appropriate wrapper
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() > self.timeout_seconds
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RetryHandler:
    """Handle retries with exponential backoff"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions
    
    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except self.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == self.max_retries:
                        break
                    
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except self.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == self.max_retries:
                        break
                    
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    
                    time.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper