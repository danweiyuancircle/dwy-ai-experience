import type { HTMLAttributes } from 'vue'

export interface TreeNode {
  key: string | number
  label: string
  children?: TreeNode[]
  disabled?: boolean
}

export interface ETreeProps {
  class?: HTMLAttributes['class']
  data?: TreeNode[]
  modelValue?: (string | number)[]
  checkable?: boolean
  expandedKeys?: (string | number)[]
  defaultExpandAll?: boolean
}

export interface ETreeEmits {
  (e: 'update:modelValue', keys: (string | number)[]): void
  (e: 'update:expandedKeys', keys: (string | number)[]): void
  (e: 'check', key: string | number, checked: boolean): void
  (e: 'select', key: string | number): void
}
