import type { HTMLAttributes } from 'vue'
import type { TableColumn } from '@/types'

export interface FetchParams {
  page: number
  pageSize: number
  keyword?: string
}

export interface FetchResult {
  items: any[]
  total: number
}

export interface EDataPageProps {
  class?: HTMLAttributes['class']
  columns: TableColumn[]
  fetchFn: (params: FetchParams) => Promise<FetchResult>
  searchable?: boolean
  pageSize?: number
}
