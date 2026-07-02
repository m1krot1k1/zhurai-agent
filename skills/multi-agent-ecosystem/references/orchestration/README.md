# Orchestration references (ZCode)

On-demand reference library for the **multi-agent-ecosystem** skill. Load these files when routing, delegating, or closing a wave — not at skill install time.

## When to load what

| Situation | Read first |
|-----------|------------|
| `/start` or start-router handoff | [start-workflow.md](./start-workflow.md), [delegation-chain.md](./delegation-chain.md) |
| `/orchestrator` or multi-branch work | [delegation-chain.md](./delegation-chain.md), [completion-contracts.md](./completion-contracts.md) |
| Choosing a specialist | [routing-table.md](./routing-table.md) |
| Claiming "done" | [evidence-first-acceptance.md](./evidence-first-acceptance.md), [completion-contracts.md](./completion-contracts.md) |
| Path / layout questions | [zcode-paths.md](./zcode-paths.md) |

## Index

| File | Purpose |
|------|---------|
| [delegation-chain.md](./delegation-chain.md) | Canonical chain: `/start` → orchestrator → specialists; swarm and escalation rules |
| [start-workflow.md](./start-workflow.md) | Operator runbook: DUA, act-first, footer, continuous mode, state glossary |
| [routing-table.md](./routing-table.md) | Task → agent routing for all 33 specialists |
| [completion-contracts.md](./completion-contracts.md) | YAML schema for branch completion and wave synthesis |
| [evidence-first-acceptance.md](./evidence-first-acceptance.md) | Claim-to-evidence matrix and reviewer checklist |
| [process-and-quality-gates.md](./process-and-quality-gates.md) | Verification checklist, routing gates, autonomy footer |
| [zcode-paths.md](./zcode-paths.md) | Canonical paths inside this ZCode plugin |

## How the skill loads references

The master skill lives at `skills/multi-agent-ecosystem/SKILL.md` (sibling to this `references/` tree). ZCode resolves paths relative to the plugin root declared in `.zcode-plugin/plugin.json`.

**On-demand loading pattern:**

1. User invokes a slash command (`/start`, `/orchestrator`, or a specialist command).
2. The command front-matter sets `skills: multi-agent-ecosystem` and a mode (start router vs orchestrator).
3. The active agent reads only the references needed for the current decision — typically one orchestration doc plus one agent brief from `references/agents/<name>.md`.
4. Orchestrator mode explicitly requires [delegation-chain.md](./delegation-chain.md) and `references/rules/orchestrator.mdc` before decomposition (see `commands/orchestrator.md`).

**Do not** preload the full reference tree into context. Pull files by role:

```text
/start router     → start-workflow.md + delegation-chain.md (chain only)
/orchestrator     → delegation-chain.md + completion-contracts.md + routing-table.md
specialist branch → references/agents/<name>.md + completion-contracts.md (on close)
```

## Related references (outside this folder)

| Path | Role |
|------|------|
| `commands/start.md` | Start router command contract |
| `commands/orchestrator.md` | Orchestrator command contract |
| `references/rules/orchestrator.mdc` | Full orchestration policy (adapted from orchestrator rules) |
| `references/agents/*.md` | Per-specialist briefs |
| `references/skills/*/SKILL.md` | Optional deep skills (start-workflow, orchestrator, etc.) |

## Policy anchors

These references implement behavior defined in:

- `references/rules/orchestrator.mdc` — delegation envelopes, writer limits, evidence schema
- `references/rules/specialists.mdc` — routing table source, Mandatory SWARM
- `references/rules/aleksander.mdc` — DUA, anti-hallucination, mandatory footer

When a reference and a rule file disagree, the rule file wins.
