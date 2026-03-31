import type { HTMLAttributes } from 'vue'

export interface ECheckboxProps {
  class?: HTMLAttributes['class']
  modelValue?: boolean
  label?: string
  disabled?: boolean
  indeterminate?: boolean
}

export interface ECheckboxEmits {
  'update:modelValue': [value: boolean]
  change: [value: boolean]
}
