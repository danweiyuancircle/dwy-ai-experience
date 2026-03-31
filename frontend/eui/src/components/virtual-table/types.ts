export interface VirtualTableColumn {
  key: string
  title: string
  width?: number | string
  align?: 'left' | 'center' | 'right'
}

export interface EVirtualTableProps {
  class?: string
  columns?: VirtualTableColumn[]
  data?: Record<string, any>[]
  height?: number
  estimateRowHeight?: number
  rowKey?: string
  loading?: boolean
  emptyText?: string
}

export interface EVirtualTableEmits {
  (e: 'row-click', row: Record<string, any>, index: number): void
}
