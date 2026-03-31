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
}

export interface ETableEmits {
  'row-click': [row: Record<string, any>, index: number]
  'update:selectedKeys': [keys: (string | number)[]]
  sort: [key: string, direction: 'asc' | 'desc' | null]
}
