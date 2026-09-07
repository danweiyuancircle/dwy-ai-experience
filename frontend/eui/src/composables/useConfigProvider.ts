/**
 * 全局配置 Provider 的注入 key、默认文案、以及消费端 composable
 * EConfigProvider 在应用顶层注入 size/zIndex/locale，子组件通过 useConfigProvider 读取
 */
import type { InjectionKey, Ref } from 'vue'
import { inject, ref } from 'vue'
import type { Size } from '@/types'

/** 默认手机断点（px）。与 Tailwind md（768）对齐，含本值及以下视为手机。 */
export const DEFAULT_MOBILE_BREAKPOINT = 767

/** EConfigProvider 的注入 key，包含统一的尺寸、弹层层级、国际化文案、手机断点 */
export const CONFIG_PROVIDER_KEY = Symbol() as InjectionKey<{
  size: Ref<Size>
  zIndex: Ref<number>
  locale: Ref<Record<string, string>>
  /** 进入手机布局的最大宽度（px），默认 767 */
  mobileBreakpoint: Ref<number>
}>

/** 默认中文语言包，覆盖所有需要文案的组件（上传、选择器、消息框等） */
export const defaultLocale: Record<string, string> = {
  name: 'zh-CN',
  confirm: '确定',
  cancel: '取消',
  close: '关闭',
  loading: '加载中...',
  empty: '暂无数据',
  search: '搜索',
  selectPlaceholder: '请选择',
  inputPlaceholder: '请输入',
  uploadClick: '点击上传',
  uploadDrag: '将文件拖拽到此处，或',
  uploadDragLink: '点击上传',
  uploadCard: '上传',
  timePickerPlaceholder: '请选择时间',
  timePickerHour: '时',
  timePickerMinute: '分',
  uploadExceed: '文件数量超出限制，最多 {limit} 个',
  uploadSizeExceed: '文件 "{name}" 大小为 {size}，超出 {maxSize}MB 限制',
  uploadValidationFailed: '文件 "{name}" 校验未通过',
}

/**
 * 读取全局配置；未包裹 EConfigProvider 时回落到默认值，保证组件在任意位置都能工作
 * @returns 全局 size / zIndex / locale 的响应式引用
 */
export function useConfigProvider() {
  const config = inject(CONFIG_PROVIDER_KEY, {
    size: ref('default' as Size),
    zIndex: ref(2000),
    locale: ref(defaultLocale),
    mobileBreakpoint: ref(DEFAULT_MOBILE_BREAKPOINT),
  })
  return config
}
