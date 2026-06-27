import { useStore } from '@nanostores/react'
import { type ReactNode, useEffect, useMemo, useRef, useState } from 'react'

import { useElapsedSeconds } from '@/components/chat/activity-timer'
import { ActivityTimerText } from '@/components/chat/activity-timer-text'
import { FadeText } from '@/components/ui/fade-text'
import { GlyphSpinner } from '@/components/ui/glyph-spinner'
import { type Translations, useI18n } from '@/i18n'
import { AlertCircle, CheckCircle2, Sparkles, Users } from '@/lib/icons'
import { useEnterAnimation } from '@/lib/use-enter-animation'
import { cn } from '@/lib/utils'
import { $repoAgents, refreshRepoAgents, type RepoAgentsState } from '@/store/agent-discovery'
import { $activeSessionId } from '@/store/session'
import {
  $focusSubagentId,
  $subagentsBySession,
  buildSubagentTree,
  setFocusSubagentId,
  type SubagentNode,
  type SubagentStatus,
  type SubagentStreamEntry
} from '@/store/subagents'

import { OverlayView } from '../overlays/overlay-view'

// Mirrors statusGlyph() in tool-fallback.tsx so subagent rows speak the
// same visual vocabulary as the chat tool blocks.
function statusGlyph(status: SubagentStatus, a: Translations['agents']): ReactNode {
  if (status === 'running' || status === 'queued') {
    return (
      <GlyphSpinner
        ariaLabel={a.running}
        className="size-3.5 shrink-0 text-[0.95rem] text-muted-foreground/80"
        spinner="breathe"
      />
    )
  }

  if (status === 'failed' || status === 'error' || status === 'interrupted' || status === 'timeout') {
    return <AlertCircle aria-label={a.failed} className="size-3.5 shrink-0 text-destructive" />
  }

  return <CheckCircle2 aria-label={a.done} className="size-3.5 shrink-0 text-emerald-600/85 dark:text-emerald-400/85" />
}

const STREAM_TONE: Record<SubagentStreamEntry['kind'], string> = {
  progress: 'text-muted-foreground/75',
  summary: 'text-foreground/85',
  thinking: 'text-muted-foreground/80',
  tool: 'text-foreground/85'
}

function streamGlyph(entry: SubagentStreamEntry): ReactNode {
  if (entry.isError) {
    return <AlertCircle aria-hidden className="mt-0.5 size-3 shrink-0 text-destructive" />
  }

  if (entry.kind === 'tool') {
    return <span aria-hidden className="mt-0.5 size-1.5 shrink-0 rounded-full bg-foreground/55" />
  }

  if (entry.kind === 'summary') {
    return <CheckCircle2 aria-hidden className="mt-0.5 size-3 shrink-0 text-emerald-600/85 dark:text-emerald-400/85" />
  }

  if (entry.kind === 'thinking') {
    return (
      <span aria-hidden className="font-mono text-[0.7rem] leading-none text-muted-foreground/70">
        …
      </span>
    )
  }

  return <span aria-hidden className="mt-0.5 size-1 shrink-0 rounded-full bg-muted-foreground/55" />
}

interface AgentsViewProps {
  onClose: () => void
}

export function AgentsView({ onClose }: AgentsViewProps) {
  const { t } = useI18n()
  const activeSessionId = useStore($activeSessionId)
  const subagentsBySession = useStore($subagentsBySession)
  const repoAgents = useStore($repoAgents)
  const focusAgentId = useStore($focusSubagentId)

  useEffect(() => {
    void refreshRepoAgents()
  }, [])

  const activeSubagents = useMemo(
    () => (activeSessionId ? (subagentsBySession[activeSessionId] ?? []) : []),
    [activeSessionId, subagentsBySession]
  )

  const tree = useMemo(() => buildSubagentTree(activeSubagents), [activeSubagents])

  return (
    <OverlayView
      closeLabel={t.agents.close}
      contentClassName="px-5 pt-5 pb-4 sm:px-6"
      onClose={onClose}
      rootClassName="mx-auto max-w-3xl"
    >
      <header className="mb-3 shrink-0">
        <h2 className="text-sm font-semibold text-foreground">{t.agents.title}</h2>
        <p className="text-xs text-muted-foreground/80">{t.agents.subtitle}</p>
      </header>
      <RepoAgentsSection state={repoAgents} />
      <SubagentTree focusAgentId={focusAgentId} tree={tree} />
    </OverlayView>
  )
}

