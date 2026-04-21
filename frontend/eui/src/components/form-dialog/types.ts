/**
 * EFormDialog 表单对话框组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EFormDialog 表单对话框 Props
 */
export interface EFormDialogProps {
  /** 自定义 class */
  class?: HTMLAttributes['class']
  /** 是否展开 */
  open?: boolean
  /** 对话框标题 */
  title?: string
  /** 最大宽度（透传到 EDialog 的 maxWidth） */
  size?: string
  /** 确认按钮是否处于加载态，加载时禁用取消与关闭 */
  loading?: boolean
  /** 确认按钮文案 */
  confirmText?: string
  /** 取消按钮文案 */
  cancelText?: string
  /** 是否展示右上角关闭按钮 */
  showClose?: boolean
}

/**
 * EFormDialog 表单对话框事件
 */
export interface EFormDialogEmits {
  /** 展开状态变化 */
  'update:open': [value: boolean]
  /** 确认按钮点击（loading 时忽略） */
  confirm: []
  /** 取消按钮点击 */
  cancel: []
}
