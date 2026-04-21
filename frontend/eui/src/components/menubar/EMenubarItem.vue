<!--
  EMenubarItem 菜单项组件
  单个可点击的菜单条目，支持 destructive 变体
-->
<script setup lang="ts">
import { MenubarItem } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarItemProps } from './types'

const props = withDefaults(defineProps<EMenubarItemProps>(), {
  variant: 'default',
})

const emit = defineEmits<{
  /** 点击选中时触发 */
  (e: 'select', event: Event): void
}>()
</script>

<template>
  <MenubarItem
    data-slot="menubar-item"
    :data-inset="props.inset ? '' : undefined"
    :data-variant="props.variant"
    :disabled="props.disabled"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground data-[variant=destructive]:text-destructive-foreground data-[variant=destructive]:focus:bg-destructive/10 dark:data-[variant=destructive]:focus:bg-destructive/40 [&_svg:not([class*=\'text-\'])]:text-muted-foreground relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[inset]:pl-8 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class,
    )"
    @select="emit('select', $event)"
  >
    <slot />
  </MenubarItem>
</template>
