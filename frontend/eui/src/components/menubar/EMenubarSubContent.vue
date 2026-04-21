<!--
  EMenubarSubContent 子菜单内容面板
  通过 Portal 渲染到 body，承载多级子菜单项
-->
<script setup lang="ts">
import { MenubarPortal, MenubarSubContent } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarSubContentProps } from './types'

const props = defineProps<EMenubarSubContentProps>()
</script>

<template>
  <MenubarPortal>
    <MenubarSubContent
      data-slot="menubar-sub-content"
      :class="cn(
        'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 min-w-[8rem] origin-(--reka-menubar-content-transform-origin) overflow-hidden rounded-md border p-1 shadow-lg',
        props.class,
      )"
    >
      <slot />
    </MenubarSubContent>
  </MenubarPortal>
</template>
