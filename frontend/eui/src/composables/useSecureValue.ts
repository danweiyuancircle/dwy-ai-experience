import { watch, onMounted, ref, nextTick } from 'vue'
import type { Ref, ShallowRef } from 'vue'

type InputElement = HTMLInputElement | HTMLTextAreaElement

/**
 * 通过 DOM property 赋值代替 :value 绑定，避免值暴露在 HTML attribute 中。
 * 同时处理 IME 输入法和光标位置保留。
 *
 * 参考 Element Plus ElInput 的 setNativeInputValue 模式。
 */
export function useSecureValue(
  elRef: ShallowRef<InputElement | null | undefined> | Ref<InputElement | null | undefined>,
  value: () => string | number | null | undefined,
) {
  const isComposing = ref(false)

  function setNativeValue() {
    const el = elRef.value
    if (!el) return
    const strVal = String(value() ?? '')
    if (el.value === strVal) return
    el.value = strVal
  }

  // --- 光标位置保留 ---
  let cursorStart = 0
  let cursorEnd = 0

  function recordCursor() {
    const el = elRef.value
    if (!el) return
    cursorStart = el.selectionStart ?? 0
    cursorEnd = el.selectionEnd ?? 0
  }

  function setCursor() {
    const el = elRef.value
    if (!el) return
    nextTick(() => {
      el.setSelectionRange(cursorStart, cursorEnd)
    })
  }

  // --- IME 输入法 ---
  function onCompositionStart() {
    isComposing.value = true
  }

  function onCompositionEnd(event: CompositionEvent) {
    if (isComposing.value) {
      isComposing.value = false
      ;(event.target as InputElement)?.dispatchEvent(new Event('input'))
    }
  }

  // --- 同步时机 ---
  onMounted(setNativeValue)
  watch(value, setNativeValue)

  return {
    isComposing,
    recordCursor,
    setCursor,
    setNativeValue,
    onCompositionStart,
    onCompositionEnd,
  }
}
