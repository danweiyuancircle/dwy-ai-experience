import type { HTMLAttributes } from 'vue'

export interface TreeNode {
  key: string | number
  label: string
  children?: TreeNode[]
  disabled?: boolean
  isLeaf?: boolean
}

export interface ETreeProps {
  class?: HTMLAttributes['class']
  data?: TreeNode[]
  modelValue?: (string | number)[]
  checkable?: boolean
  expandedKeys?: (string | number)[]
  defaultExpandAll?: boolean
  /** When true, nodes with undefined children show expand arrow and call loadFn on expand */
  lazy?: boolean
  /** Async function to load children for a node (used with lazy) */
  loadFn?: (node: TreeNode) => Promise<TreeNode[]>
  /** When true, nodes can be dragged and dropped to reorder or reparent */
  draggable?: boolean
  /** Custom filter function; return true to show the node */
  filterMethod?: (query: string, node: TreeNode) => boolean
  /** When set, hides nodes that don't match the filter */
  filterQuery?: string
  /** When true, checking a parent does NOT cascade to children and vice versa */
  checkStrictly?: boolean
}

export interface ETreeEmits {
  (e: 'update:modelValue', keys: (string | number)[]): void
  (e: 'update:expandedKeys', keys: (string | number)[]): void
  (e: 'check', key: string | number, checked: boolean): void
  (e: 'select', key: string | number): void
  (e: 'node-drop', dragNode: TreeNode, dropNode: TreeNode, position: 'before' | 'inner' | 'after'): void
}
