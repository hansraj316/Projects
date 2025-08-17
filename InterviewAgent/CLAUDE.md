# CLAUDE.md

This file provides guidance for working with the InterviewAgent codebase.

## Project Overview

InterviewAgent is an AI-powered job application automation system built with Python, Streamlit, and OpenAI SDK. The system helps job candidates automatically apply to positions using AI agents for resume optimization, cover letter generation, and web automation.

## Current Status

**INFRASTRUCTURE COMPLETE** - Core features partially implemented

**✅ Working Features:**
- ✅ Streamlit application with professional UI and full navigation
- ✅ Supabase database integration with real data storage
- ✅ Professional architecture with dependency injection and error handling
- ✅ Security framework with encryption and input validation
- ✅ Service container and repository pattern implementation
- ✅ AI agent framework (architecture complete, agents initialize and execute)
- ✅ OpenAI configuration (fully connected to agent workflows)
- ✅ BaseAgent class (agents initialize and run successfully)

**⚠️ Partially Working:**
- ⚠️ End-to-end job application automation (workflow exists with some real components, partial simulations)
- ⚠️ Playwright web automation (integrated with MCP fallbacks, some simulation)
- ⚠️ Gmail email notifications (agent implemented, integration partial)
- ⚠️ AI-powered resume optimization and cover letter generation (agents implemented, using real OpenAI where configured)

**❌ Not Implemented:**
- ❌ Full production deployment (Streamlit Cloud/Docker pending)
- ❌ Comprehensive performance optimization

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

## Semantic Model & Codebase Architecture

### Core Architecture Patterns

**Dependency Injection Container (`src/core/container.py`)**
- Thread-safe service container with singleton, transient, and scoped lifetimes
- Automatic constructor dependency resolution using type hints
- Service validation and factory function support
- Global container instance with configurator pattern

**Protocol-Based Interfaces (`src/core/protocols.py`)**
- Runtime-checkable protocols for loose coupling
- Core interfaces: `ILogger`, `IOpenAIClient`, `IConfiguration`, `IEncryption`
- Service interfaces: `IValidator`, `IDatabaseConnection`, `IEventBus`, `IMetrics`
- Domain interfaces: `IEmailService`, `IWebAutomation`

**Agent Framework (`src/agents/base_agent.py`)**
- Abstract base class with dependency injection support
- Standardized task execution with `AgentTask`, `AgentResult`, `AgentContext`
- Built-in error handling, retry mechanisms, and execution metrics
- OpenAI integration with Responses API and multiple response parsing strategies

### Domain Layer Structure

```
src/
├── core/                    # Infrastructure & Cross-Cutting Concerns
│   ├── bootstrap.py         # Application startup and DI configuration
│   ├── container.py         # Dependency injection container
│   ├── protocols.py         # Interface definitions
│   ├── security.py          # Encryption and authentication
│   ├── validation.py        # Input validation and sanitization
│   ├── error_handler.py     # Global error handling
│   └── exceptions.py        # Custom exception hierarchy
│
├── database/                # Data Access Layer
│   ├── models.py           # Data models and schemas
│   ├── connection.py       # Database connection management
│   ├── operations.py       # Raw database operations
│   └── migrations.sql      # Database schema migrations
│
├── repositories/            # Repository Pattern Implementation
│   ├── interfaces.py       # Repository contracts
│   └── supabase_repositories.py  # Supabase-specific implementations
│
├── services/                # Business Logic Layer
│   ├── job_service.py      # Job search and management
│   └── job_automation_service.py  # End-to-end automation workflows
│
├── agents/                  # AI Agent Domain
│   ├── base_agent.py       # Base agent with DI and OpenAI integration
│   ├── job_discovery.py    # Job search and filtering
│   ├── resume_optimizer.py # AI-powered resume optimization
│   ├── cover_letter_generator.py  # Dynamic cover letter creation
│   ├── application_submitter.py   # Web form automation
│   ├── email_notification.py      # Email integration
│   └── enhanced_orchestrator.py   # Multi-agent coordination
│
├── automation/              # Web Automation Layer
│   ├── real_mcp_implementation.py  # MCP Playwright integration
│   ├── iframe_browser_server.py   # Browser server management
│   └── scheduler.py               # Task scheduling
│
├── pages/                   # Presentation Layer (Streamlit)
│   ├── dashboard.py        # Main dashboard with metrics
│   ├── job_search.py       # Job search interface
│   ├── resume_manager.py   # Resume upload and management
│   ├── applications.py     # Application tracking
│   ├── ai_agents.py        # Agent configuration and monitoring
│   ├── automation.py       # Automation workflow management
│   ├── notifications.py    # Email and notification settings
│   ├── company_management.py  # Company-specific configurations
│   └── settings.py         # User preferences and settings
│
└── utils/                   # Utility Layer
    ├── async_utils.py      # Async helpers and decorators
    ├── document_generator.py  # Document processing utilities
    ├── file_handler.py     # File I/O operations
    ├── logging_utils.py    # Structured logging configuration
    └── screenshot_generator.py  # Visual documentation tools
```

