# CLAUDE.md

This file provides guidance to Claude Code when working with the InterviewAgent codebase.

## Project Overview

InterviewAgent is an AI-powered job application automation system built with Python, Streamlit, and OpenAI SDK. The system helps job candidates automatically apply to positions using AI agents for resume optimization, cover letter generation, and web automation.

## Latest Updates

- Encrypted credential storage and secure configuration options
- Comprehensive input validation across all endpoints
- Dependency injection container with clear service layer separation
- Circuit breaker and retry mechanisms for robust error handling
- Health monitoring with real-time agent status metrics
- Streamlit UI enhancements including analytics dashboard and agent management

## Quick Start

```bash
# Setup and start application
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
cp .env.example .env  # update with your credentials
python scripts/setup_database.py
python run_app.py  # or: streamlit run streamlit_app.py

# Testing and code quality
pytest tests/
black src/
flake8 src/
```

## Architecture

**Technology Stack:**
- Frontend: Streamlit (Python web framework)
- Backend: Python with integrated Streamlit app
- Database: Supabase (PostgreSQL + Storage)
- AI: OpenAI Python SDK with function calling and MCP integration
- Automation: Playwright MCP Server for web automation
- Email: Gmail MCP Server for email notifications

**Key Directories:**
- `/src/agents/` - AI agent implementations
- `/src/database/` - Database operations and models
- `/src/pages/` - Streamlit page components
- `/src/utils/` - Utility functions
- `/docs/` - Documentation
- `/tests/` - Test suites

## Current Status

**MVP COMPLETE** - Production hardening required

**✅ Implemented Features:**
- Working Streamlit application with full navigation
- Complete AI agent framework with OpenAI integration
- End-to-end job application automation workflow
- Playwright automation for web form submission
- Gmail integration for email notifications
- BaseAgent class with proper abstraction

**⚠️ Production Requirements:**
- **Security**: API key management, credential encryption, input validation
- **Architecture**: Dependency injection, repository pattern, service layer
- **Testing**: >80% coverage, integration tests, security tests

## Development Guidelines

**Getting Started:**
1. Run `python3 run_app.py` to start the application
2. Access at http://localhost:8501
3. Use mock mode for development without Supabase

**Configuration:**
- Environment variables in `.env` file (copy from `.env.example`)
- Configuration class in `src/config.py`
- Database models in `src/database/models.py`

**Streamlit Development:**
- Main app in `streamlit_app.py`
- Page components in `src/pages/`
- Use `st.session_state` for state management
- Cache database connections with `@st.cache_resource`

### Agent Development Guidelines - PRODUCTION PATTERNS

**BASE ARCHITECTURE:**
- Base agent class in `src/agents/base_agent.py`
- Each agent should inherit from BaseAgent
- **Use the Responses API while creating agents**

**REQUIRED PRODUCTION PATTERNS:**
- **🏗️ Dependency Injection**:
  - Implement service container for agent dependencies
  - Abstract external services (OpenAI, database, email)
  - Enable easy mocking and testing
  - Support configuration-based service selection

- **📊 Repository Pattern**:
  - Abstract database operations behind repositories
  - Implement interfaces for data access
  - Enable database switching and testing
  - Add query optimization and caching

- **🔧 Service Layer**:
  - Separate business logic from agent implementations
  - Create reusable service components
  - Implement cross-cutting concerns (logging, metrics)
  - Add service-to-service communication patterns

- **⚠️ Error Handling**:
  - Implement comprehensive error handling
  - Add retry mechanisms with exponential backoff
  - Create custom exception types
  - Log all agent activities securely

- **📡 Communication**:
  - Use structured data for agent communication
  - Implement async/await patterns consistently
  - Add message validation and serialization
  - Create event-driven communication where appropriate

**AGENT IMPLEMENTATION CHECKLIST:**
```python
# Required implementation pattern
class ProductionAgent(BaseAgent):
    def __init__(self, services: ServiceContainer):
        super().__init__()
        self.services = services  # Dependency injection
        self.repository = services.get_repository()  # Data access
        self.logger = services.get_logger()  # Secure logging
    
    async def execute(self, task: AgentTask) -> AgentResult:
        # Input validation
        # Business logic through services
        # Error handling with retries
        # Secure logging
        # Structured response
```

