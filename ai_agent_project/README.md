# AI Agent Project

A modular agent framework with planning, execution, and memory.

## Structure
- `agents/`: `planner.py`, `executor.py`, `memory.py`.
- `tools/`: pluggable utilities (e.g., `web_search.py`).
- `workflows/`: YAML workflows (e.g., `task_flow.yaml`).
- `configs/`: settings and secrets.
- `tests/`: pytest suites for agents and tools.

## Setup
- `python3 -m venv venv && source venv/bin/activate`
- `pip install -r ai_agent_project/requirements.txt`

## Run & Test
- Run entrypoint: `python ai_agent_project/main.py`
- Tests: `pytest -q ai_agent_project` or with coverage: `pytest --cov=ai_agent_project --cov-report=term-missing`

## Style
- Format: `black ai_agent_project && isort --profile black ai_agent_project`
- Lint: `flake8 ai_agent_project`
- Types: `mypy ai_agent_project`