### Data Flow Architecture

**Request Flow:**
1. **Presentation Layer** (Streamlit pages) → User interactions and form submissions
2. **Service Layer** → Business logic orchestration and validation
3. **Repository Layer** → Data persistence and retrieval
4. **Agent Layer** → AI-powered processing and decision making
5. **Automation Layer** → Web automation and external system integration

**Agent Execution Pipeline:**
1. **Task Creation** → `AgentTask` with validation and metadata
2. **Context Injection** → `AgentContext` with user session and preferences
3. **Dependency Resolution** → Service container resolves agent dependencies
4. **AI Processing** → OpenAI integration with tool calling and response parsing
5. **Result Aggregation** → `AgentResult` with metrics and error handling

### Integration Patterns

**MCP (Model Context Protocol) Integration:**
- Playwright MCP Server for browser automation
- Gmail MCP Server for email notifications
- Structured tool calling with fallback mechanisms

**OpenAI Integration Layers:**
- **Configuration Layer** → API key management and model selection
- **Client Abstraction** → Protocol-based OpenAI client interface
- **Response Processing** → Multiple parsing strategies for different API responses
- **Tool Integration** → Web search, file search, and custom function calling

**Security Architecture:**
- **Credential Encryption** → AES-256 encryption for sensitive data
- **Input Validation** → Comprehensive sanitization and type checking
- **API Key Management** → Secure vault pattern with environment separation
- **Error Sanitization** → Removal of sensitive data from error messages

### State Management

**Application State:**
- **Session State** → Streamlit session management for user interactions
- **Agent Context** → Shared context across agent executions
- **Conversation State** → Agent-specific state preservation
- **Configuration State** → Runtime configuration and feature flags

**Database State:**
- **User Profiles** → Authentication and preference storage
- **Job Listings** → Search results and application tracking
- **Application History** → Automation workflow results and metrics
- **Agent Metrics** → Performance monitoring and analytics

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

**✅ Fully Working UI Pages:**
- ✅ Dashboard with professional metrics display and activity monitoring
- ✅ Resume Manager with functional file upload interface
- ✅ Job Search with filtering capabilities (UI complete)
- ✅ Application tracking with status monitoring interface
- ✅ Email notifications settings page (UI only)
- ✅ User preferences and job site configuration (UI only)
- ✅ Professional sidebar navigation with error handling and graceful fallbacks

**🚧 Backend Integration Status:**
- 🚧 All pages display sophisticated mock data and simulations
- 🚧 Database operations work for user profiles and basic data storage
- 🚧 No actual AI processing, job scraping, or automation execution
- 🚧 Real functionality needs to be implemented behind existing UI

## Critical Implementation Gaps

