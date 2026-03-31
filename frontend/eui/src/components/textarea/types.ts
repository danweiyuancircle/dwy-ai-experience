import type { HTMLAttributes } from 'vue'

export interface ETextareaProps {
  class?: HTMLAttributes['class']
  modelValue?: string
  placeholder?: string
  rows?: number
  disabled?: boolean
  readonly?: boolean
  maxlength?: number
  autoResize?: boolean
}

export interface ETextareaEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
  (e: 'blur', event: FocusEvent): void
  (e: 'focus', event: FocusEvent): void
}
