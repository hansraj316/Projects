"""
Orchestrator Agent - Manages workflow execution and coordinates between all sub-agents
Enhanced for complete multi-agent job application automation
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid
import json

from .base_agent import BaseAgent, AgentTask, AgentContext
from .job_discovery import JobDiscoveryAgent
from .resume_optimizer import ResumeOptimizerAgent
from .cover_letter_generator import CoverLetterAgent
from .application_submitter import ApplicationSubmitterAgent
from .email_notification import EmailNotificationAgent


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
            description="Manages complete job application automation workflow with multi-agent coordination, data flow management, and intelligent error handling. Orchestrates job discovery, resume optimization, cover letter generation, application submission, and email notifications.",
            config=config
        )
        
        self.registered_agents = {}
        self.active_workflows = {}
        self.workflow_history = []
        
        # Initialize all agents for the automation system
        self._initialize_automation_agents(config)
        
    def _initialize_automation_agents(self, config: Dict[str, Any] = None):
        """Initialize and register all agents for the automation system"""
        try:
            # Initialize all core agents
            self.register_agent(JobDiscoveryAgent(config))
            self.register_agent(ResumeOptimizerAgent(config))
            self.register_agent(CoverLetterAgent(config))
            self.register_agent(ApplicationSubmitterAgent(config))
            self.register_agent(EmailNotificationAgent(config))
            
            self.logger.info("All automation agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize automation agents: {str(e)}")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.registered_agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def create_job_application_workflow(self, user_id: str, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Workflow:
        """
        Create a complete job application workflow with enhanced multi-agent coordination
        
        Args:
            user_id: ID of the user
            job_data: Complete job information from job search
            user_profile: User profile and preferences
            
        Returns:
            Workflow object with integrated agent pipeline
        """
        workflow_id = str(uuid.uuid4())
        
        context = AgentContext(
            user_id=user_id,
            metadata={
                "job_data": job_data,
                "user_profile": user_profile,
                "workflow_id": workflow_id,
                "automation_mode": True
            }
        )
        
        steps = [
            WorkflowStep(
                step_id="notify_workflow_start",
                agent_name="email_notification",
                task_type="send_workflow_notification",
                description="Send workflow start notification to user",
                priority="low"
            ),
            WorkflowStep(
                step_id="analyze_job_posting",
                agent_name="job_discovery",
                task_type="analyze_job_posting",
                description="Deep analysis of job posting for optimization insights",
                depends_on=["notify_workflow_start"],
                priority="high"
            ),
            WorkflowStep(
                step_id="optimize_resume",
                agent_name="resume_optimizer",
                task_type="optimize_with_research",
                description="Optimize resume with industry research for the specific job",
                depends_on=["analyze_job_posting"],
                priority="high"
            ),
            WorkflowStep(
                step_id="generate_cover_letter",
                agent_name="cover_letter_generator",
                task_type="generate_with_research",
                description="Generate personalized cover letter with company research",
                depends_on=["analyze_job_posting"],
                priority="high"
            ),
            WorkflowStep(
                step_id="submit_application",
                agent_name="application_submitter",
                task_type="submit_application",
                description="Submit the complete application with optimized documents",
                depends_on=["optimize_resume", "generate_cover_letter"],
                priority="medium"
            ),
            WorkflowStep(
                step_id="send_confirmation",
                agent_name="email_notification",
                task_type="send_application_confirmation",
                description="Send application confirmation and next steps to user",
                depends_on=["submit_application"],
                priority="low"
            )
        ]
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name="Automated Job Application Workflow",
            description=f"Complete automated job application for {job_data.get('title', 'position')} at {job_data.get('company', 'company')}",
            steps=steps,
            context=context
        )
        
        return workflow
    
    def create_bulk_application_workflow(self, user_id: str, job_list: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Workflow:
        """
        Create a bulk application workflow for multiple jobs with intelligent batching
        
        Args:
            user_id: ID of the user
            job_list: List of job data dictionaries
            user_profile: User profile and preferences
            
        Returns:
            Bulk workflow object
        """
        workflow_id = str(uuid.uuid4())
        
        context = AgentContext(
            user_id=user_id,
            metadata={
                "job_list": job_list,
                "user_profile": user_profile,
                "workflow_id": workflow_id,
                "automation_mode": True,
                "bulk_processing": True
            }
        )
        
        steps = []
        
        # Add initial notification
        steps.append(WorkflowStep(
            step_id="notify_bulk_start",
            agent_name="email_notification",
            task_type="send_workflow_notification",
            description=f"Send bulk application workflow start notification for {len(job_list)} jobs",
            priority="low"
        ))
        
        # Create steps for each job
        for i, job_data in enumerate(job_list):
            job_id = f"job_{i}"
            
            steps.extend([
                WorkflowStep(
                    step_id=f"{job_id}_analyze",
                    agent_name="job_discovery",
                    task_type="analyze_job_posting",
                    description=f"Analyze job posting for {job_data.get('title', 'position')}",
                    depends_on=["notify_bulk_start"] if i == 0 else [f"job_{i-1}_submit"],
                    priority="high"
                ),
                WorkflowStep(
                    step_id=f"{job_id}_optimize_resume",
                    agent_name="resume_optimizer",
                    task_type="optimize_with_research",
                    description=f"Optimize resume for {job_data.get('title', 'position')}",
                    depends_on=[f"{job_id}_analyze"],
                    priority="high"
                ),
                WorkflowStep(
                    step_id=f"{job_id}_generate_cover_letter",
                    agent_name="cover_letter_generator",
                    task_type="generate_with_research",
                    description=f"Generate cover letter for {job_data.get('title', 'position')}",
                    depends_on=[f"{job_id}_analyze"],
                    priority="high"
                ),
                WorkflowStep(
                    step_id=f"{job_id}_submit",
                    agent_name="application_submitter",
                    task_type="submit_application",
                    description=f"Submit application for {job_data.get('title', 'position')}",
                    depends_on=[f"{job_id}_optimize_resume", f"{job_id}_generate_cover_letter"],
                    priority="medium"
                )
            ])
        
        # Add final summary notification
        steps.append(WorkflowStep(
            step_id="send_bulk_summary",
            agent_name="email_notification",
            task_type="send_daily_summary",
            description="Send bulk application completion summary",
            depends_on=[f"job_{len(job_list)-1}_submit"],
            priority="low"
        ))
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name="Bulk Job Application Workflow",
            description=f"Automated bulk application for {len(job_list)} positions",
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
                    task = self._create_task_from_step(step, workflow)
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
    
    def _create_task_from_step(self, step: WorkflowStep, workflow: Workflow) -> AgentTask:
        """Create an AgentTask from a WorkflowStep with enhanced data flow"""
        # Build input data with results from previous steps
        input_data = {
            "step_id": step.step_id,
            "workflow_id": workflow.workflow_id,
            "context": workflow.context.metadata
        }
        
        # Add job data for all steps
        job_data = workflow.context.metadata.get("job_data", {})
        user_profile = workflow.context.metadata.get("user_profile", {})
        
        # Customize input data based on agent and step
        if step.agent_name == "job_discovery" and step.task_type == "analyze_job_posting":
            input_data.update({
                "job_description": job_data.get("summary", ""),
                "company_name": job_data.get("company", ""),
                "job_title": job_data.get("title", "")
            })
            
        elif step.agent_name == "resume_optimizer":
            # Pass job analysis results if available
            job_analysis = workflow.results.get("analyze_job_posting", {}).get("data", {})
            input_data.update({
                "job_description": job_data.get("summary", ""),
                "company_name": job_data.get("company", ""),
                "job_title": job_data.get("title", ""),
                "industry": job_data.get("industry", ""),
                "current_resume": user_profile.get("resume_data", {}),
                "job_analysis": job_analysis
            })
            
        elif step.agent_name == "cover_letter_generator":
            # Pass job analysis and user info
            job_analysis = workflow.results.get("analyze_job_posting", {}).get("data", {})
            input_data.update({
                "job_description": job_data.get("summary", ""),
                "company_name": job_data.get("company", ""),
                "job_title": job_data.get("title", ""),
                "hiring_manager": job_data.get("hiring_manager", "Hiring Manager"),
                "candidate_info": user_profile.get("candidate_info", {}),
                "resume_summary": user_profile.get("resume_summary", {}),
                "job_analysis": job_analysis
            })
            
        elif step.agent_name == "application_submitter":
            # Pass optimized documents and job details
            resume_result = workflow.results.get("optimize_resume", {}).get("data", {})
            cover_letter_result = workflow.results.get("generate_cover_letter", {}).get("data", {})
            input_data.update({
                "job_url": job_data.get("url", ""),
                "job_site": job_data.get("source", ""),
                "candidate_info": user_profile.get("candidate_info", {}),
                "resume_path": resume_result.get("resume_file_path", ""),
                "cover_letter_path": cover_letter_result.get("cover_letter_file_path", ""),
                "optimized_resume": resume_result.get("optimized_resume", {}),
                "cover_letter_data": cover_letter_result.get("cover_letter", {})
            })
            
        elif step.agent_name == "email_notification":
            # Pass workflow summary and results
            input_data.update({
                "workflow_id": workflow.workflow_id,
                "workflow_status": workflow.status,
                "job_details": job_data,
                "agent_results": workflow.results,
                "user_email": user_profile.get("email", ""),
                "notification_type": self._determine_notification_type(step.task_type, workflow)
            })
        
        return AgentTask(
            task_id=str(uuid.uuid4()),
            task_type=step.task_type,
            description=step.description,
            input_data=input_data,
            priority=step.priority
        )
        
    def _determine_notification_type(self, task_type: str, workflow: Workflow) -> str:
        """Determine the appropriate notification type based on workflow state"""
        if task_type == "send_workflow_notification":
            if workflow.status == "running" and not workflow.results:
                return "workflow_started"
            elif workflow.status == "failed":
                return "workflow_failed"
            else:
                return "workflow_progress"
        elif task_type == "send_application_confirmation":
            return "application_submitted"
        elif task_type == "send_daily_summary":
            return "daily_summary"
        else:
            return "general_notification"
    
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