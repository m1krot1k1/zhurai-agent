import { useStore } from '@nanostores/react'
import { type PointerEvent as ReactPointerEvent, type ReactNode, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { AGENTS_ROUTE } from '@/app/routes'

import { blurComposerInput } from '@/app/chat/composer/focus'
import { useElapsedSeconds } from '@/components/chat/activity-timer'
import { ActivityTimerText } from '@/components/chat/activity-timer-text'
import { composerDockCard } from '@/components/chat/composer-dock'
import { Button } from '@/components/ui/button'
import { FadeText } from '@/components/ui/fade-text'
import { GlyphSpinner } from '@/components/ui/glyph-spinner'
import { type Translations, useI18n } from '@/i18n'
import { AlertCircle, CheckCircle2, ExternalLink, Sparkles, X } from '@/lib/icons'
import { formatSubagentDisplay, formatSubagentRoleBadge } from '@/lib/subagent-label'
import { useEnterAnimation } from '@/lib/use-enter-animation'
import { cn } from '@/lib/utils'
import { $threadScrolledUp } from '@/store/thread-scroll'
import {
  $focusSubagentId,
  $subagentInspectorOpen,
  $subagentInspectorSelectedId,
  $subagentInspectorHeight,
  $subagentsBySession,
  activeSubagentCount,
  buildSubagentTree,
  clampSubagentInspectorHeight,
  closeSubagentInspector,
  openSubagentInspector,
  setFocusSubagentId,
  setSubagentInspectorHeight,
  type SubagentNode,
  type SubagentStatus,
  type SubagentStreamEntry
} from '@/store/subagents'

const flatten = (nodes: readonly SubagentNode[]): SubagentNode[] =>
  nodes.flatMap(node => [node, ...flatten(node.children)])

const STREAM_TONE: Record<SubagentStreamEntry['kind'], string> = {
  progress: 'text-muted-foreground/75',
  summary: 'text-foreground/85',
  thinking: 'text-muted-foreground/80',
  tool: 'text-foreground/85'
}

function statusGlyph(status: SubagentStatus, a: Translations['agents']): ReactNode {
  if (status === 'running' || status === 'queued') {
    return (
      <GlyphSpinner
        ariaLabel={a.running}
        className="size-3 shrink-0 text-muted-foreground/80"
        spinner="breathe"
      />
    )
  }

  if (status === 'failed' || status === 'error' || status === 'interrupted' || status === 'timeout') {
    return <AlertCircle aria-label={a.failed} className="size-3 shrink-0 text-destructive" />
  }

  return <CheckCircle2 aria-label={a.done} className="size-3 shrink-0 text-emerald-600/85 dark:text-emerald-400/85" />
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

interface SubagentInspectorPanelProps {
  sessionId: null | string
}

export function SubagentInspectorPanel({ sessionId }: SubagentInspectorPanelProps) {
  const { t } = useI18n()
  const navigate = useNavigate()
  const open = useStore($subagentInspectorOpen)
  const selectedId = useStore($subagentInspectorSelectedId)
  const focusId = useStore($focusSubagentId)
  const panelHeight = useStore($subagentInspectorHeight)
  const subagentsBySession = useStore($subagentsBySession)
  const scrolledUp = useStore($threadScrolledUp)

  const subagents = sessionId ? (subagentsBySession[sessionId] ?? []) : []
  const tree = useMemo(() => buildSubagentTree(subagents), [subagents])
  const flat = useMemo(() => flatten(tree), [tree])

  const selected = useMemo(() => {
    if (flat.length === 0) {
      return null
    }

    if (selectedId) {
      const match = flat.find(
        node => node.id === selectedId || node.sessionId === selectedId || node.id.endsWith(`:${selectedId}`)
      )

      if (match) {
        return match
      }
    }

    const running = flat.find(n => n.status === 'running' || n.status === 'queued')

    return running ?? flat[0]!
  }, [flat, selectedId])

  useEffect(() => {
    if (focusId) {
      openSubagentInspector(focusId)
    }
  }, [focusId])

  useEffect(() => {
    if (!open || !selected || selected.id === selectedId) {
      return
    }

    $subagentInspectorSelectedId.set(selected.id)
  }, [open, selected, selectedId])

  useEffect(() => {
    if (open && flat.length === 0) {
      closeSubagentInspector()
    }
  }, [flat.length, open])

  const panelRef = useRef<HTMLDivElement | null>(null)
  const resizeRef = useRef<{ startY: number; startHeight: number } | null>(null)

  const startResize = useCallback(
    (event: ReactPointerEvent<HTMLDivElement>) => {
      event.preventDefault()
      event.stopPropagation()
      resizeRef.current = { startY: event.clientY, startHeight: panelHeight }

      const onMove = (move: PointerEvent) => {
        const state = resizeRef.current
        if (!state) {
          return
        }

        setSubagentInspectorHeight(state.startHeight + (state.startY - move.clientY))
      }

      const onUp = () => {
        resizeRef.current = null
        window.removeEventListener('pointermove', onMove)
        window.removeEventListener('pointerup', onUp)
      }

      window.addEventListener('pointermove', onMove)
      window.addEventListener('pointerup', onUp)
    },
    [panelHeight]
  )

  const openFullscreen = useCallback(() => {
    if (selected) {
      setFocusSubagentId(selected.id)
    }

    closeSubagentInspector()
    navigate(AGENTS_ROUTE)
  }, [navigate, selected])

  useLayoutEffect(() => {
    const root = document.documentElement
    const el = panelRef.current

    if (!open || !el) {
      root.style.removeProperty('--subagent-inspector-measured-height')

      return
    }

    let last = -1

    const sync = () => {
      const bucket = Math.round(el.getBoundingClientRect().height / 8) * 8

      if (bucket !== last) {
        last = bucket
        root.style.setProperty('--subagent-inspector-measured-height', `${bucket}px`)
      }
    }

    const observer = new ResizeObserver(sync)
    observer.observe(el)
    sync()

    return () => {
      observer.disconnect()
      root.style.removeProperty('--subagent-inspector-measured-height')
    }
  }, [open, flat.length, selected?.id, panelHeight])

  if (!open || !selected || flat.length === 0) {
    return null
  }

  const runningCount = activeSubagentCount(subagents)

  return (
    <div
      className="absolute inset-x-0 bottom-full z-4 translate-y-[calc(0.5rem+1px)]"
      onPointerDownCapture={() => blurComposerInput()}
      ref={panelRef}
      style={{
        height: `${panelHeight}px`,
        marginBottom: 'var(--status-stack-measured-height, 0px)',
        maxHeight: 'min(72vh, 720px)'
      }}
    >
      <div
        aria-label={t.agents.resizeInspector}
        className="group absolute inset-x-0 -top-1 z-5 h-2 cursor-row-resize"
        onDoubleClick={() => setSubagentInspectorHeight(320)}
        onPointerDown={startResize}
        role="separator"
      >
        <span className="absolute left-1/2 top-1/2 h-0.75 w-20 -translate-x-1/2 -translate-y-1/2 rounded-full bg-muted-foreground/70 opacity-0 transition-opacity group-hover:opacity-60" />
      </div>
      <div
        className={cn(
          composerDockCard('top'),
          'mx-2 flex h-full min-h-0 flex-col overflow-hidden rounded-b-none border-b-0 pt-0.5 pb-0 shadow-md'
        )}
        data-slot="subagent-inspector"
      >
        <header className="flex shrink-0 items-center gap-2 border-b border-(--ui-stroke-tertiary)/80 px-3 py-2">
          <Sparkles className="size-3.5 shrink-0 text-(--ui-accent)" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-[0.78rem] font-semibold text-foreground">{t.agents.title}</p>
            <p className="truncate text-[0.65rem] text-muted-foreground/75">
              {t.agents.agentsCount(flat.length)}
              {runningCount > 0 ? ` · ${t.agents.activeCount(runningCount)}` : ''}
            </p>
          </div>
          <Button
            aria-label={t.agents.expandFullscreen}
            className="size-7 shrink-0 text-muted-foreground/80"
            onClick={event => {
              event.stopPropagation()
              openFullscreen()
            }}
            size="icon"
            type="button"
            variant="ghost"
          >
            <ExternalLink className="size-3.5" />
          </Button>
          <Button
            aria-label={t.agents.close}
            className="size-7 shrink-0 text-muted-foreground/80"
            onClick={event => {
              event.stopPropagation()
              closeSubagentInspector()
            }}
            size="icon"
            type="button"
            variant="ghost"
          >
            <X className="size-3.5" />
          </Button>
        </header>

        <div
          className={cn(
            'flex min-h-0 min-w-0 flex-1 transition-opacity duration-200 ease-out',
            scrolledUp ? 'opacity-30 group-hover/composer:opacity-100' : 'opacity-100'
          )}
        >
          <nav
            aria-label={t.agents.title}
            className="flex w-[38%] min-w-[9.5rem] max-w-[13rem] shrink-0 flex-col gap-0.5 overflow-y-auto overscroll-contain border-r border-(--ui-stroke-tertiary)/70 py-1.5"
          >
            {flat.map(node => (
              <NavItem
                depth={node.depth}
                key={node.id}
                node={node}
                onSelect={() => openSubagentInspector(node.id)}
                selected={node.id === selected.id}
              />
            ))}
          </nav>

          <SubagentDetailPane node={selected} />
        </div>
      </div>
    </div>
  )
}

function NavItem({
  depth,
  node,
  onSelect,
  selected
}: {
  depth: number
  node: SubagentNode
  onSelect: () => void
  selected: boolean
}) {
  const { t } = useI18n()
  const running = node.status === 'running' || node.status === 'queued'
  const elapsed = useElapsedSeconds(running, `inspector-nav:${node.id}`)
  const roleBadge = formatSubagentRoleBadge(node.role)
  const { badge, title } = formatSubagentDisplay(node.goal, node.agentId, 48)

  return (
    <button
      className={cn(
        'mx-1.5 flex min-w-0 items-start gap-1.5 rounded-md py-1.5 text-left transition-colors',
        depth > 0 && 'border-l border-(--ui-stroke-tertiary)/50',
        selected
          ? 'bg-[color-mix(in_srgb,var(--ui-accent)_14%,transparent)] ring-1 ring-[color-mix(in_srgb,var(--ui-accent)_40%,transparent)]'
          : 'hover:bg-(--ui-row-hover-background)'
      )}
      data-subagent-nav-id={node.id}
      onClick={onSelect}
      style={{ marginLeft: `${Math.min(depth, 4) * 0.45 + 0.375}rem`, paddingLeft: '0.5rem', paddingRight: '0.5rem' }}
      type="button"
    >
      <span className="mt-0.5 shrink-0">{statusGlyph(node.status, t.agents)}</span>
      <span className="min-w-0 flex-1">
        <span className="flex min-w-0 flex-wrap items-center gap-1">
          {badge ? (
            <span className="shrink-0 rounded bg-emerald-500/15 px-1 py-px font-mono text-[0.58rem] font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
              {badge}
            </span>
          ) : null}
          {roleBadge && roleBadge !== badge?.toLowerCase() ? (
            <span className="shrink-0 rounded bg-primary/15 px-1 py-px font-mono text-[0.58rem] font-semibold uppercase tracking-wide text-primary">
              {roleBadge}
            </span>
          ) : null}
        </span>
        <span className={cn('mt-0.5 block truncate text-[0.7rem] leading-snug', selected ? 'text-foreground' : 'text-foreground/85')}>
          {title}
        </span>
        {running && node.currentTool ? (
          <span className="mt-0.5 block truncate text-[0.62rem] text-muted-foreground/65">{node.currentTool.replace(/_/g, ' ')}</span>
        ) : null}
      </span>
      {running ? (
        <ActivityTimerText className="mt-0.5 shrink-0 text-[0.62rem] tabular-nums text-muted-foreground/55" seconds={elapsed} />
      ) : null}
    </button>
  )
}

function SubagentDetailPane({ node }: { node: SubagentNode }) {
  const { t } = useI18n()
  const running = node.status === 'running' || node.status === 'queued'
  const elapsed = useElapsedSeconds(running, `inspector-detail:${node.id}`)
  const [nowMs, setNowMs] = useState(() => Date.now())
  const roleBadge = formatSubagentRoleBadge(node.role)
  const { badge, title } = formatSubagentDisplay(node.goal, node.agentId, 160)
  const showRoleBadge = roleBadge && roleBadge !== badge?.toLowerCase()

  const durationSeconds =
    typeof node.durationSeconds === 'number' ? Math.max(0, Math.round(node.durationSeconds)) : elapsed

  useEffect(() => {
    if (!running) {
      return
    }

    const id = window.setInterval(() => setNowMs(Date.now()), 5_000)

    return () => window.clearInterval(id)
  }, [running])

  const subtitle = [
    node.model,
    fmtDuration(durationSeconds, t.agents),
    node.toolCount ? t.agents.toolsCount(node.toolCount) : '',
    fmtTokens((node.inputTokens ?? 0) + (node.outputTokens ?? 0), t.agents),
    t.agents.updatedAgo(fmtAge(node.updatedAt, nowMs, t.agents))
  ].filter(Boolean)

  const stream = node.stream
  const fileLines = [...node.filesWritten.map(p => `+ ${p}`), ...node.filesRead.map(p => `· ${p}`)]

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
      <div className="shrink-0 border-b border-(--ui-stroke-tertiary)/50 px-3 py-2">
        <div className="flex min-w-0 items-start gap-2">
          <span className="mt-0.5 shrink-0">{statusGlyph(node.status, t.agents)}</span>
          <div className="min-w-0 flex-1">
            <p className="flex min-w-0 flex-wrap items-center gap-1.5 text-[0.82rem] font-medium leading-snug text-foreground">
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
              <span className="min-w-0 wrap-anywhere">{title}</span>
            </p>
            {subtitle.length > 0 ? (
              <FadeText className="mt-1 text-[0.66rem] leading-relaxed text-muted-foreground/70">{subtitle.join(' · ')}</FadeText>
            ) : null}
          </div>
          {running ? <ActivityTimerText className="shrink-0 text-[0.68rem]" seconds={durationSeconds} /> : null}
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-3 py-2">
        {running && stream.length === 0 ? (
          <p className="text-[0.72rem] leading-relaxed text-muted-foreground/75">
            {node.currentTool ? node.currentTool.replace(/_/g, ' ') : t.agents.waitingForActivity}
          </p>
        ) : null}

        {stream.length > 0 ? (
          <div className="grid min-w-0 gap-1.5" data-selectable-text="true">
            {stream.map((entry, i) => (
              <StreamLine
                active={running && i === stream.length - 1}
                entry={entry}
                key={`${entry.kind}:${entry.at}:${i}`}
                parentRunning={running}
                rowKey={`${node.id}:${entry.kind}:${entry.at}`}
              />
            ))}
          </div>
        ) : null}

        {node.summary && !running ? (
          <p className="mt-2 text-[0.72rem] leading-relaxed text-foreground/85">{node.summary}</p>
        ) : null}

        {fileLines.length > 0 ? (
          <div className="mt-3 grid min-w-0 gap-0.5" data-selectable-text="true">
            <p className="text-[0.58rem] font-medium tracking-wider text-muted-foreground/60 uppercase">{t.agents.files}</p>
            {fileLines.slice(0, 12).map(line => (
              <p className="wrap-break-word font-mono text-[0.67rem] leading-relaxed text-muted-foreground/80" key={line}>
                {line}
              </p>
            ))}
            {fileLines.length > 12 ? (
              <p className="font-mono text-[0.67rem] text-muted-foreground/65">{t.agents.moreFiles(fileLines.length - 12)}</p>
            ) : null}
          </div>
        ) : null}
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
  const enterRef = useEnterAnimation(parentRunning, `inspector-stream:${rowKey}`)
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
