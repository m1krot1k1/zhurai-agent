# Обновления ZhurAI Agent Desktop

## Почему «You're on the latest version», хотя в GitHub уже есть коммиты

Desktop обновляется **через git** (backend `~/.hermes/hermes-agent`), а не через список GitHub Releases.

| Что видите | Что это значит |
|------------|----------------|
| `v0.17.0 0ef7096` в углу | Версия **собранного .app** (install-stamp при сборке) |
| «Latest version» в About | Backend на выбранной ветке **совпадает** с `origin/<ветка>` |
| Нет .dmg в Releases | CI-релиз ещё не отработал или Actions/macOS runner недоступен |

### Ветка по умолчанию

Активная разработка — **`dev`**. Раньше updater смотрел на `main`, поэтому коммиты в `dev` (skills, `/start`, agents) не показывались.

С версии desktop после `fix(updates): track dev branch` конфиг `~/Library/Application Support/ZhurAI Agent/updates.json` (или Hermes userData) мигрирует с `main` → `dev`, если ветку не выбирали вручную.

## Как обновиться сейчас

### Вариант A — из приложения (рекомендуется)

1. Перезапустите Desktop после обновления репо / нового .app.
2. **About → Check for updates** (или pill в статус-баре).
3. Должно показать N commits behind **dev**.
4. **Update now** — `hermes update` + пересборка GUI на macOS.

### Вариант B — вручную в терминале

```bash
cd ~/.hermes/hermes-agent   # или ваш ZHUR_AI_AGENT_ROOT
git fetch origin dev
git checkout dev
git pull --ff-only origin dev
hermes update --yes --branch dev
```

Перезапустите ZhurAI Agent.

### Вариант C — новый .dmg (полное обновление shell)

```bash
# из клона репозитория на Mac (нужны Node 22, gh auth login)
bash scripts/release-desktop-github.sh minor
```

Или дождитесь GitHub Actions **Release Desktop macOS** после push в `dev`.

## GitHub Releases

Workflow: `.github/workflows/release-desktop-macos.yml`

- Push в **`dev`** (в т.ч. `skills/`, `agents/`, `commands/`) → minor bump + prerelease `.dmg`/`.zip`
- **workflow_dispatch** на `main`/`dev` → major/minor вручную

Если Actions падает на «Set up job» — проверьте billing и macOS runners в Settings → Actions.

## Ссылки

- Releases: https://github.com/m1krot1k1/zhurai-agent/releases
- Gatekeeper после .dmg: `docs/desktop-macos-signing.md`
