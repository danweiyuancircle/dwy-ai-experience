<!--
  ENavigationMenuTrigger 导航菜单展开触发器
  点击/悬浮展开对应 Content；展开态时下拉箭头旋转 180°
-->
<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'
import { NavigationMenuTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'

const props = defineProps<{ class?: string; disabled?: boolean }>()

const triggerStyle = 'group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1'
</script>

<template>
  <NavigationMenuTrigger
    data-slot="navigation-menu-trigger"
    :disabled="props.disabled"
    :class="cn(triggerStyle, 'group', props.class)"
  >
    <slot />
    <ChevronDown
      class="relative top-[1px] ml-1 size-3 transition duration-300 group-data-[state=open]:rotate-180"
      aria-hidden="true"
    />
  </NavigationMenuTrigger>
</template>
