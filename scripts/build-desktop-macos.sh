#!/usr/bin/env bash
# Сборка .dmg и .zip для macOS (Apple Silicon / Intel).
# Ad-hoc подпись, если нет Apple Developer ID (как install.sh).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/ensure-node.sh
source "${ROOT}/scripts/ensure-node.sh"

echo "→ npm ci (корень monorepo)..."
npm ci

echo "→ Сборка ZhurAI Agent desktop (dmg + zip)..."
if [[ -n "${CSC_LINK:-}" || -n "${APPLE_SIGNING_IDENTITY:-}" ]]; then
  echo "   (Developer ID: подпись + notarize при наличии APPLE_*)"
  npm run --prefix apps/desktop dist:mac
else
  echo "   (ad-hoc подпись — без Apple Developer ID)"
  export CSC_IDENTITY="-"
  unset CSC_IDENTITY_AUTO_DISCOVERY
  npm run --prefix apps/desktop dist:mac
fi

echo ""
echo "Готово. Артефакты:"
ls -lh apps/desktop/release/*.{dmg,zip} 2>/dev/null || ls -lh apps/desktop/release/
echo ""
echo "После установки из браузера (Firefox/Safari) один раз:"
echo "  bash scripts/fix-macos-gatekeeper.sh \"/Applications/ZhurAI Agent.app\""
