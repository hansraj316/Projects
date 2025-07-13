"""
Agent Manager - Factory and registry for all AI agents
"""

import logging
from typing import Dict, Any, Optional

from .base_agent import BaseAgent
from .orchestrator import OrchestratorAgent
from .resume_optimizer import ResumeOptimizerAgent
from .cover_letter_generator import CoverLetterAgent


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
        self.orchestrator = OrchestratorAgent(self.config)
        self.agents["orchestrator"] = self.orchestrator
        
        # Create specialized agents
        resume_optimizer = ResumeOptimizerAgent(self.config)
        cover_letter_agent = CoverLetterAgent(self.config)
        
        # Register agents
        self.agents["resume_optimizer"] = resume_optimizer
        self.agents["cover_letter_generator"] = cover_letter_agent
        
        # Register with orchestrator
        self.orchestrator.register_agent(resume_optimizer)
        self.orchestrator.register_agent(cover_letter_agent)
        
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
    
    def get_orchestrator(self) -> OrchestratorAgent:
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