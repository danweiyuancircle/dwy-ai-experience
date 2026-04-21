/**
 * EMention @提及输入组件的类型定义
 */

/**
 * 可提及的候选项
 */
export interface MentionOption {
  /** 展示文本，会作为插入文字 */
  label: string
  /** 唯一值 */
  value: string
}

/**
 * EMention @提及输入 Props
 */
export interface EMentionProps {
  /** 自定义 class */
  class?: string
  /** 当前文本值 */
  modelValue?: string
  /** 候选项数组 */
  options?: MentionOption[]
  /** 触发字符，默认 @ */
  prefix?: string
  /** 候选项是否正在加载 */
  loading?: boolean
  /** textarea 占位文本 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
}

/**
 * EMention @提及输入事件
 */
export interface EMentionEmits {
  /** 文本变化 */
  (e: 'update:modelValue', value: string): void
  /** 用户从候选列表中选择一项 */
  (e: 'select', option: MentionOption): void
}
