# LLM-as-judge playbook

Using an LLM to **score, rank, or gate** other model outputs is cheap to wire and expensive to get wrong. This playbook fits benchmark and review workflows ([agent-evals](../skills/agent-evals/SKILL.md)) and aligns with **evidence-first** acceptance ([evidence-first-acceptance](evidence-first-acceptance.md)).

## Rubric first

A judge without a **fixed rubric** is a second noisy generator.

1. **Dimensions** — e.g. correctness, policy compliance, citation quality, safety, style (only if material).
2. **Scales** — ordinal 1–5 or pass/fail per dimension; avoid vague “better/worse.”
3. **Anchors** — short examples of **score 2 vs 4** per dimension.
4. **Failure modes** — “judge agrees with longer answer,” “judge favors confident tone,” etc.

Publish the rubric **before** running evals so regressions are comparable.

## Human-held gold

**Gold** (reference behavior or reference answer) should be **human-owned** for tasks that matter:

- Store **expected outcomes** or **must-not** lists in versioned fixtures, not only in the judge prompt.
- Use the judge to **compare to** gold and to **flag** divergence — not to silently redefine gold each run.

When full gold is too costly, use **partial gold**: checked properties, invariants, or tool-call traces.

## Variance and stability

Judge outputs **jitter** across temperatures, prompt ordering, and minor wording. Treat LLM judge scores as **stochastic**:

- Run **multiple seeds** or **N trials** for critical gates; report **mean + spread** (or majority vote).
- Track **when** the judge flips verdict between runs on identical inputs — that variance is a **metric**.

For automation, prefer **binary checks** where possible (schema, linters, golden file diff); reserve the judge for **subjective** dimensions only.

## Anti-patterns

- **Single-shot “is this good?”** with no rubric — unusable for regression.
- **Judge writes the final user-facing answer** without human or policy gate on sensitive actions.
- **Oversized context** — stuffing full transcripts makes scores drift; prefer **summaries with citations** back to spans.

## Related artifacts

| Topic | Where |
| --- | --- |
| Agent evals and golden tasks | [agent-evals](../skills/agent-evals/SKILL.md), [eval-pipeline-vision](eval-pipeline-vision.md) |
| Transcript-level benchmarks | [agent-evals](../skills/agent-evals/SKILL.md) (merged from behavior-benchmarks-transcript) |
| Completion evidence | [process-and-quality-gates](process-and-quality-gates.md) |
| Council + judge patterns | [agent-council-judge](../skills/agent-council-judge/SKILL.md) |
