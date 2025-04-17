# CoachAI

A modular AI-learning assistant with multi-agent orchestration.

## Features
- FastAPI backend
- OpenAI Vector Stores for memory
- Streamlit web interface
- Kivy mobile interface
- Multi-agent system with MCP

## Project Structure
```
/project-root
├── src/              # Core application code
│   └── main.py      # FastAPI entry point
├── agents/          # MCP sub-agent implementations
├── config/         # Configuration files
│   ├── .cursor.json     # Cursor project config
│   ├── .cursor_rules    # Machine-readable rules
│   └── requirements.txt # Python dependencies
├── docs/           # Documentation
│   ├── README.md        # Project overview (this file)
│   ├── CURSOR_RULES.md  # Development guidelines
│   ├── project.md       # Project vision and goals
│   └── workflow_state.md # Onboarding progress
├── ui/
│   ├── web/        # Streamlit app files
│   └── mobile/     # Kivy app files
├── memory/         # Vector store and memory utils
└── .github/        # CI/CD workflows
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r config/requirements.txt
   ```

2. Run the app:
   ```bash
   uvicorn src.main:app --reload
   ```

## Development
Please refer to `docs/CURSOR_RULES.md` for development guidelines and conventions.

## Documentation
- Project Vision & Goals: `docs/project.md`
- Development Guidelines: `docs/CURSOR_RULES.md`
- Onboarding Progress: `docs/workflow_state.md` 