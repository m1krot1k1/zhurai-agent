import { atom } from 'nanostores'

import { listAgentsFromRepo, type RepoAgentDescriptor } from '@/lib/agent-discovery'

export interface RepoAgentsState {
  agents: RepoAgentDescriptor[]
  error: string | null
  loadedAt: number | null
  loading: boolean
  root: string | null
}

const INITIAL: RepoAgentsState = {
  agents: [],
  error: null,
  loadedAt: null,
  loading: false,
  root: null
}

export const $repoAgents = atom<RepoAgentsState>(INITIAL)

export async function refreshRepoAgents() {
  const current = $repoAgents.get()

  $repoAgents.set({ ...current, loading: true })

  try {
    const result = await listAgentsFromRepo()

    $repoAgents.set({
      agents: result.agents,
      error: result.error ?? null,
      loadedAt: Date.now(),
      loading: false,
      root: result.root
    })
  } catch (error) {
    $repoAgents.set({
      agents: [],
      error: error instanceof Error ? error.message : String(error),
      loadedAt: Date.now(),
      loading: false,
      root: null
    })
  }
}

export function resetRepoAgents() {
  $repoAgents.set(INITIAL)
}
