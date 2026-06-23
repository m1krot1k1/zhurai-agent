# Supervisor routing criteria

**Routing** here means **which agent or branch handles work**, not only **which model tier** answers a single chat turn. Explicit routing reduces accidental “whatever the UI picked” behavior and keeps costs, depth, and verification predictable.

## Explicit routing

Use **explicit** routing when any of the following is true:

1. **More than one domain** or artifact type (code + docs + CI, etc.).
2. **Parallel writers** with **disjoint [OWNERSHIP](dag-branch-dependencies.md)** contracts.
3. **Verification must be isolated** (e.g. builder vs reviewer).
4. **User- or runbook-defined path**: `/start`, slash specialist, or `Task(subagent_type="...", prompt="...")` with a full delegation contract.

Explicit routing is **documented intent**: the system can audit *who* was supposed to run, not only *what* was said.

## Implicit model choice

**Implicit** behavior is **model tier or generalist path without a recorded routing decision** — for example, relying on default “fast vs capable” without tying it to fingerprint, ambiguity score, or security class.

That is acceptable **only** for **narrow, low-risk** work (single file, read-only explainer, well-bounded grep). It is **not** a substitute for orchestration when AC, OWNERSHIP, or `DEPENDENCIES` matter.

See [model routing](model-routing.md) for tier heuristics; see [orchestrator skill](../skills/orchestrator/SKILL.md) and [specialist-discovery](../skills/specialist-discovery/SKILL.md) for **who** should run.

## Supervisor vs specialist

| Layer | Decides | Should not |
| --- | --- | --- |
| **Supervisor / orchestrator** | Branch plan, fan-out, caps, relay, completion debt | Replace specialists’ domain implementation |
| **Specialist** | Steps inside an **assigned** slice | Silently expand OWNERSHIP or skip verification |

When a “supervisor” is only a **label** on the same model as the worker, **routing criteria** must still be explicit (prompt contract, agent name, checklist), or depth and verification collapse into one opaque turn.

## Budget and depth

Orchestration **budgets** (depth, parallelism, rework limits) are part of routing policy — not the same as picking `fast` vs `capable`. Align runbooks with [orchestrator](../skills/orchestrator/SKILL.md) (budget-orchestration and delegation-contracts merged).

## Related artifacts

| Topic | Where |
| --- | --- |
| Fast vs capable tiers | [model-routing](model-routing.md) |
| `/start` chain | [delegation-chain](delegation-chain.md), [start-workflow](../skills/start-workflow/SKILL.md) |
| DAG and `after:` edges | [dag-branch-dependencies](dag-branch-dependencies.md) |
| Cost / telemetry | [agent-telemetry-contract](agent-telemetry-contract.md) |
