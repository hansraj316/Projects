"""
OpenAI Agents SDK Orchestrator - Uses official OpenAI Agents SDK with proper handoffs
Replaces custom orchestrator with industry-standard agent orchestration
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import uuid
from pydantic import BaseModel

try:
    # Import from OpenAI Agents SDK - need to handle naming conflict
    import sys
    import os
    
    # Temporarily remove our local agents module from path to import OpenAI SDK
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir in sys.path:
        sys.path.remove(parent_dir)
    
    # Import OpenAI Agents SDK
    import agents as openai_agents_sdk
    from agents import Agent, handoff, Runner, function_tool, RunContextWrapper
    from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
    
    # Restore path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        
except ImportError as e:
        # Create mock classes for development without OpenAI Agents SDK
        print(f"Warning: OpenAI Agents SDK not available: {e}")
        
        class Agent:
            def __init__(self, name, instructions, model="gpt-4o-mini", handoffs=None, **kwargs):
                self.name = name
                self.instructions = instructions
                self.model = model
                self.handoffs = handoffs or []
        
        class RunContextWrapper:
            def __init__(self, context):
                self.context = context
        
        def handoff(agent, **kwargs):
            return {"agent": agent, "config": kwargs}
        
        class Runner:
            @staticmethod
            async def run(agent, input_data, context=None):
                return {"final_output": f"Mock response from {agent.name}", "success": False, "error": "OpenAI Agents SDK not configured"}
        
        def function_tool(func):
            return func
        
        def prompt_with_handoff_instructions(prompt):
            return f"[HANDOFF ENABLED]\n{prompt}"

try:
    from agents.base_agent import BaseAgent, AgentTask, AgentContext
except ImportError:
    from .base_agent import BaseAgent, AgentTask, AgentContext

try:
    from config import get_config
except ImportError:
    from ..config import get_config


class JobApplicationContext(BaseModel):
    """Context data for job application workflow"""
    user_id: str
    job_data: Dict[str, Any]
    user_profile: Dict[str, Any]
    workflow_id: str
    automation_settings: Dict[str, Any] = {}


class HandoffData(BaseModel):
    """Structured data for agent handoffs"""
    context: JobApplicationContext
    previous_results: Dict[str, Any] = {}
    handoff_reason: str = ""


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_id: str
    success: bool
    step_results: Dict[str, Any]
    handoff_results: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None


class OpenAIAgentsOrchestrator(BaseAgent):
    """
    Orchestrator using OpenAI Agents SDK with proper handoffs
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="openai_agents_orchestrator",
            description="Orchestrates job application workflow using OpenAI Agents SDK with proper handoffs",
            config=config
        )
        
        self.config = config or get_config()
        self.active_workflows = {}
        self.workflow_history = []
        
        # Initialize agents using OpenAI Agents SDK
        self._initialize_openai_agents()
        
    def _initialize_openai_agents(self):
        """Initialize OpenAI Agents SDK agents with proper handoffs"""
        
        # Job Discovery Agent
        self.job_analysis_agent = Agent(
            name="Job Analysis Agent",
            instructions=prompt_with_handoff_instructions(
                """You are a job analysis specialist. Analyze job postings to extract key requirements, 
                skills, and company information. When analysis is complete, hand off to the Resume Optimizer 
                or Cover Letter Generator based on the workflow needs."""
            ),
            model="gpt-4o-mini"
        )
        
        # Resume Optimization Agent
        self.resume_optimizer_agent = Agent(
            name="Resume Optimizer",
            handoff_description="Specialist for optimizing resumes based on job requirements",
            instructions=prompt_with_handoff_instructions(
                """You are a resume optimization expert. You take job requirements and current resume data 
                to create optimized resumes that match job requirements. Focus on relevant skills, experience, 
                and keywords. When optimization is complete, you can hand off to the Cover Letter Generator."""
            ),
            model="gpt-4o-mini"
        )
        
        # Cover Letter Generator Agent
        self.cover_letter_agent = Agent(
            name="Cover Letter Generator",
            handoff_description="Specialist for generating personalized cover letters",
            instructions=prompt_with_handoff_instructions(
                """You are a cover letter specialist. You create personalized, compelling cover letters 
                based on job postings, company research, and candidate information. Focus on showing 
                genuine interest and relevant qualifications. When complete, hand off to Application Submitter."""
            ),
            model="gpt-4o-mini"
        )
        
        # Application Submission Agent
        self.application_submitter_agent = Agent(
            name="Application Submitter",
            handoff_description="Specialist for submitting job applications",
            instructions=prompt_with_handoff_instructions(
                """You coordinate the submission of job applications. You ensure all required documents 
                are properly formatted and submitted through the appropriate channels. When submission 
                is complete, hand off to the Notification Agent."""
            ),
            model="gpt-4o-mini"
        )
        
        # Email Notification Agent
        self.notification_agent = Agent(
            name="Notification Agent",
            handoff_description="Specialist for sending notifications and updates",
            instructions=prompt_with_handoff_instructions(
                """You handle all email notifications and updates for the job application process. 
                Send confirmation emails, status updates, and summaries to keep users informed."""
            ),
            model="gpt-4o-mini"
        )
        
        # Setup handoffs with proper OpenAI Agents SDK patterns
        self._setup_handoffs()
        
    def _setup_handoffs(self):
        """Setup proper handoffs between agents"""
        
        async def on_job_analysis_handoff(ctx, input_data):
            """Handle handoff from job analysis to next step"""
            self.logger.info(f"Job analysis handoff: {input_data.handoff_reason}")
            # Store analysis results in context
            ctx.context.job_analysis_results = input_data.previous_results
            
        async def on_resume_optimization_handoff(ctx, input_data):
            """Handle handoff from resume optimization"""
            self.logger.info(f"Resume optimization handoff: {input_data.handoff_reason}")
            ctx.context.resume_results = input_data.previous_results
            
        async def on_cover_letter_handoff(ctx, input_data):
            """Handle handoff from cover letter generation"""
            self.logger.info(f"Cover letter handoff: {input_data.handoff_reason}")
            ctx.context.cover_letter_results = input_data.previous_results
            
        async def on_submission_handoff(ctx, input_data):
            """Handle handoff from application submission"""
            self.logger.info(f"Application submission handoff: {input_data.handoff_reason}")
            ctx.context.submission_results = input_data.previous_results
        
        # Configure handoffs for job analysis agent
        self.job_analysis_agent.handoffs = [
            handoff(
                agent=self.resume_optimizer_agent,
                on_handoff=on_job_analysis_handoff,
                input_type=HandoffData,
                tool_description_override="Hand off to resume optimizer with job analysis results"
            ),
            handoff(
                agent=self.cover_letter_agent,
                on_handoff=on_job_analysis_handoff,
                input_type=HandoffData,
                tool_description_override="Hand off to cover letter generator with job analysis results"
            )
        ]
        
        # Configure handoffs for resume optimizer
        self.resume_optimizer_agent.handoffs = [
            handoff(
                agent=self.cover_letter_agent,
                on_handoff=on_resume_optimization_handoff,
                input_type=HandoffData,
                tool_description_override="Hand off to cover letter generator with optimized resume"
            ),
            handoff(
                agent=self.application_submitter_agent,
                on_handoff=on_resume_optimization_handoff,
                input_type=HandoffData,
                tool_description_override="Hand off to application submitter with optimized resume"
            )
        ]
        
        # Configure handoffs for cover letter agent
        self.cover_letter_agent.handoffs = [
            handoff(
                agent=self.application_submitter_agent,
                on_handoff=on_cover_letter_handoff,
                input_type=HandoffData,
                tool_description_override="Hand off to application submitter with cover letter"
            )
        ]
        
        # Configure handoffs for application submitter
        self.application_submitter_agent.handoffs = [
            handoff(
                agent=self.notification_agent,
                on_handoff=on_submission_handoff,
                input_type=HandoffData,
                tool_description_override="Hand off to notification agent with submission results"
            )
        ]
        
        # Main orchestrator agent with handoffs to all specialized agents
        self.orchestrator_agent = Agent(
            name="Job Application Orchestrator",
            instructions=prompt_with_handoff_instructions(
                """You orchestrate complete job application workflows. Based on the user's request, 
                determine which agents to involve and coordinate their work:
                
                1. For job analysis: Hand off to Job Analysis Agent
                2. For resume optimization: Hand off to Resume Optimizer  
                3. For cover letter generation: Hand off to Cover Letter Generator
                4. For application submission: Hand off to Application Submitter
                5. For notifications: Hand off to Notification Agent
                
                Always ensure proper data flow between agents and track the workflow progress."""
            ),
            handoffs=[
                self.job_analysis_agent,
                self.resume_optimizer_agent, 
                self.cover_letter_agent,
                self.application_submitter_agent,
                self.notification_agent
            ],
            model="gpt-4o-mini"
        )
        
    async def create_enhanced_job_workflow(self, user_id: str, job_data: Dict[str, Any], 
                                         user_profile: Dict[str, Any], 
                                         automation_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create enhanced job application workflow using OpenAI Agents SDK
        """
        workflow_id = str(uuid.uuid4())
        workflow_start = datetime.now()
        
        try:
            # Create context for the workflow
            context = JobApplicationContext(
                user_id=user_id,
                job_data=job_data,
                user_profile=user_profile,
                workflow_id=workflow_id,
                automation_settings=automation_settings or {}
            )
            
            # Prepare initial handoff data
            initial_input = f"""
            Start job application workflow for:
            Job: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}
            
            Please coordinate the complete application process:
            1. Analyze the job posting
            2. Optimize the resume
            3. Generate a cover letter
            4. Submit the application
            5. Send confirmation notifications
            
            Job Details:
            {job_data.get('summary', 'No job description available')}
            """
            
            # Execute workflow using OpenAI Agents SDK Runner
            result = await Runner.run(
                starting_agent=self.orchestrator_agent,
                input=initial_input,
                context=context
            )
            
            workflow_end = datetime.now()
            execution_time = (workflow_end - workflow_start).total_seconds()
            
            # Build workflow result
            workflow_result = WorkflowResult(
                workflow_id=workflow_id,
                success=True,
                step_results={
                    "orchestration": {
                        "success": True,
                        "final_output": result.final_output,
                        "execution_time": execution_time
                    }
                },
                handoff_results={
                    "total_handoffs": len(result.to_input_list()) - 1,  # Approximate handoff count
                    "workflow_completed": True
                },
                execution_time=execution_time
            )
            
            # Store workflow
            self.active_workflows[workflow_id] = workflow_result
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "workflow_result": workflow_result,
                "final_output": result.final_output,
                "step_results": workflow_result.step_results,
                "handoff_results": workflow_result.handoff_results
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced workflow failed: {str(e)}")
            
            workflow_result = WorkflowResult(
                workflow_id=workflow_id,
                success=False,
                step_results={},
                handoff_results={},
                execution_time=(datetime.now() - workflow_start).total_seconds(),
                error=str(e)
            )
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "workflow_result": workflow_result
            }
    
    async def create_enhanced_bulk_workflow(self, user_id: str, job_list: List[Dict[str, Any]], 
                                          user_profile: Dict[str, Any], 
                                          automation_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create enhanced bulk job application workflow
        """
        workflow_id = str(uuid.uuid4())
        workflow_start = datetime.now()
        
        try:
            bulk_results = []
            
            for i, job_data in enumerate(job_list):
                job_result = await self.create_enhanced_job_workflow(
                    user_id=user_id,
                    job_data=job_data,
                    user_profile=user_profile,
                    automation_settings=automation_settings
                )
                
                bulk_results.append(job_result)
                
                # Rate limiting
                if automation_settings and automation_settings.get("rate_limit_delay", 0) > 0:
                    await asyncio.sleep(automation_settings["rate_limit_delay"])
            
            workflow_end = datetime.now()
            execution_time = (workflow_end - workflow_start).total_seconds()
            
            successful_jobs = sum(1 for result in bulk_results if result.get("success"))
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "total_jobs": len(job_list),
                "successful_jobs": successful_jobs,
                "failed_jobs": len(job_list) - successful_jobs,
                "execution_time": execution_time,
                "individual_results": bulk_results
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced bulk workflow failed: {str(e)}")
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "execution_time": (datetime.now() - workflow_start).total_seconds()
            }
    
    async def execute_enhanced_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute enhanced workflow configuration
        """
        workflow_type = workflow_config.get("type", "single_job")
        
        if workflow_type == "single_job":
            return await self.create_enhanced_job_workflow(
                user_id=workflow_config["user_id"],
                job_data=workflow_config["job_data"],
                user_profile=workflow_config["user_profile"],
                automation_settings=workflow_config.get("automation_settings", {})
            )
        elif workflow_type == "bulk_jobs":
            return await self.create_enhanced_bulk_workflow(
                user_id=workflow_config["user_id"],
                job_list=workflow_config["job_list"],
                user_profile=workflow_config["user_profile"],
                automation_settings=workflow_config.get("automation_settings", {})
            )
        else:
            return {
                "success": False,
                "error": f"Unknown workflow type: {workflow_type}"
            }
    
    def get_workflow_details(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed workflow information"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": "completed" if workflow.success else "failed",
                "step_results": workflow.step_results,
                "handoff_results": workflow.handoff_results,
                "execution_time": workflow.execution_time,
                "error": workflow.error
            }
        
        # Check history
        for workflow in self.workflow_history:
            if workflow.workflow_id == workflow_id:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "status": "completed" if workflow.success else "failed",
                    "step_results": workflow.step_results,
                    "handoff_results": workflow.handoff_results,
                    "execution_time": workflow.execution_time,
                    "error": workflow.error
                }
        
        return {
            "success": False,
            "error": f"Workflow {workflow_id} not found"
        }
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute orchestrator task using OpenAI Agents SDK
        """
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "execute_enhanced_workflow":
                result = await self.execute_enhanced_workflow(task.input_data)
                
            elif task_type == "get_workflow_details":
                workflow_id = task.input_data.get("workflow_id")
                result = self.get_workflow_details(workflow_id)
                
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