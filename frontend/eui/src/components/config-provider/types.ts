/**
 * EConfigProvider 全局配置组件的类型定义
 */
import type { Size } from '@/types'

/**
 * EConfigProvider 全局配置 Props
 */
export interface EConfigProviderProps {
  /** 全局默认尺寸，子组件未显式指定时使用 */
  size?: Size
  /** 全局弹层 z-index 基础值 */
  zIndex?: number
  /** 国际化文案覆盖表，会与内置 defaultLocale 合并 */
  locale?: Record<string, string>
  /**
   * 进入手机布局的最大宽度（px）。
   * 默认 767，与 Tailwind `md`（768）对齐。EAdminLayout / EPagination 等共用。
   */
  mobileBreakpoint?: number
}
