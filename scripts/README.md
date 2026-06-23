# Scripts

Скрипты обслуживания репозитория. Каждый скрипт поставляется в трёх платформах: `.sh` (Linux/macOS), `.py` (Python 3, кросс-платформа), `.ps1` (Windows PowerShell).

## Реестр скриптов

| Скрипт | Назначение | Когда запускать |
|--------|-----------|----------------|
| `validate-agent-registry` | Проверяет, что все `agents/*.md` имеют корректный frontmatter, уникальные `name`, упомянуты в `agents/README.md` и `rules/specialists.mdc` | После добавления / удаления агента |
| `validate-repo-consistency` | Сквозная consistent-проверка структуры репозитория: canonical paths, mirror sync, skills, profiles | Перед релизом / после крупных изменений |
| `run-behavior-benchmarks` | Запускает статические контракты из `benchmarks/behavior-contracts.json` (regex/path-checks без LLM) | В CI при каждом push; локально перед PR |
| `run-full-repo-benchmark` | Полный цикл: check-policy-encoding → validate-registry → validate-consistency → run-behavior-benchmarks → evaluate-transcript-runs (+ exporter smoke) | Канонический прогон перед релизом |
| `evaluate-transcript-runs` | Оценивает экспортированные транскрипты Cursor/Codex по `benchmarks/transcript-cases.json` | После живых прогонов агентов |
| `export-delegation-tree` | Экспортирует дерево делегации из `state.vscdb` или `composer.composerData` | Для отладки цепочки оркестрации |
| `iteration-vcs-preflight` | Проверяет git-статус перед итерацией: clean-tree, не отстаём от remote | Перед стартом новой волны улучшений |
| `check-policy-encoding` | Проверяет UTF-8 декодирование и признаки mojibake в `rules/`, `agents/`, `skills/` | Перед merge core-policy изменений |

## Быстрый запуск (после изменений в агентах)

```powershell
# Windows PowerShell
.\scripts\validate-agent-registry.ps1
.\scripts\validate-repo-consistency.ps1
.\scripts\run-behavior-benchmarks.ps1
```

```bash
# Linux / macOS
bash scripts/validate-agent-registry.sh
bash scripts/validate-repo-consistency.sh
bash scripts/run-behavior-benchmarks.sh
```

```bash
# Python (кросс-платформа, требует Python 3.10+)
python scripts/validate-agent-registry.py
python scripts/validate-repo-consistency.py
python scripts/run-behavior-benchmarks.py
python scripts/check-policy-encoding.py
```

## Полный цикл перед релизом

```bash
bash scripts/run-full-repo-benchmark.sh
# или
.\scripts\run-full-repo-benchmark.ps1
# или (кросс-платформа)
python scripts/run-full-repo-benchmark.py
```

## Коды выхода (iteration-vcs-preflight)

| Код | Значение |
|-----|---------|
| 0 | Проверка пройдена: ветка актуальна **или** обнаружен dirty tree (в check-only режиме sync не выполняется) |
| 2 | Ветка расходится с remote (diverged: одновременно behind и ahead), требуется ручное разрешение |
| 3 | Ветка только отстаёт от remote (behind-only), запускать с `--sync` / `-Sync` |

## Требования

- Python 3.10+ — для `.py` скриптов и `.ps1` (они вызывают Python внутри)
- Git — для `iteration-vcs-preflight`
- PowerShell 5.1+ — для `.ps1` скриптов

> Установить Python: `winget install Python.Python.3.12`
