"""
Application bootstrap and dependency injection configuration

Sets up the complete application with all dependencies properly configured.
"""

import logging
import os
from typing import Dict, Any

from .container import ServiceContainer, get_container, configure_container
from .security import get_security_config
from .validation import InputValidator
from .error_handler import ErrorHandler
from .protocols import ILogger, IConfiguration, IOpenAIClient, IValidator, IMetrics
from config import AppConfig, Config
from repositories.interfaces import IJobRepository, IApplicationRepository
from repositories.supabase_repositories import SupabaseJobRepository, SupabaseApplicationRepository
from services.job_service import JobService
from agents.agent_manager import AgentManager

# Mock implementations for development/testing
class MockOpenAIClient:
    """Mock OpenAI client for development"""
    
    def create_response(self, **kwargs):
        """Mock response creation with realistic job search results"""
        input_text = kwargs.get('input', '')
        
        # Check if this is a job search request
        if 'jobs' in input_text.lower() and ('search' in input_text.lower() or 'extract' in input_text.lower()):
            # Return realistic job search JSON
            mock_jobs = self._generate_mock_jobs(input_text)
            
            class MockResponse:
                def __init__(self, jobs_json):
                    self.output_text = jobs_json
            
            return MockResponse(mock_jobs)
        
        # Default mock response for other requests
        class MockResponse:
            def __init__(self):
                self.output_text = f"[MOCK] Generated response for: {kwargs.get('input', 'unknown input')[:50]}..."
        
        return MockResponse()
    
    def create_chat_completion(self, **kwargs):
        """Mock chat completion"""
        class MockChoice:
            def __init__(self):
                self.message = type('Message', (), {
                    'content': f"[MOCK] Chat response for: {kwargs.get('messages', [{}])[-1].get('content', 'unknown')[:50]}..."
                })()
        
        class MockCompletion:
            def __init__(self):
                self.choices = [MockChoice()]
        
        return MockCompletion()
    
    def _generate_mock_jobs(self, search_input):
        """Generate realistic mock job data based on search input"""
        import json
        import random
        
        # Extract job title from input if possible
        job_title = "Software Engineer"  # Default
        if 'Technical Program Manager' in search_input:
            job_title = "Technical Program Manager"
        elif 'Data Scientist' in search_input:
            job_title = "Data Scientist"
        elif 'Product Manager' in search_input:
            job_title = "Product Manager"
        elif 'DevOps' in search_input:
            job_title = "DevOps Engineer"
        elif 'Engineer' in search_input:
            job_title = "Software Engineer"
        
        # Extract location from input if possible
        location = "Remote"  # Default
        if 'Seattle' in search_input:
            location = "Seattle, WA"
        elif 'San Francisco' in search_input:
            location = "San Francisco, CA"
        elif 'New York' in search_input:
            location = "New York, NY"
        elif 'Austin' in search_input:
            location = "Austin, TX"
        
        # Generate realistic job listings
        companies = [
            "Amazon", "Microsoft", "Google", "Meta", "Apple",
            "Netflix", "Spotify", "Uber", "Airbnb", "Stripe",
            "Shopify", "Zoom", "Slack", "Datadog", "Snowflake"
        ]
        
        job_types = ["Full-time", "Contract", "Part-time"]
        experience_levels = ["Entry Level", "Mid Level", "Senior Level"]
        remote_types = ["Remote", "Hybrid", "On-site"]
        
        jobs = []
        for i in range(random.randint(5, 12)):  # Generate 5-12 jobs
            company = random.choice(companies)
            
            # Generate realistic job URLs
            if company == "Amazon":
                job_url = f"https://amazon.jobs/en/jobs/{random.randint(1000000, 9999999)}/{job_title.lower().replace(' ', '-')}"
            elif company == "Microsoft":
                job_url = f"https://careers.microsoft.com/us/en/job/{random.randint(1000000, 9999999)}/{job_title.replace(' ', '-')}"
            elif company == "Google":
                job_url = f"https://careers.google.com/jobs/results/{random.randint(1000000, 9999999)}"
            else:
                job_url = f"https://{company.lower()}.com/careers/job/{random.randint(1000, 9999)}"
            
            # Generate salary range
            base_salary = random.randint(80, 200) * 1000
            salary_range = f"${base_salary:,} - ${base_salary + random.randint(20, 50) * 1000:,}"
            
            # Generate skills
            all_skills = [
                "Python", "JavaScript", "React", "Node.js", "AWS", "Docker",
                "Kubernetes", "Git", "SQL", "MongoDB", "Redis", "GraphQL",
                "TypeScript", "Vue.js", "Angular", "Java", "Go", "Rust"
            ]
            skills = random.sample(all_skills, random.randint(3, 6))
            
            job = {
                "job_title": f"{job_title} - {company}",
                "company": company,
                "location": location if 'remote' not in search_input.lower() else random.choice([location, "Remote"]),
                "job_url": job_url,
                "salary_range": salary_range,
                "experience_level": random.choice(experience_levels),
                "remote_type": random.choice(remote_types),
                "requirements": f"We are looking for a talented {job_title} to join our team. {random.choice(['Strong problem-solving skills required.', 'Experience with agile methodologies preferred.', 'Excellent communication skills essential.'])}",
                "posted_date": f"{random.randint(1, 14)} days ago",
                "source": random.choice(["LinkedIn", "Indeed", "Company Website"])
            }
            jobs.append(job)
        
        return json.dumps(jobs, indent=2)

