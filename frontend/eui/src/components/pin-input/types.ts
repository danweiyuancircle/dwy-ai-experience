import type { HTMLAttributes } from 'vue'

export interface EPinInputProps {
  class?: HTMLAttributes['class']
  modelValue?: string[]
  length?: number
  disabled?: boolean
  mask?: boolean
  otp?: boolean
  type?: 'text' | 'number'
}

export interface EPinInputEmits {
  'update:modelValue': [value: string[]]
  complete: [value: string[]]
}
