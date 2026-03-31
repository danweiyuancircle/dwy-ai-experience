<script setup lang="ts">
import { NavigationMenuLink } from 'reka-ui'
import { cn } from '@/utils/cn'

const props = defineProps<{ class?: string; active?: boolean; href?: string; asChild?: boolean }>()
</script>

<template>
  <NavigationMenuLink
    data-slot="navigation-menu-link"
    :active="props.active"
    :as-child="props.asChild"
    :class="cn(
      'data-active:focus:bg-accent data-active:hover:bg-accent data-active:bg-accent/50 data-active:text-accent-foreground hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground ring-ring/10 dark:ring-ring/20 dark:outline-ring/40 outline-ring/50 [&_svg:not([class*=\'text-\'])]:text-muted-foreground flex flex-col gap-1 rounded-sm p-2 text-sm transition-[color,box-shadow] focus-visible:ring-4 focus-visible:outline-1 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class,
    )"
  >
    <slot />
  </NavigationMenuLink>
</template>
