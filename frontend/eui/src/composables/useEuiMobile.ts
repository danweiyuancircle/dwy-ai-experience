/**
 * 判断当前视口是否处于 EUI 手机布局。
 * 断点与 Tailwind `md`（768px）对齐：max-width 767 为手机。
 * SSR 按桌面宽度计算，避免管理端首屏闪抽屉。
 */
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useMediaQuery } from '@vueuse/core'
import { DEFAULT_MOBILE_BREAKPOINT, useConfigProvider } from './useConfigProvider'

export { DEFAULT_MOBILE_BREAKPOINT }

/**
 * 读取是否处于手机布局。
 *
 * Args:
 *   breakpoint: 覆盖 ConfigProvider / 默认断点。不传则用全局配置。示例：`900`。
 * Returns:
 *   响应式 boolean。视口宽度 ≤ 断点时为 true。
 */
export function useEuiMobile(
  breakpoint?: MaybeRefOrGetter<number | undefined>,
) {
  const config = useConfigProvider()
  const query = computed(() => {
    const bp = toValue(breakpoint) ?? config.mobileBreakpoint.value
    return `(max-width: ${bp}px)`
  })
  // 不传 ssrWidth：浏览器走 matchMedia；SSR 走 VueUse useSSRWidth（未配置时不当手机）
  return useMediaQuery(query)
}
