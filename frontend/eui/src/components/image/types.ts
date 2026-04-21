/**
 * EImage 图片组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EImage 图片 Props
 */
export interface EImageProps {
  /** 自定义 class，透传到容器 */
  class?: HTMLAttributes['class']
  /** 图片地址 */
  src?: string
  /** alt 文本，用于无障碍与加载失败时显示 */
  alt?: string
  /** 图片填充方式（映射到 CSS object-fit） */
  fit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down'
  /** 是否启用懒加载（进入视口后才加载） */
  lazy?: boolean
  /** 加载失败时展示的兜底图 URL */
  fallback?: string
  /** 是否开启点击大图预览 */
  preview?: boolean
}
