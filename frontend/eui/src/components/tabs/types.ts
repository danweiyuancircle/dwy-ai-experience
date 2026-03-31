import type { HTMLAttributes } from 'vue'

export interface TabItem {
  key: string
  label: string
  disabled?: boolean
}

export interface ETabsProps {
  class?: HTMLAttributes['class']
  modelValue?: string
  items?: TabItem[]
}

export interface ETabsEmits {
  (e: 'update:modelValue', key: string): void
  (e: 'change', key: string): void
}
