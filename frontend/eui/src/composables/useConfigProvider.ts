import type { InjectionKey, Ref } from 'vue'
import { inject, ref } from 'vue'
import type { Size } from '@/types'

export const CONFIG_PROVIDER_KEY = Symbol() as InjectionKey<{
  size: Ref<Size>
  zIndex: Ref<number>
  locale: Ref<Record<string, string>>
}>

const defaultLocale: Record<string, string> = {
  confirm: '确定',
  cancel: '取消',
  close: '关闭',
  loading: '加载中...',
  empty: '暂无数据',
  search: '搜索',
  selectPlaceholder: '请选择',
  inputPlaceholder: '请输入',
}

export function useConfigProvider() {
  const config = inject(CONFIG_PROVIDER_KEY, {
    size: ref('default' as Size),
    zIndex: ref(2000),
    locale: ref(defaultLocale),
  })
  return config
}
