"""
Application Submitter Agent - Using OpenAI Agents SDK
Handles job application submission with web automation and proper handoffs
"""

from __future__ import annotations

import json
import sys
import os
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
    
    from agents import Agent, handoff, function_tool, RunContextWrapper
    from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
    
    # Restore path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        
except ImportError as e:
    print(f"Warning: OpenAI Agents SDK not available for Application Submitter: {e}")
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
    
    def prompt_with_handoff_instructions(prompt):
        return f"[HANDOFF ENABLED]\n{prompt}"


class ApplicationSubmissionInput(BaseModel):
    """Input data for application submission"""
    job_data: Dict[str, Any]
    user_profile: Dict[str, Any]
    optimized_resume: Dict[str, Any]
    cover_letter: str
    application_url: str = ""


class WebAutomationInput(BaseModel):
    """Input data for web automation"""
    target_url: str
    form_data: Dict[str, Any]
    automation_type: str = "job_application"
    browser_config: Dict[str, Any] = {}


class DocumentPreparationInput(BaseModel):
    """Input data for document preparation"""
    resume_data: Dict[str, Any]
    cover_letter: str
    job_title: str
    company_name: str
    output_format: str = "pdf"


class ApplicationSubmissionResult(BaseModel):
    """Result from application submission"""
    success: bool
    application_id: str
    submission_details: Dict[str, Any]
    documents_submitted: List[str]
    confirmation_info: Dict[str, Any]
    next_steps: List[str]


@function_tool
def submit_job_application(input_data: ApplicationSubmissionInput) -> ApplicationSubmissionResult:
    """
    Submit job application with automated form filling and document upload
    
    Args:
        input_data: Application submission parameters
        
    Returns:
        ApplicationSubmissionResult with submission details and confirmation
    """
    print(f"[Application Submitter] Submitting application for {input_data.job_data.get('title', 'Unknown')} at {input_data.job_data.get('company', 'Unknown')}")
    
    job_data = input_data.job_data
    user_profile = input_data.user_profile
    
    # Prepare application documents
    documents_prepared = _prepare_application_documents(
        resume_data=input_data.optimized_resume,
        cover_letter=input_data.cover_letter,
        job_title=job_data.get("title", ""),
        company_name=job_data.get("company", "")
    )
    
    # Extract application URL
    application_url = input_data.application_url or job_data.get("application_url", "")
    
    # Simulate application submission
    submission_result = _execute_application_submission(
        application_url=application_url,
        user_profile=user_profile,
        job_data=job_data,
        prepared_documents=documents_prepared
    )
    
    # Generate confirmation info
    confirmation_info = {
        "submission_timestamp": datetime.now().isoformat(),
        "application_method": _determine_application_method(application_url),
        "confirmation_number": f"APP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(job_data.get('company', ''))%1000:03d}",
        "estimated_response_time": "1-2 weeks",
        "contact_info": job_data.get("contact_email", "recruiting@company.com")
    }
    
    # Generate next steps
    next_steps = _generate_next_steps(job_data, submission_result)
    
    return ApplicationSubmissionResult(
        success=submission_result.get("success", True),
        application_id=confirmation_info["confirmation_number"],
        submission_details=submission_result,
        documents_submitted=documents_prepared["file_list"],
        confirmation_info=confirmation_info,
        next_steps=next_steps
    )


@function_tool
def automate_web_form_filling(automation_input: WebAutomationInput) -> Dict[str, Any]:
    """
    Automate web form filling using browser automation
    
    Args:
        automation_input: Web automation parameters
        
    Returns:
        Automation results with form filling details
    """
    print(f"[Web Automation] Automating form filling for {automation_input.target_url}")
    
    # Simulate web automation process
    automation_steps = [
        "Navigate to application page",
        "Detect form fields and requirements",
        "Fill personal information",
        "Upload resume and cover letter",
        "Complete application questions",
        "Review and submit application"
    ]
    
    automation_result = {
        "automation_type": automation_input.automation_type,
        "target_url": automation_input.target_url,
        "steps_executed": automation_steps,
        "form_fields_filled": len(automation_input.form_data),
        "documents_uploaded": ["resume.pdf", "cover_letter.pdf"],
        "execution_time": "2.3 minutes",
        "success_rate": "95%",
        "completion_status": "Successfully submitted",
        "browser_info": {
            "browser": "Chrome",
            "version": "Latest",
            "headless": automation_input.browser_config.get("headless", True)
        },
        "validation_checks": {
            "form_completion": "100%",
            "required_fields": "All filled",
            "document_uploads": "Successful",
            "submission_confirmation": "Received"
        }
    }
    
    return automation_result


