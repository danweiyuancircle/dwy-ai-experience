import type { HTMLAttributes } from 'vue'

export interface StepperItem {
  title: string
  description?: string
}

export interface EStepperProps {
  class?: HTMLAttributes['class']
  modelValue?: number
  items?: StepperItem[]
  direction?: 'horizontal' | 'vertical'
}

export interface EStepperEmits {
  (e: 'update:modelValue', value: number): void
}
