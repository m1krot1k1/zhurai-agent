#!/usr/bin/env bash
set -euo pipefail

BASE_BRANCH="${BASE_BRANCH:-dev}"
DO_SYNC="${1:-}"

echo "vcs-preflight: fetch --all --prune"
git fetch --all --prune

COUNTS="$(git rev-list --left-right --count "origin/${BASE_BRANCH}...HEAD")"
BEHIND="$(echo "$COUNTS" | awk '{print $1}')"
AHEAD="$(echo "$COUNTS" | awk '{print $2}')"

echo "vcs-preflight: divergence origin/${BASE_BRANCH}...HEAD = ${COUNTS}"
git status --short --branch

if [[ -n "$(git status --porcelain)" ]]; then
  echo "vcs-preflight: dirty worktree detected, sync skipped"
  exit 0
fi

if [[ "${BEHIND}" != "0" && "${AHEAD}" != "0" ]]; then
  echo "vcs-preflight: diverged branch (${BEHIND}/${AHEAD}), manual resolution required"
  exit 2
fi

if [[ "${DO_SYNC}" != "--sync" ]]; then
  if [[ "${BEHIND}" != "0" && "${AHEAD}" == "0" ]]; then
    echo "vcs-preflight: branch is behind origin/${BASE_BRANCH}, run with --sync before new changes"
    exit 3
  fi
  echo "vcs-preflight: check-only mode complete"
  exit 0
fi

if [[ "${BEHIND}" == "0" && "${AHEAD}" == "0" ]]; then
  echo "vcs-preflight: up-to-date, pull --rebase"
  if ! git pull --rebase origin "${BASE_BRANCH}"; then
    echo "vcs-preflight: pull --rebase failed, fallback to git rebase origin/${BASE_BRANCH}"
    git rebase "origin/${BASE_BRANCH}"
  fi
  exit 0
fi

if [[ "${BEHIND}" != "0" && "${AHEAD}" == "0" ]]; then
  echo "vcs-preflight: behind origin, rebase required"
  git rebase "origin/${BASE_BRANCH}"
  exit 0
fi

if [[ "${BEHIND}" == "0" && "${AHEAD}" != "0" ]]; then
  echo "vcs-preflight: local branch ahead, sync not required"
  exit 0
fi
