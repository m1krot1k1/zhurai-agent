---
name: model-routing
description: "Multi-model routing for cost optimization based on task complexity and ambiguity"
requires: none
---

> **Reference doc** — loaded on-demand from `references/skills/`. Not a separate ZCode skill; use when the master `multi-agent-ecosystem` skill or an agent brief points here.


# Multi-Model Routing

## Purpose
Оптимизация стоимости и производительности через маршрутизацию задач к разным моделям на основе сложности и неоднозначности задачи.

## Model Tiers

### Tier 1: Fast (дешёвые, быстрые)
- **Модели:** GPT-4o-mini, Claude Haiku, Gemini Flash
- **Стоимость:** $0.10-0.50 / 1M tokens
- **Латентность:** <1s
- **Применение:**
  - Простые задачи (классификация, извлечение)
  - Валидация контрактов
  - Форматирование, транслитерация
  - Pre-flight checks

### Tier 2: Balanced (средние)
- **Модели:** GPT-4o, Claude Sonnet, Gemini Pro
- **Стоимость:** $3-10 / 1M tokens
- **Латентность:** 2-5s
- **Применение:**
  - Стандартные задачи (код, анализ, ревью)
  - Большинство specialist задач
  - Context compaction

### Tier 3: Capable (дорогие, мощные)
- **Модели:** GPT-4, Claude Opus, Gemini Ultra
- **Стоимость:** $15-60 / 1M tokens
- **Латентность:** 5-15s
- **Применение:**
  - Сложные задачи (архитектура, стратегия)
  - Orchestrator synthesis
  - Ambiguous tasks с высокой неоднозначностью

## Routing Algorithm

### Ambiguity-Based Routing
```
ambiguity_score = calculate_ambiguity(task)

if ambiguity_score < 0.3:
  route_to = Tier 1 (Fast)
elif ambiguity_score < 0.7:
  route_to = Tier 2 (Balanced)
else:
  route_to = Tier 3 (Capable)
```

### Ambiguity Factors
- **Vague objective:** objective не конкретный → +0.2
- **Missing scope:** границы не определены → +0.2
- **Multiple domains:** задача затрагивает 2+ домена → +0.15
- **No acceptance criteria:** нет проверяемых условий → +0.2
- **High risk:** есть open_risks с severity=high → +0.1
- **Novel task:** нет historical success data → +0.15

### Cost Optimization
```
estimated_cost = estimate_tokens(task) * tier_price

if estimated_cost > budget_limit:
  try_lower_tier()  # понизить tier если возможно
  if cannot_lower:
    reject_with_reason("BUDGET_EXCEEDED")
```

### Fallback Chain
- Tier 1 failed → retry Tier 1 → escalate to Tier 2
- Tier 2 failed → retry Tier 2 → escalate to Tier 3
- Tier 3 failed → retry Tier 3 → BLOCKER

## Configuration
```yaml
model_routing:
  default_tier: 2  # Balanced
  ambiguity_thresholds:
    low: 0.3
    high: 0.7
  max_cost_per_task: 5.0  # USD
  max_cost_per_wave: 20.0  # USD
  retry_on_failure: true
  max_retries: 2
```

## Telemetry
- Логировать выбранный tier в telemetry (tool.token_usage)
- Отслеживать cost per task и cost per wave
- Мониторить quality score по tiers для оптимизации порогов

## Integration
- Вызывать перед ZCode sub-session delegation в orchestrator
- Результат routing добавлять в context_envelope
- Обновлять budget tracking
