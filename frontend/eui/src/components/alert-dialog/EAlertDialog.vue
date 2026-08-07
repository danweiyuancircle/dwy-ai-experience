<!--
  EAlertDialog 警告对话框组件
  基于 reka-ui AlertDialog 原语封装，强制用户选择确认或取消
  用于删除、重置等不可逆操作的二次确认
-->
<script setup lang="ts">
import {
  AlertDialogRoot,
  AlertDialogPortal,
  AlertDialogOverlay,
  AlertDialogContent,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EAlertDialogProps, EAlertDialogEmits } from './types'

const props = withDefaults(defineProps<EAlertDialogProps>(), {
  confirmText: '确认',
  cancelText: '取消',
})

const emit = defineEmits<EAlertDialogEmits>()

/**
 * 确认按钮处理：派发 confirm 事件后自动关闭对话框
 */
function handleConfirm() {
  emit('confirm')
  emit('update:open', false)
}

/**
 * 取消按钮处理：派发 cancel 事件后自动关闭对话框
 */
function handleCancel() {
  emit('cancel')
  emit('update:open', false)
}
</script>

<template>
  <AlertDialogRoot
    data-slot="alert-dialog"
    :open="props.open"
    @update:open="(val) => emit('update:open', val)"
  >
    <slot name="trigger" />
    <AlertDialogPortal>
      <AlertDialogOverlay
        data-slot="alert-dialog-overlay"
        class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
      />
      <AlertDialogContent
        data-slot="alert-dialog-content"
        :class="cn(
          'bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 fixed top-[50%] left-[50%] z-50 grid w-full max-w-[calc(100%-2rem)] translate-x-[-50%] translate-y-[-50%] gap-4 rounded-lg border p-6 shadow-lg duration-200 sm:max-w-lg',
          props.class,
        )"
      >
        <div
          data-slot="alert-dialog-header"
          class="flex flex-col gap-2 text-center sm:text-left"
        >
          <AlertDialogTitle
            v-if="title || $slots.title"
            data-slot="alert-dialog-title"
            class="text-lg font-semibold"
          >
            <slot name="title">{{ title }}</slot>
          </AlertDialogTitle>
          <AlertDialogDescription
            v-if="description || $slots.description"
            data-slot="alert-dialog-description"
            class="text-muted-foreground text-sm"
          >
            <slot name="description">{{ description }}</slot>
          </AlertDialogDescription>
          <slot />
        </div>
        <div
          data-slot="alert-dialog-footer"
          class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end"
        >
          <slot name="footer">
            <AlertDialogCancel
              class="inline-flex items-center justify-center gap-2 rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-xs transition-[color,box-shadow] hover:bg-accent hover:text-accent-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:pointer-events-none disabled:opacity-50"
              @click="handleCancel"
            >
              {{ cancelText }}
            </AlertDialogCancel>
            <AlertDialogAction
              class="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-xs transition-[color,box-shadow] hover:bg-primary/90 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:pointer-events-none disabled:opacity-50"
              @click="handleConfirm"
            >
              {{ confirmText }}
            </AlertDialogAction>
          </slot>
        </div>
      </AlertDialogContent>
    </AlertDialogPortal>
  </AlertDialogRoot>
</template>
