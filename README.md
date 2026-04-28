# Projects

[![Indian Avengers](https://img.shields.io/badge/Managed%20By-Indian%20Avengers-orange?style=flat-square&logo=gitbook)](https://github.com/hansraj316/mission-control-openclaw)

Index of personal software projects and experiments — AI agents, web apps, dev tools, and platform integrations. Each project now lives in its own repo; this README is the map.

## 🚀 Active Projects (2024–Present)

### AI Agents & Platforms

#### **[AgentDate](https://github.com/hansraj316/agentdate)**
AI agents register and discover each other — a social graph for the agentic web.
- **Tech Stack**: Next.js, Vercel, TypeScript, AI Agents
- **Status**: Shipping

#### **[AgentMesh](https://github.com/hansraj316/agentmesh)**
Real-time visibility and coordination layer for multi-agent AI systems.
- **Tech Stack**: OpenClaw, Python, SQLite, WebSocket
- **Status**: Active

#### **[Mission Control](https://github.com/hansraj316/mission-control-openclaw)**
Real-time dashboard for the Indian Avengers AI org — 25+ agents, cron jobs, security telemetry, GitHub activity.
- **Tech Stack**: Python, Chart.js, OpenClaw
- **Status**: Active

#### **[PMChat](https://github.com/hansraj316/PMChat)**
AI-powered PM assistant — turns scattered requirements into structured product specs.
- **Tech Stack**: Claude, Next.js, TypeScript
- **Status**: Active

#### **[OllamaBar](https://github.com/hansraj316/OllamaBar)**
macOS menu bar app for token tracking, budget enforcement, and local LLM monitoring.
- **Tech Stack**: Swift, macOS, Ollama
- **Status**: Production

#### **[InterviewAgent](https://github.com/hansraj316/InterviewAgent)** (showcase)
Public-facing project home: polished README, daily `features/` and `quality/` delivery journal.
- **Tech Stack**: docs-only — source lives in the implementation repo below
- **Status**: Production

#### **[interview-agent](https://github.com/hansraj316/interview-agent)** (implementation)
Multi-agent pipeline for job applications — resume optimization, cover letters, auto-submission at 500+/day.
- **Tech Stack**: Python, Streamlit, Playwright, Supabase, Claude, MCP
- **Status**: Production

#### **[coach-ai](https://github.com/hansraj316/coach-ai)**
AI coaching platform with web and iOS apps — learning plans, progress tracking, subscription management.
- **Tech Stack**: Python, Flask (web), Swift (iOS), Kivy (mobile)
- **Status**: Active

#### **[ai-agent-project](https://github.com/hansraj316/ai-agent-project)**
Modular agent framework with planning, execution, and memory (Python, YAML workflows).
- **Tech Stack**: Python, YAML
- **Status**: Experimental

#### **[EdgeShield](https://github.com/hansraj316/enterprise-edge-security-hub)**
Enterprise edge security platform for Indian mid-market — real-time threat detection, AI anomaly detection, edge computing security dashboard.
- **Tech Stack**: Next.js 15, TypeScript, Tailwind CSS, Framer Motion
- **Status**: Active

#### **[PhishShield Drill Engine](https://github.com/hansraj316/phishshield-drill-engine)**
AI-powered phishing simulation and instant coaching MVP for SMB teams.
- **Tech Stack**: Node.js, Express
- **Status**: MVP

---

## 📚 Notes

- This repo used to be a monorepo with each project as a subfolder. In 2026-04 the three substantive projects (`CoachAI`, `InterviewAgent`, `ai_agent_project`) were extracted into their own repos via `git subtree split` with history preserved. Several exploratory stubs (`ClaudeCode`, `ClaudeCode-v2`, `WikiRevamp`, `windsurf-demo`, `Project Starlink`, `Azure DevOps MCP`, `Ghostty`) were removed.
- Some of the linked repos are private — links will 404 for anyone without access.
- Sensitive config files (`.env`, `secrets.env`) are not in version control.
- Agent activity is logged to `autonomy-log.jsonl` per workspace.
- Monitor all active agents via [Mission Control](https://github.com/hansraj316/mission-control-openclaw).

## License

[MIT](LICENSE) — see also [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md).


## Daily TPM delivery update (2026-04-22)
- Functional: Add project health scorecards with milestone progress, blockers, and confidence levels
- Non-functional: Add integration tests for project CRUD and permissions with CI gating


## Daily delivery update (2026-04-28)
- Functional: Add project dependency graph view with critical path highlighting
- Non-functional: Optimize project list query performance with indexed filters
