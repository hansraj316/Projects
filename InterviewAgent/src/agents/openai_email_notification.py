"""
Email Notification Agent - Using OpenAI Agents SDK
Handles email notifications, confirmations, and updates with proper handoffs
"""

from __future__ import annotations

import json
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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
    print(f"Warning: OpenAI Agents SDK not available for Email Notification: {e}")
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


class EmailNotificationInput(BaseModel):
    """Input data for email notifications"""
    recipient_email: str
    notification_type: str
    job_data: Dict[str, Any]
    application_details: Dict[str, Any] = {}
    user_profile: Dict[str, Any] = {}


class BulkNotificationInput(BaseModel):
    """Input data for bulk email notifications"""
    recipient_email: str
    applications: List[Dict[str, Any]]
    summary_type: str = "daily"
    user_profile: Dict[str, Any] = {}


class FollowUpReminderInput(BaseModel):
    """Input data for follow-up reminders"""
    recipient_email: str
    application_data: Dict[str, Any]
    days_since_application: int
    reminder_type: str = "follow_up"


class EmailNotificationResult(BaseModel):
    """Result from email notification"""
    success: bool
    email_id: str
    recipient: str
    subject: str
    sent_timestamp: str
    delivery_status: str
    next_action: Optional[str] = None


@function_tool
def send_application_confirmation(input_data: EmailNotificationInput) -> EmailNotificationResult:
    """
    Send application confirmation email to user
    
    Args:
        input_data: Email notification parameters
        
    Returns:
        EmailNotificationResult with confirmation details
    """
    print(f"[Email Notification] Sending application confirmation for {input_data.job_data.get('title', 'Unknown')} at {input_data.job_data.get('company', 'Unknown')}")
    
    job_data = input_data.job_data
    application_details = input_data.application_details
    
    # Generate email content
    email_content = _generate_confirmation_email(
        job_data=job_data,
        application_details=application_details,
        user_profile=input_data.user_profile
    )
    
    # Simulate email sending
    email_result = _send_email(
        recipient=input_data.recipient_email,
        subject=f"Application Confirmed: {job_data.get('title', 'Position')} at {job_data.get('company', 'Company')}",
        content=email_content,
        email_type="confirmation"
    )
    
    return EmailNotificationResult(
        success=email_result["success"],
        email_id=email_result["email_id"],
        recipient=input_data.recipient_email,
        subject=email_result["subject"],
        sent_timestamp=email_result["sent_timestamp"],
        delivery_status=email_result["delivery_status"],
        next_action="Monitor for application response"
    )


@function_tool
def send_bulk_application_summary(input_data: BulkNotificationInput) -> EmailNotificationResult:
    """
    Send bulk application summary email
    
    Args:
        input_data: Bulk notification parameters
        
    Returns:
        EmailNotificationResult with summary details
    """
    print(f"[Bulk Email] Sending {input_data.summary_type} summary for {len(input_data.applications)} applications")
    
    # Generate summary email content
    email_content = _generate_summary_email(
        applications=input_data.applications,
        summary_type=input_data.summary_type,
        user_profile=input_data.user_profile
    )
    
    # Create subject line
    subject = f"{input_data.summary_type.title()} Application Summary - {len(input_data.applications)} Applications"
    
    # Simulate email sending
    email_result = _send_email(
        recipient=input_data.recipient_email,
        subject=subject,
        content=email_content,
        email_type="summary"
    )
    
    return EmailNotificationResult(
        success=email_result["success"],
        email_id=email_result["email_id"],
        recipient=input_data.recipient_email,
        subject=email_result["subject"],
        sent_timestamp=email_result["sent_timestamp"],
        delivery_status=email_result["delivery_status"],
        next_action="Review application tracking dashboard"
    )


@function_tool
def schedule_follow_up_reminder(input_data: FollowUpReminderInput) -> Dict[str, Any]:
    """
    Schedule follow-up reminder for job applications
    
    Args:
        input_data: Follow-up reminder parameters
        
    Returns:
        Scheduling confirmation and reminder details
    """
    print(f"[Follow-up Scheduler] Scheduling reminder for {input_data.application_data.get('company', 'Unknown')} application")
    
    application_data = input_data.application_data
    
    # Determine appropriate follow-up timing
    follow_up_schedule = _determine_follow_up_schedule(
        days_since_application=input_data.days_since_application,
        application_data=application_data
    )
    
    # Generate reminder content
    reminder_content = _generate_follow_up_reminder(
        application_data=application_data,
        follow_up_schedule=follow_up_schedule
    )
    
    # Schedule the reminder
    reminder_id = f"REMIND-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(application_data.get('company', ''))%1000:03d}"
    
    scheduled_reminder = {
        "reminder_id": reminder_id,
        "recipient": input_data.recipient_email,
        "application_company": application_data.get("company", ""),
        "application_title": application_data.get("title", ""),
        "scheduled_date": follow_up_schedule["next_reminder_date"],
        "reminder_type": input_data.reminder_type,
        "content_preview": reminder_content["preview"],
        "priority": follow_up_schedule["priority"],
        "automation_enabled": True,
        "created_timestamp": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "reminder_scheduled": scheduled_reminder,
        "follow_up_strategy": follow_up_schedule,
        "email_content": reminder_content,
        "next_steps": follow_up_schedule["recommended_actions"]
    }


