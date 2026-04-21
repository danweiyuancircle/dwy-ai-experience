/**
 * ECarousel 走马灯组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * ECarousel 走马灯 Props
 */
export interface ECarouselProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 是否循环播放 */
  loop?: boolean
  /** 滑动方向 */
  direction?: 'horizontal' | 'vertical'
  /** 是否显示左右切换箭头 */
  showArrows?: boolean
  /** 是否显示底部指示点 */
  showDots?: boolean
  /** 是否自动轮播 */
  autoplay?: boolean
  /** 自动轮播间隔（毫秒） */
  interval?: number
}

/**
 * ECarousel 走马灯事件
 */
export interface ECarouselEmits {
  /** 当前页变化时触发，参数为新的索引（从 0 开始） */
  (e: 'change', index: number): void
}