### Security Considerations - CRITICAL FOR PRODUCTION

**IMMEDIATE SECURITY REQUIREMENTS:**
- **🔑 API Key Management**: 
  - Remove hardcoded API keys from configuration files
  - Implement secure vault (HashiCorp Vault, AWS Secrets Manager)
  - Use short-lived tokens where possible
  - Add API key rotation mechanisms

- **🔐 Credential Storage**:
  - Encrypt job site credentials using AES-256
  - Implement proper key derivation (PBKDF2/Argon2)
  - Store encryption keys separately from encrypted data
  - Add credential access auditing

- **🛡️ Input Validation**:
  - Validate all user inputs (job criteria, resumes, settings)
  - Sanitize data before AI agent processing
  - Implement file upload validation and scanning
  - Add SQL injection protection for database queries

- **📊 Error Handling**:
  - Remove sensitive data from error messages
  - Implement secure logging without exposing credentials
  - Add error monitoring with sanitized reports
  - Create user-friendly error messages

- **🌐 Network Security**:
  - Implement rate limiting for web scraping
  - Add request throttling and circuit breakers
  - Use secure session management in Streamlit
  - Implement HTTPS enforcement

- **👤 Data Privacy**:
  - Add data retention policies
  - Implement user data deletion capabilities
  - Add GDPR compliance features
  - Secure user session management

## Testing Strategy - COMPREHENSIVE FRAMEWORK NEEDED

**CURRENT STATUS**: Basic testing implemented, comprehensive framework required

**IMMEDIATE TESTING REQUIREMENTS:**
- **🧪 Unit Testing**:
  - Expand pytest coverage for all agent methods
  - Add mock testing for external API calls
  - Test error handling and edge cases
  - Target 80%+ code coverage

- **🔗 Integration Testing**:
  - Database operations with real Supabase instance
  - Agent workflow integration tests
  - API integration testing with mocked services
  - Configuration validation tests

- **🎭 End-to-End Testing**:
  - Complete automation workflows
  - User interface testing with Selenium
  - Error recovery and retry mechanisms
  - Performance testing under load

- **🤖 Agent-Specific Testing**:
  - AI response validation and quality checks
  - Web scraping reliability tests
  - Email notification delivery verification
  - Playwright automation success rates

- **🔒 Security Testing**:
  - Penetration testing for vulnerabilities
  - Credential storage security validation
  - Input sanitization effectiveness
  - Authentication and authorization tests

**TESTING INFRASTRUCTURE NEEDED:**
```bash
# Required testing tools
pip install pytest pytest-cov pytest-mock
pip install selenium webdriver-manager
pip install pytest-asyncio pytest-xdist
pip install bandit safety  # Security testing
```

## Deployment
- **Development**: `python3 run_app.py` or `streamlit run streamlit_app.py`
- **Testing**: `python3 test_app.py` for component verification
- **Production**: Streamlit Cloud or Docker container (future)
- **Environment setup**: Virtual environment with requirements.txt
- **Database migration**: Via Supabase SQL editor using migrations.sql

## Current Application Features
- ✅ **Dashboard**: Overview with metrics, recent activity, and quick actions
- ✅ **Resume Manager**: File upload interface (placeholder)
- ✅ **Job Search**: Job discovery and filtering interface (placeholder)
- ✅ **Applications**: Application tracking and status monitoring (placeholder)
- ✅ **Notifications**: Email settings and notification history (placeholder)
- ✅ **Settings**: User preferences and job site configuration (placeholder)
- ✅ **Navigation**: Sidebar navigation between all pages
- ✅ **Mock Data**: Sample statistics and activity logs for development
- ✅ **Error Handling**: Graceful fallback to mock mode if database unavailable

## Next Development Steps
1. **OpenAI SDK Integration**: Set up AI agent framework
2. **Base Agent Classes**: Create foundation for all automation agents
3. **Resume Optimization**: Implement AI-powered resume customization
4. **Cover Letter Generation**: Build personalized cover letter creation
5. **Job Discovery**: Add web scraping capabilities with Playwright

## Production Readiness Roadmap - COORDINATED 3-WEEK PLAN

