import type { HTMLAttributes } from 'vue'

/** Standard size variants */
export type Size = 'sm' | 'default' | 'lg'

/** Standard option for list-based components */
export interface Option {
  label: string
  value: string | number
  disabled?: boolean
}

/** Option with grouping */
export interface GroupedOption {
  label: string
  options: Option[]
}

/** Base props shared by all components */
export interface BaseProps {
  class?: HTMLAttributes['class']
}

/** Config provider injection values */
export interface ConfigProviderContext {
  size: Size
  zIndex: number
  locale: Record<string, string>
}

/** Menu item definition */
export interface MenuItem {
  key: string
  label: string
  icon?: string
  /** Route path for router mode (falls back to key if not provided) */
  path?: string
  children?: MenuItem[]
  disabled?: boolean
}

/** Table column definition */
export interface TableColumn<T = any> {
  key: string
  title: string
  width?: number | string
  minWidth?: number
  sortable?: boolean
  fixed?: 'left' | 'right'
  align?: 'left' | 'center' | 'right'
  render?: (row: T, index: number) => any
}

/** Pagination info */
export interface PaginationInfo {
  page: number
  pageSize: number
  total: number
}

/** Form rule (Element Plus compatible) */
export interface FormRule {
  required?: boolean
  message?: string
  trigger?: 'blur' | 'change'
  min?: number
  max?: number
  type?: string
  pattern?: RegExp
  validator?: (rule: FormRule, value: any, callback: (error?: Error) => void) => void
}
