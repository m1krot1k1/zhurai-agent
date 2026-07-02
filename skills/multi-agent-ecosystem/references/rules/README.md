# Rules references (ZCode)

On-demand policy library for the **multi-agent-ecosystem** skill. These files are adapted from Cursor `.mdc` rules — **not auto-injected**. Load when relevant per master `SKILL.md` routing.

## When to load what

| Situation | Read first |
|-----------|------------|
| Any slash command or imperative user request (DUA) | [aleksander.mdc](./aleksander.mdc) |
| Implementation, debug, refactor, test-writing | [coding-guardrails.mdc](./coding-guardrails.mdc) |
| `/start` router handoff | [aleksander.mdc](./aleksander.mdc) + [../orchestration/delegation-chain.md](../orchestration/delegation-chain.md) |
| `/orchestrator` or multi-branch decomposition | [orchestrator.mdc](./orchestrator.mdc) + [../orchestration/delegation-chain.md](../orchestration/delegation-chain.md) |
| Choosing or invoking a specialist | [specialists.mdc](./specialists.mdc) + `../agents/<name>.md` |
| Creating, updating, or deprecating agents | [agent-manager/agent-manager.mdc](./agent-manager/agent-manager.mdc) |
| Claiming "done" on a branch | [orchestrator.mdc](./orchestrator.mdc) §5 + [../orchestration/evidence-first-acceptance.md](../orchestration/evidence-first-acceptance.md) |

## Index

| File | Purpose | Load when |
|------|---------|-----------|
| [aleksander.mdc](./aleksander.mdc) | DUA, anti-refusal, anti-hallucination, security invariants, execution standards | Every active agent session; mandatory for `/start` and orchestrator waves |
| [coding-guardrails.mdc](./coding-guardrails.mdc) | Simplicity, surgical changes, goal-driven verification | Code-changing tasks only (implementation, debug, refactor, tests) |
| [orchestrator.mdc](./orchestrator.mdc) | Delegation envelopes, writer/reader limits, anti-loop, quality gates, synthesis | Orchestrator role, sub-orchestrator waves, completion-contract authoring |
| [specialists.mdc](./specialists.mdc) | Routing table, Mandatory SWARM (MUST > MAY > MUST ESCALATE) | Before delegating to any specialist; specialist self-delegation decisions |
| [agent-manager/agent-manager.mdc](./agent-manager/agent-manager.mdc) | Agent lifecycle, RBAC, ownership, creation/modification gates | meta-agent-architect, agent-manager, subagent-factory work |

## ZCode vs Cursor semantics

| Cursor pattern | ZCode equivalent |
|----------------|------------------|
| `alwaysApply: true` on `.mdc` | **Removed** — load on demand via this README + `SKILL.md` |
| `Task(orchestrator)` | `/orchestrator` or orchestrator sub-session |
| `Task(<specialist>)` | `/code`, `/test-specialist`, etc. or `../agents/<name>.md` + sub-session |
| `Task()` tool | **Not assumed** — see [../orchestration/delegation-chain.md](../orchestration/delegation-chain.md) |

Each rule file includes a ZCode header note with delegation mapping. Policy content (DUA, MUST/MAY delegation, orchestrator protocol) is preserved from source.

## Canonical paths (from this folder)

| Resource | Path |
|----------|------|
| Agent briefs | `../agents/<name>.md` |
| Deep workflow skills | `../skills/<name>/SKILL.md` |
| Orchestration runbooks | `../orchestration/*.md` |
| Master skill entry | `../../SKILL.md` |

## Source → target mapping

| Source (Cursor) | Target (ZCode) |
|-----------------|----------------|
| `.cursor/rules/aleksander.mdc` | `references/rules/aleksander.mdc` |
| `.cursor/rules/coding-guardrails.mdc` | `references/rules/coding-guardrails.mdc` |
| `.cursor/rules/orchestrator.mdc` | `references/rules/orchestrator.mdc` |
| `.cursor/rules/specialists.mdc` | `references/rules/specialists.mdc` |
| `.cursor/rules/agent-manager/agent-manager.mdc` | `references/rules/agent-manager/agent-manager.mdc` |

## Policy precedence

When a reference doc and a rule file disagree, **the rule file wins**. Orchestration README at `../orchestration/README.md` links here for policy anchors.