### PHASE 1: SECURITY HARDENING (CRITICAL - Week 1)
**Priority: P0 - Production Blocker**
**Resource: 1 Senior Security Engineer**

**Days 1-2: API Key Security Migration**
```python
# Current (UNSAFE):
OPENAI_API_KEY = "sk-..."  # Hardcoded in config

# Required (SECURE):
from azure.keyvault.secrets import SecretClient
class SecureConfigurationService:
    def __init__(self, vault_client: IVaultClient):
        self._vault = vault_client
    
    async def get_openai_config(self) -> OpenAIConfig:
        api_key = await self._vault.get_secret("openai-api-key")
        return OpenAIConfig(api_key=api_key, model="gpt-4o-mini")
```

**Days 3-4: Credential Encryption System**
```python
# Required implementation:
from cryptography.fernet import Fernet
import json

class EncryptionService:
    def __init__(self, master_key: str):
        self._fernet = Fernet(master_key.encode())
    
    def encrypt_credentials(self, credentials: Dict[str, str]) -> str:
        json_data = json.dumps(credentials)
        return self._fernet.encrypt(json_data.encode()).decode()
    
    def decrypt_credentials(self, encrypted_data: str) -> Dict[str, str]:
        decrypted_bytes = self._fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted_bytes.decode())
```

**Days 4-5: Input Validation Framework**
```python
# Complete Pydantic integration:
from pydantic import BaseModel, validator

class JobSearchCriteria(BaseModel):
    job_title: str
    location: str
    salary_range: Optional[str]
    
    @validator('job_title')
    def validate_job_title(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Job title must be at least 2 characters')
        return v.strip()
```

**Success Gate 1:** Zero security vulnerabilities in automated scans

### PHASE 2: ARCHITECTURE IMPROVEMENTS (HIGH - Week 2)
**Priority: P1 - Technical Debt Reduction**
**Resource: 1 Senior Backend Engineer**

**Days 1-3: Service Container Implementation**
```python
# Complete dependency injection:
class ServiceContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]):
        self._services[interface] = implementation
    
    def get(self, service_type: Type[T]) -> T:
        if service_type not in self._singletons:
            impl = self._services[service_type]
            self._singletons[service_type] = impl()
        return self._singletons[service_type]

class AgentFactory:
    def __init__(self, container: ServiceContainer):
        self._container = container
    
    def create_automation_controller(self) -> SimpleAutomationController:
        return SimpleAutomationController(
            logger=self._container.get(ILogger),
            openai_client=self._container.get(IOpenAIClient),
            config=self._container.get(IConfiguration),
            job_service=self._container.get(JobService)
        )
```

**Days 3-4: Repository Pattern Completion**
```python
# Complete data access abstraction:
class IUserRepository(Protocol):
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]: ...
    async def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> bool: ...

class SupabaseUserRepository(BaseSupabaseRepository, IUserRepository):
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        # Secure implementation with input validation
        validated_id = self._validator.validate_user_id(user_id)
        return await self._execute_query("SELECT * FROM users WHERE id = %s", [validated_id])
```

**Days 4-5: Service Layer Architecture**
```python
# Business logic separation:
class UserService:
    def __init__(
        self, 
        user_repo: IUserRepository,
        encryption_service: IEncryption,
        validator: IValidator,
        logger: ILogger
    ):
        self._user_repo = user_repo
        self._encryption = encryption_service
        self._validator = validator
        self._logger = logger
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        # Business logic with validation, caching, logging
        validation_result = await self._validator.validate_user_id(user_id)
        if not validation_result.is_valid:
            raise ValidationError(validation_result.errors)
        
        profile = await self._user_repo.get_user_profile(user_id)
        await self._logger.log_user_access(user_id, "profile_access")
        return profile
```

**Success Gate 2:** All components use proper abstraction patterns

### PHASE 3: COMPREHENSIVE TESTING (HIGH - Week 3)
**Priority: P1 - Quality Assurance**
**Resource: 1 Senior QA Engineer + 1 Junior**

