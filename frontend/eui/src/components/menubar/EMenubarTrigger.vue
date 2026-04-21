<!--
  EMenubarTrigger 菜单项触发按钮
  点击后展开对应的 EMenubarContent 面板
-->
<script setup lang="ts">
import { MenubarTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarTriggerProps } from './types'

const props = defineProps<EMenubarTriggerProps>()
</script>

<template>
  <MenubarTrigger
    data-slot="menubar-trigger"
    :disabled="props.disabled"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground flex items-center rounded-sm px-2 py-1 text-sm font-medium outline-hidden select-none',
      props.class,
    )"
  >
    <slot />
  </MenubarTrigger>
</template>
