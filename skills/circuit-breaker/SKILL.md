---
name: circuit-breaker
description: Circuit breaker pattern for preventing cascading failures in agent delegation
requires: none
---

# Circuit Breaker

## Purpose
Предотвращение каскадных сбоев при делегировании задач между агентами.

## States

### CLOSED (normal operation)
- Задачи делегируются нормально
- Мониторинг failure rate
- Переход в OPEN при failure_threshold

### OPEN (failures detected)
- Задачи НЕ делегируются агенту/сервису
- Immediate rejection с ошибкой "CIRCUIT_OPEN"
- Переход в HALF_OPEN после timeout

### HALF_OPEN (testing recovery)
- Пробная задача для проверки восстановления
- При success → CLOSED
- При failure → OPEN (сброс timeout)

## Configuration

```yaml
circuit_breaker:
  failure_threshold: 3        # consecutive failures to trip
  success_threshold: 2        # consecutive successes to close
  timeout_seconds: 300        # 5 minutes before half-open
  half_open_max_tasks: 1      # пробных задач в half-open
  tracked_failures:
    - task_failed
    - contract_violation
    - timeout_exceeded
    - quality_below_threshold
  tracked_successes:
    - task_completed
    - contract_valid
    - quality_above_threshold
```

## Integration Points
- Вызов перед Task() в orchestrator
- Проверка состояния целевого агента
- Логирование в telemetry pipeline (circuit.*)

## Recovery Flow
```
CLOSED → (3 failures) → OPEN
OPEN → (5 min timeout) → HALF_OPEN
HALF_OPEN → (2 successes) → CLOSED
HALF_OPEN → (1 failure) → OPEN
```
