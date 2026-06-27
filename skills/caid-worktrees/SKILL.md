---
name: caid-worktrees
description: Concurrent Agent Isolation via git worktrees per delegation branch
requires: none
---

> **Применимость**: требует git worktree isolation. Неприменимо в контексте single-user Cursor IDE без worktree-ов. В текущей экосистеме используется CAID-совместимая альтернатива с OWNERSHIP-контрактами (см. `rules/orchestrator.mdc` §1.3 CAID git attribution). Полная CAID-изоляция через git worktrees — следующий шаг эволюции системы.

# CAID Worktrees

## Purpose
Изоляция параллельных задач через git worktrees для предотвращения конфликтов и обеспечения атомарного коммита.

## Workflow

### 1. Branch Creation
```
Root task → create main branch: task/{trace_id}
Each delegation branch → create worktree: worktrees/{branch_id}
```

### 2. Isolation
- Каждый агент работает в своём worktree
- Нет доступа к файлам других агентов
- Конфликты обнаруживаются при merge

### 3. Diff Collection
- После завершения ветки → collect diff
- Diff добавляется в evidence контракта
- Формат: unified diff с контекстом

### 4. Synthesis & Merge
- Orchestrator synthesizes результаты и выбирает порядок интеграции
- Sequential merge выполняет delegated git-ветка или `devops-specialist`, не orchestrator напрямую
- При конфликте → delegated merge branch resolve или escalate

### 5. Cleanup
- После успешного merge → delete worktree
- При abort → delete branch + worktree

## Configuration
```yaml
caid:
  worktree_base_dir: ".caid/worktrees"
  branch_prefix: "task/"
  max_concurrent_worktrees: 6
  auto_cleanup: true
  merge_strategy: "sequential"  # sequential | parallel
```

## Benefits
- Полная изоляция параллельных задач
- Атомарный коммит результатов
- Возможность rollback через git
- Audit trail через git history

<!-- Merged from caid-ownership-matrix/SKILL.md on 2026-06-09. Content from caid-ownership-matrix begins below. -->

## OWNERSHIP Matrix (merged from caid-ownership-matrix)

### Purpose
When multiple branches write files concurrently, **overlap is a merge and audit hazard**. `rules/orchestrator.mdc` **§3** (Parallel writer safety: disjoint OWNERSHIP, exclusive globs) and **§1.3** (CAID git attribution at branch completion) define the canonical rules. This section operationalizes a simple **ownership matrix** and commit ceremony.

### When to Use
- Orchestrator plans **2+ writer branches** in one wave
- Builders need clear **file/glob exclusive** assignments before execution
- You need post-branch **git attribution** commits per branch

### Workflow

#### Step 1: Build the OWNERSHIP Matrix Before Execution
1. For each branch: list **exclusive** `OWNERSHIP` as exact paths or globs. Cross-check pairwise intersection; if any overlap → split scope or serialize.
2. Record `Branch ID` (e.g. `B0-1`), parent, level, dependencies.
3. Flag **reader-only** branches (review/security): they should not claim write OWNERSHIP.

#### Step 2: Execute Writes Strictly Inside OWNERSHIP
1. Writers refuse out-of-scope paths; escalations go to orchestrator for re-planning.
2. **3+ parallel writer-branches** (any agent type that modifies files): escalate to orchestrator for OWNERSHIP management. **Reader-branches** (code-reviewer, security-auditor, ask, repo-explorer) are exempt — unlimited parallel fan-out.
3. On conflict at commit time: run `git status`, resolve **overlap** before any CAID commit.

#### Step 3: CAID Commit via devops-specialist Pattern
1. After a writer branch completes, **`devops-specialist`** (or policy-approved commit actor) stages **only** files from that branch's OWNERSHIP contract.
2. Commit message template: `[{branch_id}] {objective} — agent:{owner}`.
3. Synthesis wave close: optional aggregate commit (`[synthesis] wave-N complete — …`) when policy calls for it.

### CHECKLIST
- [ ] Pairwise disjoint OWNERSHIP verified for all parallel writers
- [ ] Branch ID + owner recorded for each writer branch
- [ ] No reader branch forced into writer CAID commit
- [ ] Staged files ⊆ OWNERSHIP before CAID commit
