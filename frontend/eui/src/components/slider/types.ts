import type { HTMLAttributes } from 'vue'

export interface ESliderProps {
  class?: HTMLAttributes['class']
  modelValue?: number[]
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  orientation?: 'horizontal' | 'vertical'
}

export interface ESliderEmits {
  'update:modelValue': [value: number[]]
}
