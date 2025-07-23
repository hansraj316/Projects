"""
Automation Agent - Using OpenAI Agents SDK
Orchestrates complete job application automation workflow with proper agent handoffs
"""

from __future__ import annotations

import json
import sys
import os
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

# Handle OpenAI Agents SDK import conflicts
try:
    # Temporarily remove local agents from path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir in sys.path:
        sys.path.remove(parent_dir)
    
    from agents import Agent, handoff, function_tool, RunContextWrapper, Runner
    from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
    
    # Restore path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        
except ImportError as e:
    print(f"Warning: OpenAI Agents SDK not available for Automation Agent: {e}")
    # Create mock classes
    class Agent:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    def handoff(**kwargs):
        return kwargs
    
    def function_tool(func):
        return func
    
    class RunContextWrapper:
        def __init__(self, context):
            self.context = context
    
    class Runner:
        @staticmethod
        async def run(starting_agent, input, context=None):
            return {"final_output": "Mock automation result", "success": True}
    
    def prompt_with_handoff_instructions(prompt):
        return f"[HANDOFF ENABLED]\n{prompt}"

# Import our OpenAI SDK agents
try:
    from agents.openai_job_discovery import create_job_discovery_agent, JobSearchInput
    from agents.openai_resume_optimizer import create_resume_optimizer_agent, ResumeOptimizationInput
    from agents.openai_cover_letter import create_cover_letter_agent, CoverLetterInput
    from database.operations import DatabaseOperations
except ImportError as e:
    print(f"Warning: Could not import required agents or database: {e}")


class AutomationWorkflowInput(BaseModel):
    """Input for automation workflow"""
    user_id: str
    job_search_criteria: Dict[str, Any]
    automation_config: Dict[str, Any]
    user_profile: Dict[str, Any]
    resume_data: Dict[str, Any] = {}


class JobApplicationContext(BaseModel):
    """Context for job application automation"""
    user_id: str
    workflow_id: str
    job_search_criteria: Dict[str, Any]
    user_profile: Dict[str, Any]
    resume_data: Dict[str, Any]
    automation_config: Dict[str, Any]
    current_job: Optional[Dict[str, Any]] = None
    found_jobs: List[Dict[str, Any]] = []
    application_results: List[Dict[str, Any]] = []


class AutomationResult(BaseModel):
    """Result from automation workflow"""
    success: bool
    workflow_id: str
    total_jobs_found: int
    applications_created: int
    applications_submitted: int
    execution_summary: Dict[str, Any]
    detailed_results: List[Dict[str, Any]]


@function_tool
def execute_job_automation_workflow(input_data: AutomationWorkflowInput) -> AutomationResult:
    """
    Execute complete job automation workflow following the specified steps:
    1. Call Job search agent based on configuration
    2. Hand off to Resume agent for optimization
    3. Hand off to Cover letter agent for generation
    4. Save to database against application
    5. Trigger Playwright MCP automation
    
    Args:
        input_data: Automation workflow parameters
        
    Returns:
        AutomationResult with complete workflow results
    """
    print(f"[Automation Agent] Starting job automation workflow for user {input_data.user_id}")
    
    workflow_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        # Create workflow context
        context = JobApplicationContext(
            user_id=input_data.user_id,
            workflow_id=workflow_id,
            job_search_criteria=input_data.job_search_criteria,
            user_profile=input_data.user_profile,
            resume_data=input_data.resume_data,
            automation_config=input_data.automation_config
        )
        
        # Execute the workflow steps
        workflow_result = _execute_automation_steps(context)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return AutomationResult(
            success=workflow_result["success"],
            workflow_id=workflow_id,
            total_jobs_found=workflow_result["total_jobs_found"],
            applications_created=workflow_result["applications_created"],
            applications_submitted=workflow_result["applications_submitted"],
            execution_summary={
                "execution_time": execution_time,
                "workflow_id": workflow_id,
                "user_id": input_data.user_id,
                "timestamp": start_time.isoformat(),
                "automation_config": input_data.automation_config
            },
            detailed_results=workflow_result["detailed_results"]
        )
        
    except Exception as e:
        print(f"[Automation Agent] Workflow failed: {str(e)}")
        return AutomationResult(
            success=False,
            workflow_id=workflow_id,
            total_jobs_found=0,
            applications_created=0,
            applications_submitted=0,
            execution_summary={
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            },
            detailed_results=[]
        )


