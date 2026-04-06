<script setup lang="ts">
import { cn } from '@/utils/cn'
import type { EInputGroupProps } from './types'

const props = defineProps<EInputGroupProps>()
</script>

<template>
  <div
    data-slot="input-group"
    role="group"
    :class="cn(
      'border-input dark:bg-input/30 relative flex w-full items-center rounded-md border shadow-xs transition-[color,box-shadow] outline-none h-9 min-w-0 has-[>textarea]:h-auto',
      'focus-within:border-ring focus-within:ring-ring/50 focus-within:ring-[3px]',
      props.class,
    )"
  >
    <slot />
  </div>
</template>

<style scoped>
:deep([data-slot="input"]) {
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  outline: none !important;
}

:deep([data-slot="input"]:focus-visible) {
  ring: none !important;
  box-shadow: none !important;
  border: none !important;
}
</style>
