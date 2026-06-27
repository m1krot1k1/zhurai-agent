/**
 * Thin re-export wrapper around @hermes/shared subagent tree.
 *
 * Preserves the TUI's richer SubagentProgress type through generic
 * parameter inference.  All pure functions (buildSubagentTree,
 * aggregate, sparkline, etc.) live in @hermes/shared so the Desktop
 * and future consumers stay in sync.
 */
import type {
  SubagentAggregate as SharedAggregate,
  SubagentNode as SharedNode,
} from '@hermes/shared'
import {
  aggregate as sharedAggregate,
  buildSubagentTree as sharedBuild,
  descendantIds as sharedDescendantIds,
  flattenTree as sharedFlatten,
  fmtCost,
  fmtDuration,
  fmtTokens,
  formatSummary as sharedFormatSummary,
  hotnessBucket,
  isRunning,
  peakHotness as sharedPeakHotness,
  sparkline,
  topLevelSubagents as sharedTopLevel,
  treeTotals as sharedTreeTotals,
  widthByDepth as sharedWidthByDepth,
} from '@hermes/shared'
import type { SubagentAggregate, SubagentNode, SubagentProgress } from '../types.js'

// Re-export types (TUI's own types from types.ts)
export type { SubagentAggregate, SubagentNode, SubagentProgress }

// Re-export constants
export { isRunning, sparkline, hotnessBucket, fmtCost, fmtDuration, fmtTokens }

// Wrapped functions with TUI types
export function buildSubagentTree(
  items: readonly SubagentProgress[]
): SubagentNode[] {
  return sharedBuild(items) as SubagentNode[]
}

export function aggregate(
  item: SubagentProgress,
  children: readonly SubagentNode[]
): SubagentAggregate {
  return sharedAggregate(item, children as any)
}

export function treeTotals(tree: readonly SubagentNode[]): SubagentAggregate {
  return sharedTreeTotals(tree as any)
}

export function widthByDepth(tree: readonly SubagentNode[]): number[] {
  return sharedWidthByDepth(tree as any)
}

export function flattenTree(tree: readonly SubagentNode[]): SubagentNode[] {
  return sharedFlatten(tree as any)
}

export function descendantIds(node: SubagentNode): string[] {
  return sharedDescendantIds(node as any)
}

export function peakHotness(tree: readonly SubagentNode[]): number {
  return sharedPeakHotness(tree as any)
}

export function formatSummary(totals: SubagentAggregate): string {
  return sharedFormatSummary(totals)
}

export function topLevelSubagents(
  items: readonly SubagentProgress[]
): SubagentProgress[] {
  return sharedTopLevel(items)
}