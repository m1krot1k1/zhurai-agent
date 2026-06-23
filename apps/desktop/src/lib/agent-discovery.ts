/**
 * Repo-sourced agent discovery for the desktop UI.
 *
 * Agents are loaded from `<ZHUR_AI_AGENT_ROOT>/agents/*.md` (or hermesRoot when
 * that directory exists). Set `ZHUR_AI_AGENT_ROOT` to point at the zhur.ai-agent
 * ecosystem checkout; the Electron main process performs filesystem scans via IPC.
 */

export interface RepoAgentDescriptor {
  description: string
  fileName: string
  id: string
  name: string
  path: string
}

export interface RepoAgentDiscoveryResult {
  agents: RepoAgentDescriptor[]
  error?: string
  root: string | null
}

export async function listAgentsFromRepo(): Promise<RepoAgentDiscoveryResult> {
  const desktop = window.hermesDesktop

  if (!desktop?.listRepoAgents) {
    return { root: null, agents: [], error: 'bridge-unavailable' }
  }

  return desktop.listRepoAgents()
}