**🚨 Immediate Blockers:**
1. ~~**Import System Failures**: Systematic import path issues prevent agent initialization~~ (RESOLVED)
2. ⚠️ **Mock Implementation Overuse**: Some core functionality still uses simulations
3. ~~**Agent Execution Blocked**: Import errors prevent any agent from actually running~~ (RESOLVED)
4. ~~**Missing AI Integration**: OpenAI client configured but not connected to agent workflows~~ (RESOLVED)

**✅ Architecture Strengths (Already Implemented):**
- ✅ Service Container with full dependency injection
- ✅ Repository Pattern with proper abstractions
- ✅ Service Layer with clean business logic separation
- ✅ Professional configuration management system
- ✅ Comprehensive monitoring and error handling framework

**📋 Implementation Tasks Needed:**
1. ~~**Fix Import Paths**: Resolve systematic import issues to enable agent execution~~ (DONE)
2. ~~**Connect OpenAI Integration**: Link existing OpenAI configuration to agent workflows~~ (DONE)
3. ⚠️ **Implement Real Automation**: Replace remaining mock implementations with actual Playwright automation
4. ⚠️ **Add Email Integration**: Complete Gmail MCP server connection
5. ✅ **Enable AI Processing**: Implement resume optimization and cover letter generation (DONE, with real AI)

## Updated Implementation Roadmap

**REVISED STATUS**: Infrastructure complete, core features partially implemented - focus on full integration and testing

**Week 1: Fix Core Execution (CRITICAL)**
- ✅ Security framework: COMPLETE
- ✅ Architecture patterns: COMPLETE  
- ✅ **Fix import system**: Enable agent initialization and execution (DONE)
- ✅ **Connect OpenAI integration**: Link AI client to agent workflows (DONE)
- ⚠️ **Basic functionality test**: Get one complete automation workflow working (PARTIAL)

**Week 2: Implement Real Features (HIGH)**
- ⚠️ **Replace mock data**: Implement actual job search and application processing (PARTIAL)
- ⚠️ **Playwright automation**: Add real web form submission capabilities (PARTIAL)
- ✅ **AI processing**: Enable resume optimization and cover letter generation (DONE)
- ⚠️ **Email notifications**: Connect Gmail MCP server for real email sending (PARTIAL)

**Week 3: Integration & Testing (MEDIUM)**
- 🧪 **End-to-end testing**: Test complete automation workflows
- 🧪 **Error handling validation**: Test failure scenarios and recovery
- 🧪 **Performance optimization**: Optimize for real-world usage patterns
- 🧪 **User acceptance testing**: Validate UI matches backend functionality

**Updated Production Deployment Checklist:**

**✅ Infrastructure Complete:**
- [x] API keys moved to secure vault
- [x] Credential encryption implemented
- [x] Input validation on all endpoints
- [x] Dependency injection container
- [x] Repository pattern implemented
- [x] Health check endpoints
- [x] Monitoring and alerting framework

**⚠️ Core Functionality Needed:**
- [x] Agent import system fixed and working
- [x] OpenAI integration functionally connected
- [ ] At least one complete automation workflow working end-to-end
- [x] Real job search and application processing (replace mocks)
- [x] Playwright web automation implementation
- [ ] Gmail email notifications working
- [x] AI resume and cover letter generation

**🧪 Quality Assurance Needed:**
- [ ] Unit tests >80% coverage
- [ ] Integration tests for all workflows
- [ ] End-to-end automation testing
- [ ] Performance testing under realistic load

## Development Notes

**Latest Status Update (2024-10-01):**
- ✅ **Infrastructure Complete**: Excellent architecture, security, and frameworks in place
- ✅ **Import Issues Resolved**: Agents now initialize and execute properly
- ✅ **OpenAI Integrated**: Real AI responses used in agents where configured
- ⚠️ **Functionality Progress**: Core agents implemented, some automation still partial
- 📋 **Next Priority**: Complete end-to-end workflow and full testing
- 🎯 **Realistic Timeline**: 1-2 weeks to complete integration and testing
- 💪 **Project Strength**: Solid foundation with working AI agents ready for final polish


