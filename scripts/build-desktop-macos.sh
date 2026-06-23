#!/usr/bin/env bash
# Сборка десктоп-приложения ZhurAI Agent для macOS (Apple Silicon / Intel).
# Требуется Node.js 20+ и npm. Репозиторий: m1krot1k1/zhurai-agent

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js не найден. Установите Node 20+ (https://nodejs.org/) или nvm." >&2
  exit 1
fi

echo "→ npm ci (корень monorepo)..."
npm ci

echo "→ Сборка desktop (dmg + zip)..."
export CSC_IDENTITY_AUTO_DISCOVERY=false
npm run --prefix apps/desktop dist:mac

echo ""
echo "Готово. Артефакты:"
ls -lh apps/desktop/release/*.{dmg,zip} 2>/dev/null || ls -lh apps/desktop/release/
