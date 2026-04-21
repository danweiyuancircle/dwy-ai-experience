/**
 * 全局 Message 轻提示 composable
 * 命令式 API，类 Element Plus 风格；顶部居中弹出，自动消失，不阻断操作
 */
import { ref } from 'vue'

/** 单条 Message 的配置项 */
export interface MessageOptions {
  /** 提示文本内容 */
  message: string
  /** 语义类型，决定配色；默认 info */
  type?: 'success' | 'warning' | 'info' | 'error'
  /** 自动关闭延迟（毫秒），<=0 表示不自动关闭；默认 3000 */
  duration?: number
  /** 是否显示关闭按钮（当前实现未渲染，保留语义字段） */
  showClose?: boolean
}

interface MessageInstance {
  id: string
  options: MessageOptions
  close: () => void
}

const instances = ref<MessageInstance[]>([])
let seed = 0

function createMessageContainer(): HTMLElement {
  let container = document.getElementById('eui-message-container')
  if (!container) {
    container = document.createElement('div')
    container.id = 'eui-message-container'
    container.style.cssText = 'position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:9999;display:flex;flex-direction:column;align-items:center;gap:8px;pointer-events:none;'
    document.body.appendChild(container)
  }
  return container
}

function showMessage(options: MessageOptions | string) {
  const opts: MessageOptions = typeof options === 'string' ? { message: options } : options
  const id = `eui-msg-${++seed}`
  const duration = opts.duration ?? 3000

  const container = createMessageContainer()
  const el = document.createElement('div')
  el.id = id
  el.style.cssText = 'pointer-events:auto;'
  container.appendChild(el)

  const typeColors: Record<string, string> = {
    success: 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-200 dark:border-emerald-800',
    warning: 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950 dark:text-amber-200 dark:border-amber-800',
    error: 'bg-red-50 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-200 dark:border-red-800',
    info: 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950 dark:text-blue-200 dark:border-blue-800',
  }

  const colorClass = typeColors[opts.type ?? 'info']

  el.className = `animate-in fade-in-0 slide-in-from-top-2 rounded-lg border px-4 py-3 text-sm shadow-md ${colorClass}`
  el.textContent = opts.message

  const close = () => {
    el.className = el.className.replace('animate-in fade-in-0 slide-in-from-top-2', 'animate-out fade-out-0 slide-out-to-top-2')
    setTimeout(() => {
      el.remove()
      instances.value = instances.value.filter(i => i.id !== id)
      if (container.childElementCount === 0) container.remove()
    }, 200)
  }

  const instance: MessageInstance = { id, options: opts, close }
  instances.value.push(instance)

  if (duration > 0) {
    setTimeout(close, duration)
  }

  return instance
}

/**
 * 获取全局 Message 调用入口
 * @returns success/warning/error/info 四种语义方法，入参可为纯文本或完整配置对象
 */
export function useMessage() {
  return {
    success: (msg: string | MessageOptions) => showMessage(typeof msg === 'string' ? { message: msg, type: 'success' } : { ...msg, type: 'success' }),
    warning: (msg: string | MessageOptions) => showMessage(typeof msg === 'string' ? { message: msg, type: 'warning' } : { ...msg, type: 'warning' }),
    error: (msg: string | MessageOptions) => showMessage(typeof msg === 'string' ? { message: msg, type: 'error' } : { ...msg, type: 'error' }),
    info: (msg: string | MessageOptions) => showMessage(typeof msg === 'string' ? { message: msg, type: 'info' } : { ...msg, type: 'info' }),
  }
}
