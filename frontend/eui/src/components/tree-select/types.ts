import type { HTMLAttributes } from 'vue'
import type { TreeNode } from '../tree/types'

export interface ETreeSelectProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number | (string | number)[]
  data?: TreeNode[]
  placeholder?: string
  multiple?: boolean
  checkable?: boolean
  disabled?: boolean
}

export interface ETreeSelectEmits {
  (e: 'update:modelValue', value: string | number | (string | number)[] | undefined): void
  (e: 'change', value: string | number | (string | number)[] | undefined): void
}
