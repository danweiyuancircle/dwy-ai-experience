/**
 * EPinInput 分格输入框组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** EPinInput Props */
export interface EPinInputProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前各格字符数组，v-model 绑定 */
  modelValue?: string[]
  /** 格子总数，默认 4 */
  length?: number
  /** 是否禁用 */
  disabled?: boolean
  /** 是否以密码形式遮盖字符，默认 true */
  mask?: boolean
  /** 是否为 OTP 模式（支持浏览器自动识别短信验证码） */
  otp?: boolean
  /** 允许的输入类型：纯文本或仅数字 */
  type?: 'text' | 'number'
}

/** EPinInput Emits */
export interface EPinInputEmits {
  /** 值更新，用于 v-model */
  'update:modelValue': [value: string[]]
  /** 所有格子填满时触发，用于自动提交 */
  complete: [value: string[]]
}
