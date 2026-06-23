# Канонические пути и зеркало `.cursor/`

## Политика

- **Канон:** корень репозитория — `rules/`, `agents/`, `skills/`, `docs/` (и прочие согласно `rules/specialists.mdc`). Правки по умолчанию вносятся **туда**.
- **Зеркало:** при наличии каталога `.cursor/` в корне репозитория IDE может держать **копию** части дерева для runtime. Это зеркало **не** считается primary-источником state_map, сканов и владения ветками без явного запроса пользователя.
- **Вложенное** `/.cursor/.cursor/**` внутри конфиг-репо пользователь может запретить трогать отдельно; согласованность с каноном для таких путей этим документом не задаётся.

## Проверка расхождений (измеримая)

| Действие | Команда | Успех |
|----------|---------|--------|
| Полный прогон с предупреждениями по зеркалу | `./scripts/run-full-repo-benchmark.sh --check-mirror` или `python3 scripts/run-full-repo-benchmark.py --check-mirror` | Процесс завершается с кодом **0**; в логе шага `validate-repo-consistency` при расхождениях — строки `[mirror]` (предупреждения, не фатальные ошибки). |
| Только валидатор с зеркалом | `CHECK_CURSOR_MIRROR=1 python3 scripts/validate-repo-consistency.py` | Код **0** если нет ошибок `errors`; предупреждения `[mirror]` печатаются в stderr. |

Переменная **`CHECK_CURSOR_MIRROR`**: включает сравнение байт файлов между корнем и `.cursor/` для каталогов `rules`, `agents`, `skills`, `docs`, `scripts` (см. `scripts/validate-repo-consistency.py`: `MIRROR_SYNC_DIRS`, `check_root_mirror_drift`).

Значения, при которых проверка **включена:** `1`, `true`, `yes`, `on` (без учёта регистра).

**Локально по умолчанию** `./scripts/run-full-repo-benchmark.sh` **без** `--check-mirror` выставляет `CHECK_CURSOR_MIRROR=0` — drift зеркала не проверяется. **CI** (`.github/workflows/repo-validation.yml`) вызывает прогон **с** `--check-mirror`, чтобы расхождения с `.cursor/**` были видны в логах шага `validate-repo-consistency`.

## Ручной fallback

Если нужно сравнить один файл без скрипта:

```bash
cmp -s rules/orchestrator.mdc .cursor/rules/orchestrator.mdc && echo "match" || echo "drift"
```

(Пути приведены как пример; при отсутствии зеркального файла `cmp` сообщит об ошибке.)
