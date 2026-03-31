import type { HTMLAttributes } from 'vue'
import type { Option } from '@/types'

export interface ERadioProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number
  options?: Option[]
  disabled?: boolean
  direction?: 'horizontal' | 'vertical'
}

export interface ERadioEmits {
  'update:modelValue': [value: string | number]
  change: [value: string | number]
}
