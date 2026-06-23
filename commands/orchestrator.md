---
description: Decompose complex work into parallel specialist branches and synthesize results.
argument-hint: "[objective, scope, or branch plan]"
skills: multi-agent-ecosystem
---

# Orchestrator mode

**ORIGINAL_REQUEST:** $ARGUMENTS

## Load skill (required)

Plugin root: `/Users/ndppd/.zcode/commands`

1. If the **Skill** tool is available → call `multi-agent-ecosystem` and operate in **orchestrator** mode.
2. If Skill tool fails → **Read**:
   `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/SKILL.md`
   Then continue as orchestrator using paths under that plugin root.

## FIRST_READ (mandatory before any work)

- `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/references/rules/aleksander.mdc`
- `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/references/rules/specialists.mdc`
- `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/references/orchestration/delegation-chain.md`
- `/Users/ndppd/.zcode/commands/skills/multi-agent-ecosystem/references/rules/orchestrator.mdc`

## Orchestrator obligations

1. Read delegation-chain and orchestrator rules before decomposing.
2. Break the task into independent branches; assign each branch an exclusive `OWNERSHIP` (file globs).
3. For each branch: load `references/agents/<name>.md` under plugin root and execute (or spawn a ZCode sub-session with that brief).
4. Launch **independent** branches in parallel when ZCode supports concurrent agents; otherwise batch sequentially but never skip decomposition.
5. Synthesize branch results with evidence per AC; escalate when 3+ parallel writer branches need coordination.
6. Apply MUST/MAY delegation rules from the master skill — specialists with 2+ independent subtasks must delegate, not do everything inline.

Return a completion contract: files changed, checks run, AC status, open risks.
