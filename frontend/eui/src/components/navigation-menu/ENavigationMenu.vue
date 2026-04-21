<!--
  ENavigationMenu 导航菜单根组件
  基于 reka-ui NavigationMenu 封装，shadcn-vue 风格的顶部横向导航
  子项结构：List > Item > (Trigger + Content | Link)；viewport=true 时在菜单下方渲染共用展开区
-->
<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'
import {
  NavigationMenuRoot,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuTrigger,
  NavigationMenuContent,
  NavigationMenuLink,
  NavigationMenuViewport,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ENavigationMenuProps } from './types'

const props = withDefaults(defineProps<ENavigationMenuProps>(), {
  viewport: true,
})
</script>

<template>
  <NavigationMenuRoot
    data-slot="navigation-menu"
    :data-viewport="props.viewport"
    :class="cn('group/navigation-menu relative flex max-w-max flex-1 items-center justify-center', props.class)"
  >
    <slot />
    <div v-if="props.viewport" class="absolute top-full left-0 isolate z-50 flex justify-center">
      <NavigationMenuViewport
        data-slot="navigation-menu-viewport"
        :class="cn(
          'origin-top-center bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-90 relative mt-1.5 h-[var(--reka-navigation-menu-viewport-height)] w-full overflow-hidden rounded-md border shadow md:w-[var(--reka-navigation-menu-viewport-width)]',
        )"
      />
    </div>
  </NavigationMenuRoot>
</template>
