"""
Orchestrator Agent - Manages workflow execution and coordinates between all sub-agents
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid

from .base_agent import BaseAgent, AgentTask, AgentContext


@dataclass
class WorkflowStep:
    """Represents a step in a workflow"""
    step_id: str
    agent_name: str
    task_type: str
    description: str
    depends_on: List[str] = None
    priority: str = "medium"
    timeout_minutes: int = 30


@dataclass
class Workflow:
    """Represents a complete workflow"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    context: AgentContext
    status: str = "pending"
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.results is None:
            self.results = {}


class OrchestratorAgent(BaseAgent):
    """
    Main orchestrator agent that manages workflow execution and coordinates between all sub-agents
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="orchestrator",
            description="Manages workflow execution and coordinates between all sub-agents",
            config=config
        )
        
        self.registered_agents = {}
        self.active_workflows = {}
        self.workflow_history = []
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.registered_agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def create_job_application_workflow(self, user_id: str, job_listing_id: str, resume_template_id: str = None) -> Workflow:
        """
        Create a complete job application workflow
        
        Args:
            user_id: ID of the user
            job_listing_id: ID of the job listing
            resume_template_id: Optional resume template ID
            
        Returns:
            Workflow object
        """
        workflow_id = str(uuid.uuid4())
        
        context = AgentContext(
            user_id=user_id,
            job_listing_id=job_listing_id,
            resume_template_id=resume_template_id
        )
        
        steps = [
            WorkflowStep(
                step_id="analyze_job",
                agent_name="job_analyzer",
                task_type="analyze_job_description",
                description="Analyze job description and extract requirements",
                priority="high"
            ),
            WorkflowStep(
                step_id="optimize_resume",
                agent_name="resume_optimizer",
                task_type="optimize_resume",
                description="Optimize resume for the specific job",
                depends_on=["analyze_job"],
                priority="high"
            ),
            WorkflowStep(
                step_id="generate_cover_letter",
                agent_name="cover_letter_generator",
                task_type="generate_cover_letter",
                description="Generate personalized cover letter",
                depends_on=["analyze_job"],
                priority="high"
            ),
            WorkflowStep(
                step_id="submit_application",
                agent_name="application_submitter",
                task_type="submit_application",
                description="Submit the application to the job site",
                depends_on=["optimize_resume", "generate_cover_letter"],
                priority="medium"
            ),
            WorkflowStep(
                step_id="send_notification",
                agent_name="notification_sender",
                task_type="send_notification",
                description="Send confirmation notification to user",
                depends_on=["submit_application"],
                priority="low"
            )
        ]
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name="Job Application Workflow",
            description=f"Complete job application process for job {job_listing_id}",
            steps=steps,
            context=context
        )
        
        return workflow
    
    async def execute_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """
        Execute a complete workflow
        
        Args:
            workflow: The workflow to execute
            
        Returns:
            Workflow execution result
        """
        self.logger.info(f"Starting workflow {workflow.workflow_id}: {workflow.name}")
        
        workflow.status = "running"
        workflow.started_at = datetime.now()
        self.active_workflows[workflow.workflow_id] = workflow
        
        try:
            # Execute steps in dependency order
            completed_steps = set()
            
            while len(completed_steps) < len(workflow.steps):
                # Find steps that can be executed (dependencies met)
                executable_steps = []
                
                for step in workflow.steps:
                    if step.step_id in completed_steps:
                        continue
                    
                    if not step.depends_on or all(dep in completed_steps for dep in step.depends_on):
                        executable_steps.append(step)
                
                if not executable_steps:
                    raise Exception("Workflow deadlock: No executable steps found")
                
                # Execute steps in parallel where possible
                tasks = []
                for step in executable_steps:
                    task = self._create_task_from_step(step, workflow.context)
                    tasks.append(self._execute_step(step, task, workflow))
                
                # Wait for all parallel tasks to complete
                step_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(step_results):
                    step = executable_steps[i]
                    
                    if isinstance(result, Exception):
                        self.logger.error(f"Step {step.step_id} failed: {str(result)}")
                        workflow.status = "failed"
                        workflow.results[step.step_id] = {
                            "success": False,
                            "error": str(result),
                            "timestamp": datetime.now().isoformat()
                        }
                        raise result
                    else:
                        workflow.results[step.step_id] = result
                        completed_steps.add(step.step_id)
                        self.logger.info(f"Step {step.step_id} completed successfully")
            
            # All steps completed successfully
            workflow.status = "completed"
            workflow.completed_at = datetime.now()
            
            return self.create_result(
                success=True,
                data={
                    "workflow_id": workflow.workflow_id,
                    "status": workflow.status,
                    "steps_completed": len(completed_steps),
                    "execution_time": (workflow.completed_at - workflow.started_at).total_seconds(),
                    "results": workflow.results
                },
                message=f"Workflow {workflow.workflow_id} completed successfully"
            )
            
        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.now()
            self.logger.error(f"Workflow {workflow.workflow_id} failed: {str(e)}")
            
            return self.create_result(
                success=False,
                message=f"Workflow {workflow.workflow_id} failed: {str(e)}",
                metadata={"workflow_id": workflow.workflow_id, "error": str(e)}
            )
        
        finally:
            # Move workflow to history
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
            self.workflow_history.append(workflow)
    
    async def _execute_step(self, step: WorkflowStep, task: AgentTask, workflow: Workflow) -> Dict[str, Any]:
        """Execute a single workflow step"""
        workflow.current_step = step.step_id
        
        # Check if agent is registered
        if step.agent_name not in self.registered_agents:
            # For now, create a mock result if agent is not available
            self.logger.warning(f"Agent {step.agent_name} not registered, creating mock result")
            
            await asyncio.sleep(1)  # Simulate processing time
            
            return self.create_result(
                success=True,
                data={"mock": True, "step_id": step.step_id},
                message=f"Mock execution of {step.task_type} by {step.agent_name}",
                metadata={"agent": step.agent_name, "task_type": step.task_type}
            )
        
        # Execute with registered agent
        agent = self.registered_agents[step.agent_name]
        return await agent.execute(task, workflow.context)
    
    def _create_task_from_step(self, step: WorkflowStep, context: AgentContext) -> AgentTask:
        """Create an AgentTask from a WorkflowStep"""
        return AgentTask(
            task_id=str(uuid.uuid4()),
            task_type=step.task_type,
            description=step.description,
            input_data={
                "step_id": step.step_id,
                "context": context
            },
            priority=step.priority
        )
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute an orchestrator task
        
        Args:
            task: The task to execute
            context: Shared context information
            
        Returns:
            Task execution result
        """
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "execute_job_application":
                # Create and execute job application workflow
                workflow = self.create_job_application_workflow(
                    user_id=context.user_id,
                    job_listing_id=context.job_listing_id,
                    resume_template_id=context.resume_template_id
                )
                
                result = await self.execute_workflow(workflow)
                
            elif task_type == "get_workflow_status":
                workflow_id = task.input_data.get("workflow_id")
                if workflow_id in self.active_workflows:
                    workflow = self.active_workflows[workflow_id]
                    result = self.create_result(
                        success=True,
                        data={
                            "workflow_id": workflow_id,
                            "status": workflow.status,
                            "current_step": workflow.current_step,
                            "progress": len([s for s in workflow.results]) / len(workflow.steps) * 100
                        }
                    )
                else:
                    result = self.create_result(
                        success=False,
                        message=f"Workflow {workflow_id} not found"
                    )
            
            else:
                result = self.create_result(
                    success=False,
                    message=f"Unknown task type: {task_type}"
                )
            
            self.log_task_completion(task, result)
            return result
            
        except Exception as e:
            self.log_task_error(task, e)
            return self.create_result(
                success=False,
                message=f"Task execution failed: {str(e)}"
            )
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get list of active workflows"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "status": wf.status,
                "current_step": wf.current_step,
                "started_at": wf.started_at.isoformat() if wf.started_at else None,
                "progress": len(wf.results) / len(wf.steps) * 100 if wf.steps else 0
            }
            for wf in self.active_workflows.values()
        ]