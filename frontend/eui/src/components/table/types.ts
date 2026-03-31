import type { HTMLAttributes } from 'vue'
import type { TableColumn } from '@/types'

export interface ETableProps {
  class?: HTMLAttributes['class']
  data?: Record<string, any>[]
  columns?: TableColumn[]
  loading?: boolean
  rowKey?: string
  striped?: boolean
  bordered?: boolean
  emptyText?: string
  selectable?: boolean
  selectedKeys?: (string | number)[]
  /** Enable expandable rows with expand/collapse icon */
  expandable?: boolean
  /** Array of row keys that are currently expanded */
  expandedRowKeys?: (string | number)[]
  /** Static class or function returning class for each row */
  rowClassName?: string | ((row: Record<string, any>, index: number) => string)
  /** Show summary footer row */
  showSummary?: boolean
  /** Custom summary calculation; returns array of values aligned to columns */
  summaryMethod?: (data: Record<string, any>[], columns: TableColumn[]) => (string | number)[]
}

export interface ETableEmits {
  'row-click': [row: Record<string, any>, index: number]
  'update:selectedKeys': [keys: (string | number)[]]
  'update:expandedRowKeys': [keys: (string | number)[]]
  sort: [key: string, direction: 'asc' | 'desc' | null]
}
