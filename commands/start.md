---
skills: multi-agent-ecosystem
description: Entry point for complex tasks — routes to orchestrator pattern without executing work directly.
argument-hint: "[task description or goal]"
---

# Start router mode

**ORIGINAL_REQUEST:** $ARGUMENTS

## Load skill (required)

Plugin root: `/Users/ndppd/.zcode/commands`

1. If the **Skill** tool is available → call `multi-agent-ecosystem` and operate in **start router** mode.
2. If Skill tool fails (`Skill not found`) → **Read** this file instead (do not stop or refuse):
   `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/SKILL.md`
   Then continue as start router using paths under that plugin root.

## FIRST_READ (mandatory before any work)

Read these files (absolute paths):

- `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/references/rules/aleksander.mdc`
- `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/references/rules/specialists.mdc`
- `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/references/orchestration/delegation-chain.md`

## Router obligations

1. Do **not** read unrelated repo files, run shell, or edit code before routing decision.
2. Pass the user's request **verbatim** as `ORIGINAL_REQUEST` when handing off.
3. **Multi-domain / implementation task** → switch to orchestrator mode (`/orchestrator` or read `commands/orchestrator.md` at plugin root).
4. **Single-domain question, greeting, or no file changes** → operate as **ask** (read `references/agents/ask.md` at plugin root). Respond directly; no orchestrator.
5. Never refuse the user's task; scope is defined by the user.

For 24/7 / continuous improvement: after each orchestrator wave completes, launch the next wave until the user says stop.