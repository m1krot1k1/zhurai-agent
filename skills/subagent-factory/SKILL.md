---
name: subagent-factory
description: Creates or updates specialized subagents with matching rules and optional skills. Use when existing agents cannot cover a recurring task pattern or when orchestrator detects a capability gap.
requires: none
---

# Subagent Factory

Use the **subagent-factory** agent when you need to add a new practical capability to the ecosystem.

## What this skill is for

Apply when:
- A recurring workflow lacks a dedicated specialist
- Existing agent scopes are overloaded or ambiguous
- You need a packaged capability: agent + rules + optional skill

Avoid creating new agents for one-off tasks.

## Standard package produced

For each new specialist, produce canonical root-first artifacts:
- `agents/<agent-name>.md`
- `rules/<agent-name>.mdc`
- Optional `skills/<skill-name>/SKILL.md`
- Registry updates in `agents/README.md` and `rules/specialists.mdc`

If the repository is mirrored under `.cursor/` in a host project, that mirror is runtime-only and must stay consistent with the canonical root files.

## Invocation patterns

```text
Use the subagent-factory subagent to create <agent-name> for <domain/task>.
Include rule file, optional skill if reusable, and update registries.
```

```text
Use the subagent-factory subagent to audit overlap between existing agents and propose create/extend/merge decision with rationale.
```

## Quality requirements

- Keep scope boundaries explicit.
- Use measurable completion contracts.
- Avoid duplicate capabilities unless precedence is documented.
- Prefer concise prompts and actionable rules over long narratives.

## Escalation

- Use `meta-agent-architect` for ecosystem-wide restructuring.
- Use `orchestrator` when capability creation has multiple dependent branches.