class MockDatabase:
    """Mock database connection for development"""
    
    async def execute_query(self, query: str, params=None):
        """Mock query execution"""
        class MockResult:
            def __init__(self):
                self.data = []
        return MockResult()
    
    async def execute_mutation(self, mutation: str, params=None):
        """Mock mutation execution"""
        class MockResult:
            def __init__(self):
                self.data = [{"id": "mock_id", "created_at": "2024-01-01T00:00:00Z"}]
        return MockResult()
    
    def close(self):
        """Mock close connection"""
        pass

class MockMetrics:
    """Mock metrics collector for development"""
    
    def increment_counter(self, name: str, tags=None):
        logging.getLogger("metrics").debug(f"Counter {name} incremented with tags: {tags}")
    
    def record_histogram(self, name: str, value: float, tags=None):
        logging.getLogger("metrics").debug(f"Histogram {name} recorded value {value} with tags: {tags}")
    
    def set_gauge(self, name: str, value: float, tags=None):
        logging.getLogger("metrics").debug(f"Gauge {name} set to {value} with tags: {tags}")

def setup_logging(config: AppConfig) -> logging.Logger:
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("interview_agent")
    logger.info(f"Logging initialized at level: {config.log_level}")
    
    return logger

def configure_services(container: ServiceContainer, config: AppConfig, logger: logging.Logger) -> None:
    """Configure all services in the dependency injection container"""
    
    # Register core services
    container.register_singleton(ILogger, type('LoggerAdapter', (), {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical
    }))
    
    container.register_singleton(IConfiguration, type('ConfigAdapter', (), {
        'get_openai_config': lambda: {
            'api_key': config.openai.api_key,
            'model': config.openai.model,
            'temperature': config.openai.temperature,
            'max_tokens': config.openai.max_tokens
        },
        'get_database_config': lambda: {
            'url': config.database.url,
            'key': config.database.key,
            'service_role_key': config.database.service_role_key
        },
        'get_security_config': lambda: {
            'master_key_set': config.security.master_key_set,
            'encryption_enabled': config.security.encryption_enabled,
            'environment': config.security.environment
        },
        'is_debug_mode': lambda: config.debug
    }))
    
    # Register validation service
    container.register_singleton(IValidator, InputValidator)
    
    # Register metrics (mock for now)
    container.register_singleton(IMetrics, MockMetrics)
    
    # Register OpenAI client (with fallback to mock)
    try:
        if config.openai.api_key and not config.debug:
            # Try to use real OpenAI client
            import openai
            real_client = openai.OpenAI(api_key=config.openai.api_key)
            container.register_singleton(IOpenAIClient, lambda: real_client)
            logger.info("Registered real OpenAI client")
        else:
            container.register_singleton(IOpenAIClient, MockOpenAIClient)
            logger.info("Registered mock OpenAI client")
    except Exception as e:
        logger.warning(f"Failed to setup OpenAI client, using mock: {e}")
        container.register_singleton(IOpenAIClient, MockOpenAIClient)
    
    # Register database connection (with fallback to mock)
    try:
        if config.database.url and config.database.key and not config.debug:
            # Try to use real database
            # Note: In a real implementation, you'd create the actual database connection here
            container.register_singleton(type('IDatabaseConnection', (), {}), MockDatabase)
            logger.info("Registered database connection (mock for now)")
        else:
            container.register_singleton(type('IDatabaseConnection', (), {}), MockDatabase)
            logger.info("Registered mock database connection")
    except Exception as e:
        logger.warning(f"Failed to setup database connection, using mock: {e}")
        container.register_singleton(type('IDatabaseConnection', (), {}), MockDatabase)
    
    # Register repositories
    container.register_singleton(IJobRepository, SupabaseJobRepository)
    container.register_singleton(IApplicationRepository, SupabaseApplicationRepository)
    
    # Register services
    container.register_singleton(JobService, JobService)
    
    # Register error handler
    container.register_singleton(ErrorHandler, ErrorHandler)
    
    # Register agent manager
    container.register_singleton(AgentManager, AgentManager)
    
    logger.info("All services configured successfully")

