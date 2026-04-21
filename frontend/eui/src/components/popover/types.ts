/**
 * EPopover 气泡弹出层组件类型定义
 */
import type { PopoverContentProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

/** EPopover Props */
export interface EPopoverProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 弹出方向：top/right/bottom/left */
  side?: PopoverContentProps['side']
  /** 与触发器的偏移距离（px），默认 4 */
  sideOffset?: number
  /** 对齐方式：start/center/end */
  align?: PopoverContentProps['align']
  /** 受控打开状态，使用 v-model:open 绑定 */
  open?: boolean
  /** 关闭时是否销毁默认插槽内容，避免内部状态残留；默认 true */
  destroyOnClose?: boolean
}

/** EPopover Emits */
export interface EPopoverEmits {
  /** 打开状态变化，用于 v-model:open */
  'update:open': [value: boolean]
}
