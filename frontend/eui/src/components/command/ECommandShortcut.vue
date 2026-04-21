<!--
  ECommandShortcut 命令条目右侧的快捷键提示
  显示 "⌘K" 这类组合键说明，右对齐显示
-->
<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps<{
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <span
    data-slot="command-shortcut"
    :class="cn('text-muted-foreground ml-auto text-xs tracking-widest', props.class)"
  >
    <slot />
  </span>
</template>