def create_application() -> Dict[str, Any]:
    """
    Create and configure the complete application
    
    Returns:
        Dictionary containing all configured application components
    """
    # Load configuration
    try:
        config = AppConfig.from_env()
        config.validate()
        config.ensure_directories()
    except Exception as e:
        # Fallback to legacy config for backward compatibility
        legacy_config = Config()
        legacy_config.validate_config()
        # Convert to new config format
        config = legacy_config.get_app_config()
    
    # Setup logging
    logger = setup_logging(config)
    
    # Get dependency injection container
    container = get_container()
    
    # Configure all services
    configure_services(container, config, logger)
    
    # Create main application components
    try:
        error_handler = container.get(ErrorHandler)
        validator = container.get(IValidator)
        metrics = container.get(IMetrics)
        
        # Create agent manager
        agent_manager = container.get(AgentManager)
        
        # Create job service
        job_service = container.get(JobService)
        
        logger.info("Application created successfully")
        
        return {
            "config": config,
            "logger": logger,
            "container": container,
            "error_handler": error_handler,
            "validator": validator,
            "metrics": metrics,
            "agent_manager": agent_manager,
            "job_service": job_service,
            "security_config": get_security_config()
        }
        
    except Exception as e:
        logger.critical(f"Failed to create application: {e}")
        raise

async def initialize_application(app_components: Dict[str, Any]) -> None:
    """
    Initialize the application components
    
    Args:
        app_components: Components returned from create_application()
    """
    logger = app_components["logger"]
    agent_manager = app_components["agent_manager"]
    
    try:
        logger.info("Initializing application components...")
        
        # Initialize agents
        await agent_manager.initialize_agents()
        
        # Test agents
        test_results = await agent_manager.test_agents()
        healthy_agents = sum(1 for result in test_results.values() if result.get("overall_health", False))
        total_agents = len(test_results)
        
        logger.info(f"Agent health check completed: {healthy_agents}/{total_agents} agents healthy")
        
        # Validate security configuration
        security_config = app_components["security_config"]
        security_validation = security_config.validate_security_requirements()
        
        if security_validation.get("security_warnings"):
            for warning in security_validation["security_warnings"]:
                logger.warning(f"Security warning: {warning}")
        
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.critical(f"Failed to initialize application: {e}")
        raise

def get_application_info(app_components: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get comprehensive application information
    
    Args:
        app_components: Components returned from create_application()
        
    Returns:
        Application information dictionary
    """
    config = app_components["config"]
    agent_manager = app_components["agent_manager"]
    security_config = app_components["security_config"]
    
    return {
        "application": {
            "name": config.app_name,
            "debug_mode": config.debug,
            "log_level": config.log_level,
            "environment": config.security.environment
        },
        "agents": agent_manager.get_agent_status(),
        "agent_health": agent_manager.get_agent_health(),
        "security": security_config.validate_security_requirements(),
        "dependencies": {
            "openai_configured": bool(config.openai.api_key),
            "database_configured": bool(config.database.url and config.database.key),
            "gmail_configured": bool(config.gmail_email and config.gmail_app_password)
        }
    }