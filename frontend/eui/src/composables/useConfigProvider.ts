import type { InjectionKey, Ref } from 'vue'
import { inject, ref } from 'vue'
import type { Size } from '@/types'

export const CONFIG_PROVIDER_KEY = Symbol() as InjectionKey<{
  size: Ref<Size>
  zIndex: Ref<number>
  locale: Ref<Record<string, string>>
}>

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

export function useConfigProvider() {
  const config = inject(CONFIG_PROVIDER_KEY, {
    size: ref('default' as Size),
    zIndex: ref(2000),
    locale: ref(defaultLocale),
  })
  return config
}
