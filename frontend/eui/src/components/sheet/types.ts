/**
 * ESheet 抽屉侧拉面板组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** ESheet Props */
export interface ESheetProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 是否打开，v-model:open 绑定 */
  open?: boolean
  /** 标题文本（未使用 header 插槽时生效） */
  title?: string
  /** 描述文本 */
  description?: string
  /** 弹出方向，默认 right */
  side?: 'top' | 'right' | 'bottom' | 'left'
  /** 是否显示右上角关闭按钮，默认 true */
  showClose?: boolean
}

/** ESheet Emits */
export interface ESheetEmits {
  /** 打开状态更新，用于 v-model:open */
  (e: 'update:open', value: boolean): void
  /** 关闭事件（只在关闭时触发一次） */
  (e: 'close'): void
}
