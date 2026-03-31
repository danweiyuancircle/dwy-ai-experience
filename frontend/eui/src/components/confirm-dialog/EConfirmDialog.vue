<script setup lang="ts">
import { computed } from 'vue'
import { AlertTriangle, Info, XCircle } from 'lucide-vue-next'
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import { EButton } from '../button'
import type { EConfirmDialogProps, EConfirmDialogEmits } from './types'

const props = withDefaults(defineProps<EConfirmDialogProps>(), {
  type: 'info',
  confirmText: '确认',
  cancelText: '取消',
})

const emit = defineEmits<EConfirmDialogEmits>()

const typeConfig = computed(() => {
  const configs = {
    info: {
      icon: Info,
      iconClass: 'text-blue-500',
      confirmClass: 'bg-primary hover:bg-primary/90',
    },
    warning: {
      icon: AlertTriangle,
      iconClass: 'text-yellow-500',
      confirmClass: 'bg-yellow-500 hover:bg-yellow-500/90 text-white',
    },
    error: {
      icon: XCircle,
      iconClass: 'text-destructive',
      confirmClass: 'bg-destructive hover:bg-destructive/90',
    },
  }
  return configs[props.type]
})

function handleConfirm() {
  emit('confirm')
  emit('update:open', false)
}

function handleCancel() {
  emit('cancel')
  emit('update:open', false)
}
</script>

<template>
  <DialogRoot
    data-slot="confirm-dialog"
    :open="props.open"
    @update:open="(val) => emit('update:open', val)"
  >
    <DialogPortal>
      <DialogOverlay
        class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
      />
      <DialogContent
        :class="cn(
          'bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 fixed top-[50%] left-[50%] z-50 w-full max-w-sm translate-x-[-50%] translate-y-[-50%] rounded-lg border p-6 shadow-lg duration-200',
          props.class,
        )"
      >
        <div class="flex items-start gap-4">
          <component
            :is="typeConfig.icon"
            :class="cn('mt-0.5 size-5 shrink-0', typeConfig.iconClass)"
          />
          <div class="flex flex-col gap-1.5">
            <DialogTitle
              v-if="title"
              class="text-base font-semibold leading-none"
            >
              {{ title }}
            </DialogTitle>
            <DialogDescription
              v-if="message"
              class="text-muted-foreground text-sm"
            >
              {{ message }}
            </DialogDescription>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-2">
          <EButton
            variant="outline"
            @click="handleCancel"
          >
            {{ cancelText }}
          </EButton>
          <EButton
            :class="typeConfig.confirmClass"
            @click="handleConfirm"
          >
            {{ confirmText }}
          </EButton>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
