import type { HTMLAttributes } from 'vue'
import type { Size } from '@/types'

export interface EInputProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number
  type?: string
  placeholder?: string
  size?: Size
  disabled?: boolean
  readonly?: boolean
  clearable?: boolean
  maxlength?: number
  showPassword?: boolean
  showWordLimit?: boolean
}

export interface EInputEmits {
  'update:modelValue': [value: string]
  change: [value: string]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  clear: []
}
