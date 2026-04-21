/**
 * EToast 全局消息通知组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** Toast 弹出位置（六象限） */
export type ToastPosition =
  | 'top-left'
  | 'top-right'
  | 'top-center'
  | 'bottom-left'
  | 'bottom-right'
  | 'bottom-center'

/** EToast Props */
export interface EToastProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 弹出位置 */
  position?: ToastPosition
  /** 是否展开显示多条（false 时会堆叠） */
  expand?: boolean
  /** 是否按类型使用丰富配色 */
  richColors?: boolean
}
