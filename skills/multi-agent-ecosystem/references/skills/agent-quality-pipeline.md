---
name: agent-quality-pipeline
description: "Пайплайн качества многоагентных задач: граф работ, метрики, отладка, рубрика оценки оркестрации, Agent Council для multi-variant решений."
requires: [web-research-fact-pack, caid-worktrees]
---

> **Reference doc** — loaded on-demand from `references/skills/`. Not a separate ZCode skill; use when the master `multi-agent-ecosystem` skill or an agent brief points here.


## Purpose

Ensure reproducible quality in multi-agent delegation and multi-voice architectures. Define observable metrics, feedback loops, verification gates, and the Agent Council Protocol for high-stakes core decisions.

## When to Use

- Assessing or improving multi-agent task delegation quality.
- Debugging agent orchestration failures or performance issues.
- Benchmarking orchestration decisions against a quality rubric.
- Enforcing quality gates before task completion.
- Evaluating trade-offs between multiple implementation approaches via Agent Council (§17).

## Implementation Steps

**P1: Work Graph**
- Deduplicate tasks: `{norm(B_input) == norm(A_output)} → skip B, reuse A`
- Apply parallel-first: execute all independent tasks in parallel.

**P2: Observability**
Ensure every task branch produces evidence artifacts:
- `agent_decision_log.md`: key decisions and rationales
- `audit_trail.md`: tool usage and state changes
- `delta.md`: file modifications made
- `score_rationale.md`: quality self-assessment

**P3: Reliability**
- Fail branch after `timeout_s = max(60, estimated_steps * 30)` seconds
- Retry transient failures (max 2 times), then escalate
- Log partial failures but allow graph to continue

**P4: Debugging Priorities**
1. Ambiguity → address `CRITICAL_UNKNOWNS` or form testable hypotheses
2. Empty/invalid AC → replace with observable commands/artifacts
3. Lost context → trigger `Context incomplete. Re-reading [files]`
4. Anti-loop → halt and escalate if no progress over 3+ iterations

**P4.1: A/B Gate**
```
IF best_guess_can_be_validated_in_1_step AND confidence < 70%:
    => fork Branch A (current) || Branch B (alternative)
    => compare outputs → pick winner
```

**P4.2: Canonical Metrics**

| Metric | Definition | Norm |
|--------|-----------|------|
| Accuracy | AC met / total AC | ≥90% |
| Latency | turns-to-done | ≤ L1-budget |
| Stability | no regressions | 0 |
| Cost | branches used / budget | ≤80% |

**P5: External Ideas (Extract-Compare-Classify-Implement-Verify)**
1. Extract: neutrally document external input
2. Compare: gap vs current architecture
3. Classify: Breaking / Enhancing / Neutral / Conflicting
4. Implement: only if Enhancing or Breaking (with approval)
5. Verify: AC pass post-implementation

**P6: Self-Grade Loop (0–100)**
```
Score = (AC_passed / AC_total * 70)
      + (no_regressions * 20)
      + (evidence_complete * 10)
IF score < 80: rework; IF score < 50: escalate to orchestrator
```

**P7: Orchestration Rubric (/100)**

| Criterion | Max |
|--------------------------|-----|
| Envelope completeness | 15 |
| Observable AC | 15 |
| Parallel-first applied | 10 |
| Dependency graph valid | 10 |
| Voices specified | 10 |
| Measurable stop condition | 10 |
| Evidence artifacts present | 10 |
| Anti-loop enforced | 10 |
| Web search used if needed | 5 |
| Council bonus (4+ voices) | +5 |

**P8: Agent Council Protocol**

For high-stakes or ambiguous core decisions, use the Agent Council pattern per `../rules/orchestrator.mdc` §17. Related: §14 Multi-Model Debate, §15 Adversarial Peer Refinement, §18 shared cited fact-pack.

*Council triggers (mandatory check before spawning variants):*
- `../rules/*.mdc` changes with material behavior impact — **§17** explicitly ties Council to core rules
- Large extraction / >30 candidate changes with high ambiguity — see **§17** and **§12** extraction density
- Single-writer consensus hides trade-offs; stakeholders need explicit variant + rationale

*Step 1: Confirm Council is mandatory or valuable*
1. Read **§17** in `../rules/orchestrator.mdc`: triggers, max **3 variants**, judge role (**producer type** must differ — typically code-reviewer as judge selecting among implementations).
2. If factual disagreement exists, run **`web-research-fact-pack.md`** first; Council votes use one **same cited fact-pack** per §17/§18 linkage.
3. If L1 fan-out or depth is at risk, reconcile with **§0**, **§12** restructuring before spawning variants.

*Step 2: Produce capped variants in parallel*
1. Spawn **Variant A / B (/ C)** with **disjoint or clearly scoped OWNERSHIP** if they touch files — parallel writer safety in **§3** (CAID-oriented ownership discipline; see also `caid-worktrees.md`).
2. Each variant: goal, diff sketch, risks, rollback; **no more than three**.
3. Keep factual claims anchored; if external facts matter, cite §18 pack only.

*Step 3: Judge, score, cherry-pick*
1. **Judge** task: score each variant /10 per agreed criteria, pick winner, list gaps, **cherry-pick up to two items from non-winners** — exact pattern in **§17**.
2. Record decision + dissenting merits for future audits (short matrix, not prose novels).
3. If judge finds policy violations (e.g., security-only work in wrong agent), reject per **§3** Role-Match.

## Checklist

Use this checklist as a reusable template — mark items as you validate them during each run.

- [ ] Work graph deduplicated
- [ ] All independent tasks executed in parallel
- [ ] Per-branch timeouts enforced
- [ ] AC are observable and verifiable
- [ ] Self-grade ≥80 before completion
- [ ] Evidence artifacts generated
- [ ] Rubric used in orchestration review

### Council-specific checks (when Council is triggered)

- [ ] §17 preconditions checked; variant count ≤ 3
- [ ] Fact-pack shared if web-dependent (§18)
- [ ] Judge output includes scores, winner, cherry-picks
- [ ] Ownership conflicts absent or escalated before merge
