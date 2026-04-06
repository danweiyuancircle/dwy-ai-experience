<script setup lang="ts">
import { computed, provide, toRef } from 'vue'
import { ConfigProvider as RekaConfigProvider } from 'reka-ui'
import { CONFIG_PROVIDER_KEY, defaultLocale } from '@/composables/useConfigProvider'
import type { EConfigProviderProps } from './types'

const props = withDefaults(defineProps<EConfigProviderProps>(), {
  size: 'default',
  zIndex: 2000,
})

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
