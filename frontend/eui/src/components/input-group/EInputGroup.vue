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
      'has-[[data-slot=input-group-control]:focus-visible]:border-ring has-[[data-slot=input-group-control]:focus-visible]:ring-ring/50 has-[[data-slot=input-group-control]:focus-visible]:ring-[3px]',
      props.class,
    )"
  >
    <slot />
  </div>
</template>
