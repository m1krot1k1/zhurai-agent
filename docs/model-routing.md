# Model routing (fast vs capable)

This document describes how to think about **model tier selection** in this agent ecosystem: cost, latency, and when an **orchestrator** should **fan out** work across branches or specialists.

It is **policy-aligned** with routing checklists in [process and quality gates](process-and-quality-gates.md) and the `/start` chain in [delegation chain](delegation-chain.md).

## Tiers

| Tier | Typical use | Tradeoff |
| --- | --- | --- |
| **Fast** | Tight loops: file lookup, narrow edits, deterministic checks, scripted transforms | Lower cost and latency; less tolerance for ambiguous specs |
| **Capable** | Architecture, multi-file design, adversarial review, security reasoning, large-context synthesis | Higher cost/latency; better error recovery and nuance |

Choosing fast vs capable is **not** a substitute for **delegation**: a complex objective still belongs in an orchestrated plan with explicit branches and acceptance criteria (see [evidence-first acceptance](evidence-first-acceptance.md)).

## Cost and latency heuristics

- Prefer **fast** when the task has a **small fingerprint**: single domain, bounded files, clear AC, low ambiguity.
- Prefer **capable** when **ambiguity ≥ 2**, security-sensitive scope, or the cost of a wrong answer exceeds the marginal model cost.
- **Parallelism** reduces wall-clock time but not token spend; fan out when branches are **independent** and each branch has a **narrow OWNERSHIP** contract (see [DAG and branch dependencies](dag-branch-dependencies.md)).

## When the orchestrator fans out

Fan out (multiple child tasks or specialists in one wave) when:

1. **Independent workstreams** — no `DEPENDENCIES` between branches (or only `after:` edges satisfied).
2. **Disjoint OWNERSHIP** — parallel writers must not edit the same files without coordination.
3. **Verification isolation** — e.g. `code-reviewer` and `security-auditor` as readers separate from builders.
4. **Structural gate** — many similar reader tasks (e.g. per-file review) should be launched as a **batch**, not a serial loop.

Avoid fan-out when a single sequential chain is **mandatory** (strict `DEPENDENCIES`, shared mutable state, or need for a single coherent design pass before any coding).

## Relation to skills

- [orchestrator skill](../skills/orchestrator/SKILL.md) — multi-domain pipelines.
- [specialist-discovery skill](../skills/specialist-discovery/SKILL.md) — which specialist fits which slice of work.
- Full skill list: [skills index](skills-index.md).
