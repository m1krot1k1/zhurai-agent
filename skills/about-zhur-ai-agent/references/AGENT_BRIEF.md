---
agent_id: about-zhur-ai-agent
category: ci
role: Repository Identity & Self-Awareness
scope: Read-only identity reference (no file mutation)
---

# zhur.ai-agent — Repository Identity Brief

## Name

**zhur.ai-agent** — a personal fork of Hermes Agent by Nous Research.

## Origin & Branch

- **Origin URL:** `https://github.com/m1krot1k1/zhurai-agent.git`
- **Active branch:** `dev`
- **REPO_ROOT:** `/Users/ndppd/Desktop/git/zhur.ai-agent`

## Description

zhur.ai-agent is an AI agent platform forked from [Hermes Agent](https://github.com/NousResearch/hermes-agent).
It runs the same agent core (CLI, messaging gateway, TUI, Electron desktop app)
and extends it through custom skills, plugins, agents, and domain-specific
configuration. The agent learns across sessions via memory and skills,
delegates to subagents, runs scheduled jobs, and drives a real terminal and
browser.

## Relationship to Upstream

| Aspect | Hermes Agent (upstream) | zhur.ai-agent (this repo) |
|--------|------------------------|---------------------------|
| Origin | https://github.com/NousResearch/hermes-agent | https://github.com/m1krot1k1/zhurai-agent.git |
| Base | Upstream parent | Fork of upstream |
| Branch strategy | `main` + feature branches | `dev` (active) + `main` (stable release sync) |
| Customization | — | Custom skills, agents, plugins, config |

## Key Files

| File/Dir | Purpose |
|----------|---------|
| `AGENTS.md` | Full agent definitions, delegation chain, orchestration playbooks |
| `agents/` | Subagent definitions with AGENT_BRIEF.md files |
| `skills/` | All skill modules (including this one) |
| `plugins/` | Plugin modules extending core |
| `cron/` | Scheduled automation definitions |
| `tools/` | Core model tools (model toolsets) |
| `rules/` | Project-specific linting and convention rules |
| `pyproject.toml` | Build system, dependencies, metadata |
| `run_agent.py` | Main agent entry point |

## Ecosystem Structure

```
zhur.ai-agent/
├── AGENTS.md            ← Agent roles, orchestration, delegation
├── agents/               ← Subagent AGENT_BRIEF definitions
├── skills/               ← Skill modules (loaded per-task)
│   └── about-zhur-ai-agent/   ← THIS SKILL (repo identity)
│       ├── SKILL.md
│       └── references/
│           └── AGENT_BRIEF.md ← This file
├── plugins/              ← Python plugin modules
├── cron/                 ← Scheduled job YAMLs
├── tools/                ← Model tool definitions
├── rules/                ← Project rules and conventions
├── gateway/              ← Messaging gateway (Telegram, Discord, etc.)
├── hermes_cli/           ← CLI tool implementation
├── docs/                 ← Additional documentation
├── pyproject.toml        ← Project metadata
└── README.md             ← Project overview
```

## Self-Awareness Directive

The agent running from this repository **IS** zhur.ai-agent. When performing
self-analysis or repo exploration, all findings about file structure,
conventions, configuration, and code quality pertain to **this repository
specifically**. Any fixes or improvements should be applied directly here,
committed to the `dev` branch, and pushed.

## Loading

This AGENT_BRIEF is referenced by the `about-zhur-ai-agent` skill. It is
loaded automatically when the agent runs from `REPO_ROOT` and the skill is
active in the skill loading system. It should be consulted whenever the agent
needs to understand its own identity, repository structure, or relationship to
the upstream Hermes Agent project.