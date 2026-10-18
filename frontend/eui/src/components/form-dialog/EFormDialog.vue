<!--
  EFormDialog 表单对话框组件
  在 EDialog 基础上封装确认/取消按钮 + loading 态，专为表单提交场景
  loading 期间禁用取消/关闭，避免用户重复提交或中断请求
-->
<script setup lang="ts">
import { EDialog } from '../dialog'
import { EButton } from '../button'
import { cn } from '@/utils/cn'
import type { EFormDialogProps, EFormDialogEmits } from './types'

const props = withDefaults(defineProps<EFormDialogProps>(), {
  confirmText: '确认',
  cancelText: '取消',
  loading: false,
  confirmDisabled: false,
  showClose: true,
})

const emit = defineEmits<EFormDialogEmits>()

/** 关联表单时只走原生 submit，避免与 confirm 事件形成两条提交路径。 */
function handleConfirm() {
  if (!props.form && !props.loading && !props.confirmDisabled) {
    emit('confirm')
  }
}

/** 取消按钮处理：loading 中忽略，否则派发 cancel 并关闭 */
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
    :description="props.description"
    :show-close="props.showClose && !props.loading"
    :close-on-click-modal="!props.loading"
    :close-on-press-escape="!props.loading"
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
        <!-- 业务附加操作复用默认提交按钮；整体覆盖 footer 时不渲染。 -->
        <slot name="footer-leading" />
        <EButton
          variant="outline"
          :disabled="props.loading"
          @click="handleCancel"
        >
          {{ cancelText }}
        </EButton>
        <EButton
          :type="props.form ? 'submit' : 'button'"
          :form="props.form"
          :disabled="props.loading || props.confirmDisabled"
          :loading="props.loading"
          @click="handleConfirm"
        >
          {{ confirmText }}
        </EButton>
      </slot>
    </template>
  </EDialog>
</template>
