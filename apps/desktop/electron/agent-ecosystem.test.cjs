'use strict'

const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const test = require('node:test')

const {
  discoverRepoAgents,
  listAgentsFromRepo,
  parseAgentFrontmatter,
  resolveEcosystemRoot
} = require('./agent-ecosystem.cjs')

test('parseAgentFrontmatter reads name and description', () => {
  const text = `---
name: orchestrator
description: Coordinates parallel branches.
---

## Body
`

  assert.deepEqual(parseAgentFrontmatter(text), {
    name: 'orchestrator',
    description: 'Coordinates parallel branches.'
  })
})

test('resolveEcosystemRoot prefers ZHUR_AI_AGENT_ROOT when agents/ exists', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'eco-root-'))
  const agents = path.join(root, 'agents')
  fs.mkdirSync(agents)

  const resolved = resolveEcosystemRoot({
    hermesRoot: '/tmp/hermes',
    env: { ZHUR_AI_AGENT_ROOT: root },
    fsImpl: fs
  })

  assert.equal(resolved, root)
})

test('listAgentsFromRepo scans agents/*.md frontmatter', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'eco-agents-'))
  const agentsDir = path.join(root, 'agents')
  fs.mkdirSync(agentsDir)
  fs.writeFileSync(
    path.join(agentsDir, 'code.md'),
    `---
name: code
description: Writes and refactors code.
---
`,
    'utf8'
  )
  fs.writeFileSync(path.join(agentsDir, 'README.md'), '# ignore me', 'utf8')

  const result = await listAgentsFromRepo(root)

  assert.equal(result.root, root)
  assert.equal(result.agents.length, 1)
  assert.equal(result.agents[0].id, 'code')
  assert.equal(result.agents[0].name, 'code')
  assert.match(result.agents[0].description, /refactors code/)
  assert.equal('path' in result.agents[0], false)
})

test('listAgentsFromRepo skips symlinks that resolve outside agents/', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'eco-symlink-'))
  const agentsDir = path.join(root, 'agents')
  const outsideDir = path.join(root, 'outside')
  fs.mkdirSync(agentsDir)
  fs.mkdirSync(outsideDir)
  fs.writeFileSync(
    path.join(outsideDir, 'escape.md'),
    `---
name: escape
description: Outside agents dir.
---
`,
    'utf8'
  )
  fs.symlinkSync(path.join(outsideDir, 'escape.md'), path.join(agentsDir, 'escape.md'))
  fs.writeFileSync(
    path.join(agentsDir, 'code.md'),
    `---
name: code
description: Inside agents dir.
---
`,
    'utf8'
  )

  const result = await listAgentsFromRepo(root)

  assert.equal(result.agents.length, 1)
  assert.equal(result.agents[0].id, 'code')
})

test('discoverRepoAgents returns agents-dir-missing when root has no agents/', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'eco-missing-'))

  const result = await discoverRepoAgents({
    hermesRoot: root,
    env: {},
    fsImpl: fs
  })

  assert.equal(result.error, 'agents-dir-missing')
  assert.deepEqual(result.agents, [])
})
