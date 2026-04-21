/**
 * 全局 MessageBox 模态确认框 composable
 * 以 Promise 形式返回用户选择结果（confirm/cancel），便于与业务流程串联
 */

/** MessageBox 配置项 */
export interface MessageBoxOptions {
  /** 标题文本（可选） */
  title?: string
  /** 正文消息（必填） */
  message: string
  /** 语义类型（当前实现仅保留字段，未渲染图标） */
  type?: 'success' | 'warning' | 'info' | 'error'
  /** 确认按钮文案，默认「确定」 */
  confirmButtonText?: string
  /** 取消按钮文案，默认「取消」 */
  cancelButtonText?: string
  /** 是否显示取消按钮，alert 模式会强制为 false */
  showCancelButton?: boolean
}

import { escapeHtml } from '@/utils/escape'

/**
 * 获取命令式 MessageBox 调用入口
 * @returns alert（仅确认）、confirm（确认+取消）、prompt（预留）三种方法
 */
export function useMessageBox() {
  function open(options: MessageBoxOptions): Promise<'confirm' | 'cancel'> {
    return new Promise((resolve) => {
      const overlay = document.createElement('div')
      overlay.className = 'fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 animate-in fade-in-0'

      const box = document.createElement('div')
      box.className = 'bg-background rounded-lg border shadow-lg p-6 max-w-md w-full mx-4 animate-in zoom-in-95 fade-in-0'
      box.innerHTML = `
        ${options.title ? `<div class="font-semibold text-lg mb-2">${escapeHtml(options.title)}</div>` : ''}
        <div class="text-muted-foreground text-sm mb-6">${escapeHtml(options.message)}</div>
        <div class="flex justify-end gap-2">
          ${options.showCancelButton !== false ? `<button class="eui-msgbox-cancel inline-flex items-center justify-center rounded-md border px-4 py-2 text-sm font-medium hover:bg-accent">${escapeHtml(options.cancelButtonText ?? '取消')}</button>` : ''}
          <button class="eui-msgbox-confirm inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:bg-primary/90">${escapeHtml(options.confirmButtonText ?? '确定')}</button>
        </div>
      `

      overlay.appendChild(box)
      document.body.appendChild(overlay)

      const cleanup = (result: 'confirm' | 'cancel') => {
        overlay.className = overlay.className.replace('animate-in fade-in-0', 'animate-out fade-out-0')
        setTimeout(() => {
          overlay.remove()
          resolve(result)
        }, 150)
      }

      box.querySelector('.eui-msgbox-confirm')?.addEventListener('click', () => cleanup('confirm'))
      box.querySelector('.eui-msgbox-cancel')?.addEventListener('click', () => cleanup('cancel'))
      overlay.addEventListener('click', (e) => { if (e.target === overlay) cleanup('cancel') })
    })
  }

  return {
    alert: (message: string, title?: string) => open({ message, title, showCancelButton: false }),
    confirm: (message: string, title?: string) => open({ message, title }),
    prompt: (message: string, title?: string) => open({ message, title }),
  }
}
