import type { HTMLAttributes } from 'vue'
import type { Size } from '@/types'

export interface ETagsInputProps {
  class?: HTMLAttributes['class']
  modelValue?: string[]
  placeholder?: string
  max?: number
  disabled?: boolean
  size?: Size
}

export interface ETagsInputEmits {
  'update:modelValue': [value: string[]]
  change: [value: string[]]
}
