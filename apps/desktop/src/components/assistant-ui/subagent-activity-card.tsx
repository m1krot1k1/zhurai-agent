'use client'

import { useStore } from '@nanostores/react'
import { type ReactNode, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

import { AGENTS_ROUTE } from '@/app/routes'
import { useElapsedSeconds } from '@/components/chat/activity-timer'
import { ActivityTimerText } from '@/components/chat/activity-timer-text'
import { GlyphSpinner } from '@/components/ui/glyph-spinner'
import { type Translations, useI18n } from '@/i18n'
import { formatSubagentRoleBadge, formatSubagentTitle } from '@/lib/subagent-label'
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
 * Inline subagent activity card shown inside an assistant message.
 * Lists running and recently completed subagents for the current turn
 * (cleared when the user sends the next message).
 */
export function SubagentActivityCard({ sessionId }: { sessionId: string | null }) {
  const { t } = useI18n()
  const navigate = useNavigate()
  const subagentsBySession = useStore($subagentsBySession)

  const subagents = sessionId ? (subagentsBySession[sessionId] ?? []) : []

  const sorted = useMemo(
    () =>
      [...subagents].sort((a, b) => {
        const rank = (s: SubagentProgress['status']) =>
          s === 'running' ? 0 : s === 'queued' ? 1 : 2
        const byStatus = rank(a.status) - rank(b.status)

        if (byStatus !== 0) {
          return byStatus
        }

        return a.startedAt - b.startedAt
      }),
    [subagents]
  )

  const running = activeSubagentCount(subagents)
  const completed = subagents.length - running

  if (subagents.length === 0) {
    return null
  }

  const openAgentDetail = (agentId: string) => {
    setFocusSubagentId(agentId)
    navigate(AGENTS_ROUTE)
  }

  const header =
    running > 0
      ? t.statusStack.subagents(running)
      : completed > 0
        ? t.agents.turnComplete(completed)
        : t.statusStack.subagents(0)

  return (
    <div
      className="mt-2 w-full min-w-0 rounded-lg border border-(--ui-stroke-tertiary) bg-(--ui-chat-surface-background) text-[0.78rem] leading-snug"
      data-slot="aui_subagent-activity"
    >
      <div className="flex items-center gap-1.5 border-b border-(--ui-stroke-tertiary) px-2.5 py-1.5">
        <Sparkles className="size-3 shrink-0 text-(--ui-accent)" />
        <span className="font-medium text-(--ui-text-secondary)">{header}</span>
      </div>

      <div className="divide-y divide-(--ui-stroke-tertiary)/50">
        {sorted.map(agent => (
          <SubagentRow agent={agent} key={agent.id} onClick={() => openAgentDetail(agent.id)} />
        ))}
      </div>
    </div>
  )
}

function statusGlyph(status: SubagentProgress['status'], a: Translations['agents']): ReactNode {
  if (status === 'running' || status === 'queued') {
    return (
      <GlyphSpinner
        ariaLabel={a.running}
        className="size-3.5 shrink-0 text-muted-foreground/80"
        spinner="breathe"
      />
    )
  }

  if (status === 'failed' || status === 'error' || status === 'interrupted' || status === 'timeout') {
    return <AlertCircle aria-label={a.failed} className="size-3.5 shrink-0 text-destructive" />
  }

  return <CheckCircle2 aria-label={a.done} className="size-3.5 shrink-0 text-emerald-600/85 dark:text-emerald-400/85" />
}

function SubagentRow({
  agent,
  onClick
}: {
  agent: SubagentProgress
  onClick: () => void
}) {
  const { t } = useI18n()
  const running = agent.status === 'running' || agent.status === 'queued'
  const enterRef = useEnterAnimation(running, `subagent:${agent.id}`)
  const elapsed = useElapsedSeconds(running, `subagent-timer:${agent.id}`)

  const title = formatSubagentTitle(agent.goal)
  const roleBadge = formatSubagentRoleBadge(agent.role)

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
      {statusGlyph(agent.status, t.agents)}

      <div className="flex min-w-0 flex-1 flex-col gap-0">
        <span className="flex min-w-0 items-center gap-1.5">
          {roleBadge ? (
            <span className="shrink-0 rounded bg-primary/15 px-1 py-0.5 font-mono text-[0.62rem] font-semibold uppercase tracking-wide text-primary">
              {roleBadge}
            </span>
          ) : null}
          <span className="truncate font-medium text-foreground/90">{title}</span>
        </span>
        {running && agent.currentTool ? (
          <span className="truncate text-[0.7rem] text-muted-foreground/70">
            {agent.currentTool.replace(/_/g, ' ')}
          </span>
        ) : !running && agent.summary ? (
          <span className="truncate text-[0.7rem] text-muted-foreground/70">{agent.summary}</span>
        ) : null}
      </div>

      {running ? (
        <ActivityTimerText
          className="shrink-0 text-[0.7rem] tabular-nums text-muted-foreground/60"
          seconds={elapsed}
        />
      ) : null}
    </button>
  )
}
