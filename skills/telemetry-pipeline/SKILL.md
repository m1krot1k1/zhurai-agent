---
name: telemetry-pipeline
description: Agent telemetry collection and analysis pipeline
requires: none
---

# Telemetry Pipeline

## Purpose
Сбор, агрегация и анализ метрик работы системы агентов для мониторинга и оптимизации.

## Metric Categories

### 1. Task Metrics
- `task.created` — задача создана
- `task.completed` — задача завершена
- `task.failed` — задача провалена
- `task.duration_ms` — время выполнения
- `task.depth` — глубина делегирования

### 2. Tool Metrics
- `tool.call` — вызов инструмента
- `tool.error` — ошибка инструмента
- `tool.duration_ms` — время вызова
- `tool.token_usage` — использование токенов

### 3. Quality Metrics
- `quality.contract_valid` — контракт валиден
- `quality.evidence_score` — качество evidence (0-1)
- `quality.confidence` — уверенность агента (0-1)
- `quality.rework_count` — количество переделок

### 4. Circuit Breaker Metrics
- `circuit.state` — состояние (closed/open/half-open)
- `circuit.trip_count` — количество срабатываний
- `circuit.recovery_time_ms` — время восстановления

### 5. Retry Metrics
- `retry.attempt` — попытка повтора
- `retry.budget_remaining` — оставшийся бюджет
- `retry.exhausted` — бюджет исчерпан

### 6. Policy Metrics
- `policy.violation` — нарушение политики
- `policy.type` — тип нарушения
- `policy.severity` — критичность (critical/high/medium/low)

### 7. Verification Metrics
- `verify.passed` — проверка пройдена
- `verify.failed` — проверка провалена
- `verify.type` — тип проверки (contract/benchmark/transcript)

## Collection Format
```json
{
  "trace_id": "uuid",
  "timestamp": "ISO8601",
  "agent": "agent-name",
  "metric": "category.name",
  "value": "number|string",
  "tags": {"key": "value"}
}
```

## Analysis
- Агрегация по trace_id для end-to-end tracing
- Percentile calculation (p50, p95, p99) для duration
- Trend analysis для quality metrics
- Alert thresholds для error rates

**Example: telemetry aggregation query pattern**

```json
{
  "query": "aggregate_by_trace",
  "trace_id": "c00-01",
  "window": "5m",
  "metrics": [
    {"name": "task.duration_ms", "agg": "sum", "value": 45200},
    {"name": "task.depth", "agg": "max", "value": 3},
    {"name": "tool.token_usage", "agg": "sum", "value": 124500},
    {"name": "quality.rework_count", "agg": "sum", "value": 1},
    {"name": "retry.exhausted", "agg": "count", "value": 0},
    {"name": "verify.failed", "agg": "count", "value": 0}
  ],
  "percentiles": {
    "tool.duration_ms": {"p50": 120, "p95": 3400, "p99": 8900}
  },
  "alerts": [
    {"metric": "quality.rework_count", "threshold": ">2", "triggered": false},
    {"metric": "retry.exhausted", "threshold": ">0", "triggered": false}
  ]
}
```
