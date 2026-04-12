# Projects Directory

[![Indian Avengers](https://img.shields.io/badge/Managed%20By-Indian%20Avengers-orange?style=flat-square&logo=gitbook)](https://github.com/hansraj316/mission-control-openclaw)

This directory contains software projects and experiments — AI agents, web apps, dev tools, and platform integrations.

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

#### **[InterviewAgent](https://github.com/hansraj316/InterviewAgent)**
Multi-agent pipeline for job applications — resume optimization, cover letters, auto-submission at 500+/day.
- **Tech Stack**: Python, Playwright, Supabase, Claude, MCP
- **Status**: Production

---

## 🧪 Experiments & Learning

#### **ai_agent_project**
Modular AI agent framework with planning, execution, and memory capabilities.
- **Tech Stack**: Python, YAML configurations

#### **ClaudeCode** / **ClaudeCode-v2**
Development tools and utilities for working with Claude AI.
- **Tech Stack**: Node.js

#### **Azure DevOps MCP**
Microsoft Cloud Platform integration tools.
- **Purpose**: DevOps automation and cloud integration

#### **windsurf-demo**
Demo project showcasing various development techniques.

---

## 📁 Project Structure

```
Projects/
├── agentdate/               # Agent discovery platform
├── agentmesh/               # Multi-agent visibility layer
├── mission-control-openclaw/ # Org command center
├── PMChat/                  # AI PM assistant
├── OllamaBar/               # macOS token tracker
├── InterviewAgent/          # Job automation (500+/day)
├── ai_agent_project/        # Agent framework experiments
├── ClaudeCode/              # Claude dev tools
├── Azure DevOps MCP/        # Azure integration
└── windsurf-demo/           # Demo project
```

## Getting Started

Each project contains its own README with setup instructions. Most Python projects use `venv/` for dependency isolation.

## Notes

- Sensitive config files (`.env`, `secrets.env`) are not in version control
- Agent activity is logged to `autonomy-log.jsonl` per workspace
- Monitor all active agents via [Mission Control](https://github.com/hansraj316/mission-control-openclaw)
