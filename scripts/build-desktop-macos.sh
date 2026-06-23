#!/usr/bin/env bash
# Сборка .dmg и .zip для macOS (Apple Silicon / Intel).
# Автоустановка Node 22 через nvm, если node отсутствует.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/ensure-node.sh
source "${ROOT}/scripts/ensure-node.sh"

echo "→ npm ci (корень monorepo)..."
npm ci

echo "→ Сборка ZhurAI Agent desktop (dmg + zip)..."
export CSC_IDENTITY_AUTO_DISCOVERY=false
npm run --prefix apps/desktop dist:mac

echo ""
echo "Готово. Артефакты:"
ls -lh apps/desktop/release/*.{dmg,zip} 2>/dev/null || ls -lh apps/desktop/release/
