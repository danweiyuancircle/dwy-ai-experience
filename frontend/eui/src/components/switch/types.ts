import type { HTMLAttributes } from 'vue'
import type { Size } from '@/types'

export interface ESwitchProps {
  class?: HTMLAttributes['class']
  modelValue?: boolean
  label?: string
  disabled?: boolean
  size?: Size
}

export interface ESwitchEmits {
  'update:modelValue': [value: boolean]
  change: [value: boolean]
}
