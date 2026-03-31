import type { HTMLAttributes } from 'vue'

export interface ESheetProps {
  class?: HTMLAttributes['class']
  open?: boolean
  title?: string
  description?: string
  side?: 'top' | 'right' | 'bottom' | 'left'
  showClose?: boolean
}

export interface ESheetEmits {
  (e: 'update:open', value: boolean): void
  (e: 'close'): void
}
