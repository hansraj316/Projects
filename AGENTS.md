# Repository Guidelines

## Project Structure & Module Organization
- Root contains multiple projects: `InterviewAgent/`, `CoachAI/`, `ai_agent_project/`, `Project Starlink/`, `WikiRevamp/`, `ClaudeCode/`, `Azure DevOps MCP/`, `windsurf-demo/`.
- Python sources live either under `src/` (e.g., `CoachAI/src/`, `InterviewAgent/src/`) or the project root (e.g., `Project Starlink/app.py`).
- Tests: `ai_agent_project/tests/` (pytest). Add new tests alongside modules or under `<project>/tests/>`.
- Config/assets: `.env` files per project, YAML under `ai_agent_project/configs/` and `ai_agent_project/workflows/`.

## Build, Test, and Development Commands
- Python setup (per project):
  - `python3 -m venv venv && source venv/bin/activate`
  - `pip install -r <project>/requirements.txt`
- Run tests (pytest): `pytest -q` or `pytest --cov` in the target project.
- Run CoachAI (FastAPI): `python -m uvicorn CoachAI.src.main:app --reload`.
- Run Project Starlink (Flask): `python "Project Starlink/app.py"`.
- Node (ClaudeCode): `npm install && npm test` (no tests configured by default).

## Coding Style & Naming Conventions
- Python 3.8+: 4‑space indent; line length 88–100.
- Format/lint: `black .`, `isort .`, `flake8`, and type‑check with `mypy <package_or_src>`.
- Naming: snake_case for files/functions, PascalCase for classes, UPPER_CASE for constants. Tests named `test_*.py`.

## Testing Guidelines
- Framework: pytest (+ pytest‑cov). Prefer small, isolated unit tests.
- Place tests near code (`<project>/tests/`) and mirror module names.
- Run with coverage: `pytest --cov=<package_or_src> --cov-report=term-missing`.
- Update `TEST_RESULTS.md` when adding significant suites.

## Commit & Pull Request Guidelines
- Commits: imperative, concise, scoped (examples: `Refactor: adjust input handling`, `Enhance: dashboard styling`, `Fix: import path`).
- PRs: clear description, linked issues, steps to reproduce/verify, screenshots for UI, and passing tests/linters. Request review from relevant project owners.

## Security & Configuration Tips
- Never commit secrets. Use `.env`/`secrets.env` (see `CoachAI/.env.example`, `ai_agent_project/configs/secrets.env`).
- InterviewAgent requires `OPENAI_API_KEY`, `SUPABASE_URL`, etc.; load via `dotenv`. Validate config before running.
- Store logs/data under project‑scoped `logs/` and `data/` directories.
