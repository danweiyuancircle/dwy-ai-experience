export interface NotificationOptions {
  title: string
  message?: string
  type?: 'success' | 'warning' | 'info' | 'error'
  duration?: number
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
  /** When provided, makes the notification clickable */
  onClick?: () => void
  /** When true (default), show the close button; when false, hide it */
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

/** Resolve slide animation classes based on position */
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

export function useNotification() {
  return {
    success: (opts: NotificationOptions) => showNotification({ ...opts, type: 'success' }),
    warning: (opts: NotificationOptions) => showNotification({ ...opts, type: 'warning' }),
    error: (opts: NotificationOptions) => showNotification({ ...opts, type: 'error' }),
    info: (opts: NotificationOptions) => showNotification({ ...opts, type: 'info' }),
  }
}
