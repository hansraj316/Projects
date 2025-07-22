# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InterviewAgent is an AI-powered job application automation system built with Python, Streamlit, and OpenAI SDK. The system helps job candidates automatically apply to positions using AI agents for resume optimization, cover letter generation, and web automation.

## Development Commands

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for automation)
playwright install

# Quick Start (Recommended)
python3 run_app.py

# Manual Streamlit start
streamlit run streamlit_app.py

# Run component tests
python3 test_app.py

# Database migration (manual execution in Supabase)
# Use src/database/migrations.sql in Supabase SQL editor

# Format code (when available)
black src/
flake8 src/
```

## Architecture Overview

### Agent System
- **Main Orchestrator**: Coordinates all automation workflows with intelligent data flow
- **Job Discovery Agent**: AI-powered job search, analysis, and market research
- **Resume Optimization Agent**: AI-powered resume customization with industry research
- **Cover Letter Agent**: Generates personalized cover letters with company research
- **Application Submission Agent**: Automates form filling and submission using Playwright MCP
- **Email Notification Agent**: Sends updates via Gmail MCP with workflow coordination

### Technology Stack
- Frontend: Streamlit (Python web framework)
- Backend: Python with integrated Streamlit app
- Database: Supabase (PostgreSQL + Storage)
- AI: OpenAI Python SDK with function calling and MCP integration
- Automation: Playwright MCP Server for web automation
- Email: Gmail MCP Server for email notifications
- Scheduling: APScheduler for recurring automation
- MCP Integration: Playwright and Gmail MCP servers

### Key Directories
- `/src/agents/` - AI agent implementations
- `/src/database/` - Supabase database operations and models
- `/src/pages/` - Streamlit page components
- `/src/utils/` - Utility functions and helpers
- `/docs/` - Project documentation and progress tracking
- `/tests/` - Test suites
- `/data/` - Local data storage
- `/templates/` - Default templates

## Important Development Notes

### Current Status - PRODUCTION READY ✅
**Complete automation system implemented successfully (2025-07-18)**
- ✅ **Phase 1**: Working Streamlit application with full navigation
- ✅ **Phase 2**: Complete AI agent framework with OpenAI integration
- ✅ **Phase 4**: Full automation system with MCP server integration
- ✅ End-to-end job application automation workflow
- ✅ Playwright automation for web form submission
- ✅ Gmail integration for email notifications
- ✅ APScheduler for recurring automation
- ✅ Comprehensive automation control panel

### Single-User MVP
- This is a single-user application for MVP
- No authentication system initially
- User configuration in environment variables
- Database operations assume single user context

### Getting Started
1. **Quick Start**: Run `python3 run_app.py` 
2. **Manual Start**: Run `streamlit run streamlit_app.py`
3. **Testing**: Run `python3 test_app.py` to verify components
4. **App Access**: Open http://localhost:8501

### Progress Tracking
- All major tasks are tracked in `docs/TASKS.md`
- Project plan is maintained in `docs/project-plan.md`
- Update progress files when completing milestones
- **Phase 1 completed** - ready for agent development

### Configuration Management
- Environment variables in `.env` file (copy from `.env.example`)
- Configuration class in `src/config.py`
- Job site configurations in config
- User preferences stored in database

### Database Operations
- Models defined in `src/database/models.py`
- Operations in `src/database/operations.py`
- Connection management in `src/database/connection.py`
- Migration SQL in `src/database/migrations.sql`
- **Mock mode** available for development without real Supabase

### Streamlit Development
- Main app in `streamlit_app.py`
- Page components in `src/pages/`
- Use `st.session_state` for state management
- Cache database connections with `@st.cache_resource`
- Full navigation between Dashboard, Resume Manager, Job Search, Applications, Notifications, Settings

### Agent Development Guidelines
- Base agent class in `src/agents/base_agent.py`
- Each agent should inherit from BaseAgent
- Implement comprehensive error handling
- Log all agent activities for debugging
- Use structured data for agent communication
- **Use the Responses API while creating agents**

### Security Considerations
- Encrypt job site credentials before storage
- Use environment variables for all API keys
- Implement rate limiting for web scraping
- Secure session management in Streamlit

## Testing Strategy
- Unit tests for agent logic with pytest
- Integration tests for database operations
- End-to-end tests for complete workflows
- Playwright tests for web automation scenarios

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

## Development Memories
- Make sure every step is updated in the blog-content.md