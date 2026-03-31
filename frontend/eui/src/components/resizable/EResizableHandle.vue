<script setup lang="ts">
import { GripVertical } from 'lucide-vue-next'
import { SplitterResizeHandle } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EResizableHandleProps } from './types'

const props = defineProps<EResizableHandleProps>()
</script>

<template>
  <SplitterResizeHandle
    data-slot="resizable-handle"
    :id="props.id"
    :class="cn(
      'bg-border focus-visible:ring-ring relative flex w-px items-center justify-center after:absolute after:inset-y-0 after:left-1/2 after:w-1 after:-translate-x-1/2 focus-visible:ring-1 focus-visible:ring-offset-1 focus-visible:outline-hidden data-[orientation=vertical]:h-px data-[orientation=vertical]:w-full data-[orientation=vertical]:after:left-0 data-[orientation=vertical]:after:h-1 data-[orientation=vertical]:after:w-full data-[orientation=vertical]:after:-translate-y-1/2 data-[orientation=vertical]:after:translate-x-0 [&[data-orientation=vertical]>div]:rotate-90',
      props.class,
    )"
  >
    <template v-if="props.withHandle">
      <div class="bg-border z-10 flex h-4 w-3 items-center justify-center rounded-xs border">
        <GripVertical class="size-2.5" />
      </div>
    </template>
  </SplitterResizeHandle>
</template>
