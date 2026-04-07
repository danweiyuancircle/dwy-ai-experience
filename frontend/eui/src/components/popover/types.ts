import type { PopoverContentProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

export interface EPopoverProps {
  class?: HTMLAttributes['class']
  side?: PopoverContentProps['side']
  sideOffset?: number
  align?: PopoverContentProps['align']
  open?: boolean
  /** When true (default), unmount the default slot content when popover closes */
  destroyOnClose?: boolean
}

export interface EPopoverEmits {
  'update:open': [value: boolean]
}
