/**
 * ETimetableGrid 周视图排课网格类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 单个课程/事件项 */
export interface TimetableItem {
  /** 星期序号，0 对应 days[0] */
  day: number
  /** 起始小时（24 小时制） */
  startHour: number
  /** 结束小时（不包含） */
  endHour: number
  /** 标题 */
  title: string
  /** 自定义背景色（CSS 颜色值）；未传时使用预设配色 */
  color?: string
}

/** ETimetableGrid Props */
export interface ETimetableGridProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 课程项数据 */
  data?: TimetableItem[]
  /** 时间轴起始小时，默认 8 */
  startHour?: number
  /** 时间轴结束小时，默认 22 */
  endHour?: number
  /** 星期标题列表，默认「周一」到「周日」 */
  days?: string[]
}
