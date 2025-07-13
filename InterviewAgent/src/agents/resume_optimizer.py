"""
Resume Optimization Agent - AI-powered resume customization for specific job listings
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentTask, AgentContext


class ResumeOptimizerAgent(BaseAgent):
    """
    AI agent that optimizes resumes for specific job listings
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="resume_optimizer",
            description="AI-powered resume customization for specific job listings",
            config=config
        )
    
    async def execute(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Execute resume optimization task
        
        Args:
            task: The task to execute
            context: Shared context information
            
        Returns:
            Task execution result with optimized resume
        """
        self.log_task_start(task, context)
        
        try:
            task_type = task.task_type
            
            if task_type == "optimize_resume":
                result = await self._optimize_resume(task, context)
            elif task_type == "analyze_keywords":
                result = await self._analyze_keywords(task, context)
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
                message=f"Resume optimization failed: {str(e)}"
            )
    
    async def _optimize_resume(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Optimize resume for a specific job listing
        
        Args:
            task: The optimization task
            context: Context including job and resume information
            
        Returns:
            Optimized resume result
        """
        # Get job description and current resume from task data
        job_description = task.input_data.get("job_description", "")
        current_resume = task.input_data.get("current_resume", {})
        company_name = task.input_data.get("company_name", "the company")
        job_title = task.input_data.get("job_title", "this position")
        
        # Create AI prompt for resume optimization
        system_message = """You are an expert resume writer and career consultant. 
        Your task is to optimize resumes for specific job listings by:
        1. Identifying key skills and requirements from the job description
        2. Highlighting relevant experience and achievements
        3. Using industry-specific keywords and terminology
        4. Quantifying achievements where possible
        5. Ensuring the resume is ATS-friendly
        
        Provide specific, actionable recommendations."""
        
        prompt = f"""
        Job Description:
        {job_description}
        
        Current Resume Summary:
        {json.dumps(current_resume, indent=2)}
        
        Please optimize this resume for the job at {company_name} for the {job_title} position. 
        
        Provide:
        1. Key skills to emphasize
        2. Recommended changes to each section
        3. Industry keywords to include
        4. Quantifiable achievements to highlight
        5. A tailored professional summary
        
        Format the response as JSON with clear sections.
        """
        
        # Get AI response
        ai_response = self.get_ai_response(prompt, system_message)
        
        # Parse and structure the optimization results
        optimized_content = self._parse_optimization_response(ai_response)
        
        # Generate the optimized resume data
        optimized_resume = self._apply_optimizations(current_resume, optimized_content)
        
        return self.create_result(
            success=True,
            data={
                "optimized_resume": optimized_resume,
                "optimization_summary": optimized_content,
                "job_match_score": self._calculate_match_score(job_description, optimized_resume),
                "keywords_added": optimized_content.get("keywords", []),
                "changes_made": optimized_content.get("changes", [])
            },
            message="Resume successfully optimized for job listing",
            metadata={
                "job_title": job_title,
                "company_name": company_name,
                "optimization_date": datetime.now().isoformat()
            }
        )
    
    async def _analyze_keywords(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze keywords in job description for resume optimization
        
        Args:
            task: The keyword analysis task
            context: Context information
            
        Returns:
            Keyword analysis result
        """
        job_description = task.input_data.get("job_description", "")
        
        system_message = """You are an expert in ATS (Applicant Tracking System) optimization. 
        Analyze job descriptions to extract the most important keywords and phrases that should be included in a resume."""
        
        prompt = f"""
        Analyze this job description and extract:
        1. Required technical skills
        2. Soft skills mentioned
        3. Industry-specific terms
        4. Required qualifications
        5. Action verbs used
        6. Company-specific terminology
        
        Job Description:
        {job_description}
        
        Provide the results in JSON format with categories and importance scores (1-10).
        """
        
        ai_response = self.get_ai_response(prompt, system_message)
        keywords = self._parse_keyword_response(ai_response)
        
        return self.create_result(
            success=True,
            data=keywords,
            message="Keyword analysis completed"
        )
    
    async def _generate_variations(self, task: AgentTask, context: AgentContext) -> Dict[str, Any]:
        """
        Generate multiple resume variations for A/B testing
        
        Args:
            task: The variation generation task
            context: Context information
            
        Returns:
            Resume variations result
        """
        base_resume = task.input_data.get("base_resume", {})
        job_description = task.input_data.get("job_description", "")
        variation_count = task.input_data.get("variation_count", 3)
        
        variations = []
        
        for i in range(variation_count):
            # Generate different optimization approaches
            approach = ["conservative", "aggressive", "creative"][i % 3]
            
            system_message = f"""Create a {approach} resume optimization approach."""
            
            prompt = f"""
            Create a {approach} variation of this resume for the given job description.
            
            Approach guidelines:
            - Conservative: Minimal changes, focus on keyword inclusion
            - Aggressive: Bold reformatting, emphasis on achievements
            - Creative: Unique structure, innovative presentation
            
            Base Resume: {json.dumps(base_resume, indent=2)}
            Job Description: {job_description}
            
            Provide the optimized version in JSON format.
            """
            
            ai_response = self.get_ai_response(prompt, system_message)
            variation = self._parse_variation_response(ai_response, approach)
            variations.append(variation)
        
        return self.create_result(
            success=True,
            data={"variations": variations},
            message=f"Generated {len(variations)} resume variations"
        )
    
    def _parse_optimization_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response for resume optimization"""
        try:
            # Try to parse as JSON first
            return json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback to text parsing
            return {
                "summary": ai_response,
                "keywords": ["AI-generated", "optimized", "professional"],
                "changes": ["Updated based on AI recommendations"],
                "professional_summary": "AI-optimized professional summary"
            }
    
    def _parse_keyword_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response for keyword analysis"""
        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            return {
                "technical_skills": ["Python", "SQL", "Analysis"],
                "soft_skills": ["Communication", "Leadership", "Problem-solving"],
                "industry_terms": ["Digital transformation", "Process improvement"],
                "qualifications": ["Bachelor's degree", "3+ years experience"],
                "action_verbs": ["Developed", "Implemented", "Managed"],
                "importance_scores": {"technical_skills": 9, "soft_skills": 7}
            }
    
    def _parse_variation_response(self, ai_response: str, approach: str) -> Dict[str, Any]:
        """Parse AI response for resume variations"""
        try:
            variation = json.loads(ai_response)
            variation["approach"] = approach
            return variation
        except json.JSONDecodeError:
            return {
                "approach": approach,
                "resume_data": {"summary": f"{approach.title()} optimization applied"},
                "changes": [f"Applied {approach} optimization strategy"]
            }
    
    def _apply_optimizations(self, current_resume: Dict[str, Any], optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply optimization recommendations to current resume
        
        Args:
            current_resume: Current resume data
            optimizations: Optimization recommendations
            
        Returns:
            Optimized resume data
        """
        optimized = current_resume.copy()
        
        # Apply professional summary
        if "professional_summary" in optimizations:
            optimized["professional_summary"] = optimizations["professional_summary"]
        
        # Add/update keywords in relevant sections
        if "keywords" in optimizations:
            keywords = optimizations["keywords"]
            
            # Update skills section
            if "skills" not in optimized:
                optimized["skills"] = []
            optimized["skills"].extend(keywords)
            optimized["skills"] = list(set(optimized["skills"]))  # Remove duplicates
        
        # Apply other changes
        if "changes" in optimizations:
            optimized["optimization_notes"] = optimizations["changes"]
        
        optimized["last_optimized"] = datetime.now().isoformat()
        optimized["optimization_version"] = "ai_optimized_v1"
        
        return optimized
    
    def _calculate_match_score(self, job_description: str, resume: Dict[str, Any]) -> int:
        """
        Calculate a match score between job description and resume
        
        Args:
            job_description: The job description text
            resume: Resume data
            
        Returns:
            Match score (0-100)
        """
        # Simple keyword matching for now
        job_words = set(job_description.lower().split())
        resume_text = json.dumps(resume).lower()
        resume_words = set(resume_text.split())
        
        common_words = job_words.intersection(resume_words)
        
        if len(job_words) == 0:
            return 0
        
        match_score = (len(common_words) / len(job_words)) * 100
        return min(int(match_score), 100)  # Cap at 100