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
        """Generate a learning plan using OpenAI's Responses API."""
        try:
            # Create a combined prompt for both plan and resources
            combined_prompt = f"""
            Create a comprehensive learning plan and resource list for:
            Topic: {goal.topic}
            Current Level: {goal.current_level}
            Target Level: {goal.target_level}
            Available Time: {goal.time_commitment} per week
            Learning Style: {goal.learning_style}

            Please provide your response in two clearly separated sections:

            SECTION 1 - LEARNING PLAN
            The plan should include:
            1. Clear learning objectives
            2. Step-by-step progression
            3. Practical exercises and projects
            4. Estimated time for each section
            5. Milestones and checkpoints

            SECTION 2 - RECOMMENDED RESOURCES
            List 5-7 highly relevant resources that:
            1. Are highly rated and well-reviewed
            2. Match the specified learning style
            3. Are currently available and maintained
            4. Are suitable for the user's current level

            Format each resource as:
            - Resource Name: Brief description
            """

            response = self.client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=combined_prompt
            )

            # Split the response into plan and resources
            content = response.output_text
            sections = content.split("SECTION 2 - RECOMMENDED RESOURCES")
            
            if len(sections) != 2:
                # Fallback if the response doesn't follow the format
                plan_content = content
                resources_content = ""
            else:
                plan_content = sections[0].replace("SECTION 1 - LEARNING PLAN", "").strip()
                resources_content = sections[1].strip()

            # Create the learning plan
            return LearningPlan(
                content=plan_content,
                suggested_resources=self._format_resources(resources_content),
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