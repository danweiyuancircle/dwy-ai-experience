export interface ERateProps {
  class?: string
  modelValue?: number
  max?: number
  disabled?: boolean
  allowHalf?: boolean
  showText?: boolean
}

export interface ERateEmits {
  (e: 'update:modelValue', value: number): void
  (e: 'change', value: number): void
}
