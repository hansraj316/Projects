# Cursor Rules for CoachAI

> **Note:** The `.cursor_rules` YAML file (machine-readable) and this `CURSOR_RULES.md` (human-readable) must always be kept in sync. Any changes to one should be reflected in the other.

## YAML Rules Reference
```yaml
style: pep8, type hints
models:
  core: [o4-mini, o3]
  code: [gpt-4.1, code-davinci-002]
  chat: [gpt-3.5-turbo]
memory: 
  type: supabase
  vector_stores: openai
ui:
  web: 
    framework: streamlit
    theme: dark
  mobile: kivy
intents:
  - plan: core_agent
  - code: code_agent
  - explain: chat_agent
```

This document outlines the rules and guidelines for using Cursor in the CoachAI project. Agents and developers should refer to this file for consistent project practices.

## 1. Project Type
- The project is a **Python** application using Streamlit and FastAPI.

## 2. Cursor Configuration
- The main Cursor configuration is in `.cursor.json`.
- File patterns and language associations are defined there:
  - `**/*.py` → Python
  - `requirements.txt` → Text
  - `README.md` → Markdown
- The following are ignored by Cursor:
  - `__pycache__`, `.venv`, `.env`, `*.pyc`

## 3. File Naming and Structure
- All Python code should be in `.py` files.
- Dependencies go in `requirements.txt`.
- Project documentation should be in `README.md` and other markdown files in the `docs/` directory.
- UI components:
  - `ui/web/app.py` - Main Streamlit application
  - `ui/web/dashboard.py` - Dashboard component for learning tracking
  - `ui/web/theme.py` - Dark mode and UI theming utilities
  - `ui/web/utils.py` - Helper functions for the UI
- Backend components:
  - `src/config.py` - Application configuration
  - `src/storage.py` - Supabase integration for data persistence
  - `agents/planner.py` - Learning plan generation logic
  - `agents/stripe_agent.py` - Subscription handling
  - `agents/email_agent.py` - Email notifications

## 4. Best Practices for Agents
- Always refer to `.cursor.json` for file handling rules.
- Follow the structure and conventions outlined in this document.
- When adding new file types, update `.cursor.json` accordingly.
- Keep this rules file up to date with any changes to project conventions.
- Ensure `.cursor_rules` and `CURSOR_RULES.md` are always in sync.
- Maintain UI configuration in `theme.py` for consistent appearance.
- Store data persistence logic in `storage.py`.

## 5. Updating Rules
- If you add new file types or change project structure, update both `.cursor.json`, `.cursor_rules`, and this file.
- Communicate major changes to the team.

---

_Last updated: 2024-06-15_ 