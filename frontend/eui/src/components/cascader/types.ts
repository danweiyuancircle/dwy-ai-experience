import type { HTMLAttributes } from 'vue'

export interface CascaderOption {
  label: string
  value: string | number
  children?: CascaderOption[]
  disabled?: boolean
}

export interface ECascaderProps {
  class?: HTMLAttributes['class']
  modelValue?: (string | number)[]
  options?: CascaderOption[]
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  filterable?: boolean
}

export interface ECascaderEmits {
  (e: 'update:modelValue', value: (string | number)[]): void
  (e: 'change', value: (string | number)[]): void
}
