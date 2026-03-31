<script setup lang="ts">
import { MenubarRoot } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarProps } from './types'

const props = defineProps<EMenubarProps>()
</script>

<template>
  <MenubarRoot
    data-slot="menubar"
    :class="cn('bg-background flex h-9 items-center gap-1 rounded-md border p-1 shadow-xs', props.class)"
  >
    <slot />
  </MenubarRoot>
</template>
