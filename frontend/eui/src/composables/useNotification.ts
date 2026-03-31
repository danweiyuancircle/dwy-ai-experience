export interface NotificationOptions {
  title: string
  message?: string
  type?: 'success' | 'warning' | 'info' | 'error'
  duration?: number
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
}

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

function showNotification(options: NotificationOptions) {
  const id = `eui-notif-${++seed}`
  const duration = options.duration ?? 4500
  const position = options.position ?? 'top-right'

  const container = getContainer(position)
  const el = document.createElement('div')
  el.id = id
  el.className = 'animate-in fade-in-0 slide-in-from-right-2 rounded-lg border bg-background p-4 shadow-lg'
  el.innerHTML = `<div class="font-medium text-sm">${options.title}</div>${options.message ? `<div class="text-muted-foreground text-sm mt-1">${options.message}</div>` : ''}`
  container.appendChild(el)

  const close = () => {
    el.className = el.className.replace('animate-in fade-in-0 slide-in-from-right-2', 'animate-out fade-out-0 slide-out-to-right-2')
    setTimeout(() => {
      el.remove()
      if (container.childElementCount === 0) container.remove()
    }, 200)
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
