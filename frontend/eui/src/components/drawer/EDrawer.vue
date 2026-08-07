<!--
  EDrawer 抽屉组件
  基于 reka-ui Dialog 原语封装，通过 direction 控制从四个方向滑入
  底部抽屉额外渲染一个"抓手"指示可拖动
-->
<script setup lang="ts">
import { ref, watch } from 'vue'
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
import type { EDrawerProps, EDrawerEmits } from './types'

const props = withDefaults(defineProps<EDrawerProps>(), {
  direction: 'bottom',
  showClose: true,
  destroyOnClose: true,
})

const emit = defineEmits<EDrawerEmits>()

// 本地 open ref，用于给 reka-ui v-model 承接
const localOpen = ref(props.open ?? false)

// 外部 prop 变化 → 同步到本地
watch(() => props.open, (val) => {
  localOpen.value = val ?? false
})

// 本地状态变化 → 派发事件
watch(localOpen, (val) => {
  emit('update:open', val)
  if (!val) emit('close')
})
</script>

<template>
  <DialogRoot
    v-model:open="localOpen"
    data-slot="drawer"
  >
    <DialogTrigger
      v-if="$slots.trigger"
      data-slot="drawer-trigger"
      as-child
    >
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay
        data-slot="drawer-overlay"
        :class="cn(
          'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80',
        )"
      />

      <DialogContent
        data-slot="drawer-content"
        :class="cn(
          'bg-background fixed z-50 flex flex-col shadow-lg transition ease-in-out data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:duration-300 data-[state=open]:duration-500',
          direction === 'bottom' && 'data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom inset-x-0 bottom-0 mt-24 max-h-[80vh] rounded-t-lg',
          direction === 'top' && 'data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top inset-x-0 top-0 mb-24 max-h-[80vh] rounded-b-lg',
          direction === 'right' && 'data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right inset-y-0 right-0 h-full w-3/4 sm:max-w-sm',
          direction === 'left' && 'data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left inset-y-0 left-0 h-full w-3/4 sm:max-w-sm',
          props.class,
        )"
      >
        <!-- Drag handle for bottom drawer -->
        <div
          v-if="direction === 'bottom'"
          class="bg-muted mx-auto mt-4 h-2 w-[100px] shrink-0 rounded-full"
        />

        <!-- Header -->
        <div
          v-if="title || description || $slots.header"
          data-slot="drawer-header"
          class="flex flex-col gap-1.5 p-4"
        >
          <slot name="header">
            <DialogTitle
              v-if="title"
              data-slot="drawer-title"
              class="text-foreground font-semibold"
            >
              {{ title }}
            </DialogTitle>
            <DialogDescription
              v-if="description"
              data-slot="drawer-description"
              class="text-muted-foreground text-sm"
            >
              {{ description }}
            </DialogDescription>
          </slot>
        </div>

        <!-- Body -->
        <div v-if="destroyOnClose ? localOpen : true" class="flex-1 overflow-auto px-4 py-1">
          <slot />
        </div>

        <!-- Footer -->
        <div
          v-if="$slots.footer"
          data-slot="drawer-footer"
          class="mt-auto flex flex-col gap-2 p-4"
        >
          <slot name="footer" />
        </div>

        <!-- Close button -->
        <DialogClose
          v-if="showClose"
          data-slot="drawer-close"
          class="focus-visible:ring-ring/50 absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus-visible:ring-[3px] focus-visible:outline-hidden disabled:pointer-events-none"
        >
          <X class="size-4" />
          <span class="sr-only">Close</span>
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
