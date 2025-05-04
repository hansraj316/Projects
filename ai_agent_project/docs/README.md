# AI Agent System

A modular and extensible AI agent system that can plan, execute, and learn from tasks using various tools and APIs.

## Project Structure

```
ai_agent_project/
├── agents/              # Agent components
│   ├── planner.py      # Task planning and decomposition
│   ├── executor.py     # Plan execution and monitoring
│   └── memory.py       # Context and history management
├── tools/              # Tool implementations
│   ├── web_search.py   # Web search functionality
│   ├── file_manager.py # File operations
│   └── api_connector.py # API interaction
├── workflows/          # Workflow definitions
│   ├── task_flow.yaml  # Default task workflow
│   └── decision_tree.yaml # Decision making rules
├── configs/           # Configuration files
│   ├── settings.yaml  # General settings
│   └── secrets.env    # Environment secrets
├── tests/            # Test suite
│   ├── test_agents.py # Agent tests
│   └── test_tools.py  # Tool tests
├── docs/             # Documentation
└── main.py          # Main entry point
```

## Features

- Modular agent architecture with separate planning, execution, and memory components
- Extensible tool system for web search, file operations, and API interactions
- Configuration-driven workflow management
- Comprehensive test suite
- Logging and error handling
- Memory management for context retention

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai_agent_project.git
   cd ai_agent_project
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp configs/secrets.env.example configs/secrets.env
   # Edit configs/secrets.env with your API keys and settings
   ```

## Usage

Basic usage example:

```python
from main import AIAgentSystem

# Initialize the system
agent_system = AIAgentSystem()

# Process a task
result = agent_system.process_task("Search for information about AI agents")

# Check results
if result["status"] == "success":
    print(f"Task completed successfully: {result['results']}")
else:
    print(f"Error processing task: {result['error']}")
```

## Development

1. Run tests:
   ```bash
   pytest tests/
   ```

2. Check code style:
   ```bash
   black .
   isort .
   flake8
   mypy .
   ```

3. Generate test coverage:
   ```bash
   pytest --cov=./ tests/
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 