import type { HTMLAttributes } from 'vue'
import type { Size, FormRule } from '@/types'
import type { ZodType } from 'zod'

export interface EFormProps {
  class?: HTMLAttributes['class']
  model?: Record<string, any>
  rules?: ZodType | Record<string, FormRule | FormRule[]>
  labelWidth?: string
  labelPosition?: 'left' | 'right' | 'top'
  size?: Size
  disabled?: boolean
}

export interface EFormEmits {
  submit: [values: Record<string, any>]
}

export interface EFormExpose {
  validate: () => Promise<boolean>
  resetFields: () => void
  clearValidate: () => void
}

export interface EFormItemProps {
  class?: HTMLAttributes['class']
  label?: string
  prop?: string
  required?: boolean
  labelWidth?: string
}
