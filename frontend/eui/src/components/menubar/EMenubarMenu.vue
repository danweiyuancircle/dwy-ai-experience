<!--
  EMenubarMenu 菜单项容器组件
  包裹 EMenubarTrigger + EMenubarContent 组合为单个顶层菜单
-->
<script setup lang="ts">
import { MenubarMenu } from 'reka-ui'
import type { EMenubarMenuProps } from './types'

const props = defineProps<EMenubarMenuProps>()
</script>

<template>
  <MenubarMenu :value="props.value">
    <slot />
  </MenubarMenu>
</template>
