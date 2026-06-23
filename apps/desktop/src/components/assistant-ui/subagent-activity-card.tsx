'use client'

import { useStore } from '@nanostores/react'
import { type ReactNode, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { AGENTS_ROUTE } from '@/app/routes'
import { useElapsedSeconds } from '@/components/chat/activity-timer'
import { ActivityTimerText } from '@/components/chat/activity-timer-text'
import { GlyphSpinner } from '@/components/ui/glyph-spinner'
import { useI18n } from '@/i18n'
import { AlertCircle, CheckCircle2, Sparkles } from '@/lib/icons'
import { useEnterAnimation } from '@/lib/use-enter-animation'
import { cn } from '@/lib/utils'
import {
  $subagentsBySession,
  activeSubagentCount,
  setFocusSubagentId,
  type SubagentProgress
} from '@/store/subagents'

/**
 * Inline subagent activity card shown inside an assistant message while
 * subagents are running. Displays each agent's goal, status, current tool,
 * and elapsed time — clickable to open the Agents overlay.
 *
 * Mirrors the visual vocabulary of Cursor IDE's inline agent panel:
 * a compact, real-time status feed fused into the message transcript.
 */
export function SubagentActivityCard({ sessionId }: { sessionId: string | null }) {
  const { t } = useI18n()
  const navigate = useNavigate()
  const subagentsBySession = useStore($subagentsBySession)

  const subagents = sessionId ? (subagentsBySession[sessionId] ?? []) : []
  const running = activeSubagentCount(subagents)

  // Only show when there are active (running/queued) subagents.
  if (running === 0) {
    return null
  }

  // Sort: running first, then by startedAt ascending.
  const active = useMemo(
    () =>
      [...subagents]
        .filter(s => s.status === 'running' || s.status === 'queued')
        .sort((a, b) => {
          if (a.status !== b.status) {
            return a.status === 'running' ? -1 : 1
          }
          return a.startedAt - b.startedAt
        }),
    [subagents]
  )

  if (active.length === 0) {
    return null
  }

  const openAgentDetail = (agentId: string) => {
    setFocusSubagentId(agentId)
    navigate(AGENTS_ROUTE)
  }

  return (
    <div
      className="mt-2 w-full min-w-0 rounded-lg border border-(--ui-stroke-tertiary) bg-(--ui-chat-surface-background) text-[0.78rem] leading-snug"
      data-slot="aui_subagent-activity"
    >
      {/* Header */}
      <div className="flex items-center gap-1.5 border-b border-(--ui-stroke-tertiary) px-2.5 py-1.5">
        <Sparkles className="size-3 shrink-0 text-(--ui-accent)" />
        <span className="font-medium text-(--ui-text-secondary)">
          {t.statusStack.subagents(running)}
        </span>
      </div>

      {/* Agent list */}
      <div className="divide-y divide-(--ui-stroke-tertiary)/50">
        {active.map(agent => (
          <SubagentRow
            agent={agent}
            key={agent.id}
            onClick={() => openAgentDetail(agent.id)}
          />
        ))}
      </div>
    </div>
  )
}

function statusGlyph(status: SubagentProgress['status']): ReactNode {
  if (status === 'running' || status === 'queued') {
    return (
      <GlyphSpinner
        aria-label="Running"
        className="size-3.5 shrink-0 text-muted-foreground/80"
        spinner="breathe"
      />
    )
  }

  if (status === 'failed' || status === 'interrupted') {
    return <AlertCircle className="size-3.5 shrink-0 text-destructive" />
  }

  return <CheckCircle2 className="size-3.5 shrink-0 text-emerald-600/85 dark:text-emerald-400/85" />
}

function SubagentRow({
  agent,
  onClick
}: {
  agent: SubagentProgress
  onClick: () => void
}) {
  const running = agent.status === 'running' || agent.status === 'queued'
  const enterRef = useEnterAnimation(running, `subagent:${agent.id}`)
  const elapsed = useElapsedSeconds(running, `subagent-timer:${agent.id}`)

  // Truncate goal to a single line
  const goal = agent.goal.replace(/\s+/g, ' ').trim()
  const displayGoal = goal.length > 80 ? `${goal.slice(0, 79)}…` : goal

  return (
    <button
      className={cn(
        'flex w-full min-w-0 items-center gap-2 px-2.5 py-1.5 text-left transition-colors',
        'hover:bg-(--ui-row-hover-background) focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring/60'
      )}
      data-subagent-id={agent.id}
      onClick={onClick}
      ref={enterRef}
      type="button"
    >
      {statusGlyph(agent.status)}

      <div className="flex min-w-0 flex-1 flex-col gap-0">
        <span className="truncate font-medium text-foreground/90">
          {displayGoal}
        </span>
        {running && agent.currentTool && (
          <span className="truncate text-[0.7rem] text-muted-foreground/70">
            {agent.currentTool.replace(/_/g, ' ')}
          </span>
        )}
      </div>

      {running && (
        <ActivityTimerText
          className="shrink-0 text-[0.7rem] tabular-nums text-muted-foreground/60"
          seconds={elapsed}
        />
      )}
    </button>
  )
}