import { describe, expect, it } from 'vitest'

import {
  buildSubagentTree,
  buildSubagentTreeSorted,
  type SubagentProgress
} from './subagent-tree'

const makeItem = (
  overrides: Partial<SubagentProgress> & Pick<SubagentProgress, 'id' | 'index'>
): SubagentProgress => ({
  depth: 0,
  goal: overrides.id,
  parentId: null,
  status: 'running',
  taskCount: 1,
  toolCount: 0,
  ...overrides
})

describe('buildSubagentTreeSorted', () => {
  it('returns empty list for empty input', () => {
    expect(buildSubagentTreeSorted([])).toEqual([])
  })

  it('matches buildSubagentTree for the same flat input', () => {
    const items = [
      makeItem({ id: 'a', index: 2 }),
      makeItem({ id: 'b', index: 0 }),
      makeItem({ depth: 1, id: 'c', index: 1, parentId: 'a' })
    ]

    expect(buildSubagentTreeSorted(items)).toEqual(buildSubagentTree(items))
  })

  it('keeps root nodes in flat-list insertion order, not task index order', () => {
    const items = [
      makeItem({ id: 'second-spawn', index: 5 }),
      makeItem({ id: 'first-spawn', index: 0 })
    ]

    expect(buildSubagentTreeSorted(items).map(node => node.item.id)).toEqual([
      'second-spawn',
      'first-spawn'
    ])
  })

  it('sorts siblings by (depth, index) under each parent', () => {
    const items = [
      makeItem({ id: 'parent', index: 0 }),
      makeItem({ depth: 1, id: 'child-late', index: 2, parentId: 'parent' }),
      makeItem({ depth: 1, id: 'child-first', index: 0, parentId: 'parent' }),
      makeItem({ depth: 1, id: 'child-mid', index: 1, parentId: 'parent' })
    ]

    const tree = buildSubagentTreeSorted(items)
    expect(tree).toHaveLength(1)
    expect(tree[0]!.children.map(node => node.item.id)).toEqual([
      'child-first',
      'child-mid',
      'child-late'
    ])
  })

  it('promotes orphaned children to the root when parent is unknown', () => {
    const items = [
      makeItem({ id: 'root', index: 0 }),
      makeItem({ depth: 1, id: 'orphan', index: 1, parentId: 'missing' })
    ]

    const tree = buildSubagentTreeSorted(items)
    expect(tree.map(node => node.item.id)).toEqual(['root', 'orphan'])
    expect(tree.every(node => node.children.length === 0)).toBe(true)
  })

  it('builds multi-level trees with rolled-up aggregate invariants', () => {
    const items = [
      makeItem({ durationSeconds: 10, id: 'p', index: 0, status: 'completed', toolCount: 2 }),
      makeItem({
        depth: 1,
        durationSeconds: 4,
        id: 'c',
        index: 0,
        parentId: 'p',
        status: 'completed',
        toolCount: 3
      }),
      makeItem({
        depth: 2,
        durationSeconds: 1,
        id: 'gc',
        index: 0,
        parentId: 'c',
        status: 'completed',
        toolCount: 1
      })
    ]

    const tree = buildSubagentTreeSorted(items)
    expect(tree[0]!.children[0]!.children[0]!.item.id).toBe('gc')
    expect(tree[0]!.aggregate).toMatchObject({
      descendantCount: 2,
      maxDepthFromHere: 2,
      totalDuration: 15,
      totalTools: 6
    })
  })
})
