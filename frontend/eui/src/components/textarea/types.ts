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
  /** Show "current/max" word limit counter when maxlength is set */
  showWordLimit?: boolean
  /** Minimum number of rows when autoResize is enabled */
  minRows?: number
  /** Maximum number of rows when autoResize is enabled (overflow-y: auto beyond this) */
  maxRows?: number
}

export interface ETextareaEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
  (e: 'blur', event: FocusEvent): void
  (e: 'focus', event: FocusEvent): void
}
