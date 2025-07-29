# InterviewAgent - Project Structure

**Version**: 1.0.0 (Production Ready)  
**Architecture**: Clean, modular, production-ready with dependency injection  
**Security**: Enterprise-grade with encrypted credentials and input validation

## 📁 Directory Structure

```
InterviewAgent/
├── 📋 Project Configuration
│   ├── CLAUDE.md                    # AI development guidelines
│   ├── README.md                    # Project overview
│   ├── requirements.txt             # Python dependencies
│   └── final_migrations.sql         # Database setup
│
├── 🏃 Application Entry Points
│   ├── run_app.py                   # Quick start launcher
│   └── streamlit_app.py             # Main Streamlit application
│
├── 📁 config/                       # Configuration files
│   └── mcp_agent.config.yaml       # MCP agent configuration
│
├── 📁 scripts/                      # Utility scripts
│   ├── setup_database.py           # Database initialization
│   └── show_screenshot_locations.py # Debug utilities
│
├── 📁 tests/                        # Test suites
│   ├── test_app.py                  # Application tests
│   ├── test_supabase.py            # Database tests
│   ├── test_automation_workflow.py  # Automation tests
│   ├── test_openai_agents.py       # AI agent tests
│   └── test_complete_mcp_workflow.py # Integration tests
│
├── 📁 data/                         # Data storage (not source code)
│   ├── resumes/                     # Resume files
│   ├── screenshots/                 # Automation screenshots
│   └── test_screenshots/           # Test artifacts
│
├── 📁 docs/                         # Documentation
│   ├── TASKS.md                     # Development tasks
│   ├── blog-content.md              # Development blog
│   └── project-plan.md              # Project roadmap
│
├── 📁 logs/                         # Application logs
│   └── interview_agent_*.log       # Daily log files
│
├── 📁 templates/                    # Document templates
│   └── (resume templates, etc.)
│
└── 📁 src/                          # SOURCE CODE
    ├── 🔧 Core Framework (Production-Ready)
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── bootstrap.py         # ⭐ Application initialization
    │   │   ├── container.py         # ⭐ Dependency injection
    │   │   ├── security.py          # ⭐ Secure credential management
    │   │   ├── validation.py        # ⭐ Input validation
    │   │   ├── error_handler.py     # ⭐ Centralized error handling
    │   │   ├── exceptions.py        # ⭐ Custom exception hierarchy
    │   │   └── protocols.py         # ⭐ Service interfaces
    │   │
    │   ├── config.py               # ⭐ Configuration management
    │   └── __init__.py             # ⭐ Package entry point
    │
    ├── 🤖 AI Agents (Intelligent Automation)
    │   ├── agents/
    │   │   ├── __init__.py
    │   │   ├── base_agent.py            # ⭐ Agent framework
    │   │   ├── agent_manager.py         # ⭐ Agent orchestration
    │   │   ├── enhanced_orchestrator.py # Workflow coordinator
    │   │   ├── job_discovery.py         # Job search AI
    │   │   ├── resume_optimizer.py      # Resume optimization AI
    │   │   ├── cover_letter_generator.py # Cover letter AI
    │   │   ├── application_submitter.py # Form automation
    │   │   ├── email_notification.py    # Email automation
    │   │   ├── simple_automation_controller.py # Legacy controller
    │   │   └── real_mcp_playwright_agent.py # MCP integration
    │
    ├── 🏗️ Data Layer (Repository Pattern)
    │   ├── repositories/
    │   │   ├── __init__.py
    │   │   ├── interfaces.py        # ⭐ Repository contracts
    │   │   └── supabase_repositories.py # ⭐ Database implementations
    │   │
    │   └── database/
    │       ├── __init__.py
    │       ├── models.py            # Data models
    │       ├── operations.py        # Database operations
    │       ├── connection.py        # Database connections
    │       ├── migrations.sql       # Schema definitions
    │       └── agent_migrations.sql # Agent-specific schema
    │
    ├── 💼 Business Logic (Service Layer)
    │   ├── services/
    │   │   ├── __init__.py
    │   │   └── job_service.py       # ⭐ Job management business logic
    │
    ├── 🎨 User Interface (Streamlit Pages)
    │   ├── pages/
    │   │   ├── __init__.py
    │   │   ├── dashboard.py         # Main dashboard
    │   │   ├── job_search.py        # Job search interface
    │   │   ├── applications.py      # Application tracking
    │   │   ├── resume_manager.py    # Resume management
    │   │   ├── company_management.py # Company database
    │   │   ├── automation.py        # Automation controls
    │   │   ├── ai_agents.py         # Agent management
    │   │   ├── notifications.py     # Notification center
    │   │   └── settings.py          # Configuration
    │
    ├── 🔧 Automation Engine
    │   ├── automation/
    │   │   ├── __init__.py
    │   │   ├── scheduler.py         # Job scheduling
    │   │   ├── real_mcp_implementation.py # MCP automation
    │   │   └── iframe_browser_server.py   # Browser automation
    │
    └── 🛠️ Utilities
        └── utils/
            ├── __init__.py
            ├── async_utils.py       # Async helpers
            ├── file_handler.py      # File operations
            ├── logging_utils.py     # Logging utilities
            ├── document_generator.py # Document creation
            └── screenshot_generator.py # Screenshot utilities
```

