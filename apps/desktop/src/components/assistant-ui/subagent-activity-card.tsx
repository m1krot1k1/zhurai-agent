'use client'

import { useStore } from '@nanostores/react'
import { type ReactNode, useMemo } from 'react'

import { useElapsedSeconds } from '@/components/chat/activity-timer'
import { ActivityTimerText } from '@/components/chat/activity-timer-text'
import { GlyphSpinner } from '@/components/ui/glyph-spinner'
import { type Translations, useI18n } from '@/i18n'
import { formatSubagentDisplay, formatSubagentRoleBadge } from '@/lib/subagent-label'
import { useEnterAnimation } from '@/lib/use-enter-animation'
import { AlertCircle, CheckCircle2, Sparkles } from '@/lib/icons'
import { cn } from '@/lib/utils'
import {
  $subagentsBySession,
  activeSubagentCount,
  buildSubagentTree,
  groupSubagentsByWave,
  openSubagentInspector,
  type SubagentNode,
  type SubagentProgress
} from '@/store/subagents'

/**
 * Inline subagent activity card shown inside the latest assistant message only
 * (session-wide store; avoids duplicate panels on synthesis follow-up turns).
 */
export function SubagentActivityCard({ sessionId }: { sessionId: string | null }) {
  const { t } = useI18n()
  const subagentsBySession = useStore($subagentsBySession)

  const subagents = sessionId ? (subagentsBySession[sessionId] ?? []) : []
  const waves = useMemo(() => groupSubagentsByWave(subagents), [subagents])

  const running = activeSubagentCount(subagents)
  const completed = subagents.length - running

  if (subagents.length === 0) {
    return null
  }

  const openAgentDetail = (agentId: string) => openSubagentInspector(agentId)

  const header =
    running > 0
      ? t.statusStack.subagents(running)
      : completed > 0
        ? t.agents.turnComplete(completed)
        : t.statusStack.subagents(0)

  const multiWave = waves.size > 1

  return (
    <div
      className="mt-2 w-full min-w-0 rounded-lg border border-(--ui-stroke-tertiary) bg-(--ui-chat-surface-background) text-[0.78rem] leading-snug"
      data-slot="aui_subagent-activity"
    >
      <div className="flex items-center gap-1.5 border-b border-(--ui-stroke-tertiary) px-2.5 py-1.5">
        <Sparkles className="size-3 shrink-0 text-(--ui-accent)" />
        <span className="font-medium text-(--ui-text-secondary)">{header}</span>
      </div>

      {[...waves.entries()].map(([waveNumber, waveAgents]) => {
        const tree = buildSubagentTree(waveAgents)
        const waveRunning = activeSubagentCount(waveAgents)

        return (
          <div className="divide-y divide-(--ui-stroke-tertiary)/50" key={`wave-${waveNumber}`}>
            {multiWave ? (
              <div className="flex items-center gap-1.5 bg-(--ui-row-hover-background)/40 px-2.5 py-1 text-[0.68rem] font-semibold uppercase tracking-wide text-muted-foreground">
                {t.agents.waveLabel(waveNumber)}
                {waveRunning > 0 ? (
                  <span className="font-normal normal-case text-muted-foreground/80">
                    · {t.statusStack.subagents(waveRunning)}
                  </span>
                ) : null}
              </div>
            ) : null}
            {tree.map(node => (
              <SubagentTreeRow depth={0} key={node.id} node={node} onOpen={openAgentDetail} />
            ))}
          </div>
        )
      })}
    </div>
  )
}

function SubagentTreeRow({
  depth,
  node,
  onOpen
}: {
  depth: number
  node: SubagentNode
  onOpen: (id: string) => void
}) {
  return (
    <div className={cn(depth > 0 && 'border-l border-(--ui-stroke-tertiary)/60')}>
      <SubagentRow agent={node} depth={depth} onClick={() => onOpen(node.id)} />
      {node.children.length > 0 ? (
        <div className="grid">
          {node.children.map(child => (
            <SubagentTreeRow depth={depth + 1} key={child.id} node={child} onOpen={onOpen} />
          ))}
        </div>
      ) : null}
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
  depth = 0,
  onClick
}: {
  agent: SubagentProgress
  depth?: number
  onClick: () => void
}) {
  const { t } = useI18n()
  const running = agent.status === 'running' || agent.status === 'queued'
  const enterRef = useEnterAnimation(running, `subagent:${agent.id}`)
  const elapsed = useElapsedSeconds(running, `subagent-timer:${agent.id}`)

  const { badge, title } = formatSubagentDisplay(agent.goal, agent.agentId)
  const roleBadge = formatSubagentRoleBadge(agent.role)
  const showRoleBadge = roleBadge && roleBadge !== badge?.toLowerCase()

  return (
    <button
      className={cn(
        'flex w-full min-w-0 items-center gap-2 py-1.5 text-left transition-colors',
        'hover:bg-(--ui-row-hover-background) focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring/60',
        depth > 0 ? 'pl-4 pr-2.5' : 'px-2.5'
      )}
      data-subagent-id={agent.id}
      onClick={onClick}
      ref={enterRef}
      title={t.agents.tapToExpand}
      type="button"
    >
      {statusGlyph(agent.status, t.agents)}

      <div className="flex min-w-0 flex-1 flex-col gap-0">
        <span className="flex min-w-0 items-center gap-1.5">
          {badge ? (
            <span className="shrink-0 rounded bg-emerald-500/15 px-1 py-0.5 font-mono text-[0.62rem] font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
              {badge}
            </span>
          ) : null}
          {showRoleBadge ? (
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
        ) : running ? (
          <span className="truncate text-[0.7rem] text-muted-foreground/70">{t.agents.waitingForActivity}</span>
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
