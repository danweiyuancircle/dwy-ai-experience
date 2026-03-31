import type { HTMLAttributes } from 'vue'

export type ConfirmDialogType = 'info' | 'warning' | 'error'

export interface EConfirmDialogProps {
  class?: HTMLAttributes['class']
  open?: boolean
  title?: string
  message?: string
  type?: ConfirmDialogType
  confirmText?: string
  cancelText?: string
}

export interface EConfirmDialogEmits {
  'update:open': [value: boolean]
  confirm: []
  cancel: []
}
