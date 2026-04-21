<!--
  EMenubarSeparator 菜单分隔线
  在菜单内容面板中绘制一条横向分隔线，用于分组菜单项
-->
<script setup lang="ts">
import { MenubarSeparator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarSeparatorProps } from './types'

const props = defineProps<EMenubarSeparatorProps>()
</script>

<template>
  <MenubarSeparator
    data-slot="menubar-separator"
    :class="cn('bg-border -mx-1 my-1 h-px', props.class)"
  />
</template>
