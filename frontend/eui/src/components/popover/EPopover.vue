<script setup lang="ts">
import { ref, watch } from 'vue'
import { PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EPopoverProps, EPopoverEmits } from './types'

const props = withDefaults(defineProps<EPopoverProps>(), {
  align: 'center',
  sideOffset: 4,
  destroyOnClose: true,
})

const emit = defineEmits<EPopoverEmits>()

const localOpen = ref(false)

watch(() => props.open, (val) => {
  if (val !== undefined) localOpen.value = val
})

watch(localOpen, (val) => {
  emit('update:open', val)
})
</script>

<template>
  <PopoverRoot v-model:open="localOpen" data-slot="popover">
    <PopoverTrigger data-slot="popover-trigger" as-child>
      <slot name="trigger" />
    </PopoverTrigger>
    <PopoverPortal>
      <PopoverContent
        data-slot="popover-content"
        :side="side"
        :side-offset="sideOffset"
        :align="align"
        :class="
          cn(
            'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 w-72 rounded-md border p-4 shadow-md origin-(--reka-popover-content-transform-origin) outline-hidden',
            props.class,
          )
        "
      >
        <template v-if="destroyOnClose ? localOpen : true">
          <slot />
        </template>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
