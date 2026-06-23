# Agent telemetry contract

Contract-style specification for **observability** of multi-agent runs: events, fields, privacy, and correlation. Implementations may be partial today; this doc is the **target shape** so logs, benchmarks, and future OpenTelemetry export stay aligned (see also [open telemetry future](open-telemetry-future.md)).

Handoffs and relay semantics are defined operationally in [delegation chain](delegation-chain.md). Completion evidence uses [evidence-first acceptance](evidence-first-acceptance.md).

## Goals

- Correlate **user request → waves → branches → tools → outcomes** without leaking secrets.
- Support **SLO measurement** (latency, success, rework cycles) per orchestration policy in [process and quality gates](process-and-quality-gates.md).

## Correlation identifiers

| Field | Required | Description |
| --- | --- | --- |
| `trace_id` | yes | Stable id for the user-visible session (root `/start` or top-level task). |
| `span_id` | yes | Id for the current unit of work (one agent turn, one child task, or one tool batch). |
| `parent_span_id` | yes except root | Parent span in the delegation tree. |
| `branch_id` | when branched | Phase-tree id, e.g. `B0`, `B0-2` (see [DAG and branch dependencies](dag-branch-dependencies.md)). |
| `relay_batch_id` | when relaying | Binds proxy children to a single orchestrator resume (`ORCHESTRATOR_RELAY_REQUEST`). |

**Formatting:** opaque random strings (e.g. 128-bit hex); never encode user text or secrets inside ids.

## Event types (minimal set)

| Event | When emitted | Purpose |
| --- | --- | --- |
| `task.start` | Child task dispatched | Fan-out audit; agent type and branch metadata. |
| `task.end` | Child returns completion contract | Success/fail/rework; duration; AC summary (no raw secrets). |
| `delegate.relay` | Relay handoff | Transport-only proxy path; links `relay_batch_id`. |
| `tool.invoke` | Before tool execution | Name + **sanitized** args digest (see privacy). |
| `tool.result` | After tool | Byte size / status; **no** full stdout by default. |
| `policy.violation` | Guardrail trip | Rule id + severity; redacted context. |
| `verify.gate` | Benchmark or checklist step | Pass/fail + reference to stored artifact path (repo-relative). |

## Payload fields (per event)

```yaml
event:
  name: task.start           # enum from Event types
  ts: "2026-03-31T12:00:00Z" # RFC3339 UTC
  trace_id: "<opaque>"
  span_id: "<opaque>"
  parent_span_id: "<opaque|null>"
  branch_id: "B0-2"
  agent:
    type: docs-specialist    # subagent_type / role
    entry_mode: supervised_worker
  attributes:
    task_fingerprint_hash: "<sha256 of normalized objective+scope>" # optional
    ownership_globs: ["docs/**"]                                    # optional
  redaction:
    policy_version: "2026-03"  # optional pointer to policy bundle revision
```

**Completion contract attachment:** on `task.end`, include references to YAML completion blocks consistent with [evidence-first acceptance](evidence-first-acceptance.md), not raw model prose.

## Privacy and data minimization

- **Never log:** API keys, tokens, cookies, private keys, raw auth headers, full `.env`, or unredacted PII.
- **Truncate or hash** free-form user prompts in shared sinks; store **full** prompts only in customer-controlled retention per product policy.
- **Tool args:** log command **argv template** with secrets replaced by `[REDACTED]`; file paths may be repo-relative.
- **Tool output:** default to **size + hash**; full capture only behind explicit debug flags and short TTL.

## Sampling and retention

| Stream | Recommended default | Notes |
| --- | --- | --- |
| Production | sampled (e.g. 1–5%) + always on failures | Bias sampling toward `rework` and `blocked` outcomes. |
| CI / benchmarks | 100% for benchmark suite duration | Tied to [eval pipeline vision](eval-pipeline-vision.md). |
| Security incidents | full trace for involved `trace_id` | Time-bounded retention; access controlled. |

## Consistency with quality gates

Telemetry SHOULD record whether **Final Verification Checklist** items were satisfied for a branch, as defined in [process and quality gates](process-and-quality-gates.md), so automation can reject “done” without evidence.
