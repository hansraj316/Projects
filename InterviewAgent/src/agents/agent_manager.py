"""
Agent Manager - Factory and registry for all AI agents
"""

import logging
from typing import Dict, Any, Optional

from .base_agent import BaseAgent
from .enhanced_orchestrator import EnhancedOrchestratorAgent
from .job_discovery import JobDiscoveryAgent
from .resume_optimizer import ResumeOptimizerAgent
from .cover_letter_generator import CoverLetterAgent
from .application_submitter import ApplicationSubmitterAgent
from .email_notification import EmailNotificationAgent


class AgentManager:
    """
    Manages the creation, registration, and lifecycle of all AI agents
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("agent_manager")
        self.agents = {}
        self.orchestrator = None
        
    def initialize_agents(self) -> None:
        """Initialize all agents and register them with the orchestrator"""
        self.logger.info("Initializing AI agents...")
        
        # Create orchestrator
        self.orchestrator = EnhancedOrchestratorAgent(self.config)
        self.agents["orchestrator"] = self.orchestrator
        
        # Create specialized agents
        job_discovery = JobDiscoveryAgent(self.config)
        resume_optimizer = ResumeOptimizerAgent(self.config)
        cover_letter_agent = CoverLetterAgent(self.config)
        application_submitter = ApplicationSubmitterAgent(self.config)
        email_notification = EmailNotificationAgent(self.config)
        
        # Register agents
        self.agents["job_discovery"] = job_discovery
        self.agents["resume_optimizer"] = resume_optimizer
        self.agents["cover_letter_generator"] = cover_letter_agent
        self.agents["application_submitter"] = application_submitter
        self.agents["email_notification"] = email_notification
        
        # Register with orchestrator
        self.orchestrator.register_agent(job_discovery)
        self.orchestrator.register_agent(resume_optimizer)
        self.orchestrator.register_agent(cover_letter_agent)
        self.orchestrator.register_agent(application_submitter)
        self.orchestrator.register_agent(email_notification)
        
        self.logger.info(f"Initialized {len(self.agents)} agents successfully")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name
        
        Args:
            agent_name: Name of the agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name)
    
    def get_orchestrator(self) -> EnhancedOrchestratorAgent:
        """Get the orchestrator agent"""
        return self.orchestrator
    
    def list_agents(self) -> Dict[str, str]:
        """
        List all available agents
        
        Returns:
            Dictionary mapping agent names to descriptions
        """
        return {
            name: agent.description 
            for name, agent in self.agents.items()
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status information for all agents
        
        Returns:
            Status information for each agent
        """
        status = {}
        
        for name, agent in self.agents.items():
            status[name] = {
                "name": agent.name,
                "description": agent.description,
                "has_openai": agent.openai_client is not None,
                "config_loaded": bool(agent.config)
            }
        
        return status
    
    def test_agents(self) -> Dict[str, bool]:
        """
        Test all agents to ensure they're working properly
        
        Returns:
            Test results for each agent
        """
        results = {}
        
        for name, agent in self.agents.items():
            try:
                # Simple test - check if agent can create a result
                test_result = agent.create_result(True, {"test": "data"}, "Test successful")
                results[name] = test_result.get("success", False)
                self.logger.info(f"Agent {name} test: {'PASS' if results[name] else 'FAIL'}")
            except Exception as e:
                results[name] = False
                self.logger.error(f"Agent {name} test failed: {str(e)}")
        
        return results