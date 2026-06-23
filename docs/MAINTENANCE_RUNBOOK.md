# Maintenance Runbook

Пошаговые инструкции по обслуживанию репозитория конфигурации агентной системы.

---

## Добавление нового агента

1. Создать `agents/<name>.md` с YAML-frontmatter:
   ```yaml
   ---
   name: <name>        # должно точно совпадать с именем файла (без .md)
   description: <...>  # одна строка: what it does + when to use
   ---
   ```
2. Добавить в `agents/README.md` — в нужную секцию таблицы (`Planning & Architecture` / `Development` / ...).
3. Добавить routing-строку в `rules/specialists.mdc` — в список «When to delegate».
4. Обновить счётчики в трёх местах:
   - `agents/README.md` — первая строка `*N agent definitions (4 coordination + M domain specialists in core)*`
   - `rules/specialists.mdc` — `**N agent definitions**` и `**M**` domain specialists
   - `README.md` (корень) — `**N agent definitions**`
5. Если агент для GitHub Copilot — создать `.github/agents/<name>.agent.md` (формат `.agent.md`).
6. Запустить валидаторы:
   ```bash
   bash scripts/validate-agent-registry.sh
   bash scripts/run-behavior-benchmarks.sh
   ```

---

## Переименование агента

1. Переименовать файл: `agents/<old>.md` → `agents/<new>.md`
2. Обновить `name:` в YAML-frontmatter.
3. Найти и заменить все упоминания `<old>` в:
   - `agents/README.md`
   - `rules/specialists.mdc`
   - `rules/orchestrator.mdc`
   - `.github/agents/` — переименовать `<old>.agent.md` → `<new>.agent.md`
   - `benchmarks/behavior-contracts.json` — обновить паттерны
4. Запустить валидаторы (см. выше).

---

## Удаление агента

1. Удалить `agents/<name>.md`.
2. Удалить из таблицы в `agents/README.md` и обновить счётчики.
3. Удалить routing-строку из `rules/specialists.mdc` и обновить счётчики.
4. Обновить корневой `README.md`.
5. Удалить `.github/agents/<name>.agent.md` если есть.
6. Удалить из `benchmarks/behavior-contracts.json` все `required_regex` / `required_paths`, которые зависят от этого агента.
7. Запустить валидаторы.

---

## Устаревание (deprecation) агента

Если агент заменяется другим, не удаляя сразу:
1. В YAML-frontmatter добавить: `description: "DEPRECATED: переименован в <new>. Используйте agents/<new>.md"`
2. В начало файла добавить redirect-секцию: `# DEPRECATED — redirect only`
3. В `agents/README.md` переместить в раздел `### Deprecated`.
4. Убрать routing-строку из `rules/specialists.mdc` (не уменьшая счётчик, если файл остался).

---

## Создание нового skill

1. Создать директорию `skills/<name>/`.
2. Создать `skills/<name>/SKILL.md` с YAML-frontmatter:
   ```yaml
   ---
   name: <name>
   description: <одна строка: что делает skill и когда применять>
   ---
   ```
3. Добавить строку в таблицу `skills/README.md`.
4. Если skill реализует политику из `rules/orchestrator.mdc` — добавить в конец SKILL.md раздел `## Policy Reference`: `Реализует rules/orchestrator.mdc §X`.

**Когда создавать новый skill vs расширять существующий:**
- Новый skill: самостоятельный повторяемый workflow со своим жизненным циклом (например, `repo-task-proof-loop`).
- Расширение существующего: вариант или подпаттерн уже существующего workflow.

---

## Устаревание (deprecation) skill

1. В `skills/<name>/SKILL.md` обновить `description:` → `"DEPRECATED: …. См. skills/<new>/SKILL.md"`.
2. В `skills/README.md` переместить из основной таблицы в раздел `### Deprecated`.
3. Обновить все ссылки в агентах и правилах на новый skill.

---

## Обновление правил (rules/*.mdc)

1. Редактировать `rules/<file>.mdc`.
2. Если изменение касается маршрутизации агентов — проверить `rules/specialists.mdc` и `agents/README.md`.
3. Если добавляется новое правило для оркестрации — обновить соответствующий behavior contract в `benchmarks/behavior-contracts.json`.
4. Запустить: `bash scripts/run-behavior-benchmarks.sh`

---

## Активация / деактивация профиля

Активация в host-проекте:
```bash
cp profiles/<name>/agents/*.md .cursor/agents/
cp profiles/<name>/rules/*.mdc .cursor/rules/
```

Деактивация: удалить скопированные файлы из `.cursor/agents/` и `.cursor/rules/`.

Не коммитить profile-файлы в core `agents/` или `rules/` — это нарушает контракт `profile_isolation_enforced`.

---

## Валидация после изменений

```bash
# Быстрая проверка реестра агентов
bash scripts/validate-agent-registry.sh

# Полная проверка согласованности репозитория
bash scripts/validate-repo-consistency.sh

# Поведенческие контракты
bash scripts/run-behavior-benchmarks.sh

# Полный цикл (рекомендуется перед релизом)
bash scripts/run-full-repo-benchmark.sh
```

Смотрите также: [scripts/README.md](../scripts/README.md)

---

## Смотрите также

- [agents/README.md](../agents/README.md) — реестр всех агентов
- [rules/specialists.mdc](../rules/specialists.mdc) — routing и политика маршрутизации
- [skills/README.md](../skills/README.md) — реестр skills
- [docs/GLOSSARY.md](./GLOSSARY.md) — глоссарий терминов
- [benchmarks/README.md](../benchmarks/README.md) — behaviour contracts