## 🏗️ Architecture Overview

### **Production-Ready Core Framework** ⭐
The `src/core/` directory contains enterprise-grade components:

- **Dependency Injection**: Full IoC container with singleton, transient, and scoped lifetimes
- **Security Layer**: Encrypted credential storage with master key derivation
- **Input Validation**: Comprehensive validation for all user inputs and system data
- **Error Handling**: Circuit breakers, retry mechanisms, and structured error responses
- **Service Protocols**: Clean interfaces for all system components

### **AI Agent Architecture** 🤖
The `src/agents/` directory implements a sophisticated agent system:

- **BaseAgent**: Production-ready agent framework with dependency injection
- **Agent Manager**: Health monitoring, circuit breakers, and orchestration
- **Specialized Agents**: Each agent handles specific automation tasks
- **Error Recovery**: Automatic retry and fallback mechanisms

### **Data Architecture** 🏗️
Clean separation between data access and business logic:

- **Repository Pattern**: Interfaces in `repositories/interfaces.py`
- **Concrete Implementations**: Supabase implementations with error handling
- **Service Layer**: Business logic in `services/` with validation and metrics

### **Modern UI Architecture** 🎨
Streamlit-based interface with clean separation:

- **Page Components**: Each page is a self-contained module
- **State Management**: Proper session state handling
- **Error Boundaries**: Graceful error handling in UI

## 🔐 Security Features

### **Credential Management**
- **Encrypted Storage**: All API keys encrypted at rest
- **Master Key Derivation**: PBKDF2 with 100,000 iterations
- **Key Validation**: Format validation for all API keys
- **Secure Defaults**: Automatic fallback to mock mode in development

### **Input Validation**
- **XSS Prevention**: All user inputs sanitized
- **SQL Injection Protection**: Parameterized queries throughout
- **File Upload Security**: Type and size validation
- **API Parameter Validation**: Comprehensive schema validation

## 📊 Production Features

### **Error Handling & Reliability**
- **Circuit Breakers**: Automatic failure protection
- **Retry Mechanisms**: Exponential backoff for transient failures
- **Structured Logging**: JSON-formatted logs with context
- **Health Monitoring**: Real-time system health checks

### **Performance & Scalability**
- **Connection Pooling**: Database connection management
- **Async Operations**: Non-blocking I/O throughout
- **Caching**: Response caching where appropriate
- **Metrics Collection**: Performance monitoring and alerting

### **Development & Testing**
- **Mock Implementations**: Full mock mode for development
- **Comprehensive Testing**: Unit, integration, and end-to-end tests
- **Type Safety**: Full type hints throughout codebase
- **Code Quality**: Linting, formatting, and validation

## 🚀 Quick Start

### **Development Mode**
```bash
# Install dependencies
pip install -r requirements.txt

# Quick start with mock mode
python run_app.py

# Or manual start
streamlit run streamlit_app.py
```

### **Production Setup**
```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python scripts/setup_database.py

# Run with production config
ENVIRONMENT=production python run_app.py
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key

# Security (Production)
INTERVIEW_AGENT_MASTER_KEY=your_master_key
INTERVIEW_AGENT_SALT=your_salt

# Optional
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### **Feature Flags**
- **Mock Mode**: Automatically enabled when credentials are missing
- **Debug Mode**: Enhanced logging and error details
- **Security Validation**: Automatic credential format validation

## 📈 Migration from Legacy

The codebase has been completely restructured for production readiness:

### **Removed Legacy Components**
- ❌ Old service files with inconsistent patterns
- ❌ Development artifacts and temporary files
- ❌ sys.path manipulations and path hacks
- ❌ Hardcoded configurations and insecure practices

### **New Production Architecture**
- ✅ Clean dependency injection throughout
- ✅ Proper relative imports and module structure
- ✅ Comprehensive error handling and validation
- ✅ Security-first design with encrypted storage
- ✅ Professional logging and monitoring

## 🎯 Usage Patterns

### **Application Initialization**
```python
from src import create_application, initialize_application

# Create application with all dependencies
app_components = create_application()

# Initialize all components
await initialize_application(app_components)

# Access components
agent_manager = app_components["agent_manager"]
job_service = app_components["job_service"]
```

### **Agent Usage**
```python
# Get agent with health check
agent = agent_manager.get_agent("job_discovery")

# Execute task with error handling
result = await agent_manager.execute_agent_task(
    "job_discovery", 
    task, 
    context
)
```

### **Service Usage**
```python
from src.services.job_service import JobService, JobSearchCriteria

# Search jobs with validation
criteria = JobSearchCriteria(keywords=["python", "senior"])
results = await job_service.search_jobs(criteria, user_id)
```

This structure provides a solid foundation for enterprise-level job application automation with proper security, error handling, and scalability considerations.