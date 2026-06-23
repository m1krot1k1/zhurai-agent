---
name: context-propagation
description: "Structured context envelope for reliable state propagation between agents"
requires: none
---

> **Reference doc** — loaded on-demand from `references/skills/`. Not a separate ZCode skill; use when the master `multi-agent-ecosystem` skill or an agent brief points here.


# Context Propagation

## Purpose
Структурированная передача контекста между агентами через единый формат envelope.

## Context Envelope Format

```yaml
context_envelope:
  # Trace metadata
  trace_id: "uuid"
  parent_trace_id: "uuid|null"
  created_at: "ISO8601"
  
  # Task context
  objective: "one-line objective"
  scope: "scope boundaries"
  
  # Completed work
  completed_branches:
    - agent: "agent-name"
      objective: "sub-task objective"
      result: "summary"
      evidence: ["file:line", ...]
      confidence: 0.9
  
  # Shared context
  context_files:
    - path: "relative/path"
      relevance: "high|medium|low"
      summary: "brief description"
  
  # Risk tracking
  open_risks:
    - description: "risk description"
      severity: "high|medium|low"
      mitigation: "mitigation strategy"
  
  # Budget tracking
  budget:
    depth_current: 3
    depth_max: 10
    tool_calls_current: 5
    tool_calls_max: 20
    retry_remaining: 2
```

## Propagation Rules
1. Envelope передаётся с КАЖДОЙ ZCode sub-session delegation
2. Агент добавляет свой результат в completed_branches
3. Агент обновляет budget counters
4. Агент добавляет/обновляет open_risks
5. При context compaction — суммаризировать completed_branches

## Validation
- trace_id ОБЯЗАТЕЛЕН
- completed_branches не может быть пустым если depth_current > 0
- budget.depth_current <= budget.depth_max

## Context Versioning

### Version Format
```yaml
context_version: "1.0"
schema_version: "2026-04"
```

### Versioning Rules
- Major version (1.0 → 2.0): breaking changes в формате envelope
- Minor version (1.0 → 1.1): additive changes, backward compatible
- Schema version: YYYY-MM для отслеживания даты изменения

### Compatibility
- Агент ДОЛЖЕН поддерживать текущую и предыдущую major версию
- При несовместимой версии → error "CONTEXT_VERSION_MISMATCH"
- Migration guide в docs/ при major version change

### Current Version
- context_version: "1.0"
- schema_version: "2026-04"
