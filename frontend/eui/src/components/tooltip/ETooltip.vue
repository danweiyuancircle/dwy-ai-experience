<!--
  ETooltip 文字提示组件
  指针设备：reka Tooltip（hover/focus）。
  触屏/窄屏或 trigger=click：改走 Popover，因为 Tooltip 在触摸上打不开。
-->
<script setup lang="ts">
import { computed } from 'vue'
import {
  PopoverContent,
  PopoverPortal,
  PopoverRoot,
  PopoverTrigger,
  TooltipArrow,
  TooltipContent,
  TooltipPortal,
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import { useEuiMobile } from '@/composables/useEuiMobile'
import type { ETooltipProps } from './types'

const props = withDefaults(defineProps<ETooltipProps>(), {
  sideOffset: 4,
  delayDuration: 0,
  disabled: false,
  trigger: 'auto',
})

const isMobile = useEuiMobile()

/** click 模式：强制 click，或 auto 且当前是手机视口 */
const useClick = computed(() => {
  if (props.trigger === 'click') return true
  if (props.trigger === 'hover') return false
  return isMobile.value
})

const contentClass = computed(() =>
  cn(
    'bg-foreground text-background z-50 w-fit rounded-md px-3 py-1.5 text-xs text-balance',
    props.class,
  ),
)
</script>

<template>
  <PopoverRoot v-if="useClick && !disabled" data-slot="tooltip">
    <PopoverTrigger data-slot="tooltip-trigger" as-child>
      <slot />
    </PopoverTrigger>
    <PopoverPortal>
      <PopoverContent
        data-slot="tooltip-content"
        :side="side"
        :side-offset="sideOffset"
        :class="contentClass"
      >
        <slot name="content">{{ content }}</slot>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
  <TooltipProvider v-else :delay-duration="delayDuration">
    <TooltipRoot data-slot="tooltip" :disabled="disabled">
      <TooltipTrigger data-slot="tooltip-trigger" as-child>
        <slot />
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent
          data-slot="tooltip-content"
          :side="side"
          :side-offset="sideOffset"
          :class="
            cn(
              'bg-foreground text-background animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 z-50 w-fit rounded-md px-3 py-1.5 text-xs text-balance',
              props.class,
            )
          "
        >
          <slot name="content">{{ content }}</slot>
          <TooltipArrow
            class="bg-foreground fill-foreground z-50 size-2.5 translate-y-[calc(-50%_-_2px)] rotate-45 rounded-[2px]"
          />
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>
