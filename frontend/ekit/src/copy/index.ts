/**
 * 剪贴板操作
 * useClipboard 直接再导出 @vueuse/core 的实现：内置 execCommand fallback、SSR-safe、isSupported 为 ComputedRef
 * copyText 是一行薄封装，用于非组件场景一次性复制
 */
export { useClipboard } from '@vueuse/core'

/**
 * 复制文本到剪贴板（一次性调用，非组件场景用）
 * 注意：Clipboard API 仅在 HTTPS 或 localhost 下可用；若需组件内响应式状态与兼容性 fallback，请用 useClipboard
 * @param text 要复制的文本
 */
export async function copyText(text: string): Promise<void> {
  await navigator.clipboard.writeText(text)
}
