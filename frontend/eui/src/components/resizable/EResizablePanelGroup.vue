<!--
  EResizablePanelGroup 可伸缩面板容器
  基于 reka-ui Splitter 封装，水平/垂直排列多个 EResizablePanel
  布局变化通过 layout 事件外发，便于持久化用户调整
-->
<script setup lang="ts">
import { SplitterGroup } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EResizablePanelGroupProps } from './types'

const props = withDefaults(defineProps<EResizablePanelGroupProps>(), {
  direction: 'horizontal',
})

const emit = defineEmits<{ (e: 'layout', sizes: number[]): void }>()
</script>

<template>
  <SplitterGroup
    data-slot="resizable-panel-group"
    :direction="props.direction"
    :id="props.id"
    :class="cn('flex h-full w-full data-[orientation=vertical]:flex-col', props.class)"
    @layout="emit('layout', $event)"
  >
    <slot />
  </SplitterGroup>
</template>
