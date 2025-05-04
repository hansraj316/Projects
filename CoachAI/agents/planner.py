"""Simple Planner Agent using OpenAI's Responses API for learning path generation."""

from typing import Dict, List, Union
import openai
from pydantic import BaseModel

from src.config import settings

class LearningGoal(BaseModel):
    """User's learning goals and preferences."""
    subject: str
    level: str
    current_knowledge: str
    learning_purpose: str
    time_commitment: str
    preferred_resources: Union[str, List[str]]  # Can be either string or list

    def __init__(self, **data):
        # Convert list to string if needed
        if isinstance(data.get('preferred_resources', ''), list):
            data['preferred_resources'] = ', '.join(data['preferred_resources'])
        super().__init__(**data)

class LearningPlan(BaseModel):
    """Generated learning plan."""
    content: str
    suggested_resources: List[str]
    estimated_duration: str

class PlannerAgent:
    """Simple agent for creating learning plans using OpenAI's Responses API."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = None
        self.update_api_key(settings.openai_api_key)

    def update_api_key(self, api_key: str) -> None:
        """Update the OpenAI API key."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = openai.OpenAI(api_key=api_key)

    async def create_plan(self, goal: LearningGoal) -> LearningPlan:
        """Generate a learning plan using OpenAI's Responses API."""
        try:
            if not self.client or not self.client.api_key:
                raise ValueError("OpenAI API key not configured. Please set your API key in the settings.")
                
            print(f"Creating plan for subject: {goal.subject}")
            print(f"Using OpenAI API key: {self.client.api_key[:5]}..." if self.client.api_key else "No API key found")
            
            # Create a combined prompt for both plan and resources
            combined_prompt = f"""
            Create a comprehensive learning plan and resource list for:
            Subject: {goal.subject}
            Level: {goal.level}
            Current Knowledge: {goal.current_knowledge}
            Learning Purpose: {goal.learning_purpose}
            Available Time: {goal.time_commitment} per week
            Preferred Resources: {goal.preferred_resources}

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
            2. Match the specified learning preferences
            3. Are currently available and maintained
            4. Are suitable for the user's current level

            Format each resource as:
            - Resource Name: Brief description
            """
            
            print("Sending request to OpenAI API...")
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert learning plan creator."},
                        {"role": "user", "content": combined_prompt}
                    ]
                )
                print("Received response from OpenAI API")
                content = response.choices[0].message.content
            except openai.AuthenticationError:
                raise ValueError("Invalid OpenAI API key. Please check your API key in the settings.")
            except openai.RateLimitError:
                raise ValueError("OpenAI API rate limit exceeded. Please try again in a few minutes.")
            except Exception as e:
                raise ValueError(f"OpenAI API error: {str(e)}")

            # Split the response into plan and resources
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

        except ValueError as e:
            print(f"Validation error in create_plan: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error in create_plan: {str(e)}")
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