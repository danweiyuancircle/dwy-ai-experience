import type { HTMLAttributes } from 'vue'

export interface EAlertDialogProps {
  class?: HTMLAttributes['class']
  open?: boolean
  title?: string
  description?: string
  confirmText?: string
  cancelText?: string
}

export interface EAlertDialogEmits {
  'update:open': [value: boolean]
  confirm: []
  cancel: []
}
