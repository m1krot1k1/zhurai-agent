# macOS: подпись и Gatekeeper

## Почему «приложение повреждено»

Оригинальный **Hermes Desktop** от Nous Research распространяется с **Apple Developer ID** и **notarization** — macOS доверяет такому `.dmg` сразу.

Релизы **ZhurAI Agent** без платного Apple Developer Program собираются с **ad-hoc подписью** (`codesign -`). После скачивания через браузер macOS ставит флаг **quarantine** — отсюда сообщение «повреждено», хотя файл целый.

## Быстрое исправление (после установки в Программы)

```bash
cd /path/to/zhurai-agent
bash scripts/fix-macos-gatekeeper.sh "/Applications/ZhurAI Agent.app"
open "/Applications/ZhurAI Agent.app"
```

Или вручную:

```bash
xattr -cr "/Applications/ZhurAI Agent.app"
codesign --force --deep --sign - "/Applications/ZhurAI Agent.app"
```

## Сборка с ad-hoc (по умолчанию)

```bash
bash scripts/build-desktop-macos.sh
```

Внутри: `CSC_IDENTITY="-"` + `after-pack.cjs` подписывает `.app` до упаковки в `.dmg`.

## Как у Hermes (без предупреждений)

Нужен [Apple Developer Program](https://developer.apple.com/programs/) и секреты в CI / локально:

| Переменная | Назначение |
|------------|------------|
| `CSC_LINK` | Base64 `.p12` Developer ID Application |
| `CSC_KEY_PASSWORD` | Пароль к сертификату |
| `APPLE_API_KEY` | App Store Connect API key (.p8) |
| `APPLE_API_KEY_ID` | Key ID |
| `APPLE_API_ISSUER` | Issuer ID |

Либо `APPLE_NOTARY_PROFILE` — профиль `notarytool store-credentials`.

С этими переменными `build-desktop-macos.sh` и `release-desktop-macos.yml` вызывают `scripts/notarize.cjs` автоматически.

В `package.json` для production включите `"hardenedRuntime": true` (сейчас `false` для совместимости с ad-hoc).