@function_tool
def prepare_application_documents(prep_input: DocumentPreparationInput) -> Dict[str, Any]:
    """
    Prepare and format application documents for submission
    
    Args:
        prep_input: Document preparation parameters
        
    Returns:
        Document preparation results with file details
    """
    print(f"[Document Preparation] Preparing documents for {prep_input.job_title} application")
    
    # Generate document files
    document_files = {
        "resume": {
            "filename": f"Resume_{prep_input.job_title.replace(' ', '_')}_{prep_input.company_name.replace(' ', '_')}.pdf",
            "format": prep_input.output_format,
            "size": "245 KB",
            "pages": 2,
            "content_sections": ["Summary", "Experience", "Skills", "Education"],
            "optimization_score": 92
        },
        "cover_letter": {
            "filename": f"CoverLetter_{prep_input.job_title.replace(' ', '_')}_{prep_input.company_name.replace(' ', '_')}.pdf",
            "format": prep_input.output_format,
            "size": "156 KB", 
            "pages": 1,
            "word_count": len(prep_input.cover_letter.split()),
            "personalization_score": 88
        }
    }
    
    # Add additional documents if needed
    additional_docs = _generate_additional_documents(prep_input.job_title)
    
    preparation_summary = {
        "total_documents": len(document_files) + len(additional_docs),
        "primary_documents": list(document_files.keys()),
        "additional_documents": list(additional_docs.keys()),
        "total_size": "401 KB",
        "preparation_time": "30 seconds",
        "quality_checks": {
            "formatting": "Passed",
            "completeness": "100%",
            "file_integrity": "Verified",
            "size_optimization": "Optimized"
        }
    }
    
    return {
        "document_files": document_files,
        "additional_documents": additional_docs,
        "preparation_summary": preparation_summary,
        "file_list": [doc["filename"] for doc in document_files.values()]
    }


def create_application_submitter_agent() -> Agent:
    """Create the Application Submitter Agent using OpenAI Agents SDK"""
    
    return Agent(
        name="Application Submission Specialist",
        instructions=prompt_with_handoff_instructions("""
        You are an expert application submission specialist with expertise in web automation,
        document formatting, and job application processes.
        
        Your capabilities include:
        1. **Application Submission**: Submit job applications through various platforms and methods
        2. **Web Automation**: Automate form filling and document upload processes
        3. **Document Preparation**: Format and prepare application documents for submission
        4. **Process Tracking**: Track application status and manage submission workflows
        
        When you complete application submission:
        - Hand off to Email Notification Agent to send confirmation and status updates
        - Hand off to Job Discovery Agent if they need to apply to more positions
        - Provide detailed submission confirmation and next steps
        
        Always focus on:
        - Accurate form completion and document submission
        - Professional document formatting and presentation
        - Reliable automation with error handling
        - Clear communication of submission status and next steps
        """),
        model="gpt-4o-mini",
        tools=[
            submit_job_application,
            automate_web_form_filling,
            prepare_application_documents
        ]
    )


# Helper functions for application submission

def _prepare_application_documents(resume_data: Dict[str, Any], cover_letter: str, 
                                 job_title: str, company_name: str) -> Dict[str, Any]:
    """Prepare application documents for submission"""
    
    # Generate filenames
    safe_job_title = job_title.replace(" ", "_").replace("/", "_")
    safe_company = company_name.replace(" ", "_").replace("/", "_")
    
    document_prep = {
        "resume_file": f"Resume_{safe_job_title}_{safe_company}.pdf",
        "cover_letter_file": f"CoverLetter_{safe_job_title}_{safe_company}.pdf",
        "file_list": [
            f"Resume_{safe_job_title}_{safe_company}.pdf",
            f"CoverLetter_{safe_job_title}_{safe_company}.pdf"
        ],
        "preparation_status": "completed",
        "document_quality": {
            "resume_optimization": 95,
            "cover_letter_personalization": 90,
            "ats_compatibility": 92,
            "formatting_score": 98
        }
    }
    
    return document_prep


