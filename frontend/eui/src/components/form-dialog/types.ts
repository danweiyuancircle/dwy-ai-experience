import type { HTMLAttributes } from 'vue'

export interface EFormDialogProps {
  class?: HTMLAttributes['class']
  open?: boolean
  title?: string
  size?: string
  loading?: boolean
  confirmText?: string
  cancelText?: string
  showClose?: boolean
}

export interface EFormDialogEmits {
  'update:open': [value: boolean]
  confirm: []
  cancel: []
}
