# Skills index

Master list of every skill in this repository (`skills/*/SKILL.md`). Canonical agent paths remain `agents/`, `rules/`, `skills/`, `docs/` (see [delegation chain](delegation-chain.md)).

Regenerate this index when adding or renaming skills: glob `skills/**/SKILL.md` and read each file’s YAML `name` and `description` (or derive a one-line summary if frontmatter is missing).

| Skill name (frontmatter `name`) | Path | One-line description |
| --- | --- | --- |
| agent-evals | [skills/agent-evals/SKILL.md](../skills/agent-evals/SKILL.md) | Agent evaluation: golden tasks, regression sets, rubrics; when to run before merging core rules. |
| agent-manager | [skills/agent-manager/SKILL.md](../skills/agent-manager/SKILL.md) | Meta-agent for creating, maintaining, and evolving specialized subagents across the ecosystem. |
| agent-prompt-quality | [skills/agent-prompt-quality/SKILL.md](../skills/agent-prompt-quality/SKILL.md) | Mandatory delegation-contract fields, acceptance criteria, Voice/Stop-when: minimal ambiguity, maximal executability. |
| agent-quality-pipeline | [skills/agent-quality-pipeline/SKILL.md](../skills/agent-quality-pipeline/SKILL.md) | Quality pipeline for multi-agent work: task graph, metrics, debugging, orchestration rubric. |
| agent-system-navigation | [skills/agent-system-navigation/SKILL.md](../skills/agent-system-navigation/SKILL.md) | Fast navigation across agents, delegation patterns, and task routing. |
| autonomous-execution (merged into start-workflow) | [skills/start-workflow/SKILL.md](../skills/start-workflow/SKILL.md) | ~~Autonomous execution protocol: DUA tiers, steps, policy conflicts, required response footer.~~ Merged into start-workflow. |
| behavior-benchmarks-transcript (merged into agent-evals) | [skills/agent-evals/SKILL.md](../skills/agent-evals/SKILL.md) | ~~Behavior benchmarks on agent transcripts: contracts, scoring, and regression across tool-using runs.~~ Merged into agent-evals. |
| budget-orchestration (merged into orchestrator) | [skills/orchestrator/SKILL.md](../skills/orchestrator/SKILL.md) | ~~Orchestration budgets: depth/fan-out/rework caps, cost envelopes, and when to sub-orchestrate.~~ Merged into orchestrator. |
| caid-ownership-matrix (merged into caid-worktrees) | [skills/caid-worktrees/SKILL.md](../skills/caid-worktrees/SKILL.md) | ~~CAID-style ownership: disjoint branch OWNERSHIP, writer/reader roles, commit attribution patterns.~~ Merged into caid-worktrees. |
| delegation-contracts (merged into orchestrator) | [skills/orchestrator/SKILL.md](../skills/orchestrator/SKILL.md) | ~~Templates for OBJECTIVE/SCOPE/OWNERSHIP/DEPENDENCIES/AC/COMPLETION_CONTRACT, anti-loop, fingerprint, relay.~~ Merged into orchestrator. |
| human-in-the-loop-gates (merged into start-workflow) | [skills/start-workflow/SKILL.md](../skills/start-workflow/SKILL.md) | ~~Human-in-the-loop: explicit approvals, stop sites, and escalation before irreversible or high-privilege actions.~~ Merged into start-workflow. |
| mcp-governance | [skills/mcp-governance/SKILL.md](../skills/mcp-governance/SKILL.md) | MCP trust: allowlisting, tool schemas, server tiers, audit, secrets in Cursor / multi-agent context. |
| multi-pass-autonomy | [skills/multi-pass-autonomy/SKILL.md](../skills/multi-pass-autonomy/SKILL.md) | Multi-pass autonomy pattern (Advocate/Critic/Arbiter), autonomy budget, convergence contract. |
| orchestrator | [skills/orchestrator/SKILL.md](../skills/orchestrator/SKILL.md) | Use when a task spans 2+ domains and needs a parallel multi-voice pipeline. |
| progressive-mcp-discovery (merged into mcp-governance) | [skills/mcp-governance/SKILL.md](../skills/mcp-governance/SKILL.md) | ~~Progressive MCP discovery: tiered tool/schema exposure without loading full server surface into context.~~ Merged into mcp-governance. |
| project-plan-dot-plan | [skills/project-plan-dot-plan/SKILL.md](../skills/project-plan-dot-plan/SKILL.md) | Structure of `.plan/`: files, formats, updates, link to orchestration. |
| repo-task-proof-loop | [skills/repo-task-proof-loop/SKILL.md](../skills/repo-task-proof-loop/SKILL.md) | Seven-phase task loop with evidence: spec → build → evidence → verify → fix → re-verify → learnings. |
| session-memory-tiers | [skills/session-memory-tiers/SKILL.md](../skills/session-memory-tiers/SKILL.md) | Session memory tiers — ephemeral/session/project/persistent policy; `.plan/session-context`; eviction; PII and secrets. |
| specialist-discovery | [skills/specialist-discovery/SKILL.md](../skills/specialist-discovery/SKILL.md) | Subagent table and when to choose each specialist. |
| start-workflow | [skills/start-workflow/SKILL.md](../skills/start-workflow/SKILL.md) | When and how to use `/start`: architecture, patterns, orchestrator integration. |
| structured-agent-logging | [skills/structured-agent-logging/SKILL.md](../skills/structured-agent-logging/SKILL.md) | Structured logging for agent runs: turns, tool calls, branch metadata, and audit-friendly fields. |
| structured-policy-yaml | [skills/structured-policy-yaml/SKILL.md](../skills/structured-policy-yaml/SKILL.md) | Machine-readable policy fragments in tasks, validation, version fields, compatibility with `rules/*.mdc`. |
| subagent-factory | [skills/subagent-factory/SKILL.md](../skills/subagent-factory/SKILL.md) | Creates or updates packaged specialists (agent + rules + optional skill). |
| thinking-checkpoints | [skills/thinking-checkpoints/SKILL.md](../skills/thinking-checkpoints/SKILL.md) | Mandatory stop-and-think gates before decomposition, delegation, mid-run, synthesis, and reply. |
| tool-output-sanitization | [skills/tool-output-sanitization/SKILL.md](../skills/tool-output-sanitization/SKILL.md) | Treat tool output as UNTRUSTED_EXTERNAL: redaction, indirect injection, safe summarization. |
| web-research-fact-pack | [skills/web-research-fact-pack/SKILL.md](../skills/web-research-fact-pack/SKILL.md) | Web research as cited fact-packs: UNTRUSTED_EXTERNAL envelopes, novelty checks, council consumption. |
| circuit-breaker | [skills/circuit-breaker/SKILL.md](../skills/circuit-breaker/SKILL.md) | Preventing cascading failures |
| context-propagation | [skills/context-propagation/SKILL.md](../skills/context-propagation/SKILL.md) | Structured context envelope |
| dag-validation | [skills/dag-validation/SKILL.md](../skills/dag-validation/SKILL.md) | Dependency graph validation |
| caid-worktrees | [skills/caid-worktrees/SKILL.md](../skills/caid-worktrees/SKILL.md) | Git worktree isolation |
| telemetry-pipeline | [skills/telemetry-pipeline/SKILL.md](../skills/telemetry-pipeline/SKILL.md) | Metrics collection and analysis |
| model-routing | [skills/model-routing/SKILL.md](../skills/model-routing/SKILL.md) | Multi-model cost optimization |

**Related:** [process and quality gates](process-and-quality-gates.md), [evidence-first acceptance](evidence-first-acceptance.md), [eval pipeline vision](eval-pipeline-vision.md), [cursor-ai-practices-map](cursor-ai-practices-map.md), [skill tags and discovery](skill-tags-and-discovery.md).