def create_email_notification_agent() -> Agent:
    """Create the Email Notification Agent using OpenAI Agents SDK"""
    
    return Agent(
        name="Email Notification Specialist",
        instructions=prompt_with_handoff_instructions("""
        You are an expert email communication specialist with expertise in professional 
        correspondence, notification systems, and follow-up management.
        
        Your capabilities include:
        1. **Application Confirmations**: Send confirmation emails for job applications
        2. **Bulk Summaries**: Create and send application summary reports
        3. **Follow-up Reminders**: Schedule and manage follow-up communications
        4. **Status Updates**: Send progress updates and status notifications
        
        When you complete email notifications:
        - Provide detailed delivery confirmation
        - Schedule appropriate follow-up actions
        - Log all communications for tracking
        - Hand off to other agents if additional actions are needed
        
        Always focus on:
        - Professional and clear communication
        - Timely delivery of notifications
        - Appropriate follow-up scheduling
        - Comprehensive tracking and logging
        """),
        model="gpt-4o-mini",
        tools=[
            send_application_confirmation,
            send_bulk_application_summary,
            schedule_follow_up_reminder
        ]
    )


# Helper functions for email notifications

def _generate_confirmation_email(job_data: Dict[str, Any], application_details: Dict[str, Any], 
                                user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate application confirmation email content"""
    
    company = job_data.get("company", "Company")
    job_title = job_data.get("title", "Position")
    user_name = user_profile.get("name", "")
    
    # Email body
    email_body = f"""Dear {user_name},

Your application for the {job_title} position at {company} has been successfully submitted!

Application Details:
• Position: {job_title}
• Company: {company}
• Application Date: {datetime.now().strftime('%B %d, %Y')}
• Confirmation Number: {application_details.get('confirmation_number', 'N/A')}

Documents Submitted:
"""
    
    # Add submitted documents
    documents = application_details.get("documents_submitted", [])
    for doc in documents:
        email_body += f"• {doc}\n"
    
    email_body += f"""

Next Steps:
• The hiring team will review your application
• You can expect to hear back within {application_details.get('estimated_response_time', '1-2 weeks')}
• We'll send you updates on your application status

Tips while you wait:
• Connect with {company} employees on LinkedIn
• Research the company and role further
• Prepare for potential interviews
• Continue applying to other opportunities

Thank you for your interest in {company}. We appreciate the time you took to apply!

Best regards,
InterviewAgent Automation System

---
This is an automated confirmation. For questions, please contact support.
"""

    return {
        "body": email_body,
        "html_body": _convert_to_html_email(email_body),
        "attachments": [],
        "priority": "normal"
    }


def _generate_summary_email(applications: List[Dict[str, Any]], summary_type: str, 
                           user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate bulk application summary email"""
    
    user_name = user_profile.get("name", "")
    total_apps = len(applications)
    
    # Calculate summary statistics
    companies = set(app.get("company", "") for app in applications)
    successful_submissions = sum(1 for app in applications if app.get("status") == "submitted")
    
    email_body = f"""Dear {user_name},

Here's your {summary_type} application summary:

Summary Statistics:
• Total Applications: {total_apps}
• Successful Submissions: {successful_submissions}
• Companies Applied To: {len(companies)}
• Success Rate: {(successful_submissions/total_apps*100):.1f}%

Recent Applications:
"""
    
    # Add application details
    for i, app in enumerate(applications[:10]):  # Show up to 10 recent applications
        status_emoji = "✅" if app.get("status") == "submitted" else "⏳"
        email_body += f"{status_emoji} {app.get('title', 'Unknown')} at {app.get('company', 'Unknown')}\n"
        if app.get("application_date"):
            email_body += f"   Applied: {app.get('application_date')}\n"
        email_body += "\n"
    
    if len(applications) > 10:
        email_body += f"... and {len(applications) - 10} more applications\n\n"
    
    email_body += f"""
Performance Insights:
• Most active application day: {_get_most_active_day(applications)}
• Average applications per day: {_calculate_daily_average(applications)}
• Top target industries: {', '.join(_get_top_industries(applications)[:3])}

Recommendations:
• Follow up on applications older than 2 weeks
• Continue targeting high-growth companies
• Consider expanding search to related roles
• Update your resume with recent achievements

Keep up the great work! Your consistent effort will lead to opportunities.

Best regards,
InterviewAgent Automation System
"""

    return {
        "body": email_body,
        "html_body": _convert_to_html_email(email_body),
        "attachments": [],
        "priority": "normal"
    }


def _generate_follow_up_reminder(application_data: Dict[str, Any], 
                               follow_up_schedule: Dict[str, Any]) -> Dict[str, Any]:
    """Generate follow-up reminder content"""
    
    company = application_data.get("company", "Company")
    job_title = application_data.get("title", "Position")
    application_date = application_data.get("application_date", "recently")
    
    email_body = f"""Follow-Up Reminder: {job_title} at {company}

It's been {follow_up_schedule.get('days_elapsed', 'several')} days since you applied for the {job_title} position at {company}.

Application Details:
• Position: {job_title}
• Company: {company}
• Applied: {application_date}
• Status: {application_data.get('status', 'Under Review')}

Recommended Actions:
"""
    
    # Add recommended actions
    for action in follow_up_schedule.get("recommended_actions", []):
        email_body += f"• {action}\n"
    
    email_body += f"""

Follow-Up Email Template:
"Subject: Following up on {job_title} Application

Dear Hiring Manager,

I hope this message finds you well. I wanted to follow up on my application for the {job_title} position that I submitted on {application_date}.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills and experience can contribute to {company}'s success.

Thank you for your time and consideration.

Best regards,
[Your Name]"

Remember:
• Keep follow-ups brief and professional
• Express continued interest, don't be pushy
• Wait at least 1-2 weeks before following up
• Consider connecting on LinkedIn as an alternative

Good luck!

InterviewAgent Follow-Up System
"""

    return {
        "body": email_body,
        "preview": f"Follow up on your {job_title} application at {company}",
        "html_body": _convert_to_html_email(email_body),
        "priority": follow_up_schedule.get("priority", "normal")
    }


def _send_email(recipient: str, subject: str, content: Dict[str, Any], email_type: str) -> Dict[str, Any]:
    """Simulate email sending process"""
    
    email_id = f"EMAIL-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(recipient)%1000:03d}"
    
    return {
        "success": True,
        "email_id": email_id,
        "subject": subject,
        "recipient": recipient,
        "sent_timestamp": datetime.now().isoformat(),
        "delivery_status": "delivered",
        "email_type": email_type,
        "content_length": len(content.get("body", "")),
        "attachments_count": len(content.get("attachments", [])),
        "priority": content.get("priority", "normal")
    }


def _determine_follow_up_schedule(days_since_application: int, application_data: Dict[str, Any]) -> Dict[str, Any]:
    """Determine appropriate follow-up schedule"""
    
    # Base follow-up strategy
    if days_since_application < 7:
        return {
            "next_reminder_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "priority": "low",
            "days_elapsed": days_since_application,
            "recommended_actions": [
                "Wait a bit longer before following up",
                "Continue applying to other positions",
                "Prepare for potential interviews"
            ]
        }
    elif days_since_application < 14:
        return {
            "next_reminder_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "priority": "medium",
            "days_elapsed": days_since_application,
            "recommended_actions": [
                "Send a polite follow-up email",
                "Connect with hiring manager on LinkedIn",
                "Research company recent news to mention"
            ]
        }
    else:
        return {
            "next_reminder_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "priority": "high",
            "days_elapsed": days_since_application,
            "recommended_actions": [
                "Send follow-up email expressing continued interest",
                "Consider calling the company directly",
                "Network with current employees",
                "Apply to similar roles at the company"
            ]
        }


def _convert_to_html_email(text_content: str) -> str:
    """Convert plain text email to HTML format"""
    
    html_content = text_content.replace('\n', '<br>\n')
    html_content = html_content.replace('•', '&bull;')
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            {html_content}
        </div>
    </body>
    </html>
    """


def _get_most_active_day(applications: List[Dict[str, Any]]) -> str:
    """Get the most active application day"""
    # Simplified - in production, analyze actual dates
    return "Monday"


def _calculate_daily_average(applications: List[Dict[str, Any]]) -> float:
    """Calculate daily application average"""
    # Simplified calculation
    return round(len(applications) / 7, 1)


def _get_top_industries(applications: List[Dict[str, Any]]) -> List[str]:
    """Get top target industries from applications"""
    # Extract industries from applications
    industries = []
    for app in applications:
        # Simplified industry extraction
        company = app.get("company", "").lower()
        if any(tech in company for tech in ["google", "microsoft", "apple", "amazon"]):
            industries.append("Technology")
        elif any(fin in company for fin in ["goldman", "jpmorgan", "bank"]):
            industries.append("Finance")
        else:
            industries.append("Technology")  # Default
    
    # Count and return top industries
    from collections import Counter
    industry_counts = Counter(industries)
    return [industry for industry, count in industry_counts.most_common()]


# Email template functions for different types

def _create_confirmation_template(job_data: Dict[str, Any], application_details: Dict[str, Any]) -> str:
    """Create application confirmation email template"""
    return "Your application has been successfully submitted!"


def _create_summary_template(applications: List[Dict[str, Any]], summary_type: str) -> str:
    """Create application summary email template"""
    return f"Summary of your {summary_type} applications"


def _create_follow_up_template(application_data: Dict[str, Any]) -> str:
    """Create follow-up reminder email template"""
    return "Time to follow up on your application"


def _create_status_update_template(application_data: Dict[str, Any], status_change: str) -> str:
    """Create status update email template"""
    return f"Your application status has been updated to: {status_change}"


# Create the agent instance
email_notification_agent = create_email_notification_agent()