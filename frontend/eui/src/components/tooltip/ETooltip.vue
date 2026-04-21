<!--
  ETooltip 文字提示组件
  基于 reka-ui Tooltip 封装，hover/focus 时在目标元素旁弹出提示
  content 传纯文本，复杂内容通过 content 插槽提供
-->
<script setup lang="ts">
import {
  TooltipArrow,
  TooltipContent,
  TooltipPortal,
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ETooltipProps } from './types'

const props = withDefaults(defineProps<ETooltipProps>(), {
  sideOffset: 4,
  delayDuration: 0,
  disabled: false,
})
</script>

<template>
  <TooltipProvider :delay-duration="delayDuration">
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
