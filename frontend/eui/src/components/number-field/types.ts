import type { HTMLAttributes } from 'vue'

export interface ENumberFieldProps {
  class?: HTMLAttributes['class']
  modelValue?: number
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export interface ENumberFieldEmits {
  (e: 'update:modelValue', value: number): void
  (e: 'change', value: number): void
}
