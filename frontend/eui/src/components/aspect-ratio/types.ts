/**
 * EAspectRatio 固定宽高比容器组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EAspectRatio 固定宽高比容器 Props
 */
export interface EAspectRatioProps {
  /** 自定义 class，透传到容器 */
  class?: HTMLAttributes['class']
  /** 宽高比数值，如 16/9、4/3、1 */
  ratio?: number
}