**Days 1-2: Unit Testing Expansion**
```python
# Enhanced testing with DI:
class TestAgentSystem:
    def setup_method(self):
        self.container = ServiceContainer()
        self.configure_test_services(self.container)
        
    def configure_test_services(self, container: ServiceContainer):
        container.register_singleton(IOpenAIClient, MockOpenAIClient)
        container.register_singleton(IDatabaseConnection, MockDatabase)
        container.register_singleton(ILogger, MockLogger)
    
    async def test_automation_controller_execution(self):
        factory = AgentFactory(self.container)
        controller = factory.create_automation_controller()
        
        result = await controller.execute_automation("job_search", {"title": "engineer"})
        assert result.success
        assert result.jobs_found > 0
```

**Days 2-3: Integration Testing Suite**
```bash
# Complete testing infrastructure:
pytest src/ --cov=src --cov-report=html --cov-fail-under=80
pytest tests/integration/ --integration
pytest tests/security/ --security
```

**Days 4-5: Security & Performance Testing**
```bash
# Security and performance validation:
bandit -r src/ --severity-level medium
safety check --json
locust -f tests/performance/locustfile.py --host=http://localhost:8501
```

**Success Gate 3:** >80% coverage, all security tests passed, performance benchmarks met

### COORDINATION REQUIREMENTS

**Cross-Workstream Dependencies:**
1. **Security → Architecture**: Secure service interfaces must be defined before DI implementation
2. **Architecture → Testing**: Service abstractions must be complete before comprehensive testing
3. **All Phases → Documentation**: Changes must be documented in real-time

**Daily Coordination:**
- **Morning Standup**: Progress review and blocker identification
- **Midday Check-in**: Cross-team dependency coordination
- **Evening Review**: Daily deliverable completion validation

**Integration Points:**
1. **Agent Communication**: Secure patterns between agents
2. **Database Operations**: Repository pattern with security
3. **External Services**: MCP server integration with architecture

### PRODUCTION DEPLOYMENT CHECKLIST

**SECURITY REQUIREMENTS:**
- [ ] All API keys moved to secure vault
- [ ] Credential encryption implemented
- [ ] Input validation on all endpoints
- [ ] Error messages sanitized
- [ ] Secure logging implemented
- [ ] Rate limiting configured
- [ ] HTTPS enforcement enabled

**ARCHITECTURE REQUIREMENTS:**
- [ ] Dependency injection container
- [ ] Repository pattern implemented
- [ ] Service layer created
- [ ] Database migration system
- [ ] Configuration management
- [ ] Monitoring and alerting

**TESTING REQUIREMENTS:**
- [ ] Unit tests >80% coverage
- [ ] Integration tests passing
- [ ] Security tests completed
- [ ] Performance tests under load
- [ ] End-to-end automation verified

**OPERATIONAL REQUIREMENTS:**
- [ ] Health check endpoints
- [ ] Logging and monitoring
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Backup and recovery
- [ ] Documentation complete

## Code Quality Issues Found

### HIGH PRIORITY FIXES NEEDED:

1. **agent_manager.py**:
   - Missing error handling in agent initialization
   - No retry mechanisms for agent failures
   - Unsafe exception handling exposing sensitive data

2. **simple_automation_controller.py**:
   - Mock data fallbacks in production code
   - Missing input validation
   - Hardcoded user profile data
   - Inadequate error handling in automation workflows

3. **Base Agent Classes**:
   - Missing dependency injection
   - Tight coupling to external services
   - Inconsistent error handling patterns

### ARCHITECTURAL IMPROVEMENTS NEEDED:

1. **Service Container**: Implement proper dependency injection
2. **Repository Pattern**: Abstract database operations
3. **Service Layer**: Separate business logic from infrastructure
4. **Configuration Management**: Environment-specific configurations
5. **Monitoring**: Add application monitoring and alerting

## Development Memories
- Make sure every step is updated in the blog-content.md
- **CRITICAL**: Security review completed 2025-07-29 - production deployment blocked until security fixes implemented
- **COORDINATION**: Technical Program Manager & Architecture Reviewer analysis completed 2025-08-05
- **ROADMAP**: 3-week coordinated production readiness plan established with clear dependencies
- **ARCHITECTURE**: Service container, repository pattern, and service layer blueprints completed
- **SECURITY**: Comprehensive security hardening plan with Azure Key Vault integration
- **TESTING**: Complete testing framework strategy with >80% coverage target
- Production deployment gates established with clear success criteria


