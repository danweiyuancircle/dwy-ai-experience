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
