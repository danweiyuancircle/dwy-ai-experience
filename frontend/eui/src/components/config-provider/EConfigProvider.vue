<script setup lang="ts">
import { computed, provide, toRef } from 'vue'
import { ConfigProvider as RekaConfigProvider } from 'reka-ui'
import { CONFIG_PROVIDER_KEY } from '@/composables/useConfigProvider'
import type { EConfigProviderProps } from './types'

const defaultLocale: Record<string, string> = {
  name: 'zh-CN',
  confirm: '确定',
  cancel: '取消',
  close: '关闭',
  loading: '加载中...',
  empty: '暂无数据',
  search: '搜索',
  selectPlaceholder: '请选择',
  inputPlaceholder: '请输入',
}

const props = withDefaults(defineProps<EConfigProviderProps>(), {
  size: 'default',
  zIndex: 2000,
})

const mergedLocale = computed(() => props.locale ?? defaultLocale)

provide(CONFIG_PROVIDER_KEY, {
  size: toRef(props, 'size'),
  zIndex: toRef(props, 'zIndex'),
  locale: mergedLocale,
})
</script>

<template>
  <RekaConfigProvider :locale="mergedLocale.name ?? 'zh-CN'">
    <slot />
  </RekaConfigProvider>
</template>
