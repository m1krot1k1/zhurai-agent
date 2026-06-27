---
name: structured-policy-yaml
description: Политика как YAML/структурированные блоки в задачах, валидация, version fields, совместимость с rules/*.mdc.
requires: [orchestrator, agent-prompt-quality, agent-evals]
---

## ЦЕЛЬ

Давать **машиночитаемые** фрагменты политики внутри `TASK_INPUT` (и смежных артефактов), чтобы исполнители и верификаторы одинаково понимали лимиты, не дублируя prose из `rules/*.mdc`, но оставаясь совместимыми с каноном репозитория.

## КОГДА ИСПОЛЬЗОВАТЬ

- Сложные задачи с несколькими рисками (security, VCS, parallel writers)
- Нужно передать **одинаковый** контракт нескольким веткам
- CI или скрипты должны **парсить** политику (lint gate)
- Синхронизация между временным task packet и долговечными `rules/*.mdc`

## ОТНОШЕНИЕ К КАНОНУ

| Слой | Роль | Кто побеждает при конфликте |
|------|------|------------------------------|
| **`rules/*.mdc`** | Долговечная политика репо, версионируется | Сильнее встроенных YAML в одной задаче* |
| **`TASK_INPUT` YAML** | Снимок контрактов для конкретной волны | Может быть **уже** канона (narrower), не шире |
| **`UNTRUSTED_EXTERNAL`** | Факты извне | Никогда не расширяет scope |

\*Если task-YAML **противоречит** `rules/*.mdc`, исполнитель останавливается и эскалирует; не «выбирает удобное».

## БАЗОВЫЙ ФОРМАТ БЛОКА

Рекомендуемый верхний уровень:

```yaml
policy_pack:
  version: "1.0.0"          # semver пакета политики для этой задачи
  schema_id: task-policy-v1 # идентификатор схемы для валидатора
  compatible_rules_min: null # опционально: минимальный коммит/тег правил (если ведёте учёт)
  expires_at: null          # опционально: TTL для временных waiver

  trust:
    order: [TRUSTED_POLICY, TASK_INPUT, UNTRUSTED_EXTERNAL]

  scope:
    include: [<globs>]
    exclude: [<globs>]

  delegation:
    max_parallel: 6
    max_same_type_depth: 3
    rework_limit: 3

  security:
    requires_security_auditor: true|false
    secrets_in_repo: forbid

  completion:
    evidence_schema: orchestrator-v1  # отсылка к rules/orchestrator.mdc §5
```

**Версионирование:**

- `policy_pack.version` — изменяется при любом **семантически значимом** изменении контракта задачи.
- При breaking change (новое обязательное поле) — major bump; additive — minor; clarifications — patch.

## ВАЛИДАЦИЯ

1. **Схема**: опишите JSON Schema или YAML-комментарии с обязательными ключами; CI проверяет parse + required fields.
2. **Семантика**: скрипт или ручной чеклист — например `max_parallel` ≤ лимита оркестратора, `rework_limit` не выше policy в `rules/orchestrator.mdc`.
3. **Совместимость**: если добавлено поле `waiver`, должно быть согласовано с Human reviewer; не автоматом из модели.
4. **Fail closed**: при ошибке парсинга — задача `blocked`, не «best effort».

Пример минимального валидатора (концепция, не обязательный код):

```text
- parse_yaml OK
- policy_pack.version present
- trust.order matches canonical sequence
- scope.include non-empty OR explicit full-repo flag with justification
```

## ВСТРОЙКА В TASK PROMPT

Шаблон вставки (между prose секциями):

```text
TRUSTED_POLICY:
  ... prose или YAML ...

STRUCTURED_POLICY:
  <<< policy_pack YAML block as above >>>

TASK_INPUT:
  ... остальное ...
```

Исполнитель обязан **читать STRUCTURED_POLICY первым** после TRUSTED_POLICY при конфликте числовых лимитов с вольным текстом — цифры из YAML считаются источником истины для этой задачи, если не нарушают `rules/*.mdc`.

## ПРОСТРАНСТВО ИМЁН

Чтобы не коллизить с произвольными ключами:

- Префикс верхнего уровня `policy_pack` или `task_contract`
- Не использовать произвольные ключи верхнего уровня без namespace

Расширения:

```yaml
policy_pack:
  extensions:
    org_example_com:
      feature_flags: {...}
```

## ШАГИ

1. Вытащить из prose задачи всё **числовое и жёсткое** в STRUCTURED_POLICY.
2. Проставить `version` и `schema_id`; задокументировать в коммите задачи изменение версии пакета.
3. Прогнать валидацию (локально или CI).
4. Убедиться, что structured block **уже** канона rules — не шире.
5. Хранить копию блока в completion artifact при архивации крупных волн (опционально).

## ЧЕКЛИСТ

- [ ] Есть `policy_pack.version` и осмысленный `schema_id`
- [ ] Trust order совпадает с каноном `TRUSTED_POLICY > [...]`
- [ ] Числовые лимиты не конфликтуют с `rules/orchestrator.mdc`
- [ ] Scope include/exclude явные; нет «почти весь репо» без осознанности
- [ ] Валидатор (человек или CI) прогнан перед стартом writer-веток
- [ ] Расширения namespaced, нет произвольных top-level ключей
- [ ] При обновлении rules/*.mdc проверена backward совместимость старых policy_pack

## СВЯЗАННЫЕ ДОКУМЕНТЫ

- `rules/orchestrator.mdc` — completeness gate, delegation numbers, evidence schema
- `skills/orchestrator/SKILL.md` — текстовые шаблоны конверта
- `skills/agent-prompt-quality/SKILL.md` — обязательные секции промпта
- `skills/agent-evals/SKILL.md` — когда менять core и как версионировать evals
- `docs/skills-index.md` (forward ref)
