# CLAUDE.md

This file provides guidance for working with the InterviewAgent codebase.

## Project Overview

InterviewAgent is an AI-powered job application automation system built with Python, Streamlit, and OpenAI SDK. The system helps job candidates automatically apply to positions using AI agents for resume optimization, cover letter generation, and web automation.

## Current Status

**MVP COMPLETE** - Production hardening in progress

**Key Features:**
- Working Streamlit application with full navigation
- AI agent framework with OpenAI integration
- End-to-end job application automation workflow
- Playwright automation for web form submission
- Gmail integration for email notifications
- BaseAgent class with proper abstraction

## Quick Start

```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install

# Configure application
cp .env.example .env  # Update with your credentials
python scripts/setup_database.py

# Run application
python run_app.py
# or: streamlit run streamlit_app.py

# Development tools
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

**Production Requirements:**
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

### Agent Development Guidelines

**Base Architecture:**
- Base agent class in `src/agents/base_agent.py`
- Each agent should inherit from BaseAgent
- Use the Responses API while creating agents

**Production Patterns Required:**
- **Dependency Injection**: Service container for agent dependencies
- **Repository Pattern**: Abstract database operations behind repositories
- **Service Layer**: Separate business logic from agent implementations
- **Error Handling**: Comprehensive error handling with retry mechanisms
- **Communication**: Structured data for agent communication

**Agent Implementation Pattern:**
```python
class ProductionAgent(BaseAgent):
    def __init__(self, services: ServiceContainer):
        super().__init__()
        self.services = services
        self.repository = services.get_repository()
        self.logger = services.get_logger()
    
    async def execute(self, task: AgentTask) -> AgentResult:
        # Input validation
        # Business logic through services
        # Error handling with retries
        # Secure logging
        # Structured response
```

### Security Considerations

**Critical Security Requirements:**
- **API Key Management**: Remove hardcoded keys, implement secure vault
- **Credential Storage**: Encrypt job site credentials using AES-256
- **Input Validation**: Validate all user inputs and sanitize data
- **Error Handling**: Remove sensitive data from error messages
- **Network Security**: Implement rate limiting and HTTPS enforcement
- **Data Privacy**: Add data retention policies and GDPR compliance

## Testing Strategy

**Current Status**: Basic testing implemented, comprehensive framework required

**Testing Requirements:**
- **Unit Testing**: Expand pytest coverage for all agent methods (target 80%+)
- **Integration Testing**: Database operations and agent workflow integration
- **End-to-End Testing**: Complete automation workflows and UI testing
- **Agent-Specific Testing**: AI response validation and web scraping reliability
- **Security Testing**: Penetration testing and credential storage validation

**Testing Tools:**
```bash
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

## Application Features

**Implemented:**
- Dashboard with metrics and recent activity
- Resume Manager with file upload interface
- Job Search with discovery and filtering
- Application tracking and status monitoring
- Email notifications and settings
- User preferences and job site configuration
- Sidebar navigation and error handling

## Code Quality Issues

**High Priority Fixes:**
1. **agent_manager.py**: Missing error handling and retry mechanisms
2. **simple_automation_controller.py**: Mock data fallbacks in production code
3. **Base Agent Classes**: Missing dependency injection and inconsistent error handling

**Architectural Improvements:**
- Service Container for dependency injection
- Repository Pattern for database operations
- Service Layer for business logic separation
- Configuration Management for environment-specific settings
- Monitoring and alerting system

## Production Readiness Roadmap

**Phase 1: Security Hardening (Week 1)**
- API key security migration to secure vault
- Credential encryption system implementation
- Input validation framework with Pydantic
- Error message sanitization

**Phase 2: Architecture Improvements (Week 2)**
- Service container for dependency injection
- Repository pattern for data access
- Service layer for business logic separation
- Configuration management system

**Phase 3: Comprehensive Testing (Week 3)**
- Unit testing expansion (>80% coverage)
- Integration testing suite
- Security and performance testing
- End-to-end automation verification

**Production Deployment Checklist:**
- [ ] All API keys moved to secure vault
- [ ] Credential encryption implemented
- [ ] Input validation on all endpoints
- [ ] Dependency injection container
- [ ] Repository pattern implemented
- [ ] Unit tests >80% coverage
- [ ] Security tests completed
- [ ] Health check endpoints
- [ ] Monitoring and alerting

## Development Notes

**Recent Updates:**
- Security review completed - production deployment blocked until security fixes implemented
- Production readiness plan established with clear dependencies
- Service container, repository pattern, and service layer blueprints completed
- Comprehensive security hardening plan with secure vault integration
- Testing framework strategy with >80% coverage target
- Production deployment gates established with clear success criteria


