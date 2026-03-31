import type { HTMLAttributes } from 'vue'
import type { MenuItem } from '@/types'

export interface EMenuProps {
  class?: HTMLAttributes['class']
  items?: MenuItem[]
  modelValue?: string
  collapsed?: boolean
  /** When true, clicking a menu item navigates using vue-router (item.key is used as path) */
  router?: boolean
  /** When true, only one sub-menu can be expanded at a time */
  uniqueOpened?: boolean
  /** List of sub-menu keys that should be expanded on mount */
  defaultOpeneds?: string[]
}

export interface EMenuEmits {
  'update:modelValue': [value: string]
  select: [key: string]
}
