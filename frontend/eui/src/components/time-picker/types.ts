import type { HTMLAttributes } from 'vue'

export interface ETimePickerProps {
  class?: HTMLAttributes['class']
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  format?: string
  hourStep?: number
  minuteStep?: number
}

export interface ETimePickerEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}
