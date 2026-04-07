import type { HTMLAttributes } from 'vue'

export type DrawerDirection = 'top' | 'right' | 'bottom' | 'left'

export interface EDrawerProps {
  class?: HTMLAttributes['class']
  open?: boolean
  title?: string
  description?: string
  direction?: DrawerDirection
  showClose?: boolean
  /** When true (default), unmount the default slot content when drawer closes */
  destroyOnClose?: boolean
}

export interface EDrawerEmits {
  'update:open': [value: boolean]
  close: []
}
