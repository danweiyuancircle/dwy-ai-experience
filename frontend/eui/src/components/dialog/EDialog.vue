<!--
  EDialog 通用对话框组件
  基于 reka-ui Dialog 原语封装，支持拖拽、全屏、destroyOnClose 等能力
  Header 区域可拖动改变位置；遮罩点击 / Esc 行为可开关
-->
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { X } from 'lucide-vue-next'
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
  DialogTrigger,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EDialogProps, EDialogEmits } from './types'

const props = withDefaults(defineProps<EDialogProps>(), {
  showClose: true,
  draggable: false,
  closeOnClickModal: true,
  closeOnPressEscape: true,
  fullscreen: false,
  destroyOnClose: true,
  showOverlay: true,
})

const emit = defineEmits<EDialogEmits>()

// 使用本地 ref 承接 open，reka-ui DialogRoot 要求 v-model 为可写 ref
const localOpen = ref(props.open ?? false)

// 外部 prop 变化 → 同步本地状态
watch(() => props.open, (val) => {
  localOpen.value = val ?? false
})

// 本地状态变化 → 派发事件；关闭时重置拖拽偏移
watch(localOpen, (val) => {
  emit('update:open', val)
  if (val) emit('open')
  else {
    emit('close')
    dragOffset.x = 0
    dragOffset.y = 0
  }
})

// --- 点击遮罩 / Esc 关闭行为 ---

/** 阻止 closeOnClickModal=false 时的遮罩点击关闭 */
function onInteractOutside(event: Event) {
  if (!props.closeOnClickModal) {
    event.preventDefault()
  }
}

/** 阻止 closeOnPressEscape=false 时的 Esc 关闭 */
function onEscapeKeyDown(event: KeyboardEvent) {
  if (!props.closeOnPressEscape) {
    event.preventDefault()
  }
}

// --- 拖拽实现 ---
const dragOffset = reactive({ x: 0, y: 0 })
let isDragging = false
let dragStart = { x: 0, y: 0 }
let offsetStart = { x: 0, y: 0 }

/**
 * 按下标题栏开始拖拽：仅响应鼠标主键
 */
function onHeaderPointerDown(event: PointerEvent) {
  if (!props.draggable) return
  if (event.button !== 0) return
  isDragging = true
  dragStart = { x: event.clientX, y: event.clientY }
  offsetStart = { x: dragOffset.x, y: dragOffset.y }
  document.addEventListener('pointermove', onPointerMove)
  document.addEventListener('pointerup', onPointerUp)
}

/** 拖拽中：更新偏移量 */
function onPointerMove(event: PointerEvent) {
  if (!isDragging) return
  dragOffset.x = offsetStart.x + (event.clientX - dragStart.x)
  dragOffset.y = offsetStart.y + (event.clientY - dragStart.y)
}

/** 松开鼠标：结束拖拽并移除监听 */
function onPointerUp() {
  isDragging = false
  document.removeEventListener('pointermove', onPointerMove)
  document.removeEventListener('pointerup', onPointerUp)
}
</script>

<template>
  <DialogRoot
    v-model:open="localOpen"
    data-slot="dialog"
  >
    <DialogTrigger
      v-if="$slots.trigger"
      data-slot="dialog-trigger"
      as-child
    >
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay
        v-if="showOverlay"
        data-slot="dialog-overlay"
        :class="cn(
          'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/30 backdrop-blur-sm',
        )"
      />

      <DialogContent
        data-slot="dialog-content"
        :class="cn(
          'bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 fixed top-[50%] left-[50%] z-50 flex flex-col overflow-hidden w-full max-w-[calc(100%-2rem)] max-h-[calc(100vh-2rem)] translate-x-[-50%] translate-y-[-50%] gap-4 rounded-lg border p-6 shadow-lg duration-200 sm:max-w-lg',
          fullscreen && '!max-w-full !w-full !h-full !rounded-none !translate-x-0 !translate-y-0 !top-0 !left-0',
          props.class,
        )"
        :style="{
          ...(maxWidth && !fullscreen ? { maxWidth } : {}),
          ...(draggable && !fullscreen ? { transform: `translate(calc(-50% + ${dragOffset.x}px), calc(-50% + ${dragOffset.y}px))` } : {}),
        }"
        @interact-outside="onInteractOutside"
        @escape-key-down="onEscapeKeyDown"
      >
        <div
          v-if="title || description || $slots.header"
          data-slot="dialog-header"
          :class="cn(
            'flex flex-col gap-2 text-center sm:text-left shrink-0',
            draggable && !fullscreen && 'cursor-move select-none',
          )"
          @pointerdown="onHeaderPointerDown"
        >
          <slot name="header">
            <DialogTitle
              v-if="title"
              data-slot="dialog-title"
              :class="cn('text-lg leading-none font-semibold')"
            >
              {{ title }}
            </DialogTitle>
            <DialogDescription
              v-if="description"
              data-slot="dialog-description"
              :class="cn('text-muted-foreground text-sm')"
            >
              {{ description }}
            </DialogDescription>
          </slot>
        </div>

        <!-- destroyOnClose: unmount content when closed; otherwise always render -->
        <div v-if="destroyOnClose ? localOpen : true" data-slot="dialog-body" class="flex-1 min-h-0 overflow-y-auto">
          <div class="p-1">
            <slot />
          </div>
        </div>

        <div
          v-if="$slots.footer"
          data-slot="dialog-footer"
          :class="cn('flex flex-col-reverse gap-2 sm:flex-row sm:justify-end shrink-0')"
        >
          <slot name="footer" />
        </div>

        <DialogClose
          v-if="showClose"
          data-slot="dialog-close"
          class="focus-visible:ring-ring/50 data-[state=open]:bg-accent data-[state=open]:text-muted-foreground absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus-visible:ring-[3px] focus-visible:outline-hidden disabled:pointer-events-none [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4"
        >
          <X />
          <span class="sr-only">Close</span>
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
