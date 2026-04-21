/**
 * ETimeline 时间线组件类型定义
 */

/** 单个时间线项 */
export interface TimelineItem {
  /** 标题 */
  title: string
  /** 详细内容（可选） */
  content?: string
  /** 时间戳文本（格式由调用方决定） */
  timestamp?: string
  /** 事件类型，决定圆点颜色 */
  type?: 'primary' | 'success' | 'warning' | 'danger'
}

/** ETimeline Props */
export interface ETimelineProps {
  /** 自定义类名 */
  class?: string
  /** 时间线项列表 */
  items?: TimelineItem[]
  /** 是否倒序展示（最新在顶部） */
  reverse?: boolean
}
