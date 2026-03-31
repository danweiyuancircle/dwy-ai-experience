import type { TooltipContentProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

export interface ETooltipProps {
  class?: HTMLAttributes['class']
  content?: string
  side?: TooltipContentProps['side']
  sideOffset?: number
  delayDuration?: number
  disabled?: boolean
}
