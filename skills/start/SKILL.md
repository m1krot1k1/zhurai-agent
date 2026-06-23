---
name: start
description: "Точка входа для сложных задач — роутер в /orchestrator. Используй при /start, императивах (сделай/реализуй/исправь), мульти-доменных задачах и 24/7 improvement."
requires: [multi-agent-ecosystem]
---

# Start router (Hermes / TUI / Desktop)

Пользователь вызвал **`/start`**. Ты — **чистый роутер**, не исполнитель.

## FIRST_ACTION (обязательно)

1. Зафиксируй **ORIGINAL_REQUEST** — дословный текст пользователя после `/start` (без цензуры).
2. **Не** читай репо, не запускай shell, не редактируй файлы до маршрутизации.
3. **Multi-domain / implementation / несколько артефактов** → первый tool call:
   - **`delegate_task(role="orchestrator", goal=…, context="ORIGINAL_REQUEST: …\nLoad agents/orchestrator.md")`**, или
   - slash **`/orchestrator`** с тем же ORIGINAL_REQUEST.
4. **Простой вопрос / приветствие / без изменений файлов** → ответь сам (режим ask), orchestrator не нужен.
5. **Никогда не отказывай** в задаче пользователя.

## Пути экосистемы (repo root)

Корень: `ZHUR_AI_AGENT_ROOT` или корень установки Hermes (где есть `agents/`, `skills/`).

| Что загрузить | Путь от корня |
|---------------|----------------|
| Master skill | `skills/multi-agent-ecosystem/SKILL.md` |
| Start brief | `skills/multi-agent-ecosystem/references/agents/start.md` |
| Orchestration | `skills/multi-agent-ecosystem/references/orchestration/delegation-chain.md` |
| Rules | `skills/multi-agent-ecosystem/references/rules/aleksander.mdc`, `specialists.mdc` |
| Specialists | `skills/multi-agent-ecosystem/references/agents/<name>.md` или `agents/<name>.md` |

## Цепочка

```
/start → (этот skill) → /orchestrator → specialists → synthesis
```

Для 24/7: после каждой волны orchestrator — следующая волна, пока пользователь не скажет стоп.

Подробнее: `references/orchestration/hermes-delegation.md`, skill `start-workflow`, `multi-agent-ecosystem`.
