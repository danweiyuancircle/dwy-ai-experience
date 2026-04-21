<!--
  ENavigationMenuItem 单个导航菜单项容器
  用于组合 Trigger + Content 或单个 Link
-->
<script setup lang="ts">
import { NavigationMenuItem } from 'reka-ui'
import { cn } from '@/utils/cn'

const props = defineProps<{ class?: string; value?: string }>()
</script>

<template>
  <NavigationMenuItem
    data-slot="navigation-menu-item"
    :value="props.value"
    :class="cn('relative', props.class)"
  >
    <slot />
  </NavigationMenuItem>
</template>
