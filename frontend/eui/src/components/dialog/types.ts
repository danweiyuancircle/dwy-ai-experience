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
}

export interface EDialogEmits {
  'update:open': [value: boolean]
  open: []
  close: []
}
