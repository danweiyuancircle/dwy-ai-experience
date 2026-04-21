/**
 * EAlertDialog 警告对话框组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EAlertDialog 警告对话框 Props
 */
export interface EAlertDialogProps {
  /** 自定义 class，透传到内容区域 */
  class?: HTMLAttributes['class']
  /** 是否展开对话框，v-model:open 双向绑定 */
  open?: boolean
  /** 对话框标题 */
  title?: string
  /** 对话框描述文字 */
  description?: string
  /** 确认按钮文案 */
  confirmText?: string
  /** 取消按钮文案 */
  cancelText?: string
}

/**
 * EAlertDialog 警告对话框事件
 */
export interface EAlertDialogEmits {
  /** 展开状态变化 */
  'update:open': [value: boolean]
  /** 用户点击确认按钮 */
  confirm: []
  /** 用户点击取消按钮 */
  cancel: []
}
