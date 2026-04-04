import { ref } from 'vue'

/**
 * Copy text to clipboard using the Clipboard API.
 */
export async function copyText(text: string): Promise<void> {
  await navigator.clipboard.writeText(text)
}

/**
 * Reactive clipboard composable — copy text and track state.
 */
export function useClipboard() {
  const text = ref('')
  const copied = ref(false)
  const isSupported = typeof navigator !== 'undefined' && !!navigator.clipboard

  async function copy(value: string): Promise<void> {
    if (!isSupported) return
    await navigator.clipboard.writeText(value)
    text.value = value
    copied.value = true
    setTimeout(() => { copied.value = false }, 1500)
  }

  return { text, copy, copied, isSupported }
}
