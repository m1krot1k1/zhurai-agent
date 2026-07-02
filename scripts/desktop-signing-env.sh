#!/usr/bin/env bash
# Нормализует env для electron-builder: ad-hoc, если нет полного Apple signing.
set -euo pipefail

has_dev_signing() {
  if [[ -n "${APPLE_SIGNING_IDENTITY:-}" ]]; then
    return 0
  fi
  if [[ -z "${CSC_LINK:-}" || -z "${CSC_KEY_PASSWORD:-}" ]]; then
    return 1
  fi
  # base64 / inline p12 в переменной — валидно для electron-builder
  if [[ "${CSC_LINK}" == *"BEGIN"* ]]; then
    return 0
  fi
  [[ -f "${CSC_LINK}" ]]
}

if has_dev_signing; then
  echo "→ Developer signing env detected"
  exit 0
fi

echo "→ ad-hoc signing (CSC_LINK/CSC_KEY_PASSWORD не заданы или неполные)"
export CSC_IDENTITY="-"
unset CSC_IDENTITY_AUTO_DISCOVERY CSC_LINK CSC_KEY_PASSWORD CSC_NAME CSC_INSTALLER_LINK CSC_INSTALLER_KEY_PASSWORD
