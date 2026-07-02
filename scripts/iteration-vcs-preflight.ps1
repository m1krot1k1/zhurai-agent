#Requires -Version 5.1
<#
.SYNOPSIS
    iteration-vcs-preflight.ps1 — VCS pre-flight check for Windows/PowerShell.
    PowerShell equivalent of iteration-vcs-preflight.sh

.DESCRIPTION
    Checks git divergence against a base branch.
    Optionally syncs the branch via rebase if behind.

.PARAMETER Sync
    If specified, attempts to sync (rebase) the branch when behind.

.PARAMETER Base
    Base branch to compare against. Default: dev

.OUTPUTS
    Exit codes:
        0 — clean / up-to-date
        2 — diverged branch, manual resolution required
        3 — branch is behind origin (run with -Sync)

.EXAMPLE
    .\scripts\iteration-vcs-preflight.ps1
    .\scripts\iteration-vcs-preflight.ps1 -Sync
    .\scripts\iteration-vcs-preflight.ps1 -Base main -Sync
#>

[CmdletBinding()]
param(
    [switch]$Sync,
    [string]$Base = "dev"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$BaseBranch = $Base
if (-not $BaseBranch -and $env:BASE_BRANCH) {
  $BaseBranch = $env:BASE_BRANCH
}

Write-Host "vcs-preflight: fetch --all --prune"
git fetch --all --prune

$CountsRaw = git rev-list --left-right --count "origin/${BaseBranch}...HEAD"
$Counts = $CountsRaw -split '\s+'
$Behind = [int]$Counts[0]
$Ahead  = [int]$Counts[1]

Write-Host "vcs-preflight: divergence origin/${BaseBranch}...HEAD = ${CountsRaw}"
git status --short --branch

# Dirty worktree check
$DirtyStatus = git status --porcelain
if ($DirtyStatus) {
    Write-Host "vcs-preflight: dirty worktree detected, sync skipped"
    exit 0
}

# Diverged
if ($Behind -ne 0 -and $Ahead -ne 0) {
    Write-Host "vcs-preflight: diverged branch (${Behind}/${Ahead}), manual resolution required"
    exit 2
}

if (-not $Sync) {
    if ($Behind -ne 0 -and $Ahead -eq 0) {
        Write-Host "vcs-preflight: branch is behind origin/${BaseBranch}, run with -Sync before new changes"
        exit 3
    }
    Write-Host "vcs-preflight: check-only mode complete"
    exit 0
}

# Sync mode
if ($Behind -eq 0 -and $Ahead -eq 0) {
    Write-Host "vcs-preflight: up-to-date, pull --rebase"
    $PullResult = git pull --rebase "origin" $BaseBranch 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "vcs-preflight: pull --rebase failed, fallback to git rebase origin/${BaseBranch}"
        git rebase "origin/${BaseBranch}"
    }
    exit 0
}

if ($Behind -ne 0 -and $Ahead -eq 0) {
    Write-Host "vcs-preflight: behind origin, rebase required"
    git rebase "origin/${BaseBranch}"
    exit 0
}

if ($Behind -eq 0 -and $Ahead -ne 0) {
    Write-Host "vcs-preflight: local branch ahead, sync not required"
    exit 0
}

exit 0
