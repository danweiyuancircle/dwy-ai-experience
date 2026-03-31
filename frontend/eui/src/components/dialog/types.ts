import type { HTMLAttributes } from 'vue'

export interface EDialogProps {
  class?: HTMLAttributes['class']
  open?: boolean
  title?: string
  description?: string
  showClose?: boolean
  maxWidth?: string
  draggable?: boolean
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  fullscreen?: boolean
  /** When true, unmount the default slot content when dialog closes (recreated on each open) */
  destroyOnClose?: boolean
}

export interface EDialogEmits {
  'update:open': [value: boolean]
  open: []
  close: []
}
