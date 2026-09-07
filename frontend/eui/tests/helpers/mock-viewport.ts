/**
 * 测试用视口 mock：驱动 useMediaQuery / useEuiMobile。
 * 必须在 mount 之前调用，否则 composable 读到的是 jsdom 默认桌面宽。
 */
import { vi } from 'vitest'

/**
 * 把 window.matchMedia 配成「当前宽度是否命中 query」。
 *
 * @param width 模拟的视口宽度（px）。示例：`375` 手机、`1024` 桌面。
 */
export function mockViewportWidth(width: number): void {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  })
  window.matchMedia = vi.fn().mockImplementation((query: string) => {
    const maxMatch = query.match(/max-width:\s*(\d+)px/)
    const minMatch = query.match(/min-width:\s*(\d+)px/)
    let matches = false
    if (maxMatch) matches = width <= Number(maxMatch[1])
    else if (minMatch) matches = width >= Number(minMatch[1])
    return {
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }
  })
}
