/**
 * Desktop self-update branch defaults for zhur.ai-agent.
 *
 * The fork ships active work on `dev`; tracking `main` hides ecosystem updates
 * (skills/agents) from the in-app updater.
 */

const { OFFICIAL_REPO_CANONICAL, canonicalGitHubRemote } = require('./update-remote.cjs')

const ZHUR_DEFAULT_UPDATE_BRANCH = 'dev'
const LEGACY_DEFAULT_BRANCH = 'main'

function resolveDefaultUpdateBranch({ installStampBranch = null, originUrl = null } = {}) {
  if (installStampBranch && installStampBranch !== 'HEAD') {
    return installStampBranch
  }
  if (originUrl && canonicalGitHubRemote(originUrl) === OFFICIAL_REPO_CANONICAL) {
    return ZHUR_DEFAULT_UPDATE_BRANCH
  }
  return LEGACY_DEFAULT_BRANCH
}

/**
 * Read updates.json fields with one-time migration from legacy main → dev
 * for official zhur.ai-agent checkouts (unless user explicitly chose a branch).
 */
function normalizeDesktopUpdateConfig(parsed, { installStampBranch = null, originUrl = null } = {}) {
  const explicit = parsed?.branchSource === 'user'
  const fallback = resolveDefaultUpdateBranch({ installStampBranch, originUrl })
  let branch =
    typeof parsed?.branch === 'string' && parsed.branch.trim() ? parsed.branch.trim() : fallback

  let migrated = false
  if (
    !explicit &&
    branch === LEGACY_DEFAULT_BRANCH &&
    originUrl &&
    canonicalGitHubRemote(originUrl) === OFFICIAL_REPO_CANONICAL
  ) {
    branch = ZHUR_DEFAULT_UPDATE_BRANCH
    migrated = true
  }

  return {
    branch,
    branchSource: explicit ? 'user' : parsed?.branchSource || 'default',
    migrated
  }
}

function serializeDesktopUpdateConfig({ branch, branchSource = 'default' }) {
  return JSON.stringify({ branch, branchSource }, null, 2)
}

module.exports = {
  ZHUR_DEFAULT_UPDATE_BRANCH,
  LEGACY_DEFAULT_BRANCH,
  resolveDefaultUpdateBranch,
  normalizeDesktopUpdateConfig,
  serializeDesktopUpdateConfig
}
