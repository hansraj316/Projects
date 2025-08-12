"""
Agent Manager - Factory and registry for all AI agents
"""

import logging
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from agents.base_agent import BaseAgent, AgentTask, AgentContext, AgentResult
from agents.enhanced_orchestrator import EnhancedOrchestratorAgent
from agents.job_discovery import JobDiscoveryAgent
from agents.resume_optimizer import ResumeOptimizerAgent
from agents.cover_letter_generator import CoverLetterAgent
from agents.application_submitter import ApplicationSubmitterAgent
from agents.email_notification import EmailNotificationAgent
from core.container import ServiceContainer
from core.protocols import ILogger, IConfiguration, IOpenAIClient, IMetrics
from core.exceptions import AgentExecutionError, ConfigurationError
from core.error_handler import ErrorHandler, CircuitBreaker, RetryHandler


class AgentManager:
    """
    Manages the creation, registration, and lifecycle of all AI agents with dependency injection
    """
    
    def __init__(
        self, 
        container: ServiceContainer,
        logger: ILogger,
        config: IConfiguration,
        error_handler: ErrorHandler,
        metrics: Optional[IMetrics] = None
    ):
        self._container = container
        self._logger = logger
        self._config = config
        self._error_handler = error_handler
        self._metrics = metrics
        self.agents: Dict[str, BaseAgent] = {}
        self.orchestrator: Optional[EnhancedOrchestratorAgent] = None
        self._agent_health: Dict[str, Dict[str, Any]] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        
    async def initialize_agents(self) -> None:
        """Initialize all agents with dependency injection and error handling"""
        try:
            self._logger.info("Initializing AI agents with dependency injection...")
            
            # Get dependencies from container
            openai_client = self._container.get(IOpenAIClient)
            
            # Create orchestrator with dependency injection
            self.orchestrator = EnhancedOrchestratorAgent(
                name="orchestrator",
                description="Main orchestrator for coordinating all automation workflows",
                logger=self._logger,
                openai_client=openai_client,
                config=self._config
            )
            self.agents["orchestrator"] = self.orchestrator
            
            # Create specialized agents with error handling
            agent_configs = [
                ("job_discovery", JobDiscoveryAgent, "AI-powered job search and analysis agent"),
                ("resume_optimizer", ResumeOptimizerAgent, "AI-powered resume optimization agent"),
                ("cover_letter_generator", CoverLetterAgent, "AI-powered cover letter generation agent"),
                ("application_submitter", ApplicationSubmitterAgent, "Web automation for job application submission"),
                ("email_notification", EmailNotificationAgent, "Email notification and communication agent")
            ]
            
            # Initialize agents concurrently with error handling
            agent_tasks = []
            for agent_name, agent_class, description in agent_configs:
                task = self._initialize_single_agent(agent_name, agent_class, description, openai_client)
                agent_tasks.append(task)
            
            # Wait for all agents to initialize
            initialization_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Process results and handle any failures
            successful_agents = []
            for i, result in enumerate(initialization_results):
                agent_name = agent_configs[i][0]
                
                if isinstance(result, Exception):
                    # Use secure error handling - don't expose internal details
                    sanitized_error = "Agent initialization failed due to internal error"
                    self._logger.error(f"Failed to initialize agent {agent_name}", extra={
                        "agent_name": agent_name,
                        "error_type": type(result).__name__,
                        "sanitized_error": sanitized_error
                    })
                    self._record_agent_health(agent_name, False, sanitized_error)
                else:
                    successful_agents.append(agent_name)
                    self._record_agent_health(agent_name, True)
            
            # Register successful agents with orchestrator
            if self.orchestrator:
                for agent_name in successful_agents:
                    agent = self.agents.get(agent_name)
                    if agent:
                        try:
                            self.orchestrator.register_agent(agent)
                        except Exception as e:
                            # Use secure logging - don't expose sensitive details
                            self._logger.warning(f"Failed to register agent {agent_name} with orchestrator", extra={
                                "agent_name": agent_name,
                                "error_type": type(e).__name__
                            })
            
            # Setup circuit breakers for agents
            self._setup_circuit_breakers()
            
            total_agents = len(self.agents)
            successful_count = len(successful_agents) + (1 if self.orchestrator else 0)  # +1 for orchestrator
            
            self._logger.info(f"Agent initialization completed: {successful_count}/{total_agents} agents successful")
            
            if self._metrics:
                self._metrics.set_gauge("agents.initialized", successful_count)
                self._metrics.set_gauge("agents.failed", total_agents - successful_count)
            
        except Exception as e:
            self._logger.critical("Critical failure during agent initialization", extra={
                "error": str(e)
            })
            raise ConfigurationError("Failed to initialize agent system") from e
    
    async def _initialize_single_agent(
        self, 
        agent_name: str, 
        agent_class: type, 
        description: str, 
        openai_client: IOpenAIClient
    ) -> None:
        """Initialize a single agent with error handling"""
        try:
            agent = agent_class(
                name=agent_name,
                description=description,
                logger=self._logger,
                openai_client=openai_client,
                config=self._config
            )
            
            # Test agent initialization
            test_result = agent.create_result(True, {"test": "initialization"}, None)
            if not test_result.success:
                raise AgentExecutionError(agent_name, "Agent failed initialization test")
            
            self.agents[agent_name] = agent
            self._logger.info(f"Successfully initialized agent: {agent_name}")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize agent {agent_name}", extra={
                "agent_name": agent_name,
                "agent_class": agent_class.__name__,
                "error": str(e)
            })
            raise AgentExecutionError(agent_name, f"Initialization failed: {str(e)}") from e
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for agent error handling"""
        for agent_name in self.agents.keys():
            self._circuit_breakers[agent_name] = CircuitBreaker(
                failure_threshold=5,
                timeout_seconds=60,
                expected_exception=AgentExecutionError
            )
    
    def _record_agent_health(self, agent_name: str, healthy: bool, error: Optional[str] = None):
        """Record agent health status"""
        self._agent_health[agent_name] = {
            "healthy": healthy,
            "last_check": datetime.now(),
            "error": error
        }
        
        if self._metrics:
            status = "healthy" if healthy else "unhealthy"
            self._metrics.set_gauge(f"agent.health.{agent_name}", 1 if healthy else 0, {"status": status})
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name with health check
        
        Args:
            agent_name: Name of the agent to retrieve
            
        Returns:
            Agent instance or None if not found or unhealthy
        """
        agent = self.agents.get(agent_name)
        
        if not agent:
            return None
        
        # Check if agent is healthy
        health_info = self._agent_health.get(agent_name, {})
        if not health_info.get("healthy", True):  # Default to healthy if no health info
            self._logger.warning(f"Requested agent {agent_name} is marked as unhealthy")
            return None
        
        return agent
    
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
        Get comprehensive status information for all agents
        
        Returns:
            Detailed status information for each agent
        """
        status = {}
        
        for name, agent in self.agents.items():
            # Get health information
            health_info = self._agent_health.get(name, {})
            circuit_breaker_info = self._circuit_breakers.get(name)
            last_check = health_info.get("last_check")

            status[name] = {
                "name": agent.name,
                "description": agent.description,
                "healthy": health_info.get("healthy", False),
                "last_health_check": last_check.isoformat() if last_check else None,
                "health_error": health_info.get("error"),
                "circuit_breaker_state": circuit_breaker_info.state if circuit_breaker_info else "N/A",
                "failure_count": circuit_breaker_info.failure_count if circuit_breaker_info else 0,
                "dependencies_available": {
                    "logger": hasattr(agent, '_logger') and agent._logger is not None,
                    "openai_client": hasattr(agent, '_openai_client') and agent._openai_client is not None,
                    "config": hasattr(agent, '_config') and agent._config is not None
                },
                "agent_config": bool(getattr(agent, 'agent_config', {})),
                "conversation_state": bool(getattr(agent, 'conversation_state', {}))
            }
        
        return {
            "agents": status,
            "total_agents": len(self.agents),
            "healthy_agents": sum(1 for s in status.values() if s["healthy"]),
            "orchestrator_available": self.orchestrator is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    async def test_agents(self) -> Dict[str, Any]:
        """
        Comprehensive testing of all agents with health checks
        
        Returns:
            Detailed test results for each agent
        """
        results = {}
        
        for name, agent in self.agents.items():
            try:
                start_time = datetime.now()
                
                # Basic functionality test
                basic_test = agent.create_result(True, {"test": "data"}, None)
                basic_success = basic_test.success
                
                # Agent-specific test task
                test_task = AgentTask(
                    task_type="health_check",
                    description="Health check test task",
                    input_data={"test": True}
                )
                
                test_context = AgentContext(user_id="test_user")
                
                # Execute with timeout and error handling
                try:
                    execution_result = await asyncio.wait_for(
                        agent.execute_with_error_handling(test_task, test_context),
                        timeout=30.0
                    )
                    execution_success = execution_result.success
                except asyncio.TimeoutError:
                    execution_success = False
                    execution_result = agent.create_result(False, None, "Test timeout")
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Overall health assessment
                overall_health = basic_success and execution_success
                
                results[name] = {
                    "overall_health": overall_health,
                    "basic_test": basic_success,
                    "execution_test": execution_success,
                    "execution_time_seconds": execution_time,
                    "last_test": datetime.now().isoformat(),
                    "error": execution_result.error if not execution_success else None
                }
                
                # Update health record
                self._record_agent_health(name, overall_health, execution_result.error)
                
                status = "PASS" if overall_health else "FAIL"
                self._logger.info(f"Agent {name} comprehensive test: {status} (execution time: {execution_time:.2f}s)")
                
            except Exception as e:
                error_message = str(e)
                results[name] = {
                    "overall_health": False,
                    "basic_test": False,
                    "execution_test": False,
                    "execution_time_seconds": 0,
                    "last_test": datetime.now().isoformat(),
                    "error": error_message
                }
                
                self._record_agent_health(name, False, error_message)
                self._logger.error(f"Agent {name} test failed with exception: {error_message}")
        
        # Record overall system health
        healthy_agents = sum(1 for result in results.values() if result["overall_health"])
        total_agents = len(results)
        
        if self._metrics:
            self._metrics.set_gauge("agents.healthy", healthy_agents)
            self._metrics.set_gauge("agents.total", total_agents)
        
        return results
    
    @RetryHandler(max_retries=3, retryable_exceptions=(AgentExecutionError,))
    async def execute_agent_task(
        self, 
        agent_name: str, 
        task: AgentTask, 
        context: AgentContext
    ) -> AgentResult:
        """
        Execute a task on a specific agent with error handling and retries
        
        Args:
            agent_name: Name of the agent to execute
            task: Task to execute
            context: Execution context
            
        Returns:
            Agent execution result
        """
        if agent_name not in self.agents:
            raise AgentExecutionError(agent_name, f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        circuit_breaker = self._circuit_breakers.get(agent_name)
        
        # Check circuit breaker
        if circuit_breaker and circuit_breaker.state == "OPEN":
            return agent.create_result(
                False, 
                None, 
                f"Agent {agent_name} is temporarily unavailable (circuit breaker open)"
            )
        
        try:
            # Execute with circuit breaker protection
            if circuit_breaker:
                result = await circuit_breaker(agent.execute_with_error_handling)(task, context)
            else:
                result = await agent.execute_with_error_handling(task, context)
            
            # Record successful execution
            if self._metrics:
                self._metrics.increment_counter("agent.execution.success", {"agent": agent_name})
            
            return result
            
        except Exception as e:
            # Record failed execution
            if self._metrics:
                self._metrics.increment_counter("agent.execution.failure", {"agent": agent_name})
            
            # Use error handler for consistent error processing
            error_response = self._error_handler.handle_error(
                e, 
                {"agent_name": agent_name, "task_id": task.task_id},
                f"execute_agent_task_{agent_name}"
            )
            
            return agent.create_result(False, None, error_response.get("error_message", str(e)))
    
    def get_agent_health(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        return {
            "agents": self._agent_health.copy(),
            "circuit_breakers": {
                name: {
                    "state": cb.state,
                    "failure_count": cb.failure_count,
                    "last_failure_time": cb.last_failure_time.isoformat() if cb.last_failure_time else None
                }
                for name, cb in self._circuit_breakers.items()
            },
            "overall_health": all(health.get("healthy", False) for health in self._agent_health.values()),
            "timestamp": datetime.now().isoformat()
        }