# Evaluation pipeline vision

Vision doc for **repeatable evaluation** of agents in this repo: benchmarks, rubrics, and linkage to skills. Concrete scripts may land under `scripts/` later; this describes the **target pipeline** and its ties to documentation and policy.

Operational quality expectations: [process and quality gates](process-and-quality-gates.md). Proof of completion: [evidence-first acceptance](evidence-first-acceptance.md). Multi-agent routing: [delegation chain](delegation-chain.md).

## Goals

- Measure **accuracy** (AC met?), **safety** (injection resistance), **cost/latency**, and **stability** across seeds—aligned with prompt-regression language in workspace rules.
- Tie scores to **artifacts**: transcript paths, diff stats, command outputs—not subjective prose.

## Relation to `skills/agent-evals`

The **agent-evals** skill at [skills/agent-evals/SKILL.md](../skills/agent-evals/SKILL.md) SHOULD own:

- Rubric definitions per **agent type** (`orchestrator`, `code`, readers, …).
- How to bundle **tasks** into an eval suite (tiers: smoke / nightly / adversarial).
- Required **claim-to-evidence** rows for eval reports.

Cross-index: [skills index](skills-index.md) lists all skills; this vision doc is the **docs-side** umbrella for how suites and CI eventually plug in.

## Pipeline stages (target)

1. **Build manifest** — frozen git SHA, model tier ([model routing](model-routing.md)), policy bundle hash.
2. **Fixture load** — workspaces + prompts from [replay fixtures vision](replay-fixtures-vision.md).
3. **Execute** — driver runs scenarios; captures telemetry per [agent telemetry contract](agent-telemetry-contract.md).
4. **Score** — automated checks (diff invariants, linters) + human or model-as-judge rubric (declared in advance).
5. **Publish** — JSON summary + HTML/markdown report; archive transcripts with redaction.

## Suites

| Suite | Purpose | Frequency |
| --- | --- | --- |
| Smoke | Fast regressions on orchestration invariants | Every PR touching `rules/`, `agents/`, `skills/` |
| Functional | End-to-end tasks on sample repos | Nightly or weekly |
| Adversarial | [Prompt injection probes](security/prompt-injection-probes.md) + tool-trust cases | Weekly or pre-release |

## Gates

- **Fail** if builder branches omit completion contracts or `OWNERSHIP` violations occur.
- **Warn** on high variance across seeds without a documented stability budget.

## Cross-links

- Hooks/CI glue: [cursor hooks and harness](cursor-hooks-and-harness.md).
- Future OTel: [open telemetry future](open-telemetry-future.md).
