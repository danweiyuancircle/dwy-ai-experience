<script setup lang="ts">
import { Check } from 'lucide-vue-next'
import { MenubarCheckboxItem, MenubarItemIndicator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarCheckboxItemProps } from './types'

const props = defineProps<EMenubarCheckboxItemProps>()
const emit = defineEmits<{ (e: 'update:checked', val: boolean): void; (e: 'select', event: Event): void }>()
</script>

<template>
  <MenubarCheckboxItem
    data-slot="menubar-checkbox-item"
    :checked="props.checked"
    :disabled="props.disabled"
    :class="cn(
      'focus:bg-accent focus:text-accent-foreground relative flex cursor-default items-center gap-2 rounded-xs py-1.5 pr-2 pl-8 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class,
    )"
    @update:checked="emit('update:checked', $event)"
    @select="emit('select', $event)"
  >
    <span class="pointer-events-none absolute left-2 flex size-3.5 items-center justify-center">
      <MenubarItemIndicator>
        <Check class="size-4" />
      </MenubarItemIndicator>
    </span>
    <slot />
  </MenubarCheckboxItem>
</template>
