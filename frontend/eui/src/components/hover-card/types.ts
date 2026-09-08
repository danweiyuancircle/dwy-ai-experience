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
  /**
   * 触控设备点击触发器是否切换打开。
   * reka-ui 2.10 HoverCardRoot.enableTouch，默认 false（保持 hover 语义）。
   */
  enableTouch?: boolean
}

// 当前仅非受控 Hover；若需 v-model:open 再补 open prop + emit，避免空契约误导消费者
