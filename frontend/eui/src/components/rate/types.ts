/**
 * ERate 评分组件类型定义
 */

/** ERate Props */
export interface ERateProps {
  /** 自定义类名 */
  class?: string
  /** 当前分值，v-model 绑定 */
  modelValue?: number
  /** 最大分值（等于星星数量），默认 5 */
  max?: number
  /** 是否禁用评分交互 */
  disabled?: boolean
  /** 是否允许选择半星 */
  allowHalf?: boolean
  /** 是否显示右侧文本（当前分值 / 总分） */
  showText?: boolean
}

/** ERate Emits */
export interface ERateEmits {
  /** 分值更新，用于 v-model */
  (e: 'update:modelValue', value: number): void
  /** 分值变化事件 */
  (e: 'change', value: number): void
}
