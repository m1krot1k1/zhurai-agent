const test = require('node:test')
const assert = require('node:assert/strict')

const {
  ZHUR_DEFAULT_UPDATE_BRANCH,
  resolveDefaultUpdateBranch,
  normalizeDesktopUpdateConfig
} = require('./update-config.cjs')

const OFFICIAL_SSH = 'git@github.com:m1krot1k1/zhurai-agent.git'
const FORK_HTTPS = 'https://github.com/other/hermes-agent.git'

test('resolveDefaultUpdateBranch prefers install stamp branch', () => {
  assert.equal(
    resolveDefaultUpdateBranch({ installStampBranch: 'dev', originUrl: OFFICIAL_SSH }),
    'dev'
  )
})

test('resolveDefaultUpdateBranch uses dev for official zhur repo', () => {
  assert.equal(resolveDefaultUpdateBranch({ originUrl: OFFICIAL_SSH }), ZHUR_DEFAULT_UPDATE_BRANCH)
})

test('resolveDefaultUpdateBranch keeps main for non-official remotes', () => {
  assert.equal(resolveDefaultUpdateBranch({ originUrl: FORK_HTTPS }), 'main')
})

test('normalizeDesktopUpdateConfig migrates implicit main to dev on official repo', () => {
  const next = normalizeDesktopUpdateConfig({ branch: 'main' }, { originUrl: OFFICIAL_SSH })
  assert.equal(next.branch, 'dev')
  assert.equal(next.migrated, true)
  assert.equal(next.branchSource, 'default')
})

test('normalizeDesktopUpdateConfig respects user-selected main', () => {
  const next = normalizeDesktopUpdateConfig(
    { branch: 'main', branchSource: 'user' },
    { originUrl: OFFICIAL_SSH }
  )
  assert.equal(next.branch, 'main')
  assert.equal(next.migrated, false)
})
