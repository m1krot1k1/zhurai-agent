---
name: specialist-discovery
description: Таблица субагентов и условия их выбора, включая динамическое обнаружение на основе индекса возможностей и исторической производительности.
requires: none
---

## ЦЕЛЬ

Быстро найти нужного субагента для делегирования — через статическую таблицу или динамический scoring.

## ТАБЛИЦА СУБАГЕНТОВ

| Задача | Агент |
|--------|-------|
| Архитектурное решение / ADR | `@architect` |
| Дизайн агентов и rules | `@agent-architect` |
| Написание / рефакторинг кода | `@code` |
| Ревью PR / кода | `@code-reviewer` |
| Диагностика бага | `@bug-triage` |
| Отладка / root cause analysis | `@debug` |
| Формальный git-diff review | `@review` |
| Стресс-тест плана / верификация | `@code-skeptic` |
| Управление агентами экосистемы | `@agent-manager` |
| Тест-стратегия, тесты | `@test-specialist` |
| REST/gRPC контракты | `@api-designer` |
| Схемы БД, миграции | `@database-specialist` |
| CI/CD, инфраструктура | `@devops-specialist` |
| UI/UX, компоненты | `@frontend-specialist` |
| iOS / Android | `@mobile-specialist` |
| Данные, метрики, EDA | `@data-analyst` |
| Исследование кодовой базы | `@repo-explorer` |
| OWASP, CVE, threat model | `@security-auditor` |
| Latency, CPU, память | `@performance-optimizer` |
| Снижение сложности | `@code-simplifier` |
| README, ADR, CHANGELOG | `@docs-specialist` |
| Changelog, release notes | `@release-manager` |
| Observability, алерты | `@monitoring-specialist` |
| API / сторонние провайдеры | `@provider-integrator` |
| Управление профилями | `@profile-manager` |
| Новые агенты | `@meta-agent-architect` |
| Сборка агентных пакетов | `@subagent-factory` |
| Обновление *.mdc правил | `@rules-specialist` |
| Создание / обновление SKILL.md | `@skills-specialist` |
| Контракты поведения, бенчмарки | `@benchmark-specialist` |
| Уточнить задачу | `@ask` |
| Долгосрочный план / PBI | `@start` |

## ДОПОЛНИТЕЛЬНО

- Профили пользователей: `profiles/<name>/` — применять автоматически при наличии
- Неизвестный агент — `@repo-explorer` для поиска, затем `@agent-architect` для создания

## ДИНАМИЧЕСКОЕ ОБНАРУЖЕНИЕ

Автоматическое обнаружение и маршрутизация к специалистам на основе актуального индекса возможностей и исторической производительности.

### Specialist Index

```yaml
specialists:
  - name: code
    file: agents/code.md
    keywords: [implementation, coding, development, refactoring]
    cost_tier: 2          # 1=cheap, 2=medium, 3=expensive
    success_rate: 0.95    # обновляется из telemetry
    avg_duration_ms: 45000
    total_tasks: 150
    last_active: "2026-04-04T10:00:00Z"
```

### Scoring Algorithm

```
score(specialist, task) = 
  keyword_match * 0.4 +
  success_rate * 0.3 +
  (1 - cost_tier/3) * 0.15 +
  recency_factor * 0.15

where:
  keyword_match = overlap(task_keywords, specialist.keywords) / len(task_keywords)
  recency_factor = 1.0 if last_active < 24h else 0.5
```

### Discovery Process

1. Scan `agents/*.md` для актуального списка
2. Извлечь keywords из frontmatter
3. Рассчитать score для каждого кандидата
4. Выбрать top-N (default N=3)
5. Предложить orchestrator для финального выбора

### Auto-Update

- `success_rate` обновляется после каждого `task.completed`
- `last_active` обновляется при каждом вызове
- Индекс пересчитывается каждые 100 задач или 1 час
