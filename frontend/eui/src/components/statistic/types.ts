/**
 * EStatistic 数值统计组件类型定义
 */

/** EStatistic Props */
export interface EStatisticProps {
  /** 自定义类名 */
  class?: string
  /** 标题文本 */
  title?: string
  /** 数值（数字会千分位格式化，字符串原样输出） */
  value?: number | string
  /** 前缀文本（如货币符号） */
  prefix?: string
  /** 后缀文本（如单位） */
  suffix?: string
  /** 小数精度 */
  precision?: number
}
