import type { HTMLAttributes } from 'vue'

export interface SelectOption {
  label: string
  value: string | number
}

export interface ENativeSelectProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number | string[] | number[]
  options?: SelectOption[]
  placeholder?: string
  disabled?: boolean
}

export interface ENativeSelectEmits {
  'update:modelValue': [value: string | number]
  change: [event: Event]
}
