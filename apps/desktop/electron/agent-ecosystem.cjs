'use strict'

const fs = require('node:fs')
const path = require('node:path')

/**
 * Repo-sourced agent ecosystem discovery.
 *
 * Root resolution order:
 * 1. ZHUR_AI_AGENT_ROOT — explicit override (absolute or ~-expanded)
 * 2. hermesRoot fallback when `<root>/agents` exists
 *
 * Scans `agents/*.md` and reads YAML frontmatter `name` + `description`.
 */

function parseAgentFrontmatter(text) {
  const match = String(text || '').match(/^---\r?\n([\s\S]*?)\r?\n---/)

  if (!match) {
    return {}
  }

  const fields = {}

  for (const line of match[1].split('\n')) {
    const trimmed = line.trim()

    if (!trimmed || trimmed.startsWith('#')) {
      continue
    }

    const sep = trimmed.indexOf(':')

    if (sep <= 0) {
      continue
    }

    const key = trimmed.slice(0, sep).trim()
    let value = trimmed.slice(sep + 1).trim()

    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }

    fields[key] = value
  }

  return fields
}

function isPathInside(child, parent) {
  const rel = path.relative(parent, child)

  return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel))
}

function resolveEcosystemRoot({ hermesRoot, env = process.env, fsImpl = fs } = {}) {
  const overrideRaw = env.ZHUR_AI_AGENT_ROOT && String(env.ZHUR_AI_AGENT_ROOT).trim()
  const override = overrideRaw ? path.resolve(overrideRaw.replace(/^~(?=$|[\\/])/, env.HOME || '')) : null
  const candidates = [override, hermesRoot].filter(Boolean)

  for (const root of candidates) {
    try {
      if (fsImpl.existsSync(path.join(root, 'agents'))) {
        return root
      }
    } catch {
      // try next candidate
    }
  }

  return override
}

async function listAgentsFromRepo(root, options = {}) {
  const fsImpl = options.fs || fs

  if (!root) {
    return { root: null, agents: [], error: 'root-unresolved' }
  }

  const agentsDir = path.join(root, 'agents')

  try {
    if (!fsImpl.existsSync(agentsDir)) {
      return { root, agents: [], error: 'agents-dir-missing' }
    }
  } catch {
    return { root, agents: [], error: 'agents-dir-unreadable' }
  }

  let entries = []

  try {
    entries = await fsImpl.promises.readdir(agentsDir, { withFileTypes: true })
  } catch {
    return { root, agents: [], error: 'agents-dir-unreadable' }
  }

  let resolvedAgentsDir = agentsDir

  try {
    resolvedAgentsDir = await fsImpl.promises.realpath(agentsDir)
  } catch {
    return { root, agents: [], error: 'agents-dir-unreadable' }
  }

  const agents = []

  for (const entry of entries) {
    if (entry.isDirectory() || !entry.name.endsWith('.md') || entry.name.startsWith('.')) {
      continue
    }

    if (!entry.isFile() && !entry.isSymbolicLink()) {
      continue
    }

    if (entry.name.toLowerCase() === 'readme.md') {
      continue
    }

    const filePath = path.join(agentsDir, entry.name)
    let resolvedFile = ''

    try {
      resolvedFile = await fsImpl.promises.realpath(filePath)

      if (!isPathInside(resolvedFile, resolvedAgentsDir)) {
        continue
      }
    } catch {
      continue
    }

    let text = ''

    try {
      text = await fsImpl.promises.readFile(resolvedFile, 'utf8')
    } catch {
      continue
    }

    const frontmatter = parseAgentFrontmatter(text)
    const id = entry.name.replace(/\.md$/i, '')

    agents.push({
      id,
      name: frontmatter.name || id,
      description: frontmatter.description || '',
      fileName: entry.name
    })
  }

  agents.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }))

  return { root, agents }
}

async function discoverRepoAgents({ hermesRoot, env = process.env, fsImpl = fs } = {}) {
  const root = resolveEcosystemRoot({ hermesRoot, env, fsImpl })

  return listAgentsFromRepo(root, { fs: fsImpl })
}

module.exports = {
  discoverRepoAgents,
  listAgentsFromRepo,
  parseAgentFrontmatter,
  resolveEcosystemRoot
}
