<!--
  EConfigProvider 全局配置组件
  向子树注入尺寸、zIndex、locale 等全局配置
  同时透传 reka-ui 的 ConfigProvider 以统一国际化
-->
<script setup lang="ts">
import { computed, provide, toRef } from 'vue'
import { ConfigProvider as RekaConfigProvider } from 'reka-ui'
import { CONFIG_PROVIDER_KEY, defaultLocale } from '@/composables/useConfigProvider'
import type { EConfigProviderProps } from './types'

const props = withDefaults(defineProps<EConfigProviderProps>(), {
  size: 'default',
  zIndex: 2000,
})

// 将用户 locale 与内置默认值合并，支持局部覆盖文案
const mergedLocale = computed(() => props.locale ? { ...defaultLocale, ...props.locale } : defaultLocale)

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
