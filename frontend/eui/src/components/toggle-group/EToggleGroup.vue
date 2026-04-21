<!--
  EToggleGroup 开关按钮组
  将多个 EToggle 组织为互斥（single）或多选（multiple）的按钮组
  通过 provide 将 variant/size 透传给子 EToggle，避免每个子项重复配置
-->
<script setup lang="ts">
import { ToggleGroupRoot } from 'reka-ui'
import { computed, provide } from 'vue'
import { cn } from '@/utils/cn'
import type { EToggleGroupProps, EToggleGroupEmits } from './types'

const props = withDefaults(defineProps<EToggleGroupProps>(), {
  type: 'single',
})

const emit = defineEmits<EToggleGroupEmits>()

provide('toggleGroup', {
  variant: computed(() => props.variant),
  size: computed(() => props.size),
})
</script>

<template>
  <ToggleGroupRoot
    data-slot="toggle-group"
    :type="(props.type as any)"
    :model-value="(props.modelValue as any)"
    :disabled="props.disabled"
    :class="cn('group/toggle-group flex w-fit items-center gap-1 rounded-md', props.class)"
    @update:model-value="(val) => emit('update:modelValue', val as string | string[])"
  >
    <slot />
  </ToggleGroupRoot>
</template>
