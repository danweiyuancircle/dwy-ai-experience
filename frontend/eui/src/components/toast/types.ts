import type { HTMLAttributes } from 'vue'

export type ToastPosition =
  | 'top-left'
  | 'top-right'
  | 'top-center'
  | 'bottom-left'
  | 'bottom-right'
  | 'bottom-center'

export interface EToastProps {
  class?: HTMLAttributes['class']
  position?: ToastPosition
  expand?: boolean
  richColors?: boolean
}
