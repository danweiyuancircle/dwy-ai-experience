<!--
  EResizablePanel 可伸缩面板
  作为 EResizablePanelGroup 的子面板，通过 defaultSize/minSize/maxSize 控制面板尺寸约束
-->
<script setup lang="ts">
import { SplitterPanel } from 'reka-ui'
import type { EResizablePanelProps } from './types'

const props = defineProps<EResizablePanelProps>()
</script>

<template>
  <SplitterPanel
    data-slot="resizable-panel"
    :default-size="props.defaultSize"
    :min-size="props.minSize"
    :max-size="props.maxSize"
    :id="props.id"
  >
    <slot />
  </SplitterPanel>
</template>
