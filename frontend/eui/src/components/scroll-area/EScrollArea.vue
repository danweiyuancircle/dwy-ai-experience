<script setup lang="ts">
import {
  ScrollAreaCorner,
  ScrollAreaRoot,
  ScrollAreaScrollbar,
  ScrollAreaThumb,
  ScrollAreaViewport,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EScrollAreaProps } from './types'

const props = withDefaults(defineProps<EScrollAreaProps>(), {
  type: 'hover',
})
</script>

<template>
  <ScrollAreaRoot
    data-slot="scroll-area"
    :type="props.type"
    :class="cn('relative', props.class)"
  >
    <ScrollAreaViewport
      data-slot="scroll-area-viewport"
      class="focus-visible:ring-ring/50 size-full rounded-[inherit] transition-[color,box-shadow] outline-none focus-visible:ring-[3px] focus-visible:outline-1"
    >
      <slot />
    </ScrollAreaViewport>
    <ScrollAreaScrollbar
      data-slot="scroll-area-scrollbar"
      orientation="vertical"
      class="flex touch-none p-px transition-colors select-none h-full w-2.5 border-l border-l-transparent"
    >
      <ScrollAreaThumb
        data-slot="scroll-area-thumb"
        class="bg-border relative flex-1 rounded-full"
      />
    </ScrollAreaScrollbar>
    <ScrollAreaScrollbar
      data-slot="scroll-area-scrollbar"
      orientation="horizontal"
      class="flex touch-none p-px transition-colors select-none h-2.5 flex-col border-t border-t-transparent"
    >
      <ScrollAreaThumb
        data-slot="scroll-area-thumb"
        class="bg-border relative flex-1 rounded-full"
      />
    </ScrollAreaScrollbar>
    <ScrollAreaCorner />
  </ScrollAreaRoot>
</template>
