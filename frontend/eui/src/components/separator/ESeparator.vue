<script setup lang="ts">
import { Separator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ESeparatorProps } from './types'

const props = withDefaults(defineProps<ESeparatorProps>(), {
  orientation: 'horizontal',
  decorative: true,
})
</script>

<template>
  <Separator
    data-slot="separator"
    :orientation="props.orientation"
    :decorative="props.decorative"
    :class="cn(
      'bg-border shrink-0 data-[orientation=horizontal]:h-px data-[orientation=horizontal]:w-full data-[orientation=vertical]:h-full data-[orientation=vertical]:w-px',
      props.class,
    )"
  />
</template>
