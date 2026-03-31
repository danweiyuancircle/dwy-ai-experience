import type { HTMLAttributes } from 'vue'

export interface EDatePickerProps {
  class?: HTMLAttributes['class']
  modelValue?: string | Date
  placeholder?: string
  format?: string
  disabled?: boolean
  clearable?: boolean
}

export interface EDatePickerEmits {
  (e: 'update:modelValue', value: string | undefined): void
  (e: 'change', value: string | undefined): void
}
