import type { HTMLAttributes } from 'vue'
import type { Size, Option, GroupedOption } from '@/types'

export interface ESelectProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number
  options?: Option[] | GroupedOption[]
  placeholder?: string
  disabled?: boolean
  size?: Size
  clearable?: boolean
  valueKey?: string
  labelKey?: string
}

export interface ESelectEmits {
  'update:modelValue': [value: string | number | undefined]
  change: [value: string | number | undefined]
  'visible-change': [visible: boolean]
}
