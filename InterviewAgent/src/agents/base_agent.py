"""
Base Agent class for all AI agents in InterviewAgent system
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from ..config import get_config


@dataclass
class AgentTask:
    """Represents a task for an agent to complete"""
    task_id: str
    task_type: str
    description: str
    input_data: Dict[str, Any]
    priority: str = "medium"
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentContext:
    """Context information shared between agents"""
    user_id: str
    job_listing_id: Optional[str] = None
    resume_template_id: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the system
    """
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.app_config = get_config()
        self.openai_client = None
        self.conversation_state = {}  # For managing conversation state
        
        # Initialize OpenAI client
        self._init_openai_client()
        
    def _init_openai_client(self):
        """Initialize OpenAI client with proper error handling"""
        try:
            if self.app_config.OPENAI_API_KEY:
                if OpenAI:
                    self.openai_client = self.app_config.get_responses_client()
                    self.logger.info(f"OpenAI Responses API client initialized for agent {self.name}")
                else:
                    self.logger.warning("OpenAI package not available")
            else:
                self.logger.info(f"Agent {self.name} running without OpenAI (mock mode)")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.openai_client = None
    
    @abstractmethod
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute a task with the given context
        
        Args:
            task: The task to execute
            context: Shared context information
            
        Returns:
            Dict containing the result of the task execution
        """
        pass
    
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
        Get response using OpenAI Responses API
        
        Args:
            input_text: The user input text
            tools: Optional list of tools for the agent to use
            model: OpenAI model to use (defaults to config model)
            
        Returns:
            AI response text
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available, returning mock response")
            return f"[MOCK AI RESPONSE] Generated content for: {input_text[:50]}..."
        
        # Use configured model if not specified
        if not model:
            model = self.app_config.OPENAI_MODEL
        
        try:
            # Build the request for Responses API
            request_data = {
                "model": model,
                "input": input_text,
                "instructions": self.description
            }
            
            # Add tools if provided
            if tools:
                request_data["tools"] = tools
            
            # Make the Responses API call
            response = self.openai_client.responses.create(**request_data)
            
            # Extract the text content from the response
            if hasattr(response, 'output') and response.output:
                if isinstance(response.output, list) and len(response.output) > 0:
                    message = response.output[0]
                    if hasattr(message, 'content') and message.content:
                        if isinstance(message.content, list) and len(message.content) > 0:
                            return message.content[0].text
                        elif hasattr(message.content, 'text'):
                            return message.content.text
                return str(response.output)
            return "No response generated"
            
        except Exception as e:
            self.logger.error(f"OpenAI Responses API error: {str(e)}")
            return f"[ERROR] Failed to generate response: {str(e)}"
    
    async def get_response_async(self, input_text: str, tools: List[Dict] = None, model: str = None) -> str:
        """
        Get response using OpenAI Responses API (async version)
        
        Args:
            input_text: The user input text
            tools: Optional list of tools for the agent to use
            model: OpenAI model to use (defaults to config model)
            
        Returns:
            AI response text
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available, returning mock response")
            return f"[MOCK AI RESPONSE] Generated content for: {input_text[:50]}..."
        
        # Use configured model if not specified
        if not model:
            model = self.app_config.OPENAI_MODEL
        
        try:
            # Build the request for Responses API
            request_data = {
                "model": model,
                "input": input_text,
                "instructions": self.description
            }
            
            # Add tools if provided
            if tools:
                request_data["tools"] = tools
            
            # Make the async Responses API call  
            response = await self.openai_client.responses.create(**request_data)
            
            # Extract the text content from the response
            if hasattr(response, 'output') and response.output:
                if isinstance(response.output, list) and len(response.output) > 0:
                    message = response.output[0]
                    if hasattr(message, 'content') and message.content:
                        if isinstance(message.content, list) and len(message.content) > 0:
                            return message.content[0].text
                        elif hasattr(message.content, 'text'):
                            return message.content.text
                return str(response.output)
            return "No response generated"
            
        except Exception as e:
            self.logger.error(f"OpenAI Responses API error: {str(e)}")
            return f"[ERROR] Failed to generate response: {str(e)}"
    
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
        """Log the start of task execution"""
        self.logger.info(f"Starting task {task.task_id} ({task.task_type}): {task.description}")
    
    def log_task_completion(self, task: AgentTask, result: Dict[str, Any]):
        """Log successful task completion"""
        self.logger.info(f"Completed task {task.task_id} successfully")
    
    def log_task_error(self, task: AgentTask, error: Exception):
        """Log task execution error"""
        self.logger.error(f"Task {task.task_id} failed: {str(error)}")
    
    def create_result(self, success: bool, data: Any = None, message: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a standardized result dictionary
        
        Args:
            success: Whether the operation was successful
            data: The result data
            message: Optional message
            metadata: Optional metadata
            
        Returns:
            Standardized result dictionary
        """
        return {
            "success": success,
            "data": data,
            "message": message,
            "metadata": metadata or {},
            "agent": self.name,
            "timestamp": datetime.now().isoformat()
        }