import type { HTMLAttributes } from 'vue'
import type { Option } from '@/types'

export interface ECheckboxProps {
  class?: HTMLAttributes['class']
  /** Single mode: boolean; Group mode (when options provided): array of selected values */
  modelValue?: boolean | (string | number)[]
  label?: string
  disabled?: boolean
  indeterminate?: boolean
  /** When provided, renders a group of checkboxes (one per option) */
  options?: Option[]
  /** Layout direction for group mode */
  direction?: 'horizontal' | 'vertical'
  /** When true, adds a rounded border around each checkbox item */
  border?: boolean
}

export interface ECheckboxEmits {
  'update:modelValue': [value: boolean | (string | number)[]]
  change: [value: boolean | (string | number)[]]
}
