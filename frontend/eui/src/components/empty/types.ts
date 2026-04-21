/**
 * EEmpty 空状态组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EEmpty 空状态 Props
 */
export interface EEmptyProps {
  /** 自定义 class，透传到根容器 */
  class?: HTMLAttributes['class']
  /** 标题文本 */
  title?: string
  /** 描述文本 */
  description?: string
  /** 图标（字符串，需配合 icon 插槽时可为空） */
  icon?: string
}
