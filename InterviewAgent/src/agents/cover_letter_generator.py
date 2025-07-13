"""
Cover Letter Generation Agent - AI-powered personalized cover letter creation
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask, AgentContext


class CoverLetterAgent(BaseAgent):
    """
    AI agent that generates personalized cover letters for specific job applications
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="cover_letter_generator",
            description="AI-powered personalized cover letter creation",
            config=config
        )
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute cover letter generation task
        
        Args:
            task: The task to execute
            context: Shared context information
            
        Returns:
            Task execution result with generated cover letter
        """
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "generate_cover_letter":
                result = await self._generate_cover_letter(task, context)
            elif task_type == "customize_template":
                result = await self._customize_template(task, context)
            elif task_type == "generate_variations":
                result = await self._generate_variations(task, context)
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
                message=f"Cover letter generation failed: {str(e)}"
            )
    
    async def _generate_cover_letter(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Generate a personalized cover letter for a specific job application
        
        Args:
            task: The generation task
            context: Context including job and candidate information
            
        Returns:
            Generated cover letter result
        """
        # Extract information from task data
        job_description = task.input_data.get("job_description", "")
        company_name = task.input_data.get("company_name", "the company")
        job_title = task.input_data.get("job_title", "this position")
        hiring_manager = task.input_data.get("hiring_manager", "Hiring Manager")
        candidate_info = task.input_data.get("candidate_info", {})
        resume_summary = task.input_data.get("resume_summary", {})
        company_research = task.input_data.get("company_research", {})
        
        # Create AI prompt for cover letter generation
        system_message = """You are an expert career consultant and professional writer specializing in cover letters. 
        Your task is to create compelling, personalized cover letters that:
        1. Address the specific job requirements
        2. Highlight relevant candidate experience and achievements
        3. Show genuine interest in the company and role
        4. Demonstrate cultural fit
        5. Include a strong call to action
        6. Maintain a professional yet engaging tone
        
        Always write in first person from the candidate's perspective."""
        
        prompt = f"""
        Create a personalized cover letter for the following job application:
        
        Job Details:
        - Company: {company_name}
        - Position: {job_title}
        - Hiring Manager: {hiring_manager}
        
        Job Description:
        {job_description}
        
        Candidate Information:
        {json.dumps(candidate_info, indent=2)}
        
        Resume Summary:
        {json.dumps(resume_summary, indent=2)}
        
        Company Research:
        {json.dumps(company_research, indent=2)}
        
        Requirements:
        1. Address it to {hiring_manager}
        2. Open with a compelling hook that shows enthusiasm
        3. Highlight 2-3 specific achievements that match job requirements
        4. Show knowledge of the company (use research data)
        5. Include a confident closing with next steps
        6. Keep it to 3-4 paragraphs, professional business format
        7. Use specific numbers and metrics where possible
        
        Generate the cover letter in a professional business letter format.
        """
        
        # Get AI response
        ai_response = self.get_ai_response(prompt, system_message, model="gpt-3.5-turbo")
        
        # Structure the cover letter
        cover_letter_data = self._structure_cover_letter(ai_response, {
            "company_name": company_name,
            "job_title": job_title,
            "hiring_manager": hiring_manager,
            "candidate_name": candidate_info.get("name", "Candidate Name")
        })
        
        # Calculate quality metrics
        quality_score = self._calculate_quality_score(ai_response, job_description)
        
        return self.create_result(
            success=True,
            data={
                "cover_letter": cover_letter_data,
                "quality_score": quality_score,
                "word_count": len(ai_response.split()),
                "key_points": self._extract_key_points(ai_response),
                "personalization_elements": self._identify_personalization(ai_response, company_name, job_title)
            },
            message="Cover letter successfully generated",
            metadata={
                "job_title": job_title,
                "company_name": company_name,
                "generation_date": datetime.now().isoformat(),
                "template_used": "ai_generated"
            }
        )
    
    async def _customize_template(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Customize an existing cover letter template for a specific job
        
        Args:
            task: The customization task
            context: Context information
            
        Returns:
            Customized cover letter result
        """
        template = task.input_data.get("template", "")
        job_description = task.input_data.get("job_description", "")
        company_name = task.input_data.get("company_name", "")
        job_title = task.input_data.get("job_title", "")
        placeholders = task.input_data.get("placeholders", {})
        
        system_message = """You are customizing a cover letter template for a specific job application. 
        Replace placeholders with relevant, specific content while maintaining the template's structure and tone."""
        
        prompt = f"""
        Customize this cover letter template for the specific job:
        
        Template:
        {template}
        
        Job Information:
        - Company: {company_name}
        - Position: {job_title}
        - Job Description: {job_description}
        
        Placeholder Values:
        {json.dumps(placeholders, indent=2)}
        
        Instructions:
        1. Replace all placeholders with specific, relevant content
        2. Ensure job-specific requirements are addressed
        3. Include company-specific details where appropriate
        4. Maintain the template's professional tone
        5. Ensure all content is accurate and compelling
        
        Return the fully customized cover letter.
        """
        
        ai_response = self.get_ai_response(prompt, system_message)
        
        customized_letter = self._structure_cover_letter(ai_response, {
            "company_name": company_name,
            "job_title": job_title,
            "template_based": True
        })
        
        return self.create_result(
            success=True,
            data={"cover_letter": customized_letter},
            message="Template successfully customized"
        )
    
    async def _generate_variations(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Generate multiple cover letter variations with different tones and approaches
        
        Args:
            task: The variation generation task
            context: Context information
            
        Returns:
            Cover letter variations result
        """
        base_info = task.input_data
        variation_count = task.input_data.get("variation_count", 3)
        tones = ["professional", "enthusiastic", "analytical"]
        
        variations = []
        
        for i in range(variation_count):
            tone = tones[i % len(tones)]
            
            system_message = f"""Write a cover letter with a {tone} tone and approach."""
            
            prompt = f"""
            Create a cover letter variation with a {tone} tone for:
            
            Company: {base_info.get('company_name', '')}
            Position: {base_info.get('job_title', '')}
            Job Description: {base_info.get('job_description', '')}
            
            Tone Guidelines:
            - Professional: Formal, traditional business style
            - Enthusiastic: Energetic, passionate, dynamic
            - Analytical: Data-driven, methodical, results-focused
            
            Adjust the writing style, word choice, and emphasis to match the {tone} tone
            while maintaining professionalism and relevance.
            """
            
            ai_response = self.get_ai_response(prompt, system_message)
            
            variation = {
                "tone": tone,
                "content": ai_response,
                "structured_data": self._structure_cover_letter(ai_response, {
                    "tone": tone,
                    "company_name": base_info.get('company_name', ''),
                    "job_title": base_info.get('job_title', '')
                })
            }
            
            variations.append(variation)
        
        return self.create_result(
            success=True,
            data={"variations": variations},
            message=f"Generated {len(variations)} cover letter variations"
        )
    
    def _structure_cover_letter(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure raw cover letter content into organized sections
        
        Args:
            content: Raw cover letter text
            metadata: Additional metadata about the letter
            
        Returns:
            Structured cover letter data
        """
        lines = content.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Try to identify sections
        header = []
        salutation = ""
        body_paragraphs = []
        closing = ""
        signature = ""
        
        current_paragraph = []
        in_body = False
        
        for line in lines:
            # Check for date/address header
            if any(word in line.lower() for word in ['date:', 'dear', 'to whom']):
                if current_paragraph:
                    header.extend(current_paragraph)
                    current_paragraph = []
                salutation = line
                in_body = True
            elif any(word in line.lower() for word in ['sincerely', 'best regards', 'thank you']):
                if current_paragraph:
                    body_paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                closing = line
                in_body = False
            elif not in_body and not salutation:
                header.append(line)
            elif in_body:
                if line == "":
                    if current_paragraph:
                        body_paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                else:
                    current_paragraph.append(line)
            else:
                signature = line
        
        # Add any remaining paragraph
        if current_paragraph:
            if in_body:
                body_paragraphs.append(' '.join(current_paragraph))
            else:
                signature = ' '.join(current_paragraph)
        
        return {
            "full_text": content,
            "header": header,
            "salutation": salutation,
            "body_paragraphs": body_paragraphs,
            "closing": closing,
            "signature": signature,
            "word_count": len(content.split()),
            "paragraph_count": len(body_paragraphs),
            "metadata": metadata,
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_quality_score(self, content: str, job_description: str) -> int:
        """
        Calculate a quality score for the generated cover letter
        
        Args:
            content: Cover letter content
            job_description: Job description to match against
            
        Returns:
            Quality score (0-100)
        """
        score = 0
        
        # Word count check (ideal range: 250-400 words)
        word_count = len(content.split())
        if 250 <= word_count <= 400:
            score += 20
        elif 200 <= word_count <= 500:
            score += 15
        else:
            score += 5
        
        # Check for key elements
        content_lower = content.lower()
        
        # Has compelling opening
        if any(phrase in content_lower for phrase in ['excited', 'enthusiastic', 'pleased', 'delighted']):
            score += 15
        
        # Shows company knowledge
        if any(phrase in content_lower for phrase in ['your company', 'your organization', 'your team']):
            score += 15
        
        # Includes specific achievements
        if any(char in content for char in ['%', '$', '#']) or any(word in content_lower for word in ['increased', 'improved', 'achieved', 'delivered']):
            score += 20
        
        # Professional closing
        if any(phrase in content_lower for phrase in ['sincerely', 'best regards', 'look forward']):
            score += 10
        
        # Job relevance (keyword matching)
        job_words = set(job_description.lower().split())
        content_words = set(content_lower.split())
        common_words = job_words.intersection(content_words)
        
        if len(job_words) > 0:
            relevance = len(common_words) / len(job_words)
            score += int(relevance * 20)
        
        return min(score, 100)
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key selling points from the cover letter"""
        # Simple extraction based on paragraph structure
        paragraphs = content.split('\n\n')
        key_points = []
        
        for paragraph in paragraphs[1:-1]:  # Skip opening and closing
            if len(paragraph.split()) > 20:  # Substantial paragraphs
                # Extract first sentence as key point
                sentences = paragraph.split('.')
                if sentences:
                    key_points.append(sentences[0].strip() + '.')
        
        return key_points[:3]  # Return top 3 key points
    
    def _identify_personalization(self, content: str, company_name: str, job_title: str) -> List[str]:
        """Identify personalization elements in the cover letter"""
        elements = []
        content_lower = content.lower()
        
        if company_name.lower() in content_lower:
            elements.append(f"Company name mentioned: {company_name}")
        
        if job_title.lower() in content_lower:
            elements.append(f"Job title referenced: {job_title}")
        
        # Look for research indicators
        research_indicators = ['mission', 'values', 'culture', 'recent', 'news', 'growth', 'expansion']
        for indicator in research_indicators:
            if indicator in content_lower:
                elements.append(f"Company research: {indicator} mentioned")
        
        return elements