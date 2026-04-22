/**
 * 基础 Vue composable：全部再导出 @vueuse/core，不自写
 * - useDebounce：薄封装 refDebounced，保持 ekit 历史默认 300ms（VueUse 默认 200ms）
 * - useClickOutside：再导出 onClickOutside
 * - useEventListener：直接再导出，支持 window/document/ref 目标、多事件名、自动清理
 */
import type { Ref } from 'vue'
import { refDebounced } from '@vueuse/core'

export { onClickOutside as useClickOutside, useEventListener } from '@vueuse/core'

/**
 * 防抖 ref：源 ref 变化后延迟 delay 毫秒才更新输出 ref
 * 典型用途：搜索框输入后延迟触发请求
 * @param value 源响应式值
 * @param delay 防抖延迟，默认 300ms（与 ekit 旧版本保持一致）
 * @returns 防抖后的只读 ref
 */
export function useDebounce<T>(value: Ref<T>, delay: number = 300): Readonly<Ref<T>> {
  return refDebounced(value, delay)
}
