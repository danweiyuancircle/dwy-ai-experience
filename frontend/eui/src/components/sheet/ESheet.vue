<!--
  ESheet 抽屉侧拉面板组件
  基于 reka-ui Dialog 封装，从四个方向滑入的对话框
  与 EDrawer 的差异：Sheet 是 shadcn 风格的侧拉，更贴合移动端与快速预览场景
-->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ESheetProps, ESheetEmits } from './types'

const props = withDefaults(defineProps<ESheetProps>(), {
  side: 'right',
  showClose: true,
})

const emit = defineEmits<ESheetEmits>()

/** 本地开关：reka DialogRoot 要可写 v-model，外层 open 单向灌入 */
const localOpen = ref(props.open ?? false)

watch(() => props.open, (value) => {
  if (value !== undefined) localOpen.value = value
})

watch(localOpen, (value) => {
  emit('update:open', value)
  if (!value) emit('close')
})
</script>

<template>
  <DialogRoot
    v-model:open="localOpen"
    data-slot="sheet"
  >
    <DialogTrigger v-if="$slots.trigger" as-child>
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <!-- 关闭/退场时 overlay 与 content 仍可能留在 DOM；不关 pointer-events 会挡住汉堡和侧栏菜单 -->
      <DialogOverlay
        data-slot="sheet-overlay"
        :class="cn(
          'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 pointer-events-none data-[state=open]:pointer-events-auto fixed inset-0 z-50 bg-black/80',
        )"
      />
      <DialogContent
        data-slot="sheet-content"
        :class="cn(
          'bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:pointer-events-none fixed z-50 flex flex-col gap-4 shadow-lg transition ease-in-out data-[state=closed]:duration-300 data-[state=open]:duration-500',
          side === 'right' && 'data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right inset-y-0 right-0 h-full w-3/4 border-l sm:max-w-sm',
          side === 'left' && 'data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left inset-y-0 left-0 h-full w-3/4 border-r sm:max-w-sm',
          side === 'top' && 'data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top inset-x-0 top-0 h-auto border-b',
          side === 'bottom' && 'data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom inset-x-0 bottom-0 h-auto border-t',
          props.class,
        )"
      >
        <!-- 无可见标题时仍提供 DialogTitle，满足 reka 无障碍约束 -->
        <DialogTitle v-if="!title && !$slots.header" class="sr-only">面板</DialogTitle>
        <DialogDescription v-if="!description && !$slots.header" class="sr-only">
          侧滑面板
        </DialogDescription>
        <!-- Header -->
        <div v-if="$slots.header || title || description" data-slot="sheet-header" class="flex flex-col gap-1.5 p-4">
          <slot name="header">
            <DialogTitle v-if="title" data-slot="sheet-title" class="text-foreground font-semibold">
              {{ title }}
            </DialogTitle>
            <DialogDescription v-if="description" data-slot="sheet-description" class="text-muted-foreground text-sm">
              {{ description }}
            </DialogDescription>
          </slot>
        </div>

        <!-- Default content -->
        <div :class="cn('flex-1 overflow-auto px-4 py-1', props.bodyClass)">
          <slot />
        </div>

        <!-- Footer -->
        <div v-if="$slots.footer" data-slot="sheet-footer" class="mt-auto flex flex-col gap-2 p-4">
          <slot name="footer" />
        </div>

        <!-- Close button -->
        <DialogClose
          v-if="showClose"
          class="focus-visible:ring-ring/50 data-[state=open]:bg-secondary absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus-visible:ring-[3px] focus-visible:outline-hidden disabled:pointer-events-none"
        >
          <X class="size-4" />
          <span class="sr-only">Close</span>
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
