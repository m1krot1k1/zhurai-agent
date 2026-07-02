---
name: about-zhur-ai-agent
category: ci
description: >
  Repository identity skill for zhur.ai-agent.
  Provides self-awareness so the agent knows which repo it runs from,
  its origin, active branch, and relationship to the upstream Hermes Agent.
---

# About zhur.ai-agent

This skill tells the agent its own repository identity. It is loaded when the
agent is running from the zhur.ai-agent repository.

## Repository Identity

| Field          | Value                                          |
|----------------|------------------------------------------------|
| **Name**       | zhur.ai-agent                                  |
| **REPO_ROOT**  | `/Users/ndppd/Desktop/git/zhur.ai-agent`       |
| **Origin**     | `https://github.com/m1krot1k1/zhurai-agent.git`|
| **Active Branch** | `dev`                                       |
| **Upstream**   | [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research |

## Relationship to Upstream

zhur.ai-agent is a **fork** of [Hermes Agent](https://github.com/NousResearch/hermes-agent)
by Nous Research. It inherits the core agent architecture, tool system, plugin
and skill ecosystem, and desktop/CLI/gateway surfaces from the upstream project,
then adds customizations, additional skills, domain-specific agents, and
tuning for personal use.

## Self-Awareness

The agent running **right now IS this repo**. Any problems discovered during
self-analysis — structural issues, missing files, stale configs, contradictions
between files — should be **fixed here, in this repository**, then committed
and pushed to the `dev` branch. After pushing, the agent should refresh itself
(refetch, reload) to pick up changes.

This skill is loaded automatically when the agent detects it is running inside
`REPO_ROOT`.

## Key File Ecosystem

- `AGENTS.md` — Agent definitions, roles, delegation chain, and orchestration
- `agents/` — Subagent definitions and AGENT_BRIEF files
- `skills/` — All skills including this one
- `plugins/` — Plugin modules
- `cron/` — Scheduled job definitions
- `tools/` — Core model tools
- `rules/` — Project-specific rules and conventions
- `docs/` — Additional documentation
- `pyproject.toml` — Project metadata and dependencies
- `config.yaml` — Agent configuration (after setup; loaded from `~/.hermes/`)