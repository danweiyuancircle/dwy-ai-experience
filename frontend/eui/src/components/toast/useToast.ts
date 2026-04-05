/**
 * Toast 通知封装。
 *
 * 包装 vue-sonner 的 toast API，提供统一的调用方式。
 */

import { toast as sonnerToast } from 'vue-sonner'

export interface ToastOptions {
  /** 描述信息 */
  description?: string
  /** 显示时长（毫秒） */
  duration?: number
}

/**
 * 返回 toast 通知方法。
 *
 * @example
 * ```ts
 * const toast = useToast()
 * toast.success('操作成功')
 * toast.error('操作失败', { description: '请稍后重试' })
 * ```
 */
export function useToast() {
  return {
    /** 成功提示 */
    success(message: string, options?: ToastOptions) {
      sonnerToast.success(message, options)
    },
    /** 错误提示 */
    error(message: string, options?: ToastOptions) {
      sonnerToast.error(message, options)
    },
    /** 警告提示 */
    warning(message: string, options?: ToastOptions) {
      sonnerToast.warning(message, options)
    },
    /** 信息提示 */
    info(message: string, options?: ToastOptions) {
      sonnerToast.info(message, options)
    },
  }
}
