/**
 * EAvatar 头像组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EAvatar 头像 Props
 */
export interface EAvatarProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 头像图片 URL */
  src?: string
  /** 图片 alt 文本，用于无障碍 */
  alt?: string
  /** 加载失败时显示的占位文字，通常为用户姓名首字 */
  fallback?: string
  /** 尺寸：sm=小，default=中，lg=大 */
  size?: 'sm' | 'default' | 'lg'
}
