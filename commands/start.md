---
skills: multi-agent-ecosystem
description: Entry point for complex tasks — routes to orchestrator pattern without executing work directly.
argument-hint: "[task description or goal]"
---

# Start router mode

**ORIGINAL_REQUEST:** $ARGUMENTS

## Repo root

`ZHUR_AI_AGENT_ROOT` или корень установки zhur.ai-agent (где лежат `agents/`, `skills/`).

## Load skill (required)

1. Если доступен skill **`start`** или **`multi-agent-ecosystem`** — загрузи и работай в **start router** mode.
2. Иначе прочитай:
   - `skills/start/SKILL.md`
   - `skills/multi-agent-ecosystem/SKILL.md`

## FIRST_READ (перед работой)

- `skills/multi-agent-ecosystem/references/rules/aleksander.mdc`
- `skills/multi-agent-ecosystem/references/rules/specialists.mdc`
- `skills/multi-agent-ecosystem/references/orchestration/delegation-chain.md`

## Router obligations

1. Не читай репо и не меняй файлы до решения о маршруте.
2. Передавай ORIGINAL_REQUEST **дословно** в `/orchestrator`.
3. Multi-domain → **`/orchestrator`**.
4. Простой вопрос без правок → **ask**, ответ напрямую.
5. Не отказывай в задаче пользователя.
