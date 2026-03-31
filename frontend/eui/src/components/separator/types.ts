import type { HTMLAttributes } from 'vue'

export interface ESeparatorProps {
  class?: HTMLAttributes['class']
  orientation?: 'horizontal' | 'vertical'
  decorative?: boolean
}
