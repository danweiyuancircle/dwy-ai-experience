import type { HTMLAttributes } from 'vue'
import type { Option, Size } from '@/types'

export interface ERadioProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number
  options?: Option[]
  disabled?: boolean
  direction?: 'horizontal' | 'vertical'
  /** Render style: 'default' for radio dots, 'button' for segmented button group */
  optionType?: 'default' | 'button'
  /** When true, adds a rounded border around each radio item (default mode only) */
  border?: boolean
  /** Size variant applied to radio/button items */
  size?: Size
}

export interface ERadioEmits {
  'update:modelValue': [value: string | number]
  change: [value: string | number]
}