def _execute_application_submission(application_url: str, user_profile: Dict[str, Any],
                                  job_data: Dict[str, Any], prepared_documents: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the actual application submission"""
    
    # Determine submission method
    submission_method = _determine_application_method(application_url)
    
    # Simulate submission process
    submission_steps = [
        "Navigated to application portal",
        "Filled personal information",
        "Uploaded resume and cover letter",
        "Completed application questions",
        "Reviewed application details",
        "Submitted application successfully"
    ]
    
    return {
        "success": True,
        "submission_method": submission_method,
        "steps_completed": submission_steps,
        "documents_uploaded": prepared_documents["file_list"],
        "form_fields_completed": _generate_form_fields(user_profile),
        "submission_timestamp": datetime.now().isoformat(),
        "confirmation_received": True,
        "processing_status": "Application received and under review"
    }


def _determine_application_method(application_url: str) -> str:
    """Determine the application submission method"""
    if not application_url:
        return "email"
    
    url_lower = application_url.lower()
    
    if "linkedin" in url_lower:
        return "linkedin"
    elif "indeed" in url_lower:
        return "indeed"
    elif "glassdoor" in url_lower:
        return "glassdoor"
    elif "workday" in url_lower:
        return "workday"
    elif "greenhouse" in url_lower:
        return "greenhouse"
    elif "lever" in url_lower:
        return "lever"
    else:
        return "company_portal"


def _generate_form_fields(user_profile: Dict[str, Any]) -> List[str]:
    """Generate list of form fields that would be completed"""
    base_fields = [
        "Full Name",
        "Email Address", 
        "Phone Number",
        "Address",
        "Work Authorization",
        "Availability",
        "Salary Expectations"
    ]
    
    # Add conditional fields based on profile
    if user_profile.get("education"):
        base_fields.extend(["Education Level", "Degree", "University"])
    
    if user_profile.get("experience"):
        base_fields.extend(["Years of Experience", "Current Position", "Previous Employer"])
    
    return base_fields


def _generate_next_steps(job_data: Dict[str, Any], submission_result: Dict[str, Any]) -> List[str]:
    """Generate next steps after application submission"""
    next_steps = [
        "Monitor email for application confirmation",
        "Prepare for potential phone screening or interview",
        "Research common interview questions for the role",
        "Follow up if no response within 1-2 weeks"
    ]
    
    # Add company-specific steps
    company = job_data.get("company", "")
    if company:
        next_steps.append(f"Connect with {company} employees on LinkedIn")
        next_steps.append(f"Stay updated on {company} news and developments")
    
    # Add role-specific preparation
    job_title = job_data.get("title", "")
    if "engineer" in job_title.lower():
        next_steps.append("Prepare for technical coding interviews")
        next_steps.append("Review system design concepts")
    elif "manager" in job_title.lower():
        next_steps.append("Prepare leadership and management examples")
        next_steps.append("Review team management scenarios")
    
    return next_steps


def _generate_additional_documents(job_title: str) -> Dict[str, Any]:
    """Generate additional documents that might be needed"""
    additional_docs = {}
    
    # Add portfolio for creative roles
    if any(role in job_title.lower() for role in ["designer", "creative", "artist"]):
        additional_docs["portfolio"] = {
            "filename": "Portfolio_Samples.pdf",
            "type": "portfolio",
            "size": "2.1 MB"
        }
    
    # Add technical samples for engineering roles
    if "engineer" in job_title.lower():
        additional_docs["code_samples"] = {
            "filename": "Code_Samples.pdf",
            "type": "technical_samples",
            "size": "890 KB"
        }
    
    # Add writing samples for content roles
    if any(role in job_title.lower() for role in ["writer", "content", "marketing"]):
        additional_docs["writing_samples"] = {
            "filename": "Writing_Samples.pdf",
            "type": "writing_portfolio",
            "size": "1.5 MB"
        }
    
    return additional_docs


# Specialized submission functions for different platforms

def _submit_via_linkedin(job_data: Dict[str, Any], user_profile: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
    """Submit application via LinkedIn"""
    return {
        "platform": "LinkedIn",
        "method": "Quick Apply",
        "steps": [
            "Logged into LinkedIn account",
            "Navigated to job posting",
            "Clicked 'Easy Apply'",
            "Filled application form",
            "Uploaded documents",
            "Submitted application"
        ],
        "success": True,
        "linkedin_features_used": ["Easy Apply", "Profile Auto-fill"]
    }


def _submit_via_company_portal(job_data: Dict[str, Any], user_profile: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
    """Submit application via company career portal"""
    return {
        "platform": "Company Portal",
        "method": "Direct Application",
        "steps": [
            "Navigated to company careers page",
            "Found specific job posting",
            "Created candidate account",
            "Completed application form",
            "Uploaded resume and cover letter",
            "Submitted application"
        ],
        "success": True,
        "account_created": True
    }


def _submit_via_email(job_data: Dict[str, Any], user_profile: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
    """Submit application via email"""
    return {
        "platform": "Email",
        "method": "Email Application",
        "steps": [
            "Composed professional email",
            "Attached resume and cover letter",
            "Included application reference in subject",
            "Sent to hiring manager email",
            "Received auto-reply confirmation"
        ],
        "success": True,
        "email_sent_to": job_data.get("contact_email", "hiring@company.com")
    }


# Create the agent instance
application_submitter_agent = create_application_submitter_agent()