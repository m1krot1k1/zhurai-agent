# OpenTelemetry alignment (future)

**Status:** Optional roadmap. Today’s concrete contract lives in [agent telemetry contract](agent-telemetry-contract.md). This doc sketches how agent and IDE instrumentation could map to **OpenTelemetry (OTel)** later without breaking existing YAML/JSON logs.

## Motivation

- Vendor-agnostic export of traces, metrics, and logs.
- Standard **context propagation** across nested `Task` / relay hops (see [delegation chain](delegation-chain.md)).

## Mapping sketch

| Agent concept | OTel concept |
| --- | --- |
| `trace_id` / `span_id` | `trace_id`, `span_id` (W3C trace context) |
| `task.start` / `task.end` | `Span` with `span_kind=INTERNAL` or `CLIENT/SERVER` if crossing process |
| `delegate.relay` | Span link or `Span` with `messaging` conventions |
| `tool.invoke` | Child span; attributes for tool name and redacted arg digest |
| Benchmark gate | `Span` event or separate metric `verification.gate.pass` |

Suggested **semantic attributes** (prefix custom keys to avoid collisions, e.g. `cursor.agent.branch_id`):

- `branch_id`, `agent.type`, `entry_mode`, `rework_cycles`, `status` (completion enum).

## Metrics (examples)

- Histogram: wall time per `branch_id` and `agent.type`.
- Counter: `task.rework` by reason.
- Gauge: concurrent active branches per `trace_id`.

## Privacy

OTel exporters MUST apply the same **redaction** rules as the telemetry contract: no secrets in attributes, truncated payloads, hashed prompts unless policy allows full retention.

## Adoption path

1. Implement **dual emit**: existing structured logs + optional OTLP sidecar.
2. Validate with **offline** collectors in CI (see [eval pipeline vision](eval-pipeline-vision.md)).
3. Promote OTLP to primary only after sampling and retention policies are signed off.

## Non-goals

- Mandating OTel for every contributor laptop.
- Replacing human review gates in [evidence-first acceptance](evidence-first-acceptance.md).
