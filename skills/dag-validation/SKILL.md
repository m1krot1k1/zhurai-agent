---
name: dag-validation
description: DAG (Directed Acyclic Graph) validation for agent delegation dependencies
requires: none
---

# DAG Validation

## Purpose
Валидация графа зависимостей перед делегированием для предотвращения deadlock и circular dependencies.

## Validation Rules

### 1. No Cycles
- Проверка: DFS от каждого узла
- При обнаружении цикла → REJECT с указанием цикла
- Example: A → B → C → A = CYCLE

### 2. No Missing Dependencies
- Все зависимости должны ссылаться на существующих агентов
- Example: A depends on X, но X не в agents/ → MISSING

### 3. No Self-Dependencies
- Агент не может зависеть от себя
- Example: A depends on A → SELF_DEP

### 4. No Cross-Level Dependencies
- L3 specialist не может зависеть от L1 orchestrator
- Направление: только вниз по уровням или в пределах уровня
- Example: code → orchestrator → CROSS_LEVEL

### 5. Ownership Validation
- Каждая задача имеет одного владельца
- Нет shared ownership между агентами

### 6. Max Chain Length
- Максимальная цепочка зависимостей: 10
- Example: A → B → C → ... → J (10) = OK
- Example: A → B → ... → K (11) → CHAIN_TOO_LONG

## Validation Algorithm

```text
1. Build dependency graph from task specs
2. Check for cycles (DFS with coloring)
3. Check for missing nodes
4. Check for self-deps
5. Check level constraints
6. Calculate longest path
7. Return validation result
```

**Example: pre-delegation DAG validation output**

```yaml
dag_validation:
  graph:
    B0-1: {depends_on: []}
    B0-2: {depends_on: [B0-1]}
    B0-3: {depends_on: [B0-1]}
    B0-4: {depends_on: [B0-2, B0-3]}
  checks:
    cycles: {result: pass, detail: "no cycles detected"}
    missing_nodes: {result: pass, detail: "all dependencies exist"}
    self_deps: {result: pass, detail: "no self-references"}
    cross_level: {result: pass, detail: "dependencies point only downward"}
    max_chain: {result: pass, detail: "longest chain = 3 (cap: 10)"}
  verdict: VALID
```

## Integration
- Вызывать перед Task() в orchestrator
- Результат: VALID или REJECT с diagnostic
- Логировать в telemetry (policy.violation)
