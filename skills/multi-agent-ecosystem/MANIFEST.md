# Multi-Agent Ecosystem — Migration Manifest

**Branch:** B0-8  
**Migration date:** 2026-06-23  
**Source root:** `/Users/ndppd/Desktop/git/.cursor/`  
**Target root:** `skills/multi-agent-ecosystem/` (relative to ZCode plugin root `/Users/ndppd/.zcode/commands/`)

This manifest maps every primary artifact from the Cursor-era `.cursor/` tree into the ZCode `multi-agent-ecosystem` skill layout. Target files may be **pending** until sibling migration branches complete; status is noted per row.

---

## Summary

| Category | Source count | Target location | Mapped |
|----------|-------------|-----------------|--------|
| Agents | 33 | `references/agents/*.md` | 33/33 |
| Rules | 5 | `references/rules/*.mdc` | 5/5 |
| Skills | 25 | `references/skills/*.md` | 25/25 |
| **Primary total** | **63** | — | **63/63 (100%)** |

**Supplementary (not in primary 63):** orchestration runbooks (`references/orchestration/`), master `SKILL.md`, slash `commands/*.md` — documented in [Supplementary mappings](#supplementary-mappings).

---

## Adaptation notes (global)

| Topic | Source pattern | Target pattern |
|-------|----------------|----------------|
| Agent briefs | `agents/<name>.md` | `references/agents/<name>.md` (same basename) |
| Rules | `rules/<path>.mdc` | `references/rules/<path>.mdc` (preserve subdirs) |
| Skills | `skills/<name>/SKILL.md` | `references/skills/<name>.md` (flat; no nested dirs) |
| `Task()` delegation | Runtime subagent tool | ZCode: slash commands + sub-sessions; see master `SKILL.md` |
| `.cursor/` mirror | Dual canonical tree | **None** — single plugin tree |
| Path references in body | `agents/`, `rules/`, `skills/` | Rewrite to `references/agents/`, `references/rules/`, `references/skills/` |
| Front matter | Cursor agent format | Preserve; add ZCode invocation notes where needed |

---

## Agents (33 → `references/agents/`)

Source: `Desktop/git/.cursor/agents/<file>.md`  
Target: `skills/multi-agent-ecosystem/references/agents/<file>.md`

| # | Source | Target | Adaptation | Status |
|---|--------|--------|------------|--------|
| 1 | `agents/agent-architect.md` | `references/agents/agent-architect.md` | Path refs only | done |
| 2 | `agents/agent-manager.md` | `references/agents/agent-manager.md` | Path refs only | done |
| 3 | `agents/api-designer.md` | `references/agents/api-designer.md` | Path refs only | done |
| 4 | `agents/architect.md` | `references/agents/architect.md` | Path refs only | done |
| 5 | `agents/ask.md` | `references/agents/ask.md` | Path refs only | done |
| 6 | `agents/benchmark-specialist.md` | `references/agents/benchmark-specialist.md` | Path refs only | done |
| 7 | `agents/bug-triage.md` | `references/agents/bug-triage.md` | Path refs only | done |
| 8 | `agents/code-reviewer.md` | `references/agents/code-reviewer.md` | Path refs only | done |
| 9 | `agents/code-simplifier.md` | `references/agents/code-simplifier.md` | Path refs only | done |
| 10 | `agents/code-skeptic.md` | `references/agents/code-skeptic.md` | Path refs only | done |
| 11 | `agents/code.md` | `references/agents/code.md` | Path refs only | done |
| 12 | `agents/data-analyst.md` | `references/agents/data-analyst.md` | Path refs only | done |
| 13 | `agents/database-specialist.md` | `references/agents/database-specialist.md` | Path refs only | done |
| 14 | `agents/debug.md` | `references/agents/debug.md` | Path refs only | done |
| 15 | `agents/devops-specialist.md` | `references/agents/devops-specialist.md` | Path refs only | done |
| 16 | `agents/docs-specialist.md` | `references/agents/docs-specialist.md` | Path refs only | done |
| 17 | `agents/frontend-specialist.md` | `references/agents/frontend-specialist.md` | Path refs only | done |
| 18 | `agents/meta-agent-architect.md` | `references/agents/meta-agent-architect.md` | Path refs only | done |
| 19 | `agents/mobile-specialist.md` | `references/agents/mobile-specialist.md` | Path refs only | done |
| 20 | `agents/monitoring-specialist.md` | `references/agents/monitoring-specialist.md` | Path refs only | done |
| 21 | `agents/orchestrator.md` | `references/agents/orchestrator.md` | Path refs; ZCode delegation notes | done |
| 22 | `agents/performance-optimizer.md` | `references/agents/performance-optimizer.md` | Path refs only | done |
| 23 | `agents/profile-manager.md` | `references/agents/profile-manager.md` | Path refs only | done |
| 24 | `agents/provider-integrator.md` | `references/agents/provider-integrator.md` | Path refs only | done |
| 25 | `agents/release-manager.md` | `references/agents/release-manager.md` | Path refs only | done |
| 26 | `agents/repo-explorer.md` | `references/agents/repo-explorer.md` | Path refs only | done |
| 27 | `agents/review.md` | `references/agents/review.md` | Path refs only | done |
| 28 | `agents/rules-specialist.md` | `references/agents/rules-specialist.md` | Path refs only | done |
| 29 | `agents/security-auditor.md` | `references/agents/security-auditor.md` | Path refs only | done |
| 30 | `agents/skills-specialist.md` | `references/agents/skills-specialist.md` | Path refs only | done |
| 31 | `agents/start.md` | `references/agents/start.md` | Path refs; flat-chain routing | done |
| 32 | `agents/subagent-factory.md` | `references/agents/subagent-factory.md` | Path refs only | done |
| 33 | `agents/test-specialist.md` | `references/agents/test-specialist.md` | Path refs only | done |

**Excluded from agents count:** `agents/README.md` (index, not a specialist brief).

---

## Rules (5 → `references/rules/`)

Source: `Desktop/git/.cursor/rules/<path>.mdc`  
Target: `skills/multi-agent-ecosystem/references/rules/<path>.mdc`

| # | Source | Target | Adaptation | Status |
|---|--------|--------|------------|--------|
| 1 | `rules/aleksander.mdc` | `references/rules/aleksander.mdc` | DUA + ZCode invocation cross-refs | done |
| 2 | `rules/coding-guardrails.mdc` | `references/rules/coding-guardrails.mdc` | Path refs only | done |
| 3 | `rules/orchestrator.mdc` | `references/rules/orchestrator.mdc` | `Task()` → ZCode delegation language | done |
| 4 | `rules/specialists.mdc` | `references/rules/specialists.mdc` | Routing table → `references/orchestration/routing-table.md` | done |
| 5 | `rules/agent-manager/agent-manager.mdc` | `references/rules/agent-manager/agent-manager.mdc` | Preserve subdir | done |

---

## Skills (25 → `references/skills/`)

Source: `Desktop/git/.cursor/skills/<name>/SKILL.md`  
Target: `skills/multi-agent-ecosystem/references/skills/<name>.md` (flat file, not nested `SKILL.md`)

| # | Source | Target | Adaptation | Status |
|---|--------|--------|------------|--------|
| 1 | `skills/agent-evals/SKILL.md` | `references/skills/agent-evals.md` | Flatten path; front matter preserved | done |
| 2 | `skills/agent-manager/SKILL.md` | `references/skills/agent-manager.md` | Flatten path | done |
| 3 | `skills/agent-prompt-quality/SKILL.md` | `references/skills/agent-prompt-quality.md` | Flatten path | done |
| 4 | `skills/agent-quality-pipeline/SKILL.md` | `references/skills/agent-quality-pipeline.md` | Flatten path | done |
| 5 | `skills/agent-system-navigation/SKILL.md` | `references/skills/agent-system-navigation.md` | Flatten path | done |
| 6 | `skills/caid-worktrees/SKILL.md` | `references/skills/caid-worktrees.md` | Flatten path | done |
| 7 | `skills/circuit-breaker/SKILL.md` | `references/skills/circuit-breaker.md` | Flatten path | done |
| 8 | `skills/context-propagation/SKILL.md` | `references/skills/context-propagation.md` | Flatten path | done |
| 9 | `skills/dag-validation/SKILL.md` | `references/skills/dag-validation.md` | Flatten path | done |
| 10 | `skills/mcp-governance/SKILL.md` | `references/skills/mcp-governance.md` | Flatten path | done |
| 11 | `skills/model-routing/SKILL.md` | `references/skills/model-routing.md` | Flatten path | done |
| 12 | `skills/multi-pass-autonomy/SKILL.md` | `references/skills/multi-pass-autonomy.md` | Flatten path | done |
| 13 | `skills/orchestrator/SKILL.md` | `references/skills/orchestrator.md` | Flatten path; link to `references/orchestration/` | done |
| 14 | `skills/project-plan-dot-plan/SKILL.md` | `references/skills/project-plan-dot-plan.md` | Flatten path | done |
| 15 | `skills/repo-task-proof-loop/SKILL.md` | `references/skills/repo-task-proof-loop.md` | Flatten path | done |
| 16 | `skills/session-memory-tiers/SKILL.md` | `references/skills/session-memory-tiers.md` | Flatten path | done |
| 17 | `skills/specialist-discovery/SKILL.md` | `references/skills/specialist-discovery.md` | Flatten path | done |
| 18 | `skills/start-workflow/SKILL.md` | `references/skills/start-workflow.md` | Flatten path; overlaps orchestration runbook | done |
| 19 | `skills/structured-agent-logging/SKILL.md` | `references/skills/structured-agent-logging.md` | Flatten path | done |
| 20 | `skills/structured-policy-yaml/SKILL.md` | `references/skills/structured-policy-yaml.md` | Flatten path | done |
| 21 | `skills/subagent-factory/SKILL.md` | `references/skills/subagent-factory.md` | Flatten path | done |
| 22 | `skills/telemetry-pipeline/SKILL.md` | `references/skills/telemetry-pipeline.md` | Flatten path | done |
| 23 | `skills/thinking-checkpoints/SKILL.md` | `references/skills/thinking-checkpoints.md` | Flatten path | done |
| 24 | `skills/tool-output-sanitization/SKILL.md` | `references/skills/tool-output-sanitization.md` | Flatten path | done |
| 25 | `skills/web-research-fact-pack/SKILL.md` | `references/skills/web-research-fact-pack.md` | Flatten path | done |

**Excluded from skills count:** `skills/README.md` (index).  
**Post-migration index:** `references/skills/INDEX.md` (sibling branch; not a source mapping).

---

## Supplementary mappings

These are **outside** the 63 primary files but required for a complete ZCode plugin.

### Master skill

| Source (synthesized) | Target | Notes |
|---------------------|--------|-------|
| `agents/start.md` + `agents/orchestrator.md` + `rules/*.mdc` + `skills/start-workflow/SKILL.md` | `SKILL.md` | Master entry; progressive disclosure; ZCode adaptation table |

### Orchestration runbooks (`references/orchestration/`)

| Source | Target | Notes |
|--------|--------|-------|
| `docs/delegation-chain.md` | `references/orchestration/delegation-chain.md` | Flat-chain routing canon |
| `docs/start-workflow.md` | `references/orchestration/start-workflow.md` | Operator handoff |
| `docs/evidence-first-acceptance.md` | `references/orchestration/evidence-first-acceptance.md` | PBI-006 acceptance |
| `docs/process-and-quality-gates.md` | `references/orchestration/process-and-quality-gates.md` | Quality gates |
| — (synthesized) | `references/orchestration/routing-table.md` | From `rules/specialists.mdc` routing |
| — (synthesized) | `references/orchestration/completion-contracts.md` | From `rules/orchestrator.mdc` §5 |
| — (synthesized) | `references/orchestration/zcode-paths.md` | Plugin path policy |
| — (synthesized) | `references/orchestration/README.md` | On-demand load index |

### Slash commands (plugin root)

| Source agent | Target command | Notes |
|--------------|----------------|-------|
| `agents/start.md` | `commands/start.md` | `/start` entry |
| `agents/orchestrator.md` | `commands/orchestrator.md` | `/orchestrator` entry |
| Each specialist `agents/<name>.md` | `commands/<name>.md` | Optional; parallel branch |

---

## Verification

### Count verification table

| Category | Expected source | Expected target files | Manifest rows | Complete |
|----------|----------------|----------------------|---------------|----------|
| Agents | 33 | 33 in `references/agents/` | 33 | yes |
| Rules | 5 | 5 in `references/rules/` | 5 | yes |
| Skills | 25 | 25 in `references/skills/` | 25 | yes |
| **Primary** | **63** | **63** | **63** | **100%** |

### Spot-check instructions (reviewers)

1. **Agent count**
   ```bash
   ls /Users/ndppd/Desktop/git/.cursor/agents/*.md | grep -v README | wc -l   # expect 33
   ls skills/multi-agent-ecosystem/references/agents/*.md | wc -l               # expect 33 (+ README optional)
   ```

2. **Rules count**
   ```bash
   find /Users/ndppd/Desktop/git/.cursor/rules -name '*.mdc' | wc -l            # expect 5
   find skills/multi-agent-ecosystem/references/rules -name '*.mdc' | wc -l     # expect 5
   ```

3. **Skills count**
   ```bash
   find /Users/ndppd/Desktop/git/.cursor/skills -mindepth 2 -name 'SKILL.md' | wc -l   # expect 25
   ls skills/multi-agent-ecosystem/references/skills/*.md | grep -v INDEX | wc -l      # expect 25
   ```

4. **Basename parity** — every source agent basename must exist as target:
   ```bash
   for f in /Users/ndppd/Desktop/git/.cursor/agents/*.md; do
     base=$(basename "$f")
     [[ "$base" == "README.md" ]] && continue
     test -f "skills/multi-agent-ecosystem/references/agents/$base" || echo "MISSING: $base"
   done
   ```

5. **Skill flatten check** — each `skills/<name>/SKILL.md` maps to `references/skills/<name>.md` (not `references/skills/<name>/SKILL.md`).

6. **Internal links** — after migration, grep migrated files for stale `agents/`, `rules/`, `.cursor/` paths; expect `references/` prefixes.

7. **Orchestration subset** — confirm `references/orchestration/delegation-chain.md` and `evidence-first-acceptance.md` exist and cross-link from master `SKILL.md`.

---

## Intentionally NOT migrated

| Path / artifact | Reason |
|-----------------|--------|
| `benchmarks/` | Eval fixtures and behavior contracts for CI; not runtime agent policy. ZCode plugin can add its own eval harness later. |
| `scripts/` | Repo validation (`validate-agent-registry.py`, `run-behavior-benchmarks.py`, etc.) — Cursor-repo tooling, not skill content. |
| `profiles/` | Project-specific overlays (e.g. `profiles/msnmp/` pentest pipeline) — user/project scope, not core ecosystem. |
| `docs/` (bulk) | 30+ reference docs; **orchestration subset only** migrated to `references/orchestration/`. Remainder is historical/vision docs. |
| `reports/` | One-off audit reports (architecture, security wave1) — not operational policy. |
| `agent-tasks/` | Task tracking artifacts for the source repo delivery process. |
| `.github/workflows/` | CI for source repo, not ZCode plugin runtime. |
| `agents/README.md`, `skills/README.md` | Index files; replaced by `references/skills/INDEX.md` and orchestration README. |
| `.cursor/` mirror concept | ZCode uses a single canonical tree under the plugin; no IDE mirror sync. |
| `delivery/` PBI folders | Product backlog in source repo; optional future `docs/delivery/` in plugin if needed. |

---

## Parallel branch status

At manifest creation time, sibling branches may have already populated targets. Reconcile `Status` column after wave completes:

- `references/agents/` — populated by agent migration branch
- `references/rules/` — populated by rules migration branch
- `references/skills/` — populated by skills migration branch
- `SKILL.md` — master skill branch
- `references/orchestration/` — orchestration synthesis branch
- `commands/` — slash command branch

Update each row from `pending` → `done` when the target file exists and passes spot-check #6.

---

## Manifest metadata

| Field | Value |
|-------|-------|
| Manifest path | `skills/multi-agent-ecosystem/MANIFEST.md` |
| Primary mappings | 63 |
| Mapping completeness | 100% |
| Created | 2026-06-23 |
| Owner branch | B0-8 |
