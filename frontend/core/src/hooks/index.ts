import { ref, watch, onMounted, onBeforeUnmount, type Ref } from 'vue'

/**
 * Debounced ref — value updates after delay.
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
 * Click outside detection.
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

  onMounted(() => document.addEventListener('click', listener, true))
  onBeforeUnmount(() => document.removeEventListener('click', listener, true))
}

/**
 * Event listener with auto cleanup.
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
