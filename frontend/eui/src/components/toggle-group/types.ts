import type { HTMLAttributes } from 'vue'
import type { ToggleVariants } from '../toggle/types'

export interface EToggleGroupProps {
  class?: HTMLAttributes['class']
  modelValue?: string | string[]
  type?: 'single' | 'multiple'
  variant?: ToggleVariants['variant']
  size?: ToggleVariants['size']
  disabled?: boolean
}

export interface EToggleGroupEmits {
  'update:modelValue': [value: string | string[]]
}
