import { afterEach, describe, expect, it, vi } from 'vitest'

import { listAgentsFromRepo } from './agent-discovery'

describe('listAgentsFromRepo', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns bridge-unavailable when desktop IPC is missing', async () => {
    vi.stubGlobal('window', {})

    await expect(listAgentsFromRepo()).resolves.toEqual({
      root: null,
      agents: [],
      error: 'bridge-unavailable'
    })
  })

  it('delegates to hermesDesktop.listRepoAgents', async () => {
    const listRepoAgents = vi.fn(async () => ({
      root: '/repo',
      agents: [{ id: 'code', name: 'code', description: 'dev', path: '/repo/agents/code.md', fileName: 'code.md' }]
    }))

    vi.stubGlobal('window', { hermesDesktop: { listRepoAgents } })

    await expect(listAgentsFromRepo()).resolves.toMatchObject({
      root: '/repo',
      agents: [{ id: 'code', name: 'code' }]
    })

    expect(listRepoAgents).toHaveBeenCalledOnce()
  })
})
