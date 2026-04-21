/**
 * 自研 Vue composable 工具集
 * 只提供几个强约束、轻量的 hook；更复杂的 hook 放 hooks/vueuse.ts 直接再导出 @vueuse/core 的实现
 */
import { ref, watch, onMounted, onBeforeUnmount, type Ref } from 'vue'

/**
 * 防抖 ref：源 ref 变化后延迟 delay 毫秒才更新输出 ref
 * 典型用途：搜索框输入后延迟触发请求
 * @param value 源响应式值
 * @param delay 防抖延迟，默认 300ms
 * @returns 防抖后的新 ref，值滞后于源 ref
 */
export function useDebounce<T>(value: Ref<T>, delay = 300): Ref<T> {
  const debounced = ref(value.value) as Ref<T>
  let timer: ReturnType<typeof setTimeout>

  watch(value, (val) => {
    clearTimeout(timer)
    timer = setTimeout(() => { debounced.value = val }, delay)
  })

  return debounced
}

/**
 * 点击元素外部时触发回调
 * 典型用途：下拉菜单/弹层的"点击外部关闭"
 * @param target 目标元素 ref，点击其内部不触发回调
 * @param handler 点击外部时执行的回调
 */
export function useClickOutside(
  target: Ref<HTMLElement | null | undefined>,
  handler: (event: MouseEvent) => void
) {
  function listener(event: MouseEvent) {
    const el = target.value
    if (!el || el.contains(event.target as Node)) return
    handler(event)
  }

  // 使用捕获阶段（第三个参数 true），优先于元素自身的 click 处理
  onMounted(() => document.addEventListener('click', listener, true))
  onBeforeUnmount(() => document.removeEventListener('click', listener, true))
}

/**
 * 事件监听器，组件卸载时自动移除
 * 避免手写 addEventListener/removeEventListener 导致的内存泄漏
 * @param target 监听目标（DOM/window/document 或 ref 包装）
 * @param event 事件名，如 'resize'、'scroll'
 * @param handler 事件回调
 * @param options addEventListener 原生选项（capture/passive/once 等）
 */
export function useEventListener(
  target: EventTarget | Ref<EventTarget | null | undefined>,
  event: string,
  handler: EventListenerOrEventListenerObject,
  options?: AddEventListenerOptions
) {
  const getTarget = () => {
    if (target && 'value' in target) return target.value
    return target
  }

  onMounted(() => {
    const el = getTarget()
    el?.addEventListener(event, handler, options)
  })

  onBeforeUnmount(() => {
    const el = getTarget()
    el?.removeEventListener(event, handler, options)
  })
}
