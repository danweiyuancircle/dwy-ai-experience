<!--
  EMenubarSub 子菜单容器
  包裹 EMenubarSubTrigger + EMenubarSubContent 组合，实现多级菜单
-->
<script setup lang="ts">
import { MenubarSub } from 'reka-ui'
</script>

<template>
  <MenubarSub>
    <slot />
  </MenubarSub>
</template>