function RepoAgentsSection({ state }: { state: RepoAgentsState }) {
  const { t } = useI18n()

  if (state.loading && state.agents.length === 0) {
    return (
      <section className="mb-5 grid gap-2 rounded-lg border border-border/50 bg-muted/20 px-3 py-3">
        <div className="flex items-center gap-2 text-xs text-muted-foreground/80">
          <GlyphSpinner ariaLabel={t.agents.repoLoading} className="size-3.5" spinner="breathe" />
          <span>{t.agents.repoLoading}</span>
        </div>
      </section>
    )
  }

  if (state.agents.length === 0) {
    if (state.error === 'agents-dir-missing' || state.error === 'root-unresolved') {
      return (
        <section className="mb-5 rounded-lg border border-dashed border-border/60 px-3 py-3">
          <p className="text-xs leading-relaxed text-muted-foreground/75">{t.agents.repoEmptyHint}</p>
        </section>
      )
    }

    return null
  }

  return (
    <section className="mb-5 grid min-w-0 gap-2">
      <div className="flex min-w-0 items-baseline justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          <Users aria-hidden className="size-3.5 shrink-0 text-muted-foreground/70" />
          <h3 className="text-[0.72rem] font-medium uppercase tracking-wider text-muted-foreground/75">
            {t.agents.repoTitle}
          </h3>
        </div>
        <p className="truncate text-[0.62rem] text-muted-foreground/55" title={state.root ?? undefined}>
          {state.root ? t.agents.repoFrom(state.agents.length) : t.agents.repoCount(state.agents.length)}
        </p>
      </div>
      <ul className="grid min-w-0 gap-2 rounded-lg border border-border/50 bg-muted/15 px-3 py-2">
        {state.agents.map(agent => (
          <li className="grid min-w-0 gap-0.5" key={agent.id}>
            <span className="text-[0.8rem] font-medium text-foreground/90">{agent.name}</span>
            {agent.description ? (
              <span className="wrap-anywhere text-[0.68rem] leading-relaxed text-muted-foreground/75">
                {agent.description}
              </span>
            ) : (
              <span className="font-mono text-[0.62rem] text-muted-foreground/55">{agent.fileName}</span>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}

const fmtDuration = (seconds: number | undefined, a: Translations['agents']) => {
  if (!seconds || seconds <= 0) {
    return ''
  }

  if (seconds < 60) {
    return a.durationSeconds(seconds.toFixed(1))
  }

  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)

  return a.durationMinutes(m, s)
}

const fmtTokens = (value: number | undefined, a: Translations['agents']) => {
  if (!value) {
    return ''
  }

  return value >= 1000 ? a.tokensK((value / 1000).toFixed(1)) : a.tokens(value)
}

const fmtAge = (updatedAt: number, nowMs: number, a: Translations['agents']) => {
  const s = Math.max(0, Math.round((nowMs - updatedAt) / 1000))

  if (s < 2) {
    return a.ageNow
  }

  if (s < 60) {
    return a.ageSeconds(s)
  }

  const m = Math.floor(s / 60)

  if (m < 60) {
    return a.ageMinutes(m)
  }

  return a.ageHours(Math.floor(m / 60))
}

const flatten = (nodes: readonly SubagentNode[]): SubagentNode[] =>
  nodes.flatMap(node => [node, ...flatten(node.children)])

interface RootGroup {
  id: string
  delegationIndex: number
  nodes: SubagentNode[]
  taskCount: number
}

function groupDelegations(roots: readonly SubagentNode[]): RootGroup[] {
  const groups: RootGroup[] = []
  let n = 0

  for (const node of roots) {
    const prev = groups.at(-1)
    const prevTail = prev?.nodes.at(-1)
    const closeInTime = prevTail ? Math.abs(node.startedAt - prevTail.startedAt) <= 5_000 : false
    const sameShape = prev && node.taskCount > 1 && prev.taskCount === node.taskCount
    const uniqueStep = prev ? !prev.nodes.some(item => item.taskIndex === node.taskIndex) : false

    if (prev && sameShape && closeInTime && uniqueStep) {
      prev.nodes.push(node)

      continue
    }

    if (node.taskCount > 1) {
      n += 1
      groups.push({ id: `delegation-${n}`, delegationIndex: n, nodes: [node], taskCount: node.taskCount })

      continue
    }

    groups.push({ id: node.id, delegationIndex: 0, nodes: [node], taskCount: node.taskCount })
  }

  return groups
}

function SubagentTree({ focusAgentId, tree }: { focusAgentId: null | string; tree: SubagentNode[] }) {
  const { t } = useI18n()
  const flat = useMemo(() => flatten(tree), [tree])
  const groups = useMemo(() => groupDelegations(tree), [tree])
  const [nowMs, setNowMs] = useState(() => Date.now())
  const [highlightAgentId, setHighlightAgentId] = useState<null | string>(null)
  const pendingScrollRef = useRef<null | string>(null)

  // Inline chat link → agents overlay: resolve id, expand ancestors, scroll once.
  useEffect(() => {
    if (!focusAgentId) {
      return
    }

    const match = flat.find(
      node => node.id === focusAgentId || node.sessionId === focusAgentId || node.id.endsWith(`:${focusAgentId}`)
    )

    if (match) {
      pendingScrollRef.current = match.id
      setHighlightAgentId(match.id)
    }

    setFocusSubagentId(null)
  }, [flat, focusAgentId])

  useEffect(() => {
    const target = pendingScrollRef.current

    if (!target) {
      return
    }

    pendingScrollRef.current = null

    requestAnimationFrame(() => {
      document.querySelector(`[data-subagent-id="${CSS.escape(target)}"]`)?.scrollIntoView({ block: 'nearest' })
    })
  }, [flat, groups, highlightAgentId])

  useEffect(() => {
    if (!highlightAgentId) {
      return
    }

    const timer = window.setTimeout(() => setHighlightAgentId(null), 2_500)

    return () => window.clearTimeout(timer)
  }, [highlightAgentId])

  const active = flat.filter(n => n.status === 'running' || n.status === 'queued').length
  const failed = flat.filter(n => n.status === 'failed' || n.status === 'error' || n.status === 'interrupted' || n.status === 'timeout').length
  const tools = flat.reduce((sum, n) => sum + (n.toolCount ?? 0), 0)
  const files = flat.reduce((sum, n) => sum + n.filesRead.length + n.filesWritten.length, 0)
  const tokens = flat.reduce((sum, n) => sum + (n.inputTokens ?? 0) + (n.outputTokens ?? 0), 0)
  const cost = flat.reduce((sum, n) => sum + (n.costUsd ?? 0), 0)

  useEffect(() => {
    if (active <= 0 || typeof window === 'undefined') {
      return
    }

    const id = window.setInterval(() => setNowMs(Date.now()), 500)

    return () => window.clearInterval(id)
  }, [active])

  if (tree.length === 0) {
    return (
      <div className="grid place-items-center gap-3 py-12 text-center">
        <Sparkles className="size-6 text-muted-foreground/60" />
        <p className="text-sm font-medium text-foreground/90">{t.agents.emptyTitle}</p>
        <p className="max-w-md text-xs leading-relaxed text-muted-foreground/75">{t.agents.emptyDesc}</p>
      </div>
    )
  }

  const summary = [
    t.agents.agentsCount(flat.length),
    active > 0 ? t.agents.activeCount(active) : '',
    failed > 0 ? t.agents.failedCount(failed) : '',
    tools > 0 ? t.agents.toolsCount(tools) : '',
    files > 0 ? t.agents.filesCount(files) : '',
    tokens > 0 ? fmtTokens(tokens, t.agents) : '',
    cost > 0 ? `$${cost.toFixed(2)}` : ''
  ].filter(Boolean)

  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-4 overflow-hidden">
      <p className="shrink-0 text-[0.7rem] text-muted-foreground/70">{summary.join(' · ')}</p>
      <div className="min-h-0 min-w-0 flex-1 overflow-x-hidden overflow-y-auto overscroll-contain pr-1">
        <div className="flex min-w-0 flex-col gap-6">
          {groups.map(group => (
            <DelegationGroup group={group} highlightAgentId={highlightAgentId} key={group.id} nowMs={nowMs} />
          ))}
        </div>
      </div>
    </div>
  )
}

function DelegationGroup({
  group,
  highlightAgentId,
  nowMs
}: {
  group: RootGroup
  highlightAgentId: null | string
  nowMs: number
}) {
  const { t } = useI18n()

  if (group.nodes.length === 1 && group.taskCount <= 1) {
    return <SubagentRow highlight={group.nodes[0]!.id === highlightAgentId} highlightAgentId={highlightAgentId} node={group.nodes[0]!} nowMs={nowMs} />
  }

  const activeWorkers = group.nodes.filter(n => n.status === 'running' || n.status === 'queued').length

  return (
    <section className="grid min-w-0 gap-3">
      <p className="text-[0.66rem] font-medium uppercase tracking-wider text-muted-foreground/70">
        {group.delegationIndex > 0 ? t.agents.delegation(group.delegationIndex) : ''}{' '}
        <span className="text-muted-foreground/50">·</span> {t.agents.workers(group.nodes.length)}
        {activeWorkers > 0 ? <span className="text-primary/85"> · {t.agents.workersActive(activeWorkers)}</span> : null}
      </p>
      <div className="grid min-w-0 gap-4">
        {group.nodes.map(node => (
          <SubagentRow highlight={node.id === highlightAgentId} highlightAgentId={highlightAgentId} key={node.id} node={node} nowMs={nowMs} />
        ))}
      </div>
    </section>
  )
}

function StreamLine({
  active,
  entry,
  parentRunning,
  rowKey
}: {
  active: boolean
  entry: SubagentStreamEntry
  parentRunning: boolean
  rowKey: string
}) {
  const { t } = useI18n()
  const enterRef = useEnterAnimation(parentRunning, `subagent-stream:${rowKey}`)
  const isMono = entry.kind === 'tool'
  const tone = entry.isError ? 'text-destructive' : STREAM_TONE[entry.kind]

  return (
    <div className="flex min-w-0 items-baseline gap-2 text-[0.72rem] leading-relaxed" ref={enterRef}>
      <span className="flex h-[0.95rem] shrink-0 items-center">{streamGlyph(entry)}</span>
      <span className={cn('min-w-0 flex-1 wrap-anywhere', tone, isMono && 'font-mono text-[0.69rem]')}>
        {entry.text}
        {active ? (
          <GlyphSpinner
            ariaLabel={t.agents.streaming}
            className="ml-1 inline-block size-2.5 align-middle text-muted-foreground/70"
            spinner="breathe"
          />
        ) : null}
      </span>
    </div>
  )
}

function SubagentRow({
  highlight = false,
  highlightAgentId = null,
  node,
  depth = 0,
  nowMs
}: {
  highlight?: boolean
  highlightAgentId?: null | string
  node: SubagentNode
  depth?: number
  nowMs: number
}) {
  const { t } = useI18n()
  const running = node.status === 'running' || node.status === 'queued'
  const elapsed = useElapsedSeconds(running, `subagent:${node.id}`)

  const durationSeconds =
    typeof node.durationSeconds === 'number' ? Math.max(0, Math.round(node.durationSeconds)) : elapsed

  const [open, setOpen] = useState(() => running || depth < 2)
  const enterRef = useEnterAnimation(true, `subagent-row:${node.id}`)

  useEffect(() => {
    if (running || highlight) {
      setOpen(true)
    }
  }, [highlight, running])

  const visibleRows = open ? node.stream.slice(-10) : node.stream.slice(-2)
  const fileLines = [...node.filesWritten.map(p => `+ ${p}`), ...node.filesRead.map(p => `· ${p}`)]

  const subtitle = [
    node.model,
    fmtDuration(durationSeconds, t.agents),
    node.toolCount ? t.agents.toolsCount(node.toolCount) : '',
    fmtTokens((node.inputTokens ?? 0) + (node.outputTokens ?? 0), t.agents),
    t.agents.updatedAgo(fmtAge(node.updatedAt, nowMs, t.agents))
  ].filter(Boolean)

  return (
    <div
      className={cn(
        'grid min-w-0 max-w-full gap-2 rounded-lg transition-colors',
        depth > 0 && 'pl-4',
        highlight && 'bg-[color-mix(in_srgb,var(--ui-accent)_12%,transparent)] ring-1 ring-[color-mix(in_srgb,var(--ui-accent)_35%,transparent)]'
      )}
      data-slot="tool-block"
      data-subagent-id={node.id}
      ref={enterRef}
    >
      <button
        aria-expanded={open}
        className="group flex w-full min-w-0 items-start gap-2.5 text-left"
        onClick={() => setOpen(v => !v)}
        type="button"
      >
        <span className="mt-0.5 flex h-[1.1rem] shrink-0 items-center">{statusGlyph(node.status, t.agents)}</span>
        <span className="flex min-w-0 flex-1 flex-col gap-0.5">
          <span
            className={cn(
              'wrap-anywhere text-[0.82rem] font-medium leading-[1.1rem] text-foreground/90 transition-colors group-hover:text-foreground',
              running && 'shimmer text-foreground/65'
            )}
          >
            {node.goal}
          </span>
          {subtitle.length > 0 ? (
            <FadeText className="text-[0.66rem] leading-[1.05rem] text-muted-foreground/65">
              {subtitle.join(' · ')}
            </FadeText>
          ) : null}
        </span>
        {running ? <ActivityTimerText className="mt-1 shrink-0 text-[0.6rem]" seconds={durationSeconds} /> : null}
      </button>

      {visibleRows.length > 0 ? (
        <div className="grid min-w-0 gap-1 pl-6" data-selectable-text="true">
          {visibleRows.map((entry, i) => (
            <StreamLine
              active={running && i === visibleRows.length - 1}
              entry={entry}
              key={`${entry.kind}:${entry.at}:${i}`}
              parentRunning={running}
              rowKey={`${node.id}:${entry.kind}:${entry.at}`}
            />
          ))}
        </div>
      ) : null}

      {open && fileLines.length > 0 ? (
        <div className="grid min-w-0 gap-0.5 pl-6" data-selectable-text="true">
          <p className="text-[0.58rem] font-medium tracking-wider text-muted-foreground/60 uppercase">
            {t.agents.files}
          </p>
          {fileLines.slice(0, 8).map(line => (
            <p className="wrap-break-word font-mono text-[0.67rem] leading-relaxed text-muted-foreground/80" key={line}>
              {line}
            </p>
          ))}
          {fileLines.length > 8 ? (
            <p className="font-mono text-[0.67rem] leading-relaxed text-muted-foreground/65">
              {t.agents.moreFiles(fileLines.length - 8)}
            </p>
          ) : null}
        </div>
      ) : null}

      {node.children.length > 0 ? (
        <div className="grid min-w-0 gap-3 pl-6">
          {node.children.map(child => (
            <SubagentRow
              depth={depth + 1}
              highlight={child.id === highlightAgentId}
              highlightAgentId={highlightAgentId}
              key={child.id}
              node={child}
              nowMs={nowMs}
            />
          ))}
        </div>
      ) : null}
    </div>
  )
}
