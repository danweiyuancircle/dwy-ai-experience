/**
 * EDatePicker 日期选择器组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 日期选择器类型：单日/区间/月/年 */
export type DatePickerType = 'date' | 'daterange' | 'month' | 'year'

/**
 * 日期快捷项（"今天"、"最近 7 天"等）
 */
export interface DatePickerShortcut {
  /** 按钮显示文本 */
  text: string
  /** 选中值，可以是具体日期、区间数组，或动态函数 */
  value: Date | Date[] | (() => Date | Date[])
}

/**
 * EDatePicker 日期选择器 Props
 */
export interface EDatePickerProps {
  /** 自定义 class，透传到触发按钮 */
  class?: HTMLAttributes['class']
  /** 当前值：单日为字符串/Date，区间为二元组 */
  modelValue?: string | Date | [string, string] | [Date, Date]
  /** 选择模式 */
  type?: DatePickerType
  /** 单日模式占位文本 */
  placeholder?: string
  /** 区间模式起始占位文本 */
  startPlaceholder?: string
  /** 区间模式结束占位文本 */
  endPlaceholder?: string
  /** 区间模式的分隔符 */
  rangeSeparator?: string
  /** 日期格式化 token 串，如 YYYY-MM-DD */
  format?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否显示清空按钮 */
  clearable?: boolean
  /** 自定义禁用日期判断，返回 true 时该日期不可选 */
  disabledDate?: (date: Date) => boolean
  /** 左侧快捷选项列表 */
  shortcuts?: DatePickerShortcut[]
}

/**
 * EDatePicker 日期选择器事件
 */
export interface EDatePickerEmits {
  /** 值变化，支持 v-model */
  (e: 'update:modelValue', value: string | [string, string] | undefined): void
  /** 业务 change 事件 */
  (e: 'change', value: string | [string, string] | undefined): void
}
