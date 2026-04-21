/**
 * ESeparator 分隔线组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** ESeparator Props */
export interface ESeparatorProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 分隔线方向，默认水平 */
  orientation?: 'horizontal' | 'vertical'
  /** 是否为纯装饰性分隔（true 时不参与语义与无障碍朗读） */
  decorative?: boolean
}
