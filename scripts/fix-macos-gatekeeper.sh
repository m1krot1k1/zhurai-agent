#!/usr/bin/env bash
# Снимает quarantine и применяет ad-hoc подпись — убирает «приложение повреждено» на macOS.
# Оригинальный Hermes не падает, потому что релизы подписаны Developer ID + notarization.
# Наши open-source релизы без Apple-сертификата используют ad-hoc (-) + снятие quarantine.
#
# Использование:
#   bash scripts/fix-macos-gatekeeper.sh
#   bash scripts/fix-macos-gatekeeper.sh "/Applications/ZhurAI Agent.app"
set -euo pipefail

APP="${1:-/Applications/ZhurAI Agent.app}"

if [[ ! -d "$APP" ]]; then
  echo "Не найдено: $APP" >&2
  echo "Укажите путь к ZhurAI Agent.app после установки из .dmg" >&2
  exit 1
fi

if ! command -v codesign >/dev/null 2>&1; then
  echo "codesign не найден (нужен macOS)" >&2
  exit 1
fi

echo "→ Снимаю quarantine с $APP"
xattr -cr "$APP" 2>/dev/null || true

echo "→ Ad-hoc подпись (без Apple Developer ID)"
codesign --force --deep --sign - "$APP"

echo "→ Проверка"
codesign --verify --deep --strict "$APP" 2>/dev/null || codesign --verify --deep "$APP"

echo ""
echo "Готово. Запуск: open \"$APP\""
echo ""
echo "Для релизов без предупреждений как у Hermes нужен Apple Developer Program"
echo "и секреты CSC_LINK / APPLE_API_KEY* в CI — см. docs/desktop-macos-signing.md"
