#!/usr/bin/env bash
# Устанавливает Node.js 22 через nvm, если node не найден в PATH.
set -euo pipefail

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if command -v node >/dev/null 2>&1; then
  NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]")"
  if [[ "${NODE_MAJOR}" -ge 20 ]]; then
    echo "Node $(node -v) уже доступен"
    return 0 2>/dev/null || exit 0
  fi
  echo "Node $(node -v) слишком старый, нужен 20+"
fi

if [[ ! -s "${NVM_DIR}/nvm.sh" ]]; then
  echo "→ Установка nvm..."
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
fi

# shellcheck source=/dev/null
source "${NVM_DIR}/nvm.sh"

echo "→ Установка Node.js 22..."
nvm install 22
nvm use 22

echo "Node $(node -v), npm $(npm -v)"
