<script setup lang="ts">
import { EDialog } from '../dialog'
import { EButton } from '../button'
import { cn } from '@/utils/cn'
import type { EFormDialogProps, EFormDialogEmits } from './types'

const props = withDefaults(defineProps<EFormDialogProps>(), {
  confirmText: '确认',
  cancelText: '取消',
  loading: false,
  showClose: true,
})

const emit = defineEmits<EFormDialogEmits>()

function handleConfirm() {
  if (!props.loading) {
    emit('confirm')
  }
}

function handleCancel() {
  if (!props.loading) {
    emit('cancel')
    emit('update:open', false)
  }
}
</script>

<template>
  <EDialog
    :open="props.open"
    :title="props.title"
    :show-close="props.showClose && !props.loading"
    :max-width="props.size"
    :class="props.class"
    @update:open="(val) => emit('update:open', val)"
  >
    <template v-if="$slots.trigger" #trigger>
      <slot name="trigger" />
    </template>

    <slot />

    <template #footer>
      <slot name="footer">
        <EButton
          variant="outline"
          :disabled="props.loading"
          @click="handleCancel"
        >
          {{ cancelText }}
        </EButton>
        <EButton
          :disabled="props.loading"
          :loading="props.loading"
          @click="handleConfirm"
        >
          {{ confirmText }}
        </EButton>
      </slot>
    </template>
  </EDialog>
</template>
