/**
 * EConfirmDialog 确认对话框组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 确认对话框类型：决定图标与主色 */
export type ConfirmDialogType = 'info' | 'warning' | 'error'

/**
 * EConfirmDialog 确认对话框 Props
 */
export interface EConfirmDialogProps {
  /** 自定义 class，透传到内容区 */
  class?: HTMLAttributes['class']
  /** 是否展开，支持 v-model:open */
  open?: boolean
  /** 对话框标题 */
  title?: string
  /** 消息内容 */
  message?: string
  /** 对话框类型，影响图标与主色 */
  type?: ConfirmDialogType
  /** 确认按钮文案 */
  confirmText?: string
  /** 取消按钮文案 */
  cancelText?: string
}

/**
 * EConfirmDialog 确认对话框事件
 */
export interface EConfirmDialogEmits {
  /** 展开状态变化 */
  'update:open': [value: boolean]
  /** 确认按钮点击 */
  confirm: []
  /** 取消按钮点击 */
  cancel: []
}
