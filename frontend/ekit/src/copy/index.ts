/**
 * 剪贴板操作封装
 * 基于 Clipboard API（navigator.clipboard），提供一次性复制函数和响应式 composable
 * 注意：Clipboard API 需要 HTTPS 或 localhost 环境，HTTP 下不可用
 */
import { ref } from 'vue'

/**
 * 复制文本到剪贴板
 * @param text 要复制的文本
 */
export async function copyText(text: string): Promise<void> {
  await navigator.clipboard.writeText(text)
}

/**
 * 响应式剪贴板 composable，跟踪复制状态（用于展示"已复制"反馈）
 * copied 在复制成功后置 true，1.5 秒后自动复位
 * @returns text 最近一次复制的文本；copy 执行复制；copied 是否刚复制成功；isSupported 当前环境是否支持
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
    // 1.5 秒后复位，方便模板用 v-if="copied" 展示"已复制"提示后自动消失
    setTimeout(() => { copied.value = false }, 1500)
  }

  return { text, copy, copied, isSupported }
}
