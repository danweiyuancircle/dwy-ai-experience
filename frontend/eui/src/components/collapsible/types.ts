import type { HTMLAttributes } from 'vue'

export interface ECollapsibleProps {
  class?: HTMLAttributes['class']
  modelValue?: boolean
  disabled?: boolean
}

export interface ECollapsibleEmits {
  (e: 'update:modelValue', value: boolean): void
}
