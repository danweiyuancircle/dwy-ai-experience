/**
 * 敏感输入安全绑定 composable
 * 通过 DOM property 直接写 value，避免密码/身份证等值以 attribute 形式暴露在 HTML 中
 * 同时处理中文输入法合成态与光标位置保留，参考 Element Plus ElInput 的 setNativeInputValue 实现
 */
import { watch, onMounted, ref, nextTick } from 'vue'
import type { Ref, ShallowRef } from 'vue'

type InputElement = HTMLInputElement | HTMLTextAreaElement

/**
 * 以 property 赋值方式同步响应式值到原生 input/textarea，防止数据泄露到 attribute
 * @param elRef 目标输入框 DOM 引用
 * @param value 返回当前值的 getter（配合 watch 实现响应）
 * @returns 合成状态、光标记录/恢复、强制同步及 composition 事件处理器
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
