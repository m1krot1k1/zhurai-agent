#!/usr/bin/env bash
# Локальный релиз: сборка .dmg + загрузка в GitHub Releases (нужен gh auth login).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BUMP="${1:-minor}"
if [[ "${BUMP}" != "minor" && "${BUMP}" != "major" ]]; then
  echo "Использование: $0 minor|major" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Установите GitHub CLI: brew install gh && gh auth login" >&2
  exit 1
fi

NEW_VERSION="$(bash scripts/bump-desktop-version.sh "${BUMP}")"
TAG="v${NEW_VERSION}"

echo "→ Сборка v${NEW_VERSION}..."
bash scripts/build-desktop-macos.sh

echo "→ Публикация ${TAG}..."
PRERELEASE_FLAG=""
[[ "${BUMP}" == "minor" ]] && PRERELEASE_FLAG="--prerelease"

git add apps/desktop/package.json
git commit -m "chore(release): ${TAG}"
git tag -a "${TAG}" -m "ZhurAI Agent ${TAG}"
git push origin HEAD
git push origin "${TAG}"

gh release create "${TAG}" \
  ${PRERELEASE_FLAG} \
  --title "ZhurAI Agent ${TAG}" \
  --generate-notes \
  apps/desktop/release/*.dmg \
  apps/desktop/release/*.zip

echo "Готово: https://github.com/m1krot1k1/zhurai-agent/releases/tag/${TAG}"
