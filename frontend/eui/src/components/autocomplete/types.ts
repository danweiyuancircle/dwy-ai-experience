/**
 * EAutocomplete 自动补全输入组件的类型定义
 */

/**
 * 自动补全下拉项
 */
export interface AutocompleteOption {
  /** 展示文本 */
  label: string
  /** 唯一值，用于 key 和选中标识 */
  value: string | number
}

/**
 * EAutocomplete 自动补全 Props
 */
export interface EAutocompleteProps {
  /** 自定义 class，透传到外层容器 */
  class?: string
  /** 当前输入值，支持 v-model */
  modelValue?: string
  /** 异步获取建议选项的函数，由外部实现 */
  fetchSuggestions?: (query: string) => Promise<AutocompleteOption[]>
  /** 输入防抖时长（毫秒） */
  debounce?: number
  /** 输入框占位文本 */
  placeholder?: string
  /** 是否禁用输入 */
  disabled?: boolean
}

/**
 * EAutocomplete 自动补全事件
 */
export interface EAutocompleteEmits {
  /** 输入值变化，配合 v-model */
  (e: 'update:modelValue', value: string): void
  /** 用户从下拉面板选择某一项 */
  (e: 'select', option: AutocompleteOption): void
  /** 输入内容变化（与 update:modelValue 并发，便于业务监听） */
  (e: 'change', value: string): void
}
