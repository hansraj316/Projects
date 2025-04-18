"""Email Agent for sending notifications using Gmail."""

from typing import Optional
from pydantic import BaseModel
import openai

from src.config import settings

class EmailConfig(BaseModel):
    """Email configuration."""
    recipient_email: str
    subscribe_to_notifications: bool = True

class EmailAgent:
    """Agent for sending email notifications."""
    
    def __init__(self):
        """Initialize email agent."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    async def send_learning_plan_email(self, config: EmailConfig, plan_content: str, topic: str) -> None:
        """Send an email with the learning plan."""
        try:
            # Generate email content using Responses API
            email_prompt = f"""
            Create a friendly and engaging email to send a learning plan.
            Topic: {topic}
            Plan Content: {plan_content}

            The email should:
            1. Be welcoming and encouraging
            2. Highlight the value of the learning plan
            3. Include the complete plan content
            4. Add motivational tips for success
            """

            email_response = self.client.responses.create(
                model="gpt-4.1",
                tools=[{"type": "web_search_preview"}],
                input=email_prompt
            )

            subject = f"Your Learning Plan for {topic} is Ready!"
            body = email_response.output_text
            
            # Use MCP Gmail integration to send email
            await self.mcp_send_email(
                to=config.recipient_email,
                subject=subject,
                body=body
            )
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")

    async def mcp_send_email(self, to: str, subject: str, body: str) -> None:
        """Send email using MCP Gmail integration."""
        try:
            from mcp_zapier_mcp_gmail_send_email import mcp_Zapier_MCP_gmail_send_email
            await mcp_Zapier_MCP_gmail_send_email(
                to=to,
                subject=subject,
                body=body
            )
        except Exception as e:
            raise Exception(f"MCP Gmail send failed: {str(e)}") 