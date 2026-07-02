---
name: multi-agent-ecosystem
description: "Оркестрация multi-domain задач через delegate_task. 33 агента, parallel branches, evidence-first."
---

# Multi-Agent Ecosystem

Система из **33 агентов** для сложных задач. Единственный инструмент оркестрации: **`delegate_task`**.

## Цепочка вызова

```
/start → delegate_task(role=orchestrator) → delegate_task(tasks=[специалисты]) → синтез
```

## Императивные правила

### /start (роутер)
1. **Первый вызов — `delegate_task`.** Не писать сообщение, не читать код, не задавать вопросов.
2. `delegate_task(role="orchestrator", goal="<задача>", context="ORIGINAL_REQUEST: <текст>")`
3. После получения результата от orchestrator — передать пользователю.

### Orchestrator (декомпозиция)
1. Прочитать `agents/orchestrator.md` и `agents/start.md`
2. Разбить задачу на независимые ветки
3. **`delegate_task(tasks=[{goal, context + AGENT_BRIEF_PATH}, ...])`** — параллельные ветки
4. Синтезировать результаты, предоставить evidence

### Специалисты (исполнители)
- Читают свой brief из `agents/<name>.md`
- Выполняют задачу в своей области
- Возвращают completion contract с evidence

## Routing (кратко)

| Ситуация | Действие |
|----------|----------|
| 2+ домена / несколько артефактов | `delegate_task` → orchestrator |
| Простой вопрос | Ответить напрямую |
| 1 файл, 1 задача | Выполнить напрямую |
| 3+ параллельных writer | Обязательно orchestrator |

## Агенты

33 агента в `agents/<name>.md`:
- **code.md** — реализация/багфикс
- **frontend-specialist.md** — React/UI/frontend
- **test-specialist.md** — тесты/TDD
- **security-auditor.md** — безопасность
- **code-reviewer.md** — ревью кода
- **debug.md** — отладка/root cause
- **architect.md** — архитектура
- **devops-specialist.md** — CI/CD/Docker
- **docs-specialist.md** — документация
- и 24 других специалиста

## Completion contract

Каждая ветка возвращает:
```yaml
files_changed: [paths]
checks:
  - name: <command>
    result: pass|fail
    evidence: <output>
confidence: high|medium|low
```