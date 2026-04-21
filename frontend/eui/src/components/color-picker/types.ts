/**
 * EColorPicker 颜色选择器组件的类型定义
 */

/**
 * EColorPicker 颜色选择器 Props
 */
export interface EColorPickerProps {
  /** 自定义 class，透传到触发按钮 */
  class?: string
  /** 当前颜色值，6 位或 8 位十六进制（启用 alpha 时为 8 位） */
  modelValue?: string
  /** 预设色板数组 */
  presets?: string[]
  /** 是否启用透明度通道 */
  showAlpha?: boolean
  /** 是否禁用 */
  disabled?: boolean
}

/**
 * EColorPicker 颜色选择器事件
 */
export interface EColorPickerEmits {
  /** 颜色值变化 */
  (e: 'update:modelValue', value: string): void
  /** 业务 change 事件（与 update:modelValue 并发） */
  (e: 'change', value: string): void
}
