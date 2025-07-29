# InterviewAgent 🤖

**AI-Powered Job Application Automation System**

An intelligent, production-ready automation system that helps job candidates streamline their application process using AI agents for resume optimization, cover letter generation, and automated job application submission.

## ✨ Features

### 🤖 **AI-Powered Automation**
- **Resume Optimization**: AI-driven resume customization for each application
- **Cover Letter Generation**: Personalized cover letters based on job requirements
- **Job Discovery**: Intelligent job search across multiple platforms
- **Application Submission**: Automated form filling and submission

### 🔒 **Enterprise Security**
- **Encrypted Credentials**: All API keys encrypted at rest with master key derivation
- **Input Validation**: Comprehensive validation preventing XSS and injection attacks
- **Secure Configuration**: Environment-based config with validation

### 🏗️ **Production Architecture**
- **Dependency Injection**: Clean IoC container with multiple lifetime scopes
- **Error Handling**: Circuit breakers, retry mechanisms, and structured logging
- **Health Monitoring**: Real-time agent health checks and metrics
- **Service Layer**: Clean separation of business logic and data access

### 📊 **Modern UI**
- **Streamlit Interface**: Clean, responsive web interface
- **Real-time Status**: Live updates on automation progress
- **Analytics Dashboard**: Application tracking and success metrics
- **Agent Management**: Monitor and control AI agents

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- Supabase account (for database)
- OpenAI API key
- Git

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/InterviewAgent.git
   cd InterviewAgent
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (for automation)
   ```bash
   playwright install
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

6. **Initialize database**
   ```bash
   python scripts/setup_database.py
   ```

7. **Start the application**
   ```bash
   # Quick start (recommended)
   python run_app.py
   
   # Or manual start
   streamlit run streamlit_app.py
   ```

8. **Open your browser**
   ```
   http://localhost:8501
   ```

## ⚙️ Configuration

### **Required Environment Variables**
```bash
# Database
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Security (Production)
INTERVIEW_AGENT_MASTER_KEY=your_secure_master_key
INTERVIEW_AGENT_SALT=your_unique_salt
```

### **Optional Configuration**
```bash
# Application
APP_NAME=InterviewAgent
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# OpenAI Settings
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4000

# Email (Optional)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# User Settings (Single-user MVP)
USER_NAME=Your Name
USER_EMAIL=your_email@example.com
```

## 🏗️ Architecture

### **Directory Structure**
```
InterviewAgent/
├── src/                    # Source code
│   ├── core/              # ⭐ Production framework
│   ├── agents/            # 🤖 AI agents
│   ├── services/          # 💼 Business logic
│   ├── repositories/      # 🏗️ Data access
│   ├── pages/             # 🎨 UI components
│   └── utils/             # 🛠️ Utilities
├── tests/                 # Test suites
├── scripts/               # Utility scripts
├── config/                # Configuration files
├── data/                  # Data storage
└── docs/                  # Documentation
```

### **Core Components**

#### **🤖 AI Agents**
- **JobDiscoveryAgent**: Searches and analyzes job postings
- **ResumeOptimizerAgent**: Customizes resumes for specific jobs
- **CoverLetterAgent**: Generates personalized cover letters
- **ApplicationSubmitterAgent**: Automates form submission
- **EmailNotificationAgent**: Sends updates and notifications

#### **🔒 Security Framework**
- **Credential Manager**: Encrypted storage with key derivation
- **Input Validator**: XSS and injection prevention
- **API Key Manager**: Format validation and rotation

#### **⚡ Production Features**
- **Circuit Breakers**: Automatic failure protection
- **Health Monitoring**: Real-time system status
- **Structured Logging**: JSON logs with full context
- **Metrics Collection**: Performance monitoring

## 🔧 Usage

### **Basic Workflow**

1. **Upload Resume**: Upload your base resume in PDF/Word format
2. **Configure Preferences**: Set job search criteria and preferences
3. **Discover Jobs**: AI discovers and filters relevant positions
4. **Optimize Applications**: AI customizes resume and generates cover letters
5. **Submit Applications**: Automated submission with tracking
6. **Monitor Progress**: Real-time dashboard with analytics

### **Advanced Features**

#### **Automation Scheduling**
```python
# Schedule daily job searches
automation_config = {
    "enabled": True,
    "schedule": "09:00",  # Run at 9 AM daily
    "max_applications": 10,
    "keywords": ["python", "senior", "remote"]
}
```

#### **Custom AI Prompts**
Customize AI behavior for resume optimization and cover letter generation.

#### **Integration APIs**
Connect with external job boards, ATS systems, and notification services.

## 🧪 Testing

### **Run Tests**
```bash
# All tests
python -m pytest tests/

# Specific test categories
python -m pytest tests/test_agents.py      # AI agent tests
python -m pytest tests/test_database.py    # Database tests
python -m pytest tests/test_automation.py  # Automation tests

# Integration tests
python tests/test_complete_workflow.py
```

### **Manual Testing**
```bash
# Component tests
python tests/test_app.py

# Database connectivity
python tests/test_supabase.py

# Agent functionality
python tests/test_openai_agents.py
```

## 📊 Monitoring

### **Health Checks**
- Agent health monitoring at `/health`
- Database connectivity status
- API service availability
- System resource usage

### **Logging**
- Structured JSON logs in `logs/`
- Error tracking with context
- Performance metrics
- User activity logs

### **Metrics**
- Application success rates
- Agent performance metrics
- System health indicators
- User engagement analytics

## 🚀 Deployment

### **Development Mode**
```bash
DEBUG=true python run_app.py
```

### **Production Mode**
```bash
ENVIRONMENT=production python run_app.py
```

### **Docker Deployment**
```bash
# Build image
docker build -t interview-agent .

# Run container
docker run -p 8501:8501 interview-agent
```

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Follow the coding standards
4. Add tests for new features
5. Submit a pull request

### **Code Standards**
- Python 3.8+ with type hints
- Black formatting
- Comprehensive error handling
- Unit test coverage > 80%
- Security-first design

## 📚 Documentation

- **[Project Structure](PROJECT_STRUCTURE.md)**: Detailed architecture guide
- **[API Documentation](docs/api.md)**: Service interfaces and protocols
- **[Development Guide](docs/development.md)**: Contributing guidelines
- **[Security Guide](docs/security.md)**: Security features and best practices

## 🐛 Troubleshooting

### **Common Issues**

#### **Playwright Installation**
```bash
# If browser installation fails
playwright install --with-deps
```

#### **Database Connection**
```bash
# Test database connectivity
python scripts/test_database.py
```

#### **Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### **Debug Mode**
```bash
# Enable detailed logging
DEBUG=true LOG_LEVEL=DEBUG python run_app.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: For GPT models powering the AI agents
- **Supabase**: For the database infrastructure
- **Streamlit**: For the web interface framework
- **Playwright**: For web automation capabilities

## 📞 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

**Built with ❤️ for job seekers everywhere**