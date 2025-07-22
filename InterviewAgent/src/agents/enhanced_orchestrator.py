"""
Enhanced Orchestrator Agent - Advanced workflow management with detailed handoff and step execution
Provides comprehensive job application automation with intelligent agent coordination
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid
import json
from enum import Enum

from agents.base_agent import BaseAgent, AgentTask, AgentContext
from agents.job_discovery import JobDiscoveryAgent
from agents.resume_optimizer import ResumeOptimizerAgent
from agents.cover_letter_generator import CoverLetterAgent
from agents.application_submitter import ApplicationSubmitterAgent
from agents.email_notification import EmailNotificationAgent


class StepStatus(Enum):
    """Workflow step status enumeration"""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class StepAction:
    """Specific action definition for a workflow step"""
    action_id: str
    description: str
    required_inputs: List[str]
    expected_outputs: List[str]
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HandoffSpec:
    """Detailed handoff specification between agents"""
    from_agent: str
    to_agent: str
    data_mapping: Dict[str, str]  # Maps output keys to input keys
    validation_checks: List[str]
    transformation_rules: Optional[Dict[str, Any]] = None


@dataclass
class EnhancedWorkflowStep:
    """Enhanced workflow step with detailed execution specifications"""
    step_id: str
    agent_name: str
    task_type: str
    description: str
    actions: List[StepAction]
    handoff_specs: List[HandoffSpec] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    priority: str = "medium"
    timeout_minutes: int = 30
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedWorkflow:
    """Enhanced workflow with comprehensive tracking and control"""
    workflow_id: str
    name: str
    description: str
    steps: List[EnhancedWorkflowStep]
    context: AgentContext
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    handoff_data: Dict[str, Any] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class EnhancedOrchestratorAgent(BaseAgent):
    """
    Advanced orchestrator agent with detailed workflow management, 
    intelligent handoffs, and comprehensive step execution tracking
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="enhanced_orchestrator",
            description="Advanced workflow orchestrator with intelligent agent coordination, detailed handoff management, and comprehensive execution tracking. Manages complex multi-agent job application automation workflows with real-time monitoring and error recovery.",
            config=config
        )
        
        self.registered_agents = {}
        self.active_workflows = {}
        self.workflow_history = []
        self.step_action_registry = {}
        self.handoff_handlers = {}
        
        # Initialize all agents for the automation system
        self._initialize_automation_agents(config)
        
        # Register step actions and handoff handlers
        self._register_step_actions()
        self._register_handoff_handlers()
        
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
    
    def _register_step_actions(self):
        """Register specific actions for each step type"""
        # Job Discovery Actions
        self.step_action_registry["search_jobs"] = [
            StepAction(
                action_id="search_job_listings",
                description="Search for job listings matching criteria",
                required_inputs=["search_criteria", "location", "keywords"],
                expected_outputs=["job_listings", "search_metadata"],
                validation_rules={
                    "min_results": 1,
                    "max_results": 100,
                    "required_fields": ["title", "company", "url"]
                }
            ),
            StepAction(
                action_id="analyze_job_market",
                description="Analyze job market trends and salary data",
                required_inputs=["job_listings", "target_role"],
                expected_outputs=["market_analysis", "salary_insights"],
                validation_rules={"analysis_completeness": 0.8}
            )
        ]
        
        self.step_action_registry["analyze_job_posting"] = [
            StepAction(
                action_id="extract_requirements",
                description="Extract job requirements and qualifications",
                required_inputs=["job_description", "company_info"],
                expected_outputs=["requirements_list", "skill_analysis", "culture_fit"],
                validation_rules={
                    "min_requirements": 3,
                    "confidence_threshold": 0.7
                }
            ),
            StepAction(
                action_id="research_company",
                description="Research company background and values",
                required_inputs=["company_name", "industry"],
                expected_outputs=["company_profile", "recent_news", "culture_insights"],
                validation_rules={"research_depth": "comprehensive"}
            )
        ]
        
        # Resume Optimization Actions
        self.step_action_registry["optimize_resume"] = [
            StepAction(
                action_id="analyze_current_resume",
                description="Analyze current resume against job requirements",
                required_inputs=["current_resume", "job_requirements"],
                expected_outputs=["gap_analysis", "strength_assessment"],
                validation_rules={"analysis_sections": ["skills", "experience", "education"]}
            ),
            StepAction(
                action_id="optimize_content",
                description="Optimize resume content for specific job",
                required_inputs=["current_resume", "gap_analysis", "job_requirements"],
                expected_outputs=["optimized_resume", "changes_summary"],
                validation_rules={
                    "improvement_score": 0.2,  # At least 20% improvement
                    "ats_compatibility": True
                }
            ),
            StepAction(
                action_id="generate_resume_documents",
                description="Generate professional resume documents",
                required_inputs=["optimized_resume"],
                expected_outputs=["pdf_file", "docx_file", "file_metadata"],
                validation_rules={"file_formats": ["pdf", "docx"]}
            )
        ]
        
        # Cover Letter Actions
        self.step_action_registry["generate_cover_letter"] = [
            StepAction(
                action_id="analyze_job_fit",
                description="Analyze candidate fit for specific role",
                required_inputs=["candidate_profile", "job_requirements", "company_info"],
                expected_outputs=["fit_analysis", "value_proposition"],
                validation_rules={"fit_score": 0.6}
            ),
            StepAction(
                action_id="craft_personalized_letter",
                description="Create personalized cover letter content",
                required_inputs=["fit_analysis", "company_research", "writing_style"],
                expected_outputs=["cover_letter_content", "personalization_elements"],
                validation_rules={
                    "word_count_range": [250, 400],
                    "personalization_score": 0.8
                }
            ),
            StepAction(
                action_id="generate_letter_documents",
                description="Generate professional cover letter documents",
                required_inputs=["cover_letter_content"],
                expected_outputs=["pdf_file", "docx_file", "file_metadata"],
                validation_rules={"file_formats": ["pdf", "docx"]}
            )
        ]
        
        # Application Submission Actions
        self.step_action_registry["submit_application"] = [
            StepAction(
                action_id="prepare_application_data",
                description="Prepare all application data and documents",
                required_inputs=["resume_files", "cover_letter_files", "candidate_info"],
                expected_outputs=["application_package", "submission_checklist"],
                validation_rules={"required_documents": ["resume", "cover_letter"]}
            ),
            StepAction(
                action_id="navigate_application_portal",
                description="Navigate to and access job application portal",
                required_inputs=["job_url", "credentials"],
                expected_outputs=["portal_session", "form_structure"],
                validation_rules={"portal_accessibility": True}
            ),
            StepAction(
                action_id="fill_application_form",
                description="Fill out application form with candidate data",
                required_inputs=["form_structure", "candidate_info", "application_package"],
                expected_outputs=["completed_form", "submission_preview"],
                validation_rules={"form_completeness": 0.95}
            ),
            StepAction(
                action_id="submit_and_confirm",
                description="Submit application and confirm receipt",
                required_inputs=["completed_form", "submission_preview"],
                expected_outputs=["submission_confirmation", "tracking_info"],
                validation_rules={"confirmation_received": True}
            )
        ]
        
        # Email Notification Actions
        self.step_action_registry["send_notification"] = [
            StepAction(
                action_id="prepare_notification",
                description="Prepare notification content and recipient list",
                required_inputs=["workflow_status", "results_summary", "user_preferences"],
                expected_outputs=["notification_content", "recipient_list"],
                validation_rules={"content_completeness": 0.9}
            ),
            StepAction(
                action_id="send_email",
                description="Send email notification to recipients",
                required_inputs=["notification_content", "recipient_list"],
                expected_outputs=["delivery_status", "tracking_info"],
                validation_rules={"delivery_success": True}
            )
        ]
        
        self.logger.info(f"Registered {len(self.step_action_registry)} step action types")
    
    def _register_handoff_handlers(self):
        """Register handoff handlers between agents"""
        # Job Discovery → Resume Optimizer
        self.handoff_handlers["job_discovery_to_resume"] = HandoffSpec(
            from_agent="job_discovery",
            to_agent="resume_optimizer",
            data_mapping={
                "job_requirements": "job_requirements",
                "skill_analysis": "target_skills",
                "company_info": "company_context",
                "job_description": "job_description"
            },
            validation_checks=[
                "job_requirements_exists",
                "skill_analysis_complete",
                "company_info_available"
            ],
            transformation_rules={
                "skill_prioritization": "priority_desc",
                "requirement_categorization": "mandatory_preferred_split"
            }
        )
        
        # Job Discovery → Cover Letter
        self.handoff_handlers["job_discovery_to_cover_letter"] = HandoffSpec(
            from_agent="job_discovery",
            to_agent="cover_letter_generator",
            data_mapping={
                "company_profile": "company_research",
                "culture_insights": "company_culture",
                "job_requirements": "role_requirements",
                "recent_news": "company_news"
            },
            validation_checks=[
                "company_profile_complete",
                "culture_insights_available",
                "role_requirements_defined"
            ]
        )
        
        # Resume Optimizer → Cover Letter
        self.handoff_handlers["resume_to_cover_letter"] = HandoffSpec(
            from_agent="resume_optimizer",
            to_agent="cover_letter_generator",
            data_mapping={
                "strength_assessment": "candidate_strengths",
                "optimized_resume": "resume_content",
                "gap_analysis": "improvement_areas"
            },
            validation_checks=[
                "strength_assessment_complete",
                "optimized_resume_ready"
            ]
        )
        
        # Resume & Cover Letter → Application Submitter
        self.handoff_handlers["documents_to_application"] = HandoffSpec(
            from_agent="resume_optimizer",  # Primary source
            to_agent="application_submitter",
            data_mapping={
                "pdf_file": "resume_file",
                "optimized_resume": "resume_data",
                "cover_letter_files": "cover_letter_files",
                "candidate_info": "application_data"
            },
            validation_checks=[
                "resume_file_exists",
                "cover_letter_file_exists",
                "files_accessible"
            ]
        )
        
        # Application Submitter → Email Notification
        self.handoff_handlers["application_to_notification"] = HandoffSpec(
            from_agent="application_submitter",
            to_agent="email_notification",
            data_mapping={
                "submission_confirmation": "application_status",
                "tracking_info": "follow_up_details",
                "portal_session": "application_metadata"
            },
            validation_checks=[
                "submission_confirmed",
                "tracking_available"
            ]
        )
        
        self.logger.info(f"Registered {len(self.handoff_handlers)} handoff handlers")
    
    def create_enhanced_job_application_workflow(self, user_id: str, job_data: Dict[str, Any], 
                                               user_profile: Dict[str, Any]) -> EnhancedWorkflow:
        """
        Create an enhanced job application workflow with detailed step specifications
        
        Args:
            user_id: ID of the user
            job_data: Complete job information
            user_profile: User profile and preferences
            
        Returns:
            Enhanced workflow with detailed execution plan
        """
        workflow_id = str(uuid.uuid4())
        
        context = AgentContext(
            user_id=user_id,
            metadata={
                "job_data": job_data,
                "user_profile": user_profile,
                "workflow_id": workflow_id,
                "automation_mode": True,
                "enhanced_orchestration": True
            }
        )
        
        # Step 1: Workflow Initialization Notification
        step_1 = EnhancedWorkflowStep(
            step_id="init_notification",
            agent_name="email_notification",
            task_type="send_notification",
            description="Send workflow initialization notification to user",
            actions=[self.step_action_registry["send_notification"][0]],
            priority="low"
        )
        
        # Step 2: Deep Job Analysis
        step_2 = EnhancedWorkflowStep(
            step_id="analyze_job_posting",
            agent_name="job_discovery",
            task_type="analyze_job_posting",
            description="Comprehensive job posting analysis with company research",
            actions=self.step_action_registry["analyze_job_posting"],
            depends_on=["init_notification"],
            handoff_specs=[
                self.handoff_handlers["job_discovery_to_resume"],
                self.handoff_handlers["job_discovery_to_cover_letter"]
            ],
            priority="high"
        )
        
        # Step 3: Advanced Resume Optimization
        step_3 = EnhancedWorkflowStep(
            step_id="optimize_resume",
            agent_name="resume_optimizer",
            task_type="optimize_with_research",
            description="Advanced resume optimization with industry research and ATS optimization",
            actions=self.step_action_registry["optimize_resume"],
            depends_on=["analyze_job_posting"],
            handoff_specs=[self.handoff_handlers["resume_to_cover_letter"]],
            priority="high"
        )
        
        # Step 4: Personalized Cover Letter Generation
        step_4 = EnhancedWorkflowStep(
            step_id="generate_cover_letter",
            agent_name="cover_letter_generator",
            task_type="generate_with_research",
            description="Generate highly personalized cover letter with company research",
            actions=self.step_action_registry["generate_cover_letter"],
            depends_on=["analyze_job_posting", "optimize_resume"],
            priority="high"
        )
        
        # Step 5: Application Preparation and Submission
        step_5 = EnhancedWorkflowStep(
            step_id="submit_application",
            agent_name="application_submitter",
            task_type="submit_application",
            description="Prepare and submit complete job application with document upload",
            actions=self.step_action_registry["submit_application"],
            depends_on=["optimize_resume", "generate_cover_letter"],
            handoff_specs=[self.handoff_handlers["application_to_notification"]],
            priority="medium",
            timeout_minutes=45  # Longer timeout for web automation
        )
        
        # Step 6: Completion Notification and Follow-up Setup
        step_6 = EnhancedWorkflowStep(
            step_id="completion_notification",
            agent_name="email_notification",
            task_type="send_application_confirmation",
            description="Send application completion confirmation and set up follow-up reminders",
            actions=[self.step_action_registry["send_notification"][1]],
            depends_on=["submit_application"],
            priority="low"
        )
        
        workflow = EnhancedWorkflow(
            workflow_id=workflow_id,
            name="Enhanced Automated Job Application Workflow",
            description=f"Comprehensive automated application for {job_data.get('title', 'position')} at {job_data.get('company', 'company')} with advanced orchestration",
            steps=[step_1, step_2, step_3, step_4, step_5, step_6],
            context=context
        )
        
        return workflow
    
    async def execute_enhanced_workflow(self, workflow: EnhancedWorkflow) -> Dict[str, Any]:
        """
        Execute an enhanced workflow with detailed step management and intelligent handoffs
        
        Args:
            workflow: The enhanced workflow to execute
            
        Returns:
            Comprehensive workflow execution result
        """
        self.logger.info(f"Starting enhanced workflow {workflow.workflow_id}: {workflow.name}")
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        self.active_workflows[workflow.workflow_id] = workflow
        
        # Log workflow start
        workflow.execution_log.append({
            "event": "workflow_started",
            "timestamp": workflow.started_at.isoformat(),
            "details": {"total_steps": len(workflow.steps)}
        })
        
        try:
            completed_steps = set()
            performance_start = datetime.now()
            
            while len(completed_steps) < len(workflow.steps):
                # Find steps that are ready to execute
                ready_steps = self._find_ready_steps(workflow, completed_steps)
                
                if not ready_steps:
                    if completed_steps:
                        # Some steps completed but none ready - check for failures
                        failed_steps = [s for s in workflow.steps if s.status == StepStatus.FAILED]
                        if failed_steps:
                            raise Exception(f"Workflow blocked by failed steps: {[s.step_id for s in failed_steps]}")
                        else:
                            raise Exception("Workflow deadlock: No ready steps found")
                    else:
                        raise Exception("No initial steps found - workflow configuration error")
                
                # Execute ready steps in parallel where possible
                parallel_tasks = []
                for step in ready_steps:
                    step.status = StepStatus.IN_PROGRESS
                    step.started_at = datetime.now()
                    workflow.current_step = step.step_id
                    
                    # Log step start
                    workflow.execution_log.append({
                        "event": "step_started",
                        "step_id": step.step_id,
                        "agent": step.agent_name,
                        "timestamp": step.started_at.isoformat()
                    })
                    
                    task = self._execute_enhanced_step(step, workflow)
                    parallel_tasks.append((step, task))
                
                # Wait for all parallel tasks to complete
                for step, task in parallel_tasks:
                    try:
                        result = await task
                        
                        if result.get("success"):
                            step.status = StepStatus.COMPLETED
                            step.completed_at = datetime.now()
                            
                            # Process handoffs for this step
                            await self._process_step_handoffs(step, result, workflow)
                            
                            # Store step results
                            workflow.results[step.step_id] = result
                            completed_steps.add(step.step_id)
                            
                            # Log step completion
                            workflow.execution_log.append({
                                "event": "step_completed",
                                "step_id": step.step_id,
                                "timestamp": step.completed_at.isoformat(),
                                "execution_time": (step.completed_at - step.started_at).total_seconds()
                            })
                            
                            self.logger.info(f"Step {step.step_id} completed successfully")
                            
                        else:
                            # Handle step failure
                            step.retry_count += 1
                            if step.retry_count <= step.max_retries:
                                step.status = StepStatus.PENDING  # Retry
                                step.error_message = result.get("message", "Unknown error")
                                
                                # Log retry
                                workflow.execution_log.append({
                                    "event": "step_retry",
                                    "step_id": step.step_id,
                                    "retry_count": step.retry_count,
                                    "error": step.error_message,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                self.logger.warning(f"Step {step.step_id} failed, retrying ({step.retry_count}/{step.max_retries})")
                            else:
                                step.status = StepStatus.FAILED
                                step.error_message = result.get("message", "Max retries exceeded")
                                
                                # Log failure
                                workflow.execution_log.append({
                                    "event": "step_failed",
                                    "step_id": step.step_id,
                                    "error": step.error_message,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                self.logger.error(f"Step {step.step_id} failed permanently: {step.error_message}")
                                raise Exception(f"Critical step {step.step_id} failed: {step.error_message}")
                    
                    except Exception as e:
                        step.status = StepStatus.FAILED
                        step.error_message = str(e)
                        
                        workflow.execution_log.append({
                            "event": "step_exception",
                            "step_id": step.step_id,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        self.logger.error(f"Step {step.step_id} exception: {str(e)}")
                        raise
            
            # All steps completed successfully
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            # Calculate performance metrics
            total_time = (workflow.completed_at - workflow.started_at).total_seconds()
            workflow.performance_metrics = {
                "total_execution_time": total_time,
                "steps_completed": len(completed_steps),
                "average_step_time": total_time / len(workflow.steps),
                "handoffs_processed": len([log for log in workflow.execution_log if log["event"] == "handoff_processed"]),
                "retries_total": sum(step.retry_count for step in workflow.steps)
            }
            
            # Log workflow completion
            workflow.execution_log.append({
                "event": "workflow_completed",
                "timestamp": workflow.completed_at.isoformat(),
                "performance_metrics": workflow.performance_metrics
            })
            
            return self.create_result(
                success=True,
                data={
                    "workflow_id": workflow.workflow_id,
                    "status": workflow.status.value,
                    "steps_completed": len(completed_steps),
                    "execution_time": total_time,
                    "results": workflow.results,
                    "performance_metrics": workflow.performance_metrics,
                    "execution_log": workflow.execution_log
                },
                message=f"Enhanced workflow {workflow.workflow_id} completed successfully"
            )
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            
            workflow.execution_log.append({
                "event": "workflow_failed",
                "error": str(e),
                "timestamp": workflow.completed_at.isoformat()
            })
            
            self.logger.error(f"Enhanced workflow {workflow.workflow_id} failed: {str(e)}")
            
            return self.create_result(
                success=False,
                message=f"Enhanced workflow {workflow.workflow_id} failed: {str(e)}",
                metadata={
                    "workflow_id": workflow.workflow_id,
                    "error": str(e),
                    "execution_log": workflow.execution_log
                }
            )
        
        finally:
            # Move workflow to history
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
            self.workflow_history.append(workflow)
    
    def _find_ready_steps(self, workflow: EnhancedWorkflow, completed_steps: set) -> List[EnhancedWorkflowStep]:
        """Find steps that are ready to execute"""
        ready_steps = []
        
        for step in workflow.steps:
            if (step.step_id not in completed_steps and 
                step.status in [StepStatus.PENDING, StepStatus.READY] and
                (not step.depends_on or all(dep in completed_steps for dep in step.depends_on))):
                
                step.status = StepStatus.READY
                ready_steps.append(step)
        
        return ready_steps
    
    async def _execute_enhanced_step(self, step: EnhancedWorkflowStep, workflow: EnhancedWorkflow) -> Dict[str, Any]:
        """Execute a single enhanced workflow step with detailed action processing"""
        workflow.current_step = step.step_id
        
        # Validate step prerequisites
        validation_result = await self._validate_step_prerequisites(step, workflow)
        if not validation_result["valid"]:
            return self.create_result(
                success=False,
                message=f"Step prerequisites validation failed: {validation_result['reason']}"
            )
        
        # Check if agent is registered
        if step.agent_name not in self.registered_agents:
            self.logger.warning(f"Agent {step.agent_name} not registered, creating mock result")
            
            # Create detailed mock result for enhanced steps
            await asyncio.sleep(2)  # Simulate processing time
            
            mock_result = self.create_result(
                success=True,
                data={
                    "mock": True,
                    "step_id": step.step_id,
                    "actions_executed": [action.action_id for action in step.actions],
                    "simulated_outputs": {
                        action.action_id: {output: f"mock_{output}_value" for output in action.expected_outputs}
                        for action in step.actions
                    }
                },
                message=f"Mock execution of enhanced step {step.step_id}",
                metadata={
                    "agent": step.agent_name,
                    "task_type": step.task_type,
                    "actions_count": len(step.actions)
                }
            )
            
            return mock_result
        
        # Execute with registered agent
        agent = self.registered_agents[step.agent_name]
        
        # Create enhanced task with action specifications
        task = self._create_enhanced_task_from_step(step, workflow)
        
        # Execute the task
        result = await agent.execute(task, workflow.context)
        
        # Validate step outputs
        if result.get("success"):
            output_validation = await self._validate_step_outputs(step, result, workflow)
            if not output_validation["valid"]:
                return self.create_result(
                    success=False,
                    message=f"Step output validation failed: {output_validation['reason']}"
                )
        
        return result
    
    async def _validate_step_prerequisites(self, step: EnhancedWorkflowStep, workflow: EnhancedWorkflow) -> Dict[str, Any]:
        """Validate that all step prerequisites are met"""
        try:
            # Check dependencies are completed
            for dep in step.depends_on:
                if dep not in [s.step_id for s in workflow.steps if s.status == StepStatus.COMPLETED]:
                    return {"valid": False, "reason": f"Dependency {dep} not completed"}
            
            # Check required inputs are available for each action
            for action in step.actions:
                for required_input in action.required_inputs:
                    if not self._is_input_available(required_input, workflow):
                        return {"valid": False, "reason": f"Required input {required_input} not available for action {action.action_id}"}
            
            return {"valid": True, "reason": "All prerequisites met"}
            
        except Exception as e:
            return {"valid": False, "reason": f"Validation error: {str(e)}"}
    
    async def _validate_step_outputs(self, step: EnhancedWorkflowStep, result: Dict[str, Any], workflow: EnhancedWorkflow) -> Dict[str, Any]:
        """Validate that step outputs meet requirements"""
        try:
            result_data = result.get("data", {})
            
            # Check each action's expected outputs
            for action in step.actions:
                for expected_output in action.expected_outputs:
                    if expected_output not in result_data:
                        return {"valid": False, "reason": f"Expected output {expected_output} missing from action {action.action_id}"}
                
                # Apply validation rules
                for rule_name, rule_value in action.validation_rules.items():
                    if not self._apply_validation_rule(rule_name, rule_value, result_data, action):
                        return {"valid": False, "reason": f"Validation rule {rule_name} failed for action {action.action_id}"}
            
            return {"valid": True, "reason": "All outputs validated successfully"}
            
        except Exception as e:
            return {"valid": False, "reason": f"Output validation error: {str(e)}"}
    
    def _is_input_available(self, input_name: str, workflow: EnhancedWorkflow) -> bool:
        """Check if a required input is available in the workflow context or results"""
        # Check workflow context
        if input_name in workflow.context.metadata:
            return True
        
        # Check handoff data
        if input_name in workflow.handoff_data:
            return True
        
        # Check previous step results
        for step_results in workflow.results.values():
            if isinstance(step_results, dict) and input_name in step_results.get("data", {}):
                return True
        
        return False
    
    def _apply_validation_rule(self, rule_name: str, rule_value: Any, data: Dict[str, Any], action: StepAction) -> bool:
        """Apply a specific validation rule to step output data"""
        try:
            if rule_name == "min_results" and isinstance(rule_value, int):
                results_count = len(data.get("job_listings", data.get("results", [])))
                return results_count >= rule_value
            
            elif rule_name == "confidence_threshold" and isinstance(rule_value, float):
                confidence = data.get("confidence_score", data.get("quality_score", 1.0))
                return confidence >= rule_value
            
            elif rule_name == "required_fields" and isinstance(rule_value, list):
                for item in data.get("job_listings", data.get("items", [])):
                    if not all(field in item for field in rule_value):
                        return False
                return True
            
            elif rule_name == "file_formats" and isinstance(rule_value, list):
                generated_files = data.get("generated_files", {})
                return all(fmt in generated_files for fmt in rule_value)
            
            elif rule_name == "word_count_range" and isinstance(rule_value, list):
                word_count = data.get("word_count", 0)
                return rule_value[0] <= word_count <= rule_value[1]
            
            # Add more validation rules as needed
            return True  # Default to pass for unknown rules
            
        except Exception:
            return False
    
    async def _process_step_handoffs(self, step: EnhancedWorkflowStep, result: Dict[str, Any], workflow: EnhancedWorkflow):
        """Process handoffs defined for a completed step"""
        for handoff_spec in step.handoff_specs:
            try:
                # Extract data according to mapping
                handoff_data = {}
                result_data = result.get("data", {})
                
                for output_key, input_key in handoff_spec.data_mapping.items():
                    if output_key in result_data:
                        handoff_data[input_key] = result_data[output_key]
                
                # Apply transformation rules if defined
                if handoff_spec.transformation_rules:
                    handoff_data = self._apply_transformations(handoff_data, handoff_spec.transformation_rules)
                
                # Validate handoff data
                validation_passed = True
                for check in handoff_spec.validation_checks:
                    if not self._validate_handoff_check(check, handoff_data, result_data):
                        self.logger.warning(f"Handoff validation failed: {check}")
                        validation_passed = False
                
                if validation_passed:
                    # Store handoff data for target agent
                    handoff_key = f"{handoff_spec.from_agent}_to_{handoff_spec.to_agent}"
                    workflow.handoff_data[handoff_key] = handoff_data
                    
                    # Log handoff
                    workflow.execution_log.append({
                        "event": "handoff_processed",
                        "from_agent": handoff_spec.from_agent,
                        "to_agent": handoff_spec.to_agent,
                        "data_keys": list(handoff_data.keys()),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    self.logger.info(f"Processed handoff from {handoff_spec.from_agent} to {handoff_spec.to_agent}")
                
            except Exception as e:
                self.logger.error(f"Handoff processing failed: {str(e)}")
    
    def _apply_transformations(self, data: Dict[str, Any], transformation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformation rules to handoff data"""
        transformed_data = data.copy()
        
        for rule_name, rule_config in transformation_rules.items():
            if rule_name == "skill_prioritization" and rule_config == "priority_desc":
                if "target_skills" in transformed_data:
                    skills = transformed_data["target_skills"]
                    if isinstance(skills, list):
                        # Sort skills by priority (assuming they have priority scores)
                        transformed_data["target_skills"] = sorted(skills, key=lambda x: x.get("priority", 0), reverse=True)
            
            elif rule_name == "requirement_categorization" and rule_config == "mandatory_preferred_split":
                if "job_requirements" in transformed_data:
                    requirements = transformed_data["job_requirements"]
                    if isinstance(requirements, list):
                        mandatory = [req for req in requirements if req.get("type") == "mandatory"]
                        preferred = [req for req in requirements if req.get("type") == "preferred"]
                        transformed_data["mandatory_requirements"] = mandatory
                        transformed_data["preferred_requirements"] = preferred
        
        return transformed_data
    
    def _validate_handoff_check(self, check_name: str, handoff_data: Dict[str, Any], result_data: Dict[str, Any]) -> bool:
        """Validate a specific handoff check"""
        if check_name == "job_requirements_exists":
            return "job_requirements" in handoff_data and handoff_data["job_requirements"]
        
        elif check_name == "skill_analysis_complete":
            return "target_skills" in handoff_data and len(handoff_data["target_skills"]) > 0
        
        elif check_name == "company_info_available":
            return "company_context" in handoff_data and handoff_data["company_context"]
        
        elif check_name == "optimized_resume_ready":
            return "resume_content" in handoff_data and handoff_data["resume_content"]
        
        elif check_name == "files_accessible":
            return all(key in handoff_data for key in ["resume_file", "cover_letter_files"])
        
        # Add more validation checks as needed
        return True
    
    def _create_enhanced_task_from_step(self, step: EnhancedWorkflowStep, workflow: EnhancedWorkflow) -> AgentTask:
        """Create an enhanced AgentTask from a WorkflowStep with detailed specifications"""
        # Build comprehensive input data
        input_data = {
            "step_id": step.step_id,
            "workflow_id": workflow.workflow_id,
            "context": workflow.context.metadata,
            "actions": [
                {
                    "action_id": action.action_id,
                    "description": action.description,
                    "required_inputs": action.required_inputs,
                    "expected_outputs": action.expected_outputs,
                    "validation_rules": action.validation_rules
                }
                for action in step.actions
            ],
            "handoff_data": {}
        }
        
        # Add relevant handoff data
        for handoff_key, handoff_data in workflow.handoff_data.items():
            if step.agent_name in handoff_key:
                input_data["handoff_data"][handoff_key] = handoff_data
        
        # Add job data and user profile (always available)
        job_data = workflow.context.metadata.get("job_data", {})
        user_profile = workflow.context.metadata.get("user_profile", {})
        
        input_data.update({
            "job_data": job_data,
            "user_profile": user_profile
        })
        
        # Customize input data based on agent and step type
        if step.agent_name == "job_discovery":
            input_data.update({
                "job_description": job_data.get("summary", ""),
                "company_name": job_data.get("company", ""),
                "job_title": job_data.get("title", ""),
                "industry": job_data.get("industry", "")
            })
        
        elif step.agent_name == "resume_optimizer":
            # Get handoff data from job discovery
            job_handoff = workflow.handoff_data.get("job_discovery_to_resume", {})
            input_data.update({
                "job_description": job_data.get("summary", ""),
                "current_resume": user_profile.get("resume_data", {}),
                "job_requirements": job_handoff.get("job_requirements", []),
                "target_skills": job_handoff.get("target_skills", []),
                "company_context": job_handoff.get("company_context", {}),
                "company_name": job_data.get("company", ""),
                "job_title": job_data.get("title", ""),
                "industry": job_data.get("industry", "")
            })
        
        elif step.agent_name == "cover_letter_generator":
            # Get handoff data from multiple sources
            job_handoff = workflow.handoff_data.get("job_discovery_to_cover_letter", {})
            resume_handoff = workflow.handoff_data.get("resume_to_cover_letter", {})
            
            input_data.update({
                "job_description": job_data.get("summary", ""),
                "company_name": job_data.get("company", ""),
                "job_title": job_data.get("title", ""),
                "hiring_manager": job_data.get("hiring_manager", "Hiring Manager"),
                "candidate_info": user_profile.get("candidate_info", {}),
                "company_research": job_handoff.get("company_research", {}),
                "company_culture": job_handoff.get("company_culture", {}),
                "candidate_strengths": resume_handoff.get("candidate_strengths", []),
                "resume_content": resume_handoff.get("resume_content", {})
            })
        
        elif step.agent_name == "application_submitter":
            # Get handoff data from resume and cover letter agents
            doc_handoff = workflow.handoff_data.get("documents_to_application", {})
            
            input_data.update({
                "job_url": job_data.get("url", ""),
                "job_site": job_data.get("source", ""),
                "candidate_info": user_profile.get("candidate_info", {}),
                "resume_file": doc_handoff.get("resume_file", ""),
                "cover_letter_files": doc_handoff.get("cover_letter_files", {}),
                "application_data": doc_handoff.get("application_data", {})
            })
        
        elif step.agent_name == "email_notification":
            # Get handoff data from application submitter
            app_handoff = workflow.handoff_data.get("application_to_notification", {})
            
            input_data.update({
                "workflow_id": workflow.workflow_id,
                "workflow_status": workflow.status.value,
                "job_details": job_data,
                "agent_results": workflow.results,
                "user_email": user_profile.get("email", ""),
                "application_status": app_handoff.get("application_status", {}),
                "follow_up_details": app_handoff.get("follow_up_details", {}),
                "notification_type": self._determine_enhanced_notification_type(step.task_type, workflow)
            })
        
        return AgentTask(
            task_id=str(uuid.uuid4()),
            task_type=step.task_type,
            description=step.description,
            input_data=input_data,
            priority=step.priority
        )
    
    def _determine_enhanced_notification_type(self, task_type: str, workflow: EnhancedWorkflow) -> str:
        """Determine the appropriate notification type for enhanced workflows"""
        if task_type == "send_notification":
            if workflow.status == WorkflowStatus.RUNNING and not workflow.results:
                return "enhanced_workflow_started"
            elif workflow.status == WorkflowStatus.FAILED:
                return "enhanced_workflow_failed"
            else:
                return "enhanced_workflow_progress"
        elif task_type == "send_application_confirmation":
            return "enhanced_application_submitted"
        else:
            return "enhanced_general_notification"
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """Execute an enhanced orchestrator task"""
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "execute_enhanced_job_application":
                # Create and execute enhanced job application workflow
                workflow = self.create_enhanced_job_application_workflow(
                    user_id=context.user_id,
                    job_data=task.input_data.get("job_data", {}),
                    user_profile=task.input_data.get("user_profile", {})
                )
                
                result = await self.execute_enhanced_workflow(workflow)
                
            elif task_type == "get_enhanced_workflow_status":
                workflow_id = task.input_data.get("workflow_id")
                if workflow_id in self.active_workflows:
                    workflow = self.active_workflows[workflow_id]
                    result = self.create_result(
                        success=True,
                        data={
                            "workflow_id": workflow_id,
                            "status": workflow.status.value,
                            "current_step": workflow.current_step,
                            "progress": len([s for s in workflow.steps if s.status == StepStatus.COMPLETED]) / len(workflow.steps) * 100,
                            "steps_detail": [
                                {
                                    "step_id": s.step_id,
                                    "agent": s.agent_name,
                                    "status": s.status.value,
                                    "description": s.description,
                                    "actions_count": len(s.actions),
                                    "retry_count": s.retry_count,
                                    "error": s.error_message
                                }
                                for s in workflow.steps
                            ],
                            "performance_metrics": workflow.performance_metrics,
                            "handoffs_processed": len(workflow.handoff_data)
                        }
                    )
                else:
                    result = self.create_result(
                        success=False,
                        message=f"Enhanced workflow {workflow_id} not found"
                    )
            
            else:
                result = self.create_result(
                    success=False,
                    message=f"Unknown enhanced task type: {task_type}"
                )
            
            self.log_task_completion(task, result)
            return result
            
        except Exception as e:
            self.log_task_error(task, e)
            return self.create_result(
                success=False,
                message=f"Enhanced orchestrator task execution failed: {str(e)}"
            )
    
    def get_enhanced_active_workflows(self) -> List[Dict[str, Any]]:
        """Get detailed list of enhanced active workflows"""
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "status": wf.status.value,
                "current_step": wf.current_step,
                "started_at": wf.started_at.isoformat() if wf.started_at else None,
                "progress": len([s for s in wf.steps if s.status == StepStatus.COMPLETED]) / len(wf.steps) * 100,
                "total_steps": len(wf.steps),
                "completed_steps": len([s for s in wf.steps if s.status == StepStatus.COMPLETED]),
                "failed_steps": len([s for s in wf.steps if s.status == StepStatus.FAILED]),
                "handoffs_processed": len(wf.handoff_data),
                "total_retries": sum(s.retry_count for s in wf.steps),
                "performance_metrics": wf.performance_metrics
            }
            for wf in self.active_workflows.values()
        ]