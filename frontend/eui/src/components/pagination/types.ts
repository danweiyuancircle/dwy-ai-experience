import type { HTMLAttributes } from 'vue'

export interface EPaginationProps {
  class?: HTMLAttributes['class']
  modelValue?: number
  total?: number
  pageSize?: number
  siblingCount?: number
  showSizeChanger?: boolean
  pageSizes?: number[]
  showTotal?: boolean
  jumper?: boolean
  layout?: string
  disabled?: boolean
}

export interface EPaginationEmits {
  (e: 'update:modelValue', page: number): void
  (e: 'change', page: number): void
  (e: 'update:pageSize', size: number): void
  (e: 'size-change', size: number): void
}
