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
  /** 操作按钮 */
  action?: { label: string; onClick: () => void }
}

export interface PromiseOptions<T> {
  /** 加载中提示 */
  loading: string
  /** 成功提示 */
  success: string | ((data: T) => string)
  /** 失败提示 */
  error: string | ((error: unknown) => string)
}

/**
 * Toast 通知函数。
 *
 * 支持直接调用和类型方法：
 *
 * @example
 * ```ts
 * const toast = useToast()
 *
 * // 类型方法
 * toast.success('操作成功')
 * toast.error('操作失败', { description: '请稍后重试' })
 *
 * // 直接调用（普通消息）
 * toast('提示内容', { action: { label: '撤销', onClick: () => {} } })
 *
 * // Promise 自动处理
 * toast.promise(fetchData(), { loading: '加载中', success: '完成', error: '失败' })
 * ```
 */
export function useToast() {
  /** 普通消息 */
  function toast(message: string, options?: ToastOptions) {
    sonnerToast(message, options)
  }

  /** 成功提示 */
  toast.success = (message: string, options?: ToastOptions) => {
    sonnerToast.success(message, options)
  }

  /** 错误提示 */
  toast.error = (message: string, options?: ToastOptions) => {
    sonnerToast.error(message, options)
  }

  /** 警告提示 */
  toast.warning = (message: string, options?: ToastOptions) => {
    sonnerToast.warning(message, options)
  }

  /** 信息提示 */
  toast.info = (message: string, options?: ToastOptions) => {
    sonnerToast.info(message, options)
  }

  /** Promise 自动处理 loading/success/error 状态 */
  toast.promise = <T>(promise: Promise<T>, options: PromiseOptions<T>) => {
    sonnerToast.promise(promise, options)
  }

  return toast
}
