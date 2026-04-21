<!--
  ECollapsible 可折叠内容组件
  基于 reka-ui Collapsible 原语封装，提供 trigger 插槽与默认内容插槽
  比 EAccordion 更轻量，仅用于单个展开/收起场景
-->
<script setup lang="ts">
import { CollapsibleContent, CollapsibleRoot, CollapsibleTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ECollapsibleProps, ECollapsibleEmits } from './types'

const props = withDefaults(defineProps<ECollapsibleProps>(), {
  disabled: false,
})

const emit = defineEmits<ECollapsibleEmits>()

/**
 * 转发 reka-ui 的 open 变化事件到外部 v-model
 */
function onUpdate(value: boolean) {
  emit('update:modelValue', value)
}
</script>

<template>
  <CollapsibleRoot
    data-slot="collapsible"
    :open="modelValue"
    :disabled="disabled"
    :class="cn(props.class)"
    @update:open="onUpdate"
  >
    <CollapsibleTrigger data-slot="collapsible-trigger" as-child>
      <slot name="trigger" />
    </CollapsibleTrigger>
    <CollapsibleContent data-slot="collapsible-content">
      <slot />
    </CollapsibleContent>
  </CollapsibleRoot>
</template>
