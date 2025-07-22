"""
Email Notification Agent - Uses Gmail MCP Server for automated email notifications
Integrates with the multi-agent automation system for coordinated workflow notifications
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask, AgentContext


class EmailNotificationAgent(BaseAgent):
    """
    AI agent that sends email notifications using Gmail MCP Server
    Coordinates with other agents in the automation workflow to provide status updates
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="email_notification", 
            description="You are an expert email communication specialist that sends automated notifications about job application workflows. You coordinate with other agents to provide timely updates about resume optimization, cover letter generation, application submissions, and overall automation progress. You craft professional, informative emails using Gmail integration.",
            config=config
        )
        
        # Track notification types for multi-agent coordination
        self.notification_types = {
            "workflow_started": "Job application automation workflow initiated",
            "resume_optimized": "Resume optimized for specific job",
            "cover_letter_generated": "Cover letter generated successfully", 
            "application_submitted": "Job application submitted successfully",
            "workflow_completed": "Complete job application workflow finished",
            "workflow_failed": "Job application workflow encountered errors",
            "daily_summary": "Daily automation activity summary",
            "weekly_report": "Weekly job application progress report"
        }
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute email notification task with multi-agent awareness
        
        Args:
            task: The task to execute
            context: Shared context information including workflow state
            
        Returns:
            Task execution result with email delivery details
        """
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "send_workflow_notification":
                result = await self._send_workflow_notification(task, context)
            elif task_type == "send_agent_status_update":
                result = await self._send_agent_status_update(task, context)
            elif task_type == "send_daily_summary":
                result = await self._send_daily_summary(task, context)
            elif task_type == "send_error_notification":
                result = await self._send_error_notification(task, context)
            elif task_type == "send_application_confirmation":
                result = await self._send_application_confirmation(task, context)
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
                message=f"Email notification failed: {str(e)}"
            )
    
    async def _send_workflow_notification(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Send notification about workflow progress with multi-agent coordination data
        
        Args:
            task: The notification task
            context: Context including workflow and agent states
            
        Returns:
            Email notification result
        """
        # Extract workflow information from task data
        workflow_id = task.input_data.get("workflow_id", "")
        workflow_status = task.input_data.get("workflow_status", "unknown")
        job_details = task.input_data.get("job_details", {})
        agent_results = task.input_data.get("agent_results", {})
        user_email = task.input_data.get("user_email", "")
        
        # Use Gmail MCP tools for email composition and sending
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "gmail_compose_send",
                    "description": "Compose and send Gmail email"
                }
            }
        ]
        
        # Create AI prompt for workflow notification email
        prompt = f"""
        Compose and send a professional email notification about job application workflow progress.
        
        Workflow Details:
        - Workflow ID: {workflow_id}
        - Status: {workflow_status}
        - Job Information: {json.dumps(job_details, indent=2)}
        
        Agent Results Summary:
        {json.dumps(agent_results, indent=2)}
        
        Email Details:
        - To: {user_email}
        - Subject: Job Application Automation Update - {job_details.get('job_title', 'Position')} at {job_details.get('company_name', 'Company')}
        
        Email Content Requirements:
        1. Professional greeting and workflow identification
        2. Clear status update with current progress
        3. Summary of completed agent actions:
           - Job Discovery: Jobs found and analyzed
           - Resume Optimization: Resume customized for this role
           - Cover Letter Generation: Personalized cover letter created
           - Application Submission: Application status and details
        4. Next steps or pending actions
        5. Any errors or issues encountered
        6. Professional closing with automation signature
        
        Make the email informative but concise, highlighting key achievements and any required user actions.
        Use the Gmail MCP tool to send this email.
        """
        
        # Execute with Gmail MCP tools
        ai_response = self.get_response(prompt, tools=tools)
        
        # Parse email delivery results
        email_data = self._parse_email_response(ai_response, "workflow_notification")
        
        return self.create_result(
            success=email_data.get("sent", False),
            data={
                "email_details": email_data,
                "workflow_id": workflow_id,
                "notification_type": "workflow_notification", 
                "recipient": user_email,
                "agent_coordination": agent_results,
                "email_content": ai_response
            },
            message=f"Workflow notification {'sent successfully' if email_data.get('sent') else 'failed to send'} for {workflow_status} status",
            metadata={
                "workflow_id": workflow_id,
                "notification_type": "workflow_notification",
                "sent_at": datetime.now().isoformat(),
                "email_method": "gmail_mcp"
            }
        )
    
    async def _send_agent_status_update(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Send notification about specific agent completion in the multi-agent workflow
        
        Args:
            task: The notification task
            context: Context information
            
        Returns:
            Agent status notification result
        """
        agent_name = task.input_data.get("agent_name", "")
        agent_result = task.input_data.get("agent_result", {})
        workflow_context = task.input_data.get("workflow_context", {})
        user_email = task.input_data.get("user_email", "")
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "gmail_compose_send",
                    "description": "Compose and send Gmail email for agent status"
                }
            }
        ]
        
        prompt = f"""
        Send a status update email about a specific agent completion in the job application automation.
        
        Agent Information:
        - Agent Name: {agent_name}
        - Agent Result: {json.dumps(agent_result, indent=2)}
        
        Workflow Context:
        {json.dumps(workflow_context, indent=2)}
        
        Email to: {user_email}
        Subject: {agent_name.replace('_', ' ').title()} Completed - Job Application Automation
        
        Email should include:
        1. Which agent just completed its task
        2. Summary of what was accomplished
        3. Key outputs or files generated
        4. Integration with overall workflow progress
        5. Next agents in the pipeline
        6. Any user actions required
        
        Keep it brief but informative about the multi-agent coordination progress.
        """
        
        ai_response = self.get_response(prompt, tools=tools)
        email_data = self._parse_email_response(ai_response, "agent_status")
        
        return self.create_result(
            success=email_data.get("sent", False),
            data={
                "email_details": email_data,
                "agent_name": agent_name,
                "notification_type": "agent_status_update"
            },
            message=f"Agent status notification sent for {agent_name}"
        )
    
    async def _send_daily_summary(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Send daily summary of all automation activities across multiple workflows
        
        Args:
            task: The summary task
            context: Context information
            
        Returns:
            Daily summary email result
        """
        daily_stats = task.input_data.get("daily_stats", {})
        workflows_completed = task.input_data.get("workflows_completed", [])
        user_email = task.input_data.get("user_email", "")
        
        tools = [
            {
                "type": "function", 
                "function": {
                    "name": "gmail_compose_send",
                    "description": "Compose and send daily summary email"
                }
            }
        ]
        
        prompt = f"""
        Send a comprehensive daily summary email of job application automation activities.
        
        Daily Statistics:
        {json.dumps(daily_stats, indent=2)}
        
        Completed Workflows:
        {json.dumps(workflows_completed, indent=2)}
        
        Email to: {user_email}
        Subject: Daily Job Application Automation Summary - {datetime.now().strftime('%Y-%m-%d')}
        
        Include:
        1. Overview of automation activities for the day
        2. Number of jobs discovered, resumes optimized, cover letters generated
        3. Applications submitted successfully
        4. Multi-agent workflow performance metrics
        5. Any errors or issues encountered
        6. Recommendations for tomorrow's automation
        7. Weekly/monthly progress toward goals
        
        Make it a professional daily report with actionable insights.
        """
        
        ai_response = self.get_response(prompt, tools=tools)
        email_data = self._parse_email_response(ai_response, "daily_summary")
        
        return self.create_result(
            success=email_data.get("sent", False),
            data={
                "email_details": email_data,
                "summary_date": datetime.now().date().isoformat(),
                "daily_stats": daily_stats
            },
            message="Daily automation summary sent"
        )
    
    async def _send_error_notification(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Send immediate notification about workflow or agent errors requiring attention
        
        Args:
            task: The error notification task
            context: Context information
            
        Returns:
            Error notification result
        """
        error_details = task.input_data.get("error_details", {})
        failed_agent = task.input_data.get("failed_agent", "")
        workflow_id = task.input_data.get("workflow_id", "")
        user_email = task.input_data.get("user_email", "")
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "gmail_compose_send", 
                    "description": "Send urgent error notification email"
                }
            }
        ]
        
        prompt = f"""
        Send an urgent error notification email about automation workflow failure.
        
        Error Information:
        - Failed Agent: {failed_agent}
        - Workflow ID: {workflow_id}
        - Error Details: {json.dumps(error_details, indent=2)}
        
        Email to: {user_email}
        Subject: URGENT: Job Application Automation Error - Action Required
        
        Email should include:
        1. Clear indication this is an error notification
        2. Which part of the automation failed
        3. Specific error details and potential causes
        4. Impact on the overall workflow
        5. Recommended actions for the user
        6. Whether automation will retry automatically
        7. Contact information for support if needed
        
        Mark as high priority and provide clear next steps.
        """
        
        ai_response = self.get_response(prompt, tools=tools)
        email_data = self._parse_email_response(ai_response, "error_notification")
        
        return self.create_result(
            success=email_data.get("sent", False),
            data={
                "email_details": email_data,
                "error_severity": "high",
                "failed_component": failed_agent,
                "workflow_id": workflow_id
            },
            message="Error notification sent for immediate attention"
        )
    
    async def _send_application_confirmation(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Send confirmation email when complete application workflow succeeds
        
        Args:
            task: The confirmation task
            context: Context information
            
        Returns:
            Application confirmation result
        """
        application_details = task.input_data.get("application_details", {})
        job_details = task.input_data.get("job_details", {})
        workflow_summary = task.input_data.get("workflow_summary", {})
        user_email = task.input_data.get("user_email", "")
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "gmail_compose_send",
                    "description": "Send application confirmation email"
                }
            }
        ]
        
        prompt = f"""
        Send a professional confirmation email for successful job application completion.
        
        Application Details:
        {json.dumps(application_details, indent=2)}
        
        Job Information:
        {json.dumps(job_details, indent=2)}
        
        Workflow Summary:
        {json.dumps(workflow_summary, indent=2)}
        
        Email to: {user_email}
        Subject: ✅ Application Submitted Successfully - {job_details.get('job_title')} at {job_details.get('company_name')}
        
        Email content:
        1. Congratulations on successful application submission
        2. Job details and company information
        3. Summary of automation workflow completion:
           - Resume optimized and customized
           - Cover letter generated with company research
           - Application submitted through proper channels
        4. Files used (resume version, cover letter)
        5. Application tracking information if available
        6. Next steps and follow-up recommendations
        7. Timeline for potential employer response
        
        Make it celebratory but professional, with useful next-step guidance.
        """
        
        ai_response = self.get_response(prompt, tools=tools)
        email_data = self._parse_email_response(ai_response, "application_confirmation")
        
        return self.create_result(
            success=email_data.get("sent", False),
            data={
                "email_details": email_data,
                "application_confirmed": True,
                "job_details": job_details,
                "workflow_summary": workflow_summary
            },
            message="Application confirmation sent successfully"
        )
    
    def _parse_email_response(self, ai_response: str, notification_type: str) -> Dict[str, Any]:
        """Parse AI response for email delivery details with multi-agent context"""
        return {
            "sent": "sent" in ai_response.lower() or "delivered" in ai_response.lower(),
            "message_id": self._extract_message_id(ai_response),
            "delivery_status": "delivered" if "sent" in ai_response.lower() else "failed",
            "notification_type": notification_type,
            "response_log": ai_response,
            "sent_at": datetime.now().isoformat(),
            "multi_agent_coordination": True,
            "automation_source": "workflow_orchestration"
        }
    
    def _extract_message_id(self, response: str) -> str:
        """Extract Gmail message ID from response if available"""
        # Look for message ID patterns in the response
        import re
        message_id_pattern = r"message[_\s]?id[:\s]+([a-zA-Z0-9]+)"
        match = re.search(message_id_pattern, response, re.IGNORECASE)
        
        if match:
            return match.group(1)
        else:
            # Generate a placeholder ID
            return f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def create_notification_context(self, workflow_state: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create rich context for email notifications that includes multi-agent coordination data
        
        Args:
            workflow_state: Current state of the workflow
            agent_results: Results from all agents in the workflow
            
        Returns:
            Rich notification context
        """
        return {
            "workflow_progress": {
                "total_steps": len(workflow_state.get("steps", [])),
                "completed_steps": len([s for s in workflow_state.get("results", {}).values() if s.get("success")]),
                "current_step": workflow_state.get("current_step", "unknown"),
                "estimated_completion": workflow_state.get("estimated_completion", "unknown")
            },
            "agent_coordination": {
                "agents_involved": list(agent_results.keys()),
                "successful_agents": [name for name, result in agent_results.items() if result.get("success")],
                "failed_agents": [name for name, result in agent_results.items() if not result.get("success")],
                "data_flow": self._map_agent_data_flow(agent_results)
            },
            "automation_metrics": {
                "workflow_start_time": workflow_state.get("started_at"),
                "estimated_total_time": workflow_state.get("estimated_duration"),
                "efficiency_score": self._calculate_workflow_efficiency(workflow_state, agent_results)
            }
        }
    
    def _map_agent_data_flow(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Map how data flows between agents in the workflow"""
        return {
            "job_discovery_to_resume": "Job requirements extracted for resume optimization",
            "job_discovery_to_cover_letter": "Company research used for cover letter personalization", 
            "resume_optimizer_to_submitter": "Optimized resume file ready for upload",
            "cover_letter_to_submitter": "Personalized cover letter ready for submission",
            "submitter_to_notification": "Application confirmation data for user notification"
        }
    
    def _calculate_workflow_efficiency(self, workflow_state: Dict[str, Any], agent_results: Dict[str, Any]) -> float:
        """Calculate overall workflow efficiency score"""
        if not agent_results:
            return 0.0
        
        successful_agents = sum(1 for result in agent_results.values() if result.get("success"))
        total_agents = len(agent_results)
        
        base_efficiency = successful_agents / total_agents if total_agents > 0 else 0
        
        # Bonus for complete workflow
        if successful_agents == total_agents:
            base_efficiency += 0.1
        
        return min(base_efficiency, 1.0)