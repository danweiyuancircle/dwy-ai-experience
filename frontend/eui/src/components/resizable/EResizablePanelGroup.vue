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
