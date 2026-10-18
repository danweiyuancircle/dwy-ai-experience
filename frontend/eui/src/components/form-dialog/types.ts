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
  /** 对话框说明，供用户和辅助技术理解当前操作 */
  description?: string
  /** 最大宽度（透传到 EDialog 的 maxWidth） */
  size?: string
  /** 提交加载态：禁用确认、取消、X、Esc 和遮罩关闭；父组件仍可通过 open=false 收起 */
  loading?: boolean
  /** 业务条件未满足时禁用确认，不影响取消与关闭 */
  confirmDisabled?: boolean
  /** 关联原生 form 的 id；默认确认按钮提交该表单，不再派发 confirm，业务只监听表单 submit */
  form?: string
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
  /** 未关联 form 时的确认按钮点击（loading 或 confirmDisabled 时忽略） */
  confirm: []
  /** 取消按钮点击 */
  cancel: []
}
