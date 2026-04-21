/**
 * ECalendar 日历组件的类型定义
 * 日期值类型由 reka-ui / @internationalized/date 决定，此处用 any 避免循环依赖
 */

/**
 * ECalendar 日历 Props
 */
export interface ECalendarProps {
  /** 自定义 class，透传到根元素 */
  class?: string
  /** 当前选中日期，类型由 reka-ui 决定（DateValue） */
  // DateValue 类型复杂且可能为单值/数组，此处放宽为 any
  modelValue?: any
  /** 默认日期 */
  defaultValue?: any
  /** 是否允许多选 */
  multiple?: boolean
  /** 是否禁用 */
  disabled?: boolean
  /** 是否只读 */
  readonly?: boolean
  /** 语言区域，如 zh-CN / en-US */
  locale?: string
  /** 最小可选日期 */
  minValue?: any
  /** 最大可选日期 */
  maxValue?: any
}

/**
 * ECalendar 日历事件
 */
export interface ECalendarEmits {
  /** 选中日期变化 */
  (e: 'update:modelValue', value: any): void
}
