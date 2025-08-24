# CoachAI Learning Platform

A modular AI-powered learning assistant that creates personalized learning plans using OpenAI's GPT API. Built with FastAPI for modern web API development.

## Features

- 🎯 **Personalized Learning Plans**: AI-generated study plans tailored to your goals
- 🤖 **OpenAI Integration**: Powered by GPT models for intelligent content generation
- ⚡ **FastAPI Backend**: Modern async Python web framework
- 📊 **Progress Tracking**: Monitor your learning journey
- 🔧 **Configurable**: Environment-based configuration management

## Quick Start

### Prerequisites
- Python 3.10+ recommended
- OpenAI API key

### Installation
```bash
# Clone and setup environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Edit with your OpenAI API key
```

### Running the Application
```bash
# Development server
python -m uvicorn CoachAI.src.main:app --reload

# Production server
python -m uvicorn CoachAI.src.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

## Configuration

Environment variables (`.env` file):
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DEBUG`: Enable debug mode (default: False)
- `HOST`: Server host (default: localhost)
- `PORT`: Server port (default: 8000)

Configuration is managed in `src/config.py`.

## Project Structure

```
CoachAI/
├── src/
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Environment and settings management
│   ├── agents/          # AI learning plan generation logic
│   └── api/             # API endpoints and routes
├── tests/               # Test suites
├── docs/               # Documentation
└── requirements.txt    # Python dependencies
```

## API Endpoints

- `GET /`: Health check and API information
- `POST /learning-plan`: Generate personalized learning plan
- `GET /health`: System health status

## Testing

Run tests with pytest:
```bash
pytest tests/ -v
pytest tests/ --cov=src  # With coverage
```

## Development

### Adding New Features
1. Create feature branch
2. Add tests for new functionality
3. Update documentation
4. Submit pull request

### Code Quality
- Use type hints
- Follow PEP 8 style guidelines
- Maintain test coverage > 80%

## License

MIT License - see LICENSE file for details.

