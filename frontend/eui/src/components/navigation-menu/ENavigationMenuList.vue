<script setup lang="ts">
import { NavigationMenuList } from 'reka-ui'
import { cn } from '@/utils/cn'

const props = defineProps<{ class?: string }>()
</script>

<template>
  <NavigationMenuList
    data-slot="navigation-menu-list"
    :class="cn('group flex flex-1 list-none items-center justify-center gap-1', props.class)"
  >
    <slot />
  </NavigationMenuList>
</template>
