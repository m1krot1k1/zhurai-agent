import type { SubagentStatus } from '@/store/subagents'

/**
 * Canonical SubagentProgress contract (unified across TUI/Desktop gateway consumers).
 * Covers deep orchestrator support: nested delegation trees via parent_id + depth + role.
 * Consumed by Desktop via gateway subagent.* events (start/progress/complete) same as TUI.
 */
export interface SubagentProgress {
  id: string
  parentId: string | null
  goal: string
  agentId?: string
  role?: string
  sessionId?: string
  model?: string
  status: SubagentStatus
  depth: number
  index: number
  taskCount: number
  taskIndex: number
  startedAt: number
  updatedAt: number
  durationSeconds?: number
  costUsd?: number
  inputTokens?: number
  outputTokens?: number
  toolCount: number
  filesRead: string[]
  filesWritten: string[]
  stream: Array<{
    at: number
    isError?: boolean
    kind: 'progress' | 'summary' | 'thinking' | 'tool'
    text: string
  }>
  reasoningTokens?: number
  summary?: string
  instruction?: string
  currentTool?: string
  waveNumber?: number
  // progress snapshot for live updates (tool or text preview)
  progress?: string
}

export type SubagentProgressPayload = Record<string, unknown>
