"""
Base Agent class for all AI agents in InterviewAgent system
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from src.core.protocols import ILogger, IOpenAIClient, IConfiguration
from src.core.exceptions import AgentExecutionError, ConfigurationError


@dataclass
class AgentTask:
    """Represents a task for an agent to complete"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    description: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        """Validate task data after initialization"""
        if not self.task_type:
            raise ValueError("task_type is required")
        if not self.description:
            raise ValueError("description is required")
        if self.priority not in ["low", "medium", "high", "critical"]:
            raise ValueError("priority must be one of: low, medium, high, critical")

@dataclass
class AgentResult:
    """Standardized result from agent execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    agent_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata
        }

@dataclass
class AgentContext:
    """Context information shared between agents"""
    user_id: str = "default_user"
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_listing_id: Optional[str] = None
    resume_template_id: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def create_child_context(self, **updates) -> 'AgentContext':
        """Create a child context with updated values"""
        data = {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'job_listing_id': self.job_listing_id,
            'resume_template_id': self.resume_template_id,
            'preferences': self.preferences.copy(),
            'metadata': self.metadata.copy(),
            'trace_id': self.trace_id
        }
        data.update(updates)
        return AgentContext(**data)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the system with dependency injection support
    """
    
    def __init__(
        self, 
        name: str, 
        description: str,
        logger: ILogger,
        openai_client: IOpenAIClient,
        config: IConfiguration,
        agent_config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.agent_config = agent_config or {}
        self._logger = logger
        self._openai_client = openai_client
        self._config = config
        self.conversation_state = {}  # For managing conversation state
        self._execution_metrics = {}
        
        # Log agent initialization
        self._logger.info(f"Initialized agent: {name}")
        
    def _validate_dependencies(self) -> None:
        """Validate that all required dependencies are available"""
        if not self._logger:
            raise ConfigurationError("Logger is required")
        if not self._openai_client:
            raise ConfigurationError("OpenAI client is required")
        if not self._config:
            raise ConfigurationError("Configuration is required")
    
    @abstractmethod
    async def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        """
        Execute a task with the given context
        
        Args:
            task: The task to execute
            context: Shared context information
            
        Returns:
            AgentResult containing the result of the task execution
        """
        pass
    
    async def execute_with_error_handling(self, task: AgentTask, context: AgentContext) -> AgentResult:
        """
        Execute task with comprehensive error handling and metrics
        """
        start_time = datetime.now()
        
        try:
            # Validate dependencies
            self._validate_dependencies()
            
            # Validate task
            if not self.validate_task(task):
                return self._create_error_result(
                    task, 
                    "Task validation failed", 
                    start_time
                )
            
            # Log task start
            self.log_task_start(task, context)
            
            # Execute the task
            result = await self.execute(task, context)
            
            # Ensure result is properly typed
            if not isinstance(result, AgentResult):
                # Convert legacy dict results to AgentResult
                if isinstance(result, dict):
                    result = AgentResult(
                        success=result.get('success', True),
                        data=result.get('data'),
                        error=result.get('error'),
                        agent_name=self.name,
                        metadata=result.get('metadata', {})
                    )
                else:
                    result = AgentResult(
                        success=True,
                        data=result,
                        agent_name=self.name
                    )
            
            # Add execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time
            
            # Log success
            self.log_task_completion(task, result)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Agent {self.name} execution failed", extra={
                'task_id': task.task_id,
                'task_type': task.task_type,
                'error': str(e),
                'trace_id': context.trace_id
            })
            
            return self._create_error_result(task, str(e), start_time)
    
    def _create_error_result(self, task: AgentTask, error_message: str, start_time: datetime) -> AgentResult:
        """Create standardized error result"""
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return AgentResult(
            success=False,
            error=error_message,
            agent_name=self.name,
            execution_time_ms=execution_time,
            metadata={'task_id': task.task_id, 'task_type': task.task_type}
        )
    
    def validate_task(self, task: AgentTask) -> bool:
        """
        Validate that the task can be executed by this agent
        
        Args:
            task: The task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        return True
    
    def get_response(self, input_text: str, tools: List[Dict] = None, model: str = None) -> str:
        """
        Get response using OpenAI client with proper error handling
        
        Args:
            input_text: The user input text
            tools: Optional list of tools for the agent to use
            model: OpenAI model to use (defaults to config model)
            
        Returns:
            AI response text
        """
        if not self._openai_client:
            self._logger.warning("OpenAI client not available, returning mock response")
            return f"[MOCK AI RESPONSE] Generated content for: {input_text[:50]}..."
        
        try:
            # Get OpenAI configuration
            openai_config = self._config.get_openai_config()
            
            # Use configured model if not specified
            if not model:
                model = openai_config.get('model', 'gpt-4o-mini')
            
            # Build the request
            request_data = {
                "model": model,
                "input": input_text,
                "instructions": self.description,
                "temperature": openai_config.get('temperature', 0.7),
                "max_output_tokens": openai_config.get('max_tokens', 4000)
            }
            
            # Add tools if provided
            if tools:
                request_data["tools"] = tools
            
            # Make the API call
            response = self._openai_client.create_response(**request_data)
            
            # Extract response text with improved parsing
            return self._extract_response_text(response)
            
        except Exception as e:
            self._logger.error(f"OpenAI API error in agent {self.name}", extra={
                'error': str(e),
                'input_length': len(input_text),
                'model': model
            })
            raise AgentExecutionError(self.name, f"Failed to get AI response: {str(e)}") from e
    
    def _extract_response_text(self, response: Any) -> str:
        """Extract text from OpenAI response with multiple fallback strategies"""
        try:
            # Try Responses API structure
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text
            
            # Try output array structure
            if hasattr(response, 'output') and response.output:
                for output_item in response.output:
                    if hasattr(output_item, 'content') and output_item.content:
                        for content_item in output_item.content:
                            if hasattr(content_item, 'text') and content_item.text:
                                return content_item.text
            
            # Try chat completion structure
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    return choice.message.content
            
            # Last resort: convert to string
            response_str = str(response)
            self._logger.warning(f"Unexpected response structure, using string conversion")
            return response_str
            
        except Exception as e:
            self._logger.error(f"Failed to extract response text: {str(e)}")
            return "[ERROR] Failed to parse AI response"
    
    async def get_response_async(self, input_text: str, tools: List[Dict] = None, model: str = None) -> str:
        """
        Get response using OpenAI client (async version)
        
        Args:
            input_text: The user input text
            tools: Optional list of tools for the agent to use
            model: OpenAI model to use (defaults to config model)
            
        Returns:
            AI response text
        """
        # For now, delegate to sync version as most OpenAI clients are sync
        # TODO: Implement true async when OpenAI client supports it
        return self.get_response(input_text, tools, model)
    
    def add_web_search_tool(self) -> Dict:
        """Add web search tool for Responses API"""
        return {"type": "web_search_preview"}
    
    def add_file_search_tool(self) -> Dict:
        """Add file search tool for Responses API"""
        return {"type": "file_search"}
    
    def create_custom_tool(self, name: str, description: str, parameters: Dict) -> Dict:
        """
        Create a custom tool definition for Responses API
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Tool parameters schema
            
        Returns:
            Tool definition dictionary
        """
        return {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": parameters
        }
    
    def log_task_start(self, task: AgentTask, context: AgentContext):
        """Log the start of task execution with structured logging"""
        self._logger.info(f"Starting task execution", extra={
            'agent_name': self.name,
            'task_id': task.task_id,
            'task_type': task.task_type,
            'task_description': task.description,
            'priority': task.priority,
            'trace_id': context.trace_id,
            'user_id': context.user_id
        })
    
    def log_task_completion(self, task: AgentTask, result: AgentResult):
        """Log successful task completion with metrics"""
        self._logger.info(f"Task completed successfully", extra={
            'agent_name': self.name,
            'task_id': task.task_id,
            'task_type': task.task_type,
            'execution_time_ms': result.execution_time_ms,
            'success': result.success
        })
    
    def log_task_error(self, task: AgentTask, error: Exception):
        """Log task execution error with context"""
        self._logger.error(f"Task execution failed", extra={
            'agent_name': self.name,
            'task_id': task.task_id,
            'task_type': task.task_type,
            'error': str(error),
            'error_type': type(error).__name__
        })
    
    def create_result(
        self, 
        success: bool, 
        data: Any = None, 
        error: Optional[str] = None, 
        metadata: Dict[str, Any] = None
    ) -> AgentResult:
        """
        Create a standardized result object
        
        Args:
            success: Whether the operation was successful
            data: The result data
            error: Error message if unsuccessful
            metadata: Optional metadata
            
        Returns:
            AgentResult object
        """
        return AgentResult(
            success=success,
            data=data,
            error=error,
            agent_name=self.name,
            metadata=metadata or {}
        )