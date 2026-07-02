#!/usr/bin/env python3
"""iteration-vcs-preflight.py — cross-platform VCS pre-flight check.
Python equivalent of iteration-vcs-preflight.sh

Usage:
    python scripts/iteration-vcs-preflight.py [--sync] [--base BRANCH]

Exit codes:
    0 — preflight passed (clean/up-to-date OR dirty worktree in check-only mode)
    2 — diverged branch, manual resolution required
    3 — branch is behind origin (run with --sync)
"""

import argparse
import re
import subprocess
import sys


def validate_branch_name(name: str) -> bool:
    """Validate branch name matches safe pattern: alphanumeric, hyphens, underscores."""
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name))


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(description="VCS pre-flight check")
    parser.add_argument("--sync", action="store_true", help="Sync branch if behind")
    parser.add_argument("--base", default="dev", help="Base branch (default: dev)")
    args = parser.parse_args()

    base_branch = args.base
    do_sync = args.sync

    # Validate base_branch name
    if not validate_branch_name(base_branch):
        print(f"vcs-preflight: ERROR: invalid base branch name '{base_branch}'")
        print("vcs-preflight: branch name must match: ^[a-zA-Z0-9_-]+$")
        return 1

    do_sync = args.sync

    print("vcs-preflight: fetch --all --prune")
    run(["git", "fetch", "--all", "--prune"])

    result = run(["git", "rev-list", "--left-right", "--count",
                  f"origin/{base_branch}...HEAD"])
    counts = result.stdout.strip().split()
    behind, ahead = int(counts[0]), int(counts[1])

    print(f"vcs-preflight: divergence origin/{base_branch}...HEAD = {behind}\t{ahead}")
    status = run(["git", "status", "--short", "--branch"])
    print(status.stdout, end="")

    # Dirty worktree is informational in check-only mode:
    # we do not auto-sync and keep exit code 0 for tooling compatibility.
    dirty = run(["git", "status", "--porcelain"])
    if dirty.stdout.strip():
        print("vcs-preflight: dirty worktree detected, sync skipped")
        return 0

    # Diverged
    if behind != 0 and ahead != 0:
        print(f"vcs-preflight: diverged branch ({behind}/{ahead}), manual resolution required")
        return 2

    if not do_sync:
        if behind != 0 and ahead == 0:
            print(f"vcs-preflight: branch is behind origin/{base_branch}, run with --sync before new changes")
            return 3
        print("vcs-preflight: check-only mode complete")
        return 0

    # Sync mode
    if behind == 0 and ahead == 0:
        print("vcs-preflight: up-to-date, pull --rebase")
        result = run(["git", "pull", "--rebase", "origin", base_branch], check=False)
        if result.returncode != 0:
            print(f"vcs-preflight: pull --rebase failed, fallback to git rebase origin/{base_branch}")
            run(["git", "rebase", f"origin/{base_branch}"])
        return 0

    if behind != 0 and ahead == 0:
        print("vcs-preflight: behind origin, rebase required")
        run(["git", "rebase", f"origin/{base_branch}"])
        return 0

    if behind == 0 and ahead != 0:
        print("vcs-preflight: local branch ahead, sync not required")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
