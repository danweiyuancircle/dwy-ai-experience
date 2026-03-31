import type { HTMLAttributes } from 'vue'

export interface EInputOTPProps {
  class?: HTMLAttributes['class']
  modelValue?: string
  length?: number
  disabled?: boolean
  placeholder?: string
}

export interface EInputOTPEmits {
  'update:modelValue': [value: string]
  complete: [value: string]
}
