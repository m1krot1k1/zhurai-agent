$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Get-Command python3 -ErrorAction SilentlyContinue) {
  & python3 (Join-Path $ScriptDir "run-full-repo-benchmark.py")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  & python (Join-Path $ScriptDir "run-full-repo-benchmark.py")
} else {
  Write-Error "python3 or python is required to run run-full-repo-benchmark"
  exit 127
}
