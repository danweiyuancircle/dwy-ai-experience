import type { HTMLAttributes } from 'vue'
import type { Option } from '@/types'

export interface EComboboxProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number
  options?: Option[]
  placeholder?: string
  disabled?: boolean
  emptyText?: string
}

export interface EComboboxEmits {
  (e: 'update:modelValue', value: string | number | undefined): void
  (e: 'change', value: string | number | undefined): void
}
