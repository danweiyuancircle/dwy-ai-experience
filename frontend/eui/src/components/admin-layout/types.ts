import type { HTMLAttributes } from 'vue'
import type { MenuItem } from '@/types'

export interface EAdminLayoutProps {
  class?: HTMLAttributes['class']
  logo?: string
  title?: string
  menuItems?: MenuItem[]
  activeKey?: string
  collapsed?: boolean
  showFooter?: boolean
  headerHeight?: string | number
  sidebarWidth?: string | number
  collapsedWidth?: string | number
}

export interface EAdminLayoutEmits {
  'update:activeKey': [key: string]
  'update:collapsed': [value: boolean]
  'menu-select': [key: string]
}
