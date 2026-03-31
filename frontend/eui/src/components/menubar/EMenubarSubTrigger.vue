<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import { MenubarSubTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarSubTriggerProps } from './types'

const props = defineProps<EMenubarSubTriggerProps>()
</script>

<template>
  <MenubarSubTrigger
    data-slot="menubar-sub-trigger"
    :data-inset="props.inset ? '' : undefined"
    :disabled="props.disabled"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-none select-none data-[inset]:pl-8',
      props.class,
    )"
  >
    <slot />
    <ChevronRight class="ml-auto size-4" />
  </MenubarSubTrigger>
</template>
