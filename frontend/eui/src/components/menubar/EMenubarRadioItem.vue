<!--
  EMenubarRadioItem 单选菜单项
  必须放在 EMenubarRadioGroup 内，左侧显示选中指示点
-->
<script setup lang="ts">
import { Circle } from 'lucide-vue-next'
import { MenubarRadioItem, MenubarItemIndicator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarRadioItemProps } from './types'

const props = defineProps<EMenubarRadioItemProps>()
const emit = defineEmits<{
  /** 选中时触发 */
  (e: 'select', event: Event): void
}>()
</script>

<template>
  <MenubarRadioItem
    data-slot="menubar-radio-item"
    :value="props.value"
    :disabled="props.disabled"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground relative flex cursor-default items-center gap-2 rounded-xs py-1.5 pr-2 pl-8 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class,
    )"
    @select="emit('select', $event)"
  >
    <span class="pointer-events-none absolute left-2 flex size-3.5 items-center justify-center">
      <MenubarItemIndicator>
        <Circle class="size-2 fill-current" />
      </MenubarItemIndicator>
    </span>
    <slot />
  </MenubarRadioItem>
</template>
