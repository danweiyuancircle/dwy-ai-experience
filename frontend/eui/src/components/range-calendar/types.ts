/**
 * ERangeCalendar 日期范围日历组件类型定义
 * 注：使用 any 是因日期对象沿用 @internationalized/date 的 DateValue 类型，
 * reka-ui 对外暴露为泛型，此处不强制绑定具体实现以保持灵活性
 */

/** ERangeCalendar Props */
export interface ERangeCalendarProps {
  /** 自定义类名 */
  class?: string
  /** 当前选中的日期范围，v-model 绑定 */
  modelValue?: { start: any; end: any }
  /** 非受控模式下的默认范围 */
  defaultValue?: { start: any; end: any }
  /** 是否禁用 */
  disabled?: boolean
  /** 是否只读 */
  readonly?: boolean
  /** 语言区域标识，如 'zh-CN' */
  locale?: string
  /** 允许选择的最小日期 */
  minValue?: any
  /** 允许选择的最大日期 */
  maxValue?: any
}

/** ERangeCalendar Emits */
export interface ERangeCalendarEmits {
  /** 选中范围更新，用于 v-model；清除时为 null */
  (e: 'update:modelValue', value: { start: any; end: any } | null): void
}