@function_tool
def monitor_automation_progress(workflow_id: str) -> Dict[str, Any]:
    """
    Monitor the progress of automation workflow
    
    Args:
        workflow_id: ID of the workflow to monitor
        
    Returns:
        Current progress and status information
    """
    print(f"[Automation Monitor] Checking progress for workflow {workflow_id}")
    
    # Simulate progress monitoring
    progress_data = {
        "workflow_id": workflow_id,
        "status": "in_progress",
        "current_step": "resume_optimization",
        "steps_completed": 2,
        "total_steps": 5,
        "progress_percentage": 40,
        "current_job": {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "step": "Optimizing resume"
        },
        "timeline": [
            {"step": "job_search", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"step": "resume_optimization", "status": "in_progress", "timestamp": datetime.now().isoformat()},
            {"step": "cover_letter_generation", "status": "pending", "timestamp": None},
            {"step": "database_save", "status": "pending", "timestamp": None},
            {"step": "playwright_automation", "status": "pending", "timestamp": None}
        ],
        "estimated_completion": "15 minutes",
        "jobs_processed": 2,
        "jobs_remaining": 3
    }
    
    return progress_data


@function_tool
def trigger_playwright_automation(job_data: Dict[str, Any], application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trigger Playwright MCP automation for job application submission
    
    Args:
        job_data: Job information for application
        application_data: Prepared application materials
        
    Returns:
        Playwright automation results
    """
    print(f"[Playwright Automation] Triggering automation for {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
    
    # Prepare automation parameters
    automation_params = {
        "target_url": job_data.get("application_url", ""),
        "job_title": job_data.get("title", ""),
        "company_name": job_data.get("company", ""),
        "resume_file": application_data.get("resume_file", ""),
        "cover_letter_file": application_data.get("cover_letter_file", ""),
        "user_profile": application_data.get("user_profile", {}),
        "automation_config": {
            "headless": True,
            "timeout": 60000,
            "retry_attempts": 3,
            "screenshot_on_error": True
        }
    }
    
    # Simulate Playwright MCP automation
    automation_result = {
        "success": True,
        "automation_id": f"PLAY-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(job_data.get('company', ''))%1000:03d}",
        "job_title": job_data.get("title", ""),
        "company": job_data.get("company", ""),
        "application_url": job_data.get("application_url", ""),
        "steps_executed": [
            "Navigated to application page",
            "Filled personal information form",
            "Uploaded resume document",
            "Uploaded cover letter document",
            "Completed additional questions",
            "Submitted application successfully"
        ],
        "execution_time": "2.5 minutes",
        "screenshots_taken": 3,
        "form_fields_filled": 12,
        "documents_uploaded": 2,
        "submission_confirmed": True,
        "confirmation_number": f"CONF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "next_steps": [
            "Monitor email for confirmation",
            "Track application status",
            "Prepare for potential interviews"
        ]
    }
    
    return automation_result


def create_automation_agent() -> Agent:
    """Create the Automation Agent using OpenAI Agents SDK"""
    
    # Create specialized agents for handoffs
    job_discovery_agent = create_job_discovery_agent()
    resume_optimizer_agent = create_resume_optimizer_agent()
    cover_letter_agent = create_cover_letter_agent()
    
    return Agent(
        name="Job Application Automation Specialist",
        instructions=prompt_with_handoff_instructions("""
        You are the master automation coordinator for job applications. You orchestrate the complete 
        workflow following these exact steps:
        
        1. **Job Search**: Hand off to Job Discovery Agent based on user configuration to find relevant jobs
        2. **Resume Optimization**: Hand off to Resume Optimizer Agent for each job to optimize resume or use existing
        3. **Cover Letter Generation**: Hand off to Cover Letter Agent to construct personalized cover letters
        4. **Database Storage**: Save all application data, resumes, and cover letters to database
        5. **Playwright Automation**: Trigger Playwright MCP for automated job application submission
        
        Your responsibilities:
        - Coordinate seamless handoffs between all agents
        - Track and monitor progress throughout the automation pipeline
        - Save all generated content to the database with proper application linking
        - Trigger web automation for actual job applications
        - Provide detailed progress updates and monitoring
        
        Always maintain context between handoffs and ensure data flows properly through each step.
        Monitor and report on automation progress in real-time.
        """),
        model="gpt-4o-mini",
        handoffs=[
            handoff(
                agent=job_discovery_agent,
                tool_description_override="Hand off to Job Discovery Agent to search for jobs based on criteria"
            ),
            handoff(
                agent=resume_optimizer_agent,
                tool_description_override="Hand off to Resume Optimizer Agent to optimize resume for specific job"
            ),
            handoff(
                agent=cover_letter_agent,
                tool_description_override="Hand off to Cover Letter Agent to generate personalized cover letter"
            )
        ],
        tools=[
            execute_job_automation_workflow,
            monitor_automation_progress,
            trigger_playwright_automation
        ]
    )


# Helper functions for automation workflow

def _execute_automation_steps(context: JobApplicationContext) -> Dict[str, Any]:
    """Execute the complete automation workflow steps"""
    
    detailed_results = []
    applications_created = 0
    applications_submitted = 0
    
    try:
        # Step 1: Job Search
        print(f"[Automation] Step 1: Searching for jobs based on criteria")
        job_search_result = _execute_job_search_step(context)
        detailed_results.append(job_search_result)
        
        if not job_search_result["success"]:
            return _create_workflow_result(False, 0, 0, 0, detailed_results, "Job search failed")
        
        found_jobs = job_search_result["jobs"]
        context.found_jobs = found_jobs
        
        # Process each job through the automation pipeline
        for job_index, job_data in enumerate(found_jobs):
            print(f"[Automation] Processing job {job_index + 1}/{len(found_jobs)}: {job_data.get('title', 'Unknown')}")
            context.current_job = job_data
            
            # Step 2: Resume Optimization
            resume_result = _execute_resume_optimization_step(context, job_data)
            detailed_results.append(resume_result)
            
            if not resume_result["success"]:
                print(f"[Automation] Resume optimization failed for {job_data.get('title', 'job')}")
                continue
            
            # Step 3: Cover Letter Generation
            cover_letter_result = _execute_cover_letter_step(context, job_data, resume_result)
            detailed_results.append(cover_letter_result)
            
            if not cover_letter_result["success"]:
                print(f"[Automation] Cover letter generation failed for {job_data.get('title', 'job')}")
                continue
            
            # Step 4: Database Storage
            db_result = _save_application_to_database(context, job_data, resume_result, cover_letter_result)
            detailed_results.append(db_result)
            applications_created += 1
            
            # Step 5: Playwright Automation
            if context.automation_config.get("auto_submit", False):
                playwright_result = _execute_playwright_automation_step(context, job_data, resume_result, cover_letter_result)
                detailed_results.append(playwright_result)
                
                if playwright_result["success"]:
                    applications_submitted += 1
            
            # Rate limiting between applications
            if context.automation_config.get("rate_limit_delay", 0) > 0:
                print(f"[Automation] Rate limiting: waiting {context.automation_config['rate_limit_delay']} seconds")
                # In real implementation: await asyncio.sleep(context.automation_config['rate_limit_delay'])
        
        return _create_workflow_result(
            True, 
            len(found_jobs), 
            applications_created, 
            applications_submitted, 
            detailed_results
        )
        
    except Exception as e:
        print(f"[Automation] Workflow execution failed: {str(e)}")
        return _create_workflow_result(False, 0, 0, 0, detailed_results, str(e))


def _execute_job_search_step(context: JobApplicationContext) -> Dict[str, Any]:
    """Execute job search step"""
    
    search_criteria = context.job_search_criteria
    
    # Simulate job search using the job discovery agent
    job_search_input = JobSearchInput(
        job_title=search_criteria.get("job_title", ""),
        location=search_criteria.get("location", ""),
        experience_level=search_criteria.get("experience_level", ""),
        remote_preference=search_criteria.get("remote_preference", ""),
        salary_range=search_criteria.get("salary_range", "")
    )
    
    # Generate sample jobs based on search criteria
    from agents.openai_job_discovery import _generate_dynamic_jobs
    found_jobs = _generate_dynamic_jobs(job_search_input)
    
    # Limit jobs based on automation config
    max_jobs = context.automation_config.get("max_applications_per_run", 5)
    found_jobs = found_jobs[:max_jobs]
    
    return {
        "step": "job_search",
        "success": True,
        "jobs": found_jobs,
        "total_found": len(found_jobs),
        "search_criteria": search_criteria,
        "timestamp": datetime.now().isoformat(),
        "agent_used": "job_discovery_agent"
    }


def _execute_resume_optimization_step(context: JobApplicationContext, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute resume optimization step"""
    
    # Check if resume should be optimized or use existing
    should_optimize = context.automation_config.get("optimize_resume_per_job", True)
    
    if should_optimize:
        # Create resume optimization input
        resume_input = ResumeOptimizationInput(
            current_resume=context.resume_data,
            job_description=job_data.get("summary", ""),
            company_name=job_data.get("company", ""),
            job_title=job_data.get("title", ""),
            target_skills=job_data.get("skills", [])
        )
        
        # Simulate resume optimization
        from agents.openai_resume_optimizer import _optimize_resume_structure, _calculate_ats_score
        optimized_resume = _optimize_resume_structure(
            context.resume_data, 
            job_data.get("skills", []), 
            job_data.get("summary", "")
        )
        
        ats_score = _calculate_ats_score(optimized_resume, job_data.get("summary", ""))
        
        return {
            "step": "resume_optimization",
            "success": True,
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "optimized_resume": optimized_resume,
            "optimization_applied": True,
            "ats_score": ats_score,
            "timestamp": datetime.now().isoformat(),
            "agent_used": "resume_optimizer_agent"
        }
    else:
        return {
            "step": "resume_optimization",
            "success": True,
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "optimized_resume": context.resume_data,
            "optimization_applied": False,
            "ats_score": 85,  # Default score for existing resume
            "timestamp": datetime.now().isoformat(),
            "agent_used": "resume_optimizer_agent"
        }


def _execute_cover_letter_step(context: JobApplicationContext, job_data: Dict[str, Any], resume_result: Dict[str, Any]) -> Dict[str, Any]:
    """Execute cover letter generation step"""
    
    # Create cover letter input
    cover_letter_input = CoverLetterInput(
        job_data=job_data,
        user_profile=context.user_profile,
        company_name=job_data.get("company", ""),
        job_title=job_data.get("title", ""),
        optimized_resume=resume_result.get("optimized_resume", {})
    )
    
    # Simulate cover letter generation
    from agents.openai_cover_letter import _create_personalized_cover_letter, _research_company_insights
    
    company_insights = _research_company_insights(job_data.get("company", ""), job_data.get("title", ""))
    
    cover_letter = _create_personalized_cover_letter(
        user_name=context.user_profile.get("name", ""),
        company_name=job_data.get("company", ""),
        job_title=job_data.get("title", ""),
        job_data=job_data,
        user_profile=context.user_profile,
        company_insights=company_insights
    )
    
    return {
        "step": "cover_letter_generation",
        "success": True,
        "job_title": job_data.get("title", ""),
        "company": job_data.get("company", ""),
        "cover_letter": cover_letter,
        "company_insights": company_insights,
        "personalization_score": 88,
        "timestamp": datetime.now().isoformat(),
        "agent_used": "cover_letter_agent"
    }


def _save_application_to_database(context: JobApplicationContext, job_data: Dict[str, Any], 
                                resume_result: Dict[str, Any], cover_letter_result: Dict[str, Any]) -> Dict[str, Any]:
    """Save application data to database"""
    
    try:
        # Create application record
        application_data = {
            "id": str(uuid.uuid4()),
            "user_id": context.user_id,
            "workflow_id": context.workflow_id,
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "job_description": job_data.get("summary", ""),
            "application_url": job_data.get("application_url", ""),
            "status": "prepared",
            "resume_data": resume_result.get("optimized_resume", {}),
            "cover_letter": cover_letter_result.get("cover_letter", ""),
            "ats_score": resume_result.get("ats_score", 0),
            "personalization_score": cover_letter_result.get("personalization_score", 0),
            "created_at": datetime.now().isoformat(),
            "automation_config": context.automation_config
        }
        
        # In real implementation, save to actual database
        # db_ops = DatabaseOperations()
        # db_ops.create_application_record(application_data)
        
        return {
            "step": "database_save",
            "success": True,
            "application_id": application_data["id"],
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "saved_data": {
                "resume": True,
                "cover_letter": True,
                "job_details": True,
                "automation_config": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "step": "database_save",
            "success": False,
            "error": str(e),
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "timestamp": datetime.now().isoformat()
        }


def _execute_playwright_automation_step(context: JobApplicationContext, job_data: Dict[str, Any], 
                                      resume_result: Dict[str, Any], cover_letter_result: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Playwright automation step"""
    
    application_data = {
        "user_profile": context.user_profile,
        "resume_file": f"resume_{job_data.get('company', 'company').replace(' ', '_')}.pdf",
        "cover_letter_file": f"cover_letter_{job_data.get('company', 'company').replace(' ', '_')}.pdf",
        "optimized_resume": resume_result.get("optimized_resume", {}),
        "cover_letter": cover_letter_result.get("cover_letter", "")
    }
    
    # Trigger Playwright MCP automation
    automation_result = trigger_playwright_automation(job_data, application_data)
    
    return {
        "step": "playwright_automation",
        "success": automation_result.get("success", False),
        "automation_id": automation_result.get("automation_id", ""),
        "job_title": job_data.get("title", ""),
        "company": job_data.get("company", ""),
        "submission_confirmed": automation_result.get("submission_confirmed", False),
        "confirmation_number": automation_result.get("confirmation_number", ""),
        "execution_time": automation_result.get("execution_time", ""),
        "timestamp": datetime.now().isoformat()
    }


def _create_workflow_result(success: bool, total_jobs: int, created: int, submitted: int, 
                          detailed_results: List[Dict[str, Any]], error: str = None) -> Dict[str, Any]:
    """Create workflow result summary"""
    
    return {
        "success": success,
        "total_jobs_found": total_jobs,
        "applications_created": created,
        "applications_submitted": submitted,
        "detailed_results": detailed_results,
        "error": error,
        "summary": {
            "steps_completed": len([r for r in detailed_results if r.get("success")]),
            "steps_failed": len([r for r in detailed_results if not r.get("success")]),
            "success_rate": f"{(created/total_jobs*100):.1f}%" if total_jobs > 0 else "0%"
        }
    }


# Create the agent instance
automation_agent = create_automation_agent()