<!--
  EButtonGroup 按钮组组件
  将多个 EButton 视觉合并为相连的一组，用于相关联的操作集合
-->
<script setup lang="ts">
import { cn } from '@/utils/cn'
import { buttonGroupVariants } from './types'
import type { EButtonGroupProps } from './types'

const props = withDefaults(defineProps<EButtonGroupProps>(), {
  orientation: 'horizontal',
})
</script>

<template>
  <div
    role="group"
    data-slot="button-group"
    :data-orientation="props.orientation"
    :class="cn(buttonGroupVariants({ orientation: props.orientation }), props.class)"
  >
    <slot />
  </div>
</template>
