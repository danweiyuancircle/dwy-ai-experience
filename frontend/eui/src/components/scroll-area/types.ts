/**
 * EScrollArea 自定义滚动区域组件类型定义
 */

/** EScrollArea Props */
export interface EScrollAreaProps {
  /** 自定义类名 */
  class?: string
  /** 滚动条显示时机：auto=内容溢出显示，always=常驻，scroll=滚动时显示，hover=悬浮时显示（默认） */
  type?: 'auto' | 'always' | 'scroll' | 'hover'
}
