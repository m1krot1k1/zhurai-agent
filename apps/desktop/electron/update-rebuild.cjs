'use strict'

/**
 * Retry-once policy for the desktop `--build-only` rebuild during self-update.
 *
 * The first rebuild can return nonzero on a still-settling post-update tree or a
 * network-blocked Electron fetch that the installer's self-heal repaired mid-run.
 * A second attempt then builds clean off the healed dist (the content-hash stamp
 * makes it a near-no-op when the first actually succeeded). Without the retry the
 * updater bails before the relaunch step — the app updates but doesn't restart.
 *
 * Network-blocked Electron downloads (GitHub rate limits, corporate firewalls,
 * China GFW, etc.) are handled by:
 *   1. Respecting ELECTRON_MIRROR env var if the user sets it.
 *   2. Auto-fallback to a public mirror (npmmirror.com) on the retry attempt.
 *   3. Clear actionable error messages pointing to the mirror workaround.
 */

const DEFAULT_ELECTRON_MIRROR = 'https://npmmirror.com/mirrors/electron/'

function shouldRetryRebuild(code) {
  return code !== 0
}

/**
 * Inject ELECTRON_MIRROR into env for the rebuild attempt.
 * Priority: explicit env var > auto-fallback on retry > nothing.
 */
function withElectronMirror(env, attempt) {
  const base = { ...(env || {}) }
  if (base.ELECTRON_MIRROR) {
    return base // user-provided, respect it
  }
  if (attempt > 0) {
    base.ELECTRON_MIRROR = DEFAULT_ELECTRON_MIRROR
  }
  return base
}

/**
 * Run `rebuild()` (async, resolves `{ code, ... }`), retrying once on failure.
 * On the retry attempt, automatically sets ELECTRON_MIRROR to a public fallback
 * if the user has not provided one. Returns the final result.
 */
async function runRebuildWithRetry(rebuild, baseEnv) {
  let result = await rebuild(0, withElectronMirror(baseEnv, 0))
  if (shouldRetryRebuild(result.code)) {
    result = await rebuild(1, withElectronMirror(baseEnv, 1))
  }
  return result
}

module.exports = { shouldRetryRebuild, runRebuildWithRetry, DEFAULT_ELECTRON_MIRROR }
