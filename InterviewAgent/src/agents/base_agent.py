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
        self.openai_client = None
        
        # Initialize OpenAI client if API key is available
        if self.config.get('OPENAI_API_KEY'):
            if OpenAI:
                self.openai_client = OpenAI(api_key=self.config['OPENAI_API_KEY'])
                self.logger.info(f"OpenAI client initialized for agent {name}")
            else:
                self.logger.warning("OpenAI package not available")
        else:
            self.logger.info(f"Agent {name} running without OpenAI (mock mode)")
    
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
    
    def get_ai_response(self, prompt: str, system_message: str = None, model: str = "gpt-3.5-turbo") -> str:
        """
        Get response from OpenAI API
        
        Args:
            prompt: The user prompt
            system_message: Optional system message
            model: OpenAI model to use
            
        Returns:
            AI response text
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available, returning mock response")
            return f"[MOCK AI RESPONSE] Generated content for: {prompt[:50]}..."
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            return f"[ERROR] Failed to generate AI response: {str(e)}"
    
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