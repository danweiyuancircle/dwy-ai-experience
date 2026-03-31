import type { HTMLAttributes } from 'vue'

export interface EDialogProps {
  class?: HTMLAttributes['class']
  open?: boolean
  title?: string
  description?: string
  showClose?: boolean
  maxWidth?: string
}

export interface EDialogEmits {
  'update:open': [value: boolean]
  open: []
  close: []
}
