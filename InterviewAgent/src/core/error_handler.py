"""
Comprehensive error handling framework for InterviewAgent

Provides secure error handling, logging, circuit breakers, and retry mechanisms
to prevent information disclosure and improve system reliability.
"""

import time
import logging
import traceback
from typing import Any, Dict, Optional, Callable, List, Type, Union
from functools import wraps
from enum import Enum
import asyncio
from datetime import datetime, timedelta

from .exceptions import (
    BaseInterviewAgentError, SecurityError, ValidationError, 
    ConfigurationError, DatabaseError, AgentExecutionError
)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"  
    HALF_OPEN = "half_open"


class RetryStrategy(Enum):
    """Retry strategies"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIXED = "fixed"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecureErrorResponse:
    """Secure error response that prevents information disclosure"""
    
    def __init__(
        self, 
        error_id: str,
        user_message: str,
        severity: ErrorSeverity,
        context: Dict[str, Any] = None,
        retry_after: Optional[int] = None
    ):
        self.error_id = error_id
        self.user_message = user_message
        self.severity = severity
        self.context = context or {}
        self.retry_after = retry_after
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        response = {
            "error_id": self.error_id,
            "message": self.user_message,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat()
        }
        
        if self.retry_after:
            response["retry_after"] = self.retry_after
            
        return response


class CircuitBreaker:
    """Circuit breaker for preventing cascade failures"""
    
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
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
        
    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker"""
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self._execute_async(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return self._execute_sync(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    async def _execute_async(self, func: Callable, *args, **kwargs):
        """Execute async function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise SecurityError("Service temporarily unavailable (circuit breaker open)")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _execute_sync(self, func: Callable, *args, **kwargs):
        """Execute sync function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise SecurityError("Service temporarily unavailable (circuit breaker open)")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if not self.last_failure_time:
            return True
        
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds)
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class RetryHandler:
    """Retry handler with different strategies and backoff"""
    
    def __init__(
        self,
        max_retries: int = 3,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_retries = max_retries
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retryable_exceptions = retryable_exceptions
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to add retry logic to functions"""
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self._execute_with_retry_async(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return self._execute_with_retry_sync(func, *args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    async def _execute_with_retry_async(self, func: Callable, *args, **kwargs):
        """Execute async function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except self.retryable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    break
            except Exception as e:
                # Non-retryable exception
                raise
        
        # All retries exhausted
        raise last_exception
    
    def _execute_with_retry_sync(self, func: Callable, *args, **kwargs):
        """Execute sync function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.retryable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
                    continue
                else:
                    break
            except Exception as e:
                # Non-retryable exception
                raise
        
        # All retries exhausted
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        if self.strategy == RetryStrategy.FIXED:
            return self.base_delay
        elif self.strategy == RetryStrategy.LINEAR:
            return min(self.base_delay * (attempt + 1), self.max_delay)
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            return min(self.base_delay * (2 ** attempt), self.max_delay)
        else:
            return self.base_delay


class ErrorHandler:
    """Central error handling system with secure logging and response generation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_mappings = self._initialize_error_mappings()
        self.error_metrics = {}
    
    def _initialize_error_mappings(self) -> Dict[Type[Exception], Dict[str, Any]]:
        """Initialize error type to user message mappings"""
        return {
            ValidationError: {
                "user_message": "The provided input is invalid. Please check your data and try again.",
                "severity": ErrorSeverity.MEDIUM,
                "log_level": logging.WARNING
            },
            SecurityError: {
                "user_message": "A security check failed. Please contact support if this persists.",
                "severity": ErrorSeverity.HIGH,
                "log_level": logging.ERROR
            },
            ConfigurationError: {
                "user_message": "There was a configuration issue. Please contact support.",
                "severity": ErrorSeverity.HIGH,
                "log_level": logging.ERROR
            },
            DatabaseError: {
                "user_message": "A database error occurred. Please try again later.",
                "severity": ErrorSeverity.HIGH,
                "log_level": logging.ERROR
            },
            AgentExecutionError: {
                "user_message": "The AI agent encountered an error. Please try again later.",
                "severity": ErrorSeverity.MEDIUM,
                "log_level": logging.WARNING
            },
            ConnectionError: {
                "user_message": "Unable to connect to external service. Please try again later.",
                "severity": ErrorSeverity.MEDIUM,
                "log_level": logging.WARNING
            },
            TimeoutError: {
                "user_message": "The operation timed out. Please try again.",
                "severity": ErrorSeverity.MEDIUM,
                "log_level": logging.WARNING
            },
            FileNotFoundError: {
                "user_message": "A required file was not found. Please contact support.",
                "severity": ErrorSeverity.MEDIUM,
                "log_level": logging.WARNING
            },
            PermissionError: {
                "user_message": "Insufficient permissions to complete the operation.",
                "severity": ErrorSeverity.HIGH,
                "log_level": logging.ERROR
            }
        }
    
    def handle_error(
        self, 
        error: Exception, 
        context: Dict[str, Any] = None,
        operation: str = "unknown"
    ) -> SecureErrorResponse:
        """
        Handle an error with secure logging and response generation
        
        Args:
            error: The exception that occurred
            context: Additional context information
            operation: Name of the operation that failed
            
        Returns:
            SecureErrorResponse with sanitized user message
        """
        error_id = self._generate_error_id()
        context = context or {}
        
        # Get error mapping
        error_type = type(error)
        mapping = self.error_mappings.get(error_type, {
            "user_message": "An unexpected error occurred. Please try again later.",
            "severity": ErrorSeverity.MEDIUM,
            "log_level": logging.ERROR
        })
        
        # Log the error securely (without exposing sensitive data)
        self._log_error_securely(
            error=error,
            error_id=error_id,
            context=context,
            operation=operation,
            log_level=mapping["log_level"]
        )
        
        # Track error metrics
        self._track_error_metrics(error_type, mapping["severity"])
        
        # Determine retry strategy
        retry_after = self._calculate_retry_after(error_type, mapping["severity"])
        
        return SecureErrorResponse(
            error_id=error_id,
            user_message=mapping["user_message"],
            severity=mapping["severity"],
            context={"operation": operation},
            retry_after=retry_after
        )
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID for tracking"""
        import uuid
        return f"ERR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    
    def _log_error_securely(
        self, 
        error: Exception, 
        error_id: str,
        context: Dict[str, Any],
        operation: str,
        log_level: int
    ):
        """Log error information securely without exposing sensitive data"""
        
        # Sanitize context to remove sensitive information
        safe_context = self._sanitize_context(context)
        
        log_data = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "operation": operation,
            "context": safe_context,
            "timestamp": datetime.now().isoformat()
        }
        
        # Only include error message for certain error types
        if isinstance(error, BaseInterviewAgentError):
            log_data["error_details"] = str(error)
        
        self.logger.log(log_level, f"Error {error_id} in operation '{operation}'", extra=log_data)
        
        # Log full traceback only for critical errors and only in debug mode
        if log_level >= logging.ERROR and self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Full traceback for error {error_id}", extra={
                "error_id": error_id,
                "traceback": traceback.format_exc()
            })
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from context"""
        sensitive_keys = {
            'password', 'api_key', 'token', 'secret', 'credential', 
            'auth', 'session', 'cookie', 'ssn', 'social_security',
            'credit_card', 'ccn', 'account_number', 'routing_number'
        }
        
        safe_context = {}
        for key, value in context.items():
            key_lower = key.lower()
            if any(sensitive_key in key_lower for sensitive_key in sensitive_keys):
                safe_context[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 500:
                safe_context[key] = value[:500] + "...[TRUNCATED]"
            else:
                safe_context[key] = value
        
        return safe_context
    
    def _track_error_metrics(self, error_type: Type[Exception], severity: ErrorSeverity):
        """Track error metrics for monitoring"""
        error_key = error_type.__name__
        
        if error_key not in self.error_metrics:
            self.error_metrics[error_key] = {
                "count": 0,
                "severity_counts": {s.value: 0 for s in ErrorSeverity},
                "last_occurrence": None
            }
        
        self.error_metrics[error_key]["count"] += 1
        self.error_metrics[error_key]["severity_counts"][severity.value] += 1
        self.error_metrics[error_key]["last_occurrence"] = datetime.now()
    
    def _calculate_retry_after(self, error_type: Type[Exception], severity: ErrorSeverity) -> Optional[int]:
        """Calculate retry delay based on error type and severity"""
        if severity == ErrorSeverity.CRITICAL:
            return 300  # 5 minutes
        elif severity == ErrorSeverity.HIGH:
            return 60   # 1 minute
        elif error_type in [ConnectionError, TimeoutError]:
            return 30   # 30 seconds
        else:
            return None  # No specific retry delay
    
    def get_error_metrics(self) -> Dict[str, Any]:
        """Get error metrics for monitoring"""
        return {
            "error_types": self.error_metrics.copy(),
            "total_errors": sum(m["count"] for m in self.error_metrics.values()),
            "critical_errors": sum(
                m["severity_counts"]["critical"] for m in self.error_metrics.values()
            ),
            "last_update": datetime.now().isoformat()
        }


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None

def get_global_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        logger = logging.getLogger("error_handler")
        _global_error_handler = ErrorHandler(logger)
    return _global_error_handler


def secure_error_boundary(operation: str = "unknown"):
    """Decorator to add secure error handling to functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler = get_global_error_handler()
                error_response = error_handler.handle_error(e, {}, operation)
                raise SecurityError(error_response.user_message) from e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = get_global_error_handler()
                error_response = error_handler.handle_error(e, {}, operation)
                raise SecurityError(error_response.user_message) from e
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator