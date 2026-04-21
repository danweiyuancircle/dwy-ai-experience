/**
 * 全局 Notification 通知 composable
 * 四角弹出、带标题和正文的卡片式通知，适用于非阻塞、需长时停留的提醒
 */

/** Notification 配置项 */
export interface NotificationOptions {
  /** 通知标题（必填） */
  title: string
  /** 通知正文（可选） */
  message?: string
  /** 语义类型，决定配色（当前实现仅保留字段） */
  type?: 'success' | 'warning' | 'info' | 'error'
  /** 自动关闭延迟（毫秒），<=0 不自动关闭；默认 4500 */
  duration?: number
  /** 弹出位置，默认 top-right */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
  /** 传入后整张通知变为可点击，用于跳转详情等场景 */
  onClick?: () => void
  /** 是否显示关闭按钮，默认 true */
  closable?: boolean
}

import { escapeHtml } from '@/utils/escape'

let seed = 0

function getContainer(position: string): HTMLElement {
  const id = `eui-notification-${position}`
  let container = document.getElementById(id)
  if (!container) {
    container = document.createElement('div')
    container.id = id
    const posStyles: Record<string, string> = {
      'top-right': 'top:16px;right:16px;',
      'top-left': 'top:16px;left:16px;',
      'bottom-right': 'bottom:16px;right:16px;',
      'bottom-left': 'bottom:16px;left:16px;',
    }
    container.style.cssText = `position:fixed;${posStyles[position]}z-index:9999;display:flex;flex-direction:column;gap:8px;max-width:380px;`
    document.body.appendChild(container)
  }
  return container
}

/** 根据弹出位置返回对应的进入/退出滑动动画 class（左侧从左滑入，其余从右滑入） */
function getSlideClasses(position: string): { enter: string; exit: string } {
  if (position.includes('left')) {
    return {
      enter: 'animate-in fade-in-0 slide-in-from-left-2',
      exit: 'animate-out fade-out-0 slide-out-to-left-2',
    }
  }
  return {
    enter: 'animate-in fade-in-0 slide-in-from-right-2',
    exit: 'animate-out fade-out-0 slide-out-to-right-2',
  }
}

function showNotification(options: NotificationOptions) {
  const id = `eui-notif-${++seed}`
  const duration = options.duration ?? 4500
  const position = options.position ?? 'top-right'
  const closable = options.closable ?? true

  const container = getContainer(position)
  const slideClasses = getSlideClasses(position)

  const el = document.createElement('div')
  el.id = id
  el.className = `${slideClasses.enter} rounded-lg border bg-background p-4 shadow-lg`

  // Clickable styling
  if (options.onClick) {
    el.style.cursor = 'pointer'
    el.addEventListener('click', (e) => {
      // Don't trigger onClick if the close button was clicked
      if ((e.target as HTMLElement).closest('[data-notification-close]')) return
      options.onClick!()
    })
    el.addEventListener('mouseenter', () => { el.style.opacity = '0.85' })
    el.addEventListener('mouseleave', () => { el.style.opacity = '1' })
  }

  // Build inner HTML
  const titleHtml = `<div class="font-medium text-sm">${escapeHtml(options.title)}</div>`
  const messageHtml = options.message ? `<div class="text-muted-foreground text-sm mt-1">${escapeHtml(options.message)}</div>` : ''

  const closeButtonHtml = closable
    ? `<button data-notification-close class="absolute top-2 right-2 text-muted-foreground hover:text-foreground transition-colors p-0.5 rounded-sm" aria-label="Close">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
      </button>`
    : ''

  el.style.position = 'relative'
  el.innerHTML = `${closeButtonHtml}<div class="${closable ? 'pr-5' : ''}">${titleHtml}${messageHtml}</div>`

  container.appendChild(el)

  const close = () => {
    el.className = el.className.replace(slideClasses.enter, slideClasses.exit)
    setTimeout(() => {
      el.remove()
      if (container.childElementCount === 0) container.remove()
    }, 200)
  }

  // Bind close button
  if (closable) {
    const closeBtn = el.querySelector('[data-notification-close]')
    closeBtn?.addEventListener('click', (e) => {
      e.stopPropagation()
      close()
    })
  }

  if (duration > 0) setTimeout(close, duration)
  return { id, close }
}

/**
 * 获取全局 Notification 调用入口
 * @returns success/warning/error/info 四种语义方法，均返回 `{ id, close }`，支持手动关闭
 */
export function useNotification() {
  return {
    success: (opts: NotificationOptions) => showNotification({ ...opts, type: 'success' }),
    warning: (opts: NotificationOptions) => showNotification({ ...opts, type: 'warning' }),
    error: (opts: NotificationOptions) => showNotification({ ...opts, type: 'error' }),
    info: (opts: NotificationOptions) => showNotification({ ...opts, type: 'info' }),
  }
}
