import type { HTMLAttributes } from 'vue'

export type TabPosition = 'top' | 'bottom' | 'left' | 'right'

export interface TabItem {
  key: string
  label: string
  disabled?: boolean
}

export interface ETabsProps {
  class?: HTMLAttributes['class']
  modelValue?: string
  items?: TabItem[]
  /** When true, show a close button on each non-disabled tab */
  closable?: boolean
  /** When true, show a "+" button after the last tab to add new tabs */
  addable?: boolean
  /** Position of the tab bar relative to the content area */
  tabPosition?: TabPosition
}

export interface ETabsEmits {
  (e: 'update:modelValue', key: string): void
  (e: 'change', key: string): void
  /** Emitted when the close button on a tab is clicked */
  (e: 'close', key: string): void
  /** Emitted when the add button is clicked */
  (e: 'add'): void
}
