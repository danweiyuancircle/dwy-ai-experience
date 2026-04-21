/**
 * EHoverCard 悬浮卡片组件的类型定义
 */

/**
 * EHoverCard 悬浮卡片 Props
 */
export interface EHoverCardProps {
  /** 自定义 class，透传到内容区 */
  class?: string
  /** 悬浮多长时间后打开（毫秒） */
  openDelay?: number
  /** 鼠标离开后延迟关闭的时间（毫秒） */
  closeDelay?: number
}

/**
 * EHoverCard 悬浮卡片事件
 */
export interface EHoverCardEmits {
  /** 展开状态变化 */
  (e: 'update:open', open: boolean): void
}
