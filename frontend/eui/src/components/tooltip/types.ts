/**
 * ETooltip 文字提示组件类型定义
 */
import type { TooltipContentProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

/** ETooltip Props */
export interface ETooltipProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 纯文本提示内容；复杂内容使用 content 插槽 */
  content?: string
  /** 弹出方向 */
  side?: TooltipContentProps['side']
  /** 与触发器的偏移（px），默认 4 */
  sideOffset?: number
  /** 悬停延迟（ms），默认 0 */
  delayDuration?: number
  /** 是否禁用提示 */
  disabled?: boolean
}
