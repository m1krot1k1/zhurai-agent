$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Get-Command py -ErrorAction SilentlyContinue) {
  py -3 (Join-Path $ScriptDir "evaluate-transcript-runs.py") @args
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
  python3 (Join-Path $ScriptDir "evaluate-transcript-runs.py") @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  python (Join-Path $ScriptDir "evaluate-transcript-runs.py") @args
} else {
  throw "Python 3 is required to run transcript benchmarks"
}
