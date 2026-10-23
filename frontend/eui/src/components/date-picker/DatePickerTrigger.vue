<!-- 内部触发器，不公开导出：同步 Popover 的关联 ID，避免覆盖 DOM id 后弹层仍引用旧的 triggerId。 -->
<script setup lang="ts">
import { PopoverTrigger, injectPopoverRootContext } from 'reka-ui'
import { useFormField } from '@/composables/useFormField'

const formField = useFormField()
const popover = injectPopoverRootContext()
// 必须处于 PopoverRoot 内，并在 PopoverTrigger 挂载前设置公开上下文的 triggerId。
// 这样触发器和弹层 aria-labelledby 共用同一 ID；表单外保留 Reka 自行生成的 ID。
if (formField) popover.triggerId = formField.formItemId
</script>

<template>
  <PopoverTrigger
    as-child
    :aria-invalid="formField?.error.value ? true : undefined"
    :aria-describedby="formField?.error.value ? formField.formMessageId : undefined"
  >
    <slot />
  </PopoverTrigger>
</template>
