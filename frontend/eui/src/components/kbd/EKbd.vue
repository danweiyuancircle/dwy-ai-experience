<!--
  EKbd 键盘按键展示组件
  渲染原生 <kbd>，用于在文档/命令说明中显示快捷键样式
-->
<script setup lang="ts">
import { cn } from '@/utils/cn'
import type { EKbdProps } from './types'

const props = defineProps<EKbdProps>()
</script>

<template>
  <kbd
    data-slot="kbd"
    :class="cn(
      'bg-muted text-muted-foreground pointer-events-none inline-flex h-5 w-fit min-w-5 items-center justify-center gap-1 rounded-sm px-1 font-sans text-xs font-medium select-none',
      '[&_svg:not([class*=\'size-\'])]:size-3',
      props.class,
    )"
  >
    <slot />
  </kbd>
</template>
