<!--
  EToggle 开关按钮
  基于 reka-ui Toggle，按下/抬起切换布尔状态，适合工具栏加粗/斜体等二态按钮
  reka-ui 原生使用 pressed，这里桥接为 v-model modelValue 保持 eui 约定
-->
<script setup lang="ts">
import { Toggle } from 'reka-ui'
import { cn } from '@/utils/cn'
import { toggleVariants } from './types'
import type { EToggleProps, EToggleEmits } from './types'

const props = withDefaults(defineProps<EToggleProps>(), {
  variant: 'default',
  size: 'default',
  disabled: false,
})

const emit = defineEmits<EToggleEmits>()
</script>

<template>
  <Toggle
    data-slot="toggle"
    :model-value="props.modelValue"
    :disabled="props.disabled"
    :class="cn(toggleVariants({ variant: props.variant, size: props.size }), props.class)"
    @update:model-value="(val: boolean) => emit('update:modelValue', val)"
  >
    <slot />
  </Toggle>
</template>
