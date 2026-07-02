#!/usr/bin/env bash
# Публикация уже собранных .dmg/.zip в GitHub Releases.
# Требует: GITHUB_TOKEN (classic, repo) или `gh auth login`.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REPO="${GITHUB_REPOSITORY:-m1krot1k1/zhurai-agent}"
VERSION="$(node -p "require('./apps/desktop/package.json').version")"
TAG="v${VERSION}"
RELEASE_DIR="${ROOT}/apps/desktop/release"

shopt -s nullglob
ASSETS=("${RELEASE_DIR}/ZhurAI-Agent-${VERSION}-mac-arm64.dmg" "${RELEASE_DIR}/ZhurAI-Agent-${VERSION}-mac-arm64.zip")
if [[ ! -f "${ASSETS[0]}" ]]; then
  echo "Нет артефактов для v${VERSION}. Сначала: bash scripts/build-desktop-macos.sh" >&2
  exit 1
fi

publish_with_gh() {
  command -v gh >/dev/null 2>&1 || return 1
  gh release view "${TAG}" -R "${REPO}" >/dev/null 2>&1 || \
    gh release create "${TAG}" -R "${REPO}" --prerelease --title "ZhurAI Agent ${TAG}" \
      --notes "Сборка v${VERSION}. Gatekeeper: \`bash scripts/fix-macos-gatekeeper.sh \\\"/Applications/ZhurAI Agent.app\\\"\`"
  gh release upload "${TAG}" -R "${REPO}" "${ASSETS[@]}" --clobber
  echo "https://github.com/${REPO}/releases/tag/${TAG}"
}

publish_with_api() {
  [[ -n "${GITHUB_TOKEN:-}" ]] || return 1
  local api="https://api.github.com/repos/${REPO}/releases"
  local release_id
  release_id="$(curl -fsSL -H "Authorization: Bearer ${GITHUB_TOKEN}" -H "Accept: application/vnd.github+json" \
    "${api}/tags/${TAG}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || true)"
  if [[ -z "${release_id}" ]]; then
    release_id="$(curl -fsSL -X POST -H "Authorization: Bearer ${GITHUB_TOKEN}" -H "Accept: application/vnd.github+json" \
      -d "$(python3 -c "import json; print(json.dumps({'tag_name':'${TAG}','name':'ZhurAI Agent ${TAG}','prerelease':True,'generate_release_notes':True}))")" \
      "${api}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")"
  fi
  for asset in "${ASSETS[@]}"; do
    name="$(basename "${asset}")"
    echo "→ upload ${name}"
    curl -fsSL -X POST \
      -H "Authorization: Bearer ${GITHUB_TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      -H "Content-Type: application/octet-stream" \
      --data-binary "@${asset}" \
      "${api}/${release_id}/assets?name=${name}"
  done
  echo "https://github.com/${REPO}/releases/tag/${TAG}"
}

if publish_with_gh; then
  exit 0
fi
if publish_with_api; then
  exit 0
fi

cat >&2 <<EOF
Не удалось опубликовать релиз.

1) Установите GitHub CLI и войдите:
   brew install gh && gh auth login

2) Или задайте GITHUB_TOKEN и повторите:
   export GITHUB_TOKEN=ghp_...
   bash scripts/publish-release-assets.sh

Артефакты уже собраны:
  ${ASSETS[*]}
EOF
exit 1
