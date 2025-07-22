"""
Application Submission Agent - Uses Playwright MCP Server for automated job applications
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask, AgentContext


class ApplicationSubmitterAgent(BaseAgent):
    """
    AI agent that submits job applications using Playwright MCP Server for web automation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="application_submitter",
            description="You are an expert web automation specialist that submits job applications on various job sites. You navigate job portals, fill out application forms, upload documents, and handle the complete application submission process using Playwright browser automation. You can handle different job sites like LinkedIn, Indeed, Glassdoor, and company career pages.",
            config=config
        )
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute application submission task
        
        Args:
            task: The task to execute
            context: Shared context information
            
        Returns:
            Task execution result with application submission details
        """
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "submit_application":
                result = await self._submit_application(task, context)
            elif task_type == "check_application_status":
                result = await self._check_application_status(task, context)
            elif task_type == "fill_application_form":
                result = await self._fill_application_form(task, context)
            elif task_type == "upload_documents":
                result = await self._upload_documents(task, context)
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
                message=f"Application submission failed: {str(e)}"
            )
    
    async def _submit_application(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Submit a complete job application using Playwright MCP Server
        
        Args:
            task: The submission task
            context: Context including job and candidate information
            
        Returns:
            Application submission result
        """
        # Extract information from task data
        job_url = task.input_data.get("job_url", "")
        candidate_info = task.input_data.get("candidate_info", {})
        resume_path = task.input_data.get("resume_path", "")
        cover_letter_path = task.input_data.get("cover_letter_path", "")
        job_site = task.input_data.get("job_site", "unknown")
        
        # Use Playwright MCP tools to navigate and submit application
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_navigate",
                    "description": "Navigate to job application URL"
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "mcp__playwright__browser_snapshot",
                    "description": "Take accessibility snapshot of the page"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_click",
                    "description": "Click on application buttons"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_type",
                    "description": "Type text into form fields"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_file_upload", 
                    "description": "Upload resume and cover letter files"
                }
            }
        ]
        
        # Create AI prompt for application submission
        prompt = f"""
        Submit a job application using the Playwright browser automation tools.
        
        Job Details:
        - URL: {job_url}
        - Job Site: {job_site}
        - Resume Path: {resume_path}
        - Cover Letter Path: {cover_letter_path}
        
        Candidate Information:
        {json.dumps(candidate_info, indent=2)}
        
        Steps to perform:
        1. Navigate to the job URL
        2. Take a snapshot to see the page layout
        3. Find and click the "Apply" or "Apply Now" button
        4. Fill out the application form with candidate information
        5. Upload the resume file at {resume_path}
        6. Upload the cover letter file at {cover_letter_path}
        7. Complete any additional required fields
        8. Submit the application
        9. Capture confirmation details
        
        Handle common scenarios:
        - Login requirements (skip if login required)
        - Multi-step application forms
        - Required vs optional fields
        - File upload validation
        - Application confirmation pages
        
        Return detailed results about the submission process.
        """
        
        # Execute with Playwright MCP tools
        ai_response = self.get_response(prompt, tools=tools)
        
        # Parse the submission results
        submission_data = self._parse_submission_response(ai_response)
        
        # Calculate success probability based on response
        success_score = self._calculate_submission_success(ai_response)
        
        return self.create_result(
            success=success_score > 0.7,
            data={
                "submission_details": submission_data,
                "job_url": job_url,
                "job_site": job_site,
                "success_probability": success_score,
                "automation_log": ai_response,
                "files_uploaded": {
                    "resume": resume_path,
                    "cover_letter": cover_letter_path
                },
                "candidate_info": candidate_info
            },
            message=f"Application {'submitted successfully' if success_score > 0.7 else 'submission attempted'} for {job_site}",
            metadata={
                "job_url": job_url,
                "job_site": job_site,
                "submission_date": datetime.now().isoformat(),
                "automation_method": "playwright_mcp"
            }
        )
    
    async def _check_application_status(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Check the status of a previously submitted application
        
        Args:
            task: The status check task
            context: Context information
            
        Returns:
            Application status result
        """
        application_url = task.input_data.get("application_url", "")
        job_site = task.input_data.get("job_site", "")
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_navigate",
                    "description": "Navigate to application status page"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_snapshot", 
                    "description": "Take snapshot to read status information"
                }
            }
        ]
        
        prompt = f"""
        Check the status of a job application by navigating to {application_url} on {job_site}.
        
        Steps:
        1. Navigate to the application status URL
        2. Take a snapshot to see the current status
        3. Look for status indicators like:
           - "Application Submitted"
           - "Under Review" 
           - "Interview Scheduled"
           - "Application Rejected"
           - "Position Filled"
        4. Extract any additional details like review dates, next steps, etc.
        
        Return the current application status and any relevant details.
        """
        
        ai_response = self.get_response(prompt, tools=tools)
        status_data = self._parse_status_response(ai_response)
        
        return self.create_result(
            success=True,
            data=status_data,
            message=f"Application status checked for {job_site}"
        )
    
    async def _fill_application_form(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Fill out application form fields with candidate information
        
        Args:
            task: The form filling task
            context: Context information
            
        Returns:
            Form filling result
        """
        form_data = task.input_data.get("form_data", {})
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_snapshot",
                    "description": "Take snapshot to identify form fields"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_type",
                    "description": "Type information into form fields"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_select_option",
                    "description": "Select options from dropdown menus"
                }
            }
        ]
        
        prompt = f"""
        Fill out the job application form with the provided candidate information.
        
        Form Data:
        {json.dumps(form_data, indent=2)}
        
        Steps:
        1. Take a snapshot to identify all form fields
        2. Fill out each field with the appropriate information:
           - Personal information (name, email, phone)
           - Address and location details
           - Work experience and education
           - Skills and qualifications
           - Salary expectations (if required)
           - Availability and start date
        3. Handle dropdown selections for experience level, job type, etc.
        4. Ensure all required fields are completed
        
        Be thorough and accurate when filling out the form.
        """
        
        ai_response = self.get_response(prompt, tools=tools)
        
        return self.create_result(
            success=True,
            data={"form_completion": ai_response},
            message="Application form filled successfully"
        )
    
    async def _upload_documents(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Upload resume and cover letter documents
        
        Args:
            task: The document upload task
            context: Context information
            
        Returns:
            Document upload result
        """
        resume_path = task.input_data.get("resume_path", "")
        cover_letter_path = task.input_data.get("cover_letter_path", "")
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_snapshot",
                    "description": "Identify upload buttons and fields"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp__playwright__browser_file_upload",
                    "description": "Upload files to the application"
                }
            }
        ]
        
        prompt = f"""
        Upload the resume and cover letter files for the job application.
        
        Files to upload:
        - Resume: {resume_path}
        - Cover Letter: {cover_letter_path}
        
        Steps:
        1. Take a snapshot to identify file upload areas
        2. Upload the resume file to the appropriate field
        3. Upload the cover letter file if there's a separate field
        4. Verify that files were uploaded successfully
        5. Check for any file format or size validation messages
        
        Handle common upload scenarios and validation requirements.
        """
        
        ai_response = self.get_response(prompt, tools=tools)
        
        return self.create_result(
            success=True,
            data={
                "uploads": {
                    "resume": resume_path,
                    "cover_letter": cover_letter_path
                },
                "upload_log": ai_response
            },
            message="Documents uploaded successfully"
        )
    
    def _parse_submission_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response for application submission details"""
        return {
            "submission_completed": "submitted" in ai_response.lower() or "success" in ai_response.lower(),
            "confirmation_received": "confirmation" in ai_response.lower(),
            "errors_encountered": "error" in ai_response.lower() or "failed" in ai_response.lower(),
            "additional_steps_required": "login" in ai_response.lower() or "required" in ai_response.lower(),
            "submission_log": ai_response,
            "timestamp": datetime.now().isoformat()
        }
    
    def _parse_status_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response for application status details"""
        status_keywords = {
            "submitted": ["submitted", "received", "pending"],
            "reviewing": ["review", "reviewing", "under review"],
            "interview": ["interview", "phone screen", "next round"],
            "rejected": ["rejected", "not selected", "unsuccessful"],
            "filled": ["position filled", "filled", "closed"]
        }
        
        current_status = "unknown"
        for status, keywords in status_keywords.items():
            if any(keyword in ai_response.lower() for keyword in keywords):
                current_status = status
                break
        
        return {
            "status": current_status,
            "status_details": ai_response,
            "last_updated": datetime.now().isoformat(),
            "next_steps": self._extract_next_steps(ai_response)
        }
    
    def _extract_next_steps(self, response: str) -> List[str]:
        """Extract next steps from status response"""
        next_steps = []
        if "interview" in response.lower():
            next_steps.append("Prepare for interview")
        if "follow up" in response.lower():
            next_steps.append("Follow up on application")
        if "wait" in response.lower():
            next_steps.append("Wait for further communication")
        
        return next_steps if next_steps else ["Monitor application status"]
    
    def _calculate_submission_success(self, ai_response: str) -> float:
        """Calculate probability of successful submission based on AI response"""
        success_indicators = ["submitted", "confirmation", "success", "completed"]
        failure_indicators = ["error", "failed", "unable", "blocked", "login required"]
        
        success_count = sum(1 for indicator in success_indicators if indicator in ai_response.lower())
        failure_count = sum(1 for indicator in failure_indicators if indicator in ai_response.lower())
        
        if failure_count > success_count:
            return 0.3  # Low success probability
        elif success_count > 0:
            return 0.9  # High success probability
        else:
            return 0.6  # Moderate success probability (unclear response)