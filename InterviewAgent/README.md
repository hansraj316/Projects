# InterviewAgent 🤖

** AI-Powered Job Application Automation System**

An intelligent automation system that helps job candidates streamline their application process using AI agents for resume optimization, cover letter generation, and automated job application submission.

## ✨ Key Features

- 🤖 **AI-Powered Automation**: Resume optimization and cover letter generation
- 🔍 **Intelligent Job Discovery**: Automated job search across multiple platforms
- 🔒 **Enterprise Security**: Encrypted credentials and secure configuration
- 📊 **Application Tracking**: Monitor job application status and success rates
- 🎯 **Personalization**: Tailored applications for each job opportunity

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ and `pip`
- OpenAI API key
- Supabase account (for database)

### Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install browser automation (if needed)
playwright install

# Configure environment
cp .env.example .env  # Edit with your credentials
```

### Configuration
Required environment variables in `.env`:
```bash
# Database
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Security
INTERVIEW_AGENT_MASTER_KEY=your_secure_master_key
INTERVIEW_AGENT_SALT=your_unique_salt
```

### Running the Application
```bash
# Start the Streamlit application
python run_app.py

# Or run directly
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501` to access the application.

## 🏗️ Architecture

### Core Components
- **AI Agents**: JobDiscoveryAgent, ResumeOptimizerAgent, CoverLetterAgent
- **Web Automation**: Playwright-based form submission
- **Security Framework**: Encrypted credential storage and input validation
- **Database Layer**: Supabase integration with repository pattern

### Project Structure
```
InterviewAgent/
├── src/
│   ├── agents/          # AI agent implementations
│   ├── core/           # Core framework and dependency injection
│   ├── database/       # Database models and operations
│   ├── pages/          # Streamlit UI components
│   └── services/       # Business logic layer
├── tests/              # Test suites
└── scripts/           # Utility scripts
```

## 🔧 Usage

1. **Upload Resume**: Upload your base resume in PDF/Word format
2. **Configure Preferences**: Set job search criteria and preferences  
3. **Discover Jobs**: AI discovers and filters relevant positions
4. **Optimize Applications**: AI customizes resume and generates cover letters
5. **Submit Applications**: Automated submission with tracking
6. **Monitor Progress**: Real-time dashboard with analytics

## 🧪 Testing

Run the test suite:
```bash
# All tests
python -m pytest tests/ -v

# Specific test categories
python -m pytest tests/test_agents.py      # AI agent tests
python -m pytest tests/test_database.py    # Database tests

# Integration tests
python tests/test_complete_workflow.py
```

## 🔒 Security

- **Encrypted Credentials**: All API keys encrypted at rest
- **Input Validation**: Comprehensive XSS and injection prevention
- **Secure Configuration**: Environment-based configuration
- **Error Sanitization**: Sensitive data removed from error messages

## 📊 Monitoring

- Agent health monitoring and metrics
- Application success rates tracking
- System performance indicators
- Structured logging with JSON format

## 🚀 Development

### Development Setup
```bash
# Load configuration
from InterviewAgent.src.config import get_config
cfg = get_config()

# Run in development mode
DEBUG=true python run_app.py
```

### Architecture Patterns
- **Dependency Injection**: Service container pattern
- **Repository Pattern**: Data access abstraction
- **Agent Framework**: Standardized AI agent implementation
- **Security-First Design**: Comprehensive validation and encryption

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Follow security best practices
5. Submit a pull request

---



