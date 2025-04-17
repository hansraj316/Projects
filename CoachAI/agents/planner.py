"""Simple Planner Agent using OpenAI's Responses API for learning path generation."""

from typing import Dict, List
import openai
from pydantic import BaseModel

from src.config import settings

class LearningGoal(BaseModel):
    """User's learning goals and preferences."""
    topic: str
    current_level: str
    target_level: str
    time_commitment: str
    learning_style: str

class LearningPlan(BaseModel):
    """Generated learning plan."""
    content: str
    suggested_resources: List[str]
    estimated_duration: str

class PlannerAgent:
    """Simple agent for creating learning plans using OpenAI's Responses API."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def create_plan(self, goal: LearningGoal) -> LearningPlan:
        """Generate a learning plan using OpenAI's Responses API with web search."""
        try:
            # Create the learning plan using Responses API with web search
            plan_prompt = f"""
            Create a detailed learning plan for:
            Topic: {goal.topic}
            Current Level: {goal.current_level}
            Target Level: {goal.target_level}
            Available Time: {goal.time_commitment} per week
            Learning Style: {goal.learning_style}

            Use web search to find current and relevant information about learning paths, 
            best practices, and modern approaches for this topic.
            """

            plan_response = self.client.responses.create(
                model="gpt-4.1",
                tools=[{"type": "web_search_preview"}],
                input=plan_prompt
            )

            # Get resource suggestions using web search
            resources_prompt = f"""
            Search for and suggest the most relevant and up-to-date learning resources for:
            Topic: {goal.topic}
            Level: {goal.current_level}
            Learning Style: {goal.learning_style}

            Focus on resources that:
            1. Are highly rated and well-reviewed
            2. Match the specified learning style
            3. Are currently available and maintained
            4. Are suitable for the user's current level
            """

            resources_response = self.client.responses.create(
                model="gpt-4.1",
                tools=[{"type": "web_search_preview"}],
                input=resources_prompt
            )

            # Create the learning plan
            return LearningPlan(
                content=plan_response.output_text,
                suggested_resources=self._format_resources(resources_response.output_text),
                estimated_duration=f"Based on {goal.time_commitment} per week commitment"
            )

        except Exception as e:
            raise Exception(f"Failed to generate learning plan: {str(e)}")

    def _format_resources(self, text: str) -> List[str]:
        """Format the resources text into a list of strings."""
        # Split by newlines and filter out empty lines
        resources = [r.strip() for r in text.split('\n') if r.strip()]
        # Remove any numbering or bullet points at the start
        resources = [r.lstrip('1234567890.-* ') for r in resources]
        # Filter out any empty strings after cleaning
        resources = [r for r in resources if r]
        return resources 